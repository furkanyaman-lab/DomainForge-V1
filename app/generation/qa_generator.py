import os
import json, math
from collections import Counter
from typing import List, Dict, Any, Optional
from pathlib import Path
import ollama
from openai import OpenAI

from app.ingestion.text_cleaner import clean_generated_answer, extract_json_payload
from app.schemas import GenerationProfile, ValidatedQAPair, SynthesizedQA, ContextSourceReference, RetrievedContext, GenerationDepth
from app.rag.retriever import RetrievedContext
from app.generation.qa_validator import QAValidator
from app.generation.summarizer import FrameworkSummarizer
from app.generation.prompts import (
    build_question_catalog_prompt,
    build_targeted_synthesis_prompt,
    build_balanced_gap_catalog_prompt
)

class QAGenerator:
    def __init__(self, model_name: str = "deepseek-r1:14b", api_key: Optional[str] = None, raw_dir: Optional[Path] = None):
        self.model_name = model_name
        self.client = ollama.Client()
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if self.api_key:
            masked_key = self.api_key[:8] + "..." + self.api_key[-4:]
            print(
                f"  🌐 [LLM Engine] OpenRouter CLOUD MODE is active! Model:"
                f" {self.model_name} | Key: {masked_key}"
            )
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            self.is_cloud = True
        else:
            print(
                f"  🖥️  [LLM Engine] WARNING: OPENROUTER_API_KEY not found! Being LOCAL"
                f" is active. Model: {self.model_name}"
            )
            self.client = ollama.Client()
            self.is_cloud = False
        
        self.raw_dir = raw_dir or Path("data/raw")
        self.summarizer = FrameworkSummarizer(
            model_name=self.model_name,
            output_dir=Path("data/interim")
        )

    def _generate_json(
        self, prompt: str, temperature: float = 0.3, max_retries: int = 3
    ) -> str:
        raw_text = ""

        if self.is_cloud:
            import time

            for attempt in range(1, max_retries + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        extra_headers={
                            "HTTP-Referer": "https://github.com/local-rag-pipeline",
                            "X-Title": "AI Governance QA Dataset Generator",
                        },
                    )
                    if (
                        response
                        and response.choices
                        and len(response.choices) > 0
                        and response.choices[0].message
                    ):
                        content = response.choices[0].message.content
                        if content:
                            raw_text = content
                            break

                    print(
                        f" [OpenRouter] No response received (Attempt {attempt}/{max_retries}), waiting..."
                    )
                    time.sleep(2)
                except Exception as e:
                    print(
                        f" [OpenRouter Error] (To try {attempt}/{max_retries}): {e}"
                    )
                    time.sleep(2)
        else:
            try:
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={"temperature": temperature},
                )
                raw_text = response.get("response", "")
            except Exception as e:
                print(f" [Ollama Error]: {e}")
                raw_text = ""

        if not raw_text:
            return "{}"

        return extract_json_payload(raw_text)

    def answer_question_with_context(
            self, question: str, contexts: List[RetrievedContext]
    ) -> Optional[SynthesizedQA]:

        prompt = build_targeted_synthesis_prompt(question, contexts)

        clean_json_str = self._generate_json(prompt, temperature=0.2)
        try:
            data = json.loads(clean_json_str)
        except Exception as e:
            print(f" Sentez JSON parsing error:{e}")
            return None

        raw_answer = data.get("answer", "")
        if not raw_answer:
            return None

        clean_answer = clean_generated_answer(raw_answer)

        used_refs = data.get("used_references_numbers", list(range(1, len(contexts) + 1)))
        source_refs = []
        for ref_idx in used_refs:
            if 1 <= ref_idx <= len(contexts):
                c = contexts[ref_idx - 1]
                source_refs.append(
                    ContextSourceReference(source=c.source, page=c.page, chunk_id=c.chunk_id)
                )

        clean_answer = clean_generated_answer(raw_answer)

        return SynthesizedQA(
            question= question,
            answer=clean_answer,
            sources= source_refs if source_refs else [
                ContextSourceReference(
                    source=contexts[0].source,
                    page=contexts[0].page,
                    chunk_id=contexts[0].chunk_id,
                )
            ],
            depth="comparative",
        )
    def analyze_existing_coverage(self, dataset: List[SynthesizedQA]) -> Dict[str, int]:
        doc_counter = Counter()
        for item in dataset:
            seen_docs_in_item = set()
            for src in item.sources:
                doc_name = src.source.replace(".pdf", "")
                seen_docs_in_item.add(doc_name)
            for doc in seen_docs_in_item:
                doc_counter[doc] += 1
        return dict(doc_counter)

    def generate_balanced_gap_catalog(
        self, target_count: int, coverage_summary: Dict[str, int]
    ) -> List[str]:
        framework_summaries = self.summarizer.get_or_create_summaries(self.raw_dir)

        prompt = build_balanced_gap_catalog_prompt(
            framework_summaries=framework_summaries,
            coverage_summary=coverage_summary,
            target_count=target_count,
        )

        clean_json_str = self._generate_json(prompt, temperature=0.3)
        try:
            data = json.loads(clean_json_str)
            catalog = data.get("catalog", [])
        except Exception as e:
            print(f" Catalogue JSON parsing error: {e}")
            catalog = []

        return catalog[:target_count]

    def generate_topdown_dataset(
        self,
        retriever: RetrievedContext,
        validator: QAValidator,
        total_target: int,
        output_file: Optional[Path] = None,
        max_retries_per_question: int = 1,
    ) -> List[SynthesizedQA]:

        clean_dataset: List[SynthesizedQA] = []
        existing_questions = set()

        if output_file and output_file.exists():
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            record = SynthesizedQA.model_validate_json(line)
                            clean_dataset.append(record)
                            existing_questions.add(record.question.strip().lower())
                        except Exception:
                            continue

            print(f"  📂 [Resume] Number of records found: {len(clean_dataset)}/{total_target}")

        if len(clean_dataset) >= total_target:
            print(f"  ✨ The target has already been reached ({len(clean_dataset)}/{total_target}). Production is being skipped.")
            return clean_dataset

        if clean_dataset:
            validator.load_history(clean_dataset)

        coverage = self.analyze_existing_coverage(clean_dataset)
        print(f"  📊 Current Coverage Distribution: {coverage}")

        remaining_needed = total_target - len(clean_dataset)
        print(f"\n🚀 Production is starting for the remaining {remaining_needed} records...")

        catalog_buffer_size = min(remaining_needed * 2, 20)
        catalog = self.generate_balanced_gap_catalog(
            target_count=catalog_buffer_size, coverage_summary=coverage
        )
        catalog_idx = 0
        total_attempts = 0
        max_total_attempts = remaining_needed * 4

        print(f"\n Running Resilient Top-Down Synthesis (Target: {total_target} VALID pairs)...")
        while len(clean_dataset) < total_target and total_attempts < max_total_attempts:
            total_attempts += 1

            if catalog_idx >= len(catalog):
                current_needed = total_target - len(clean_dataset)
                next_batch_size = min(current_needed * 2, 20)
                print(f"  🔄 Catalog exhausted, fetching fresh batch ({next_batch_size} questions)...")
                
                current_coverage = self.analyze_existing_coverage(clean_dataset)
                fresh_batch = self.generate_balanced_gap_catalog(
                    target_count=next_batch_size, coverage_summary=current_coverage
                )
                catalog.extend(fresh_batch)

            if catalog_idx >= len(catalog):
                print(" No more questions could be generated into catalog.")
                break

            current_question = catalog[catalog_idx]
            catalog_idx += 1

            if current_question.strip().lower() in existing_questions:
                continue

            current_valid_count = len(clean_dataset) + 1
            print(f"\n[{current_valid_count}/{total_target}] Question: {current_question[:75]}...")

            question_passed = False

            for attempt in range(1, max_retries_per_question + 2):
                search_k = 4 if attempt == 1 else 6
                contexts = retriever.retrieve(query=current_question, top_k=search_k)

                if not contexts:
                    print(f"   ⚠️ [Attempt {attempt}] No contexts found.")
                    continue

                candidate = self.answer_question_with_context(current_question, contexts)
                if not candidate:
                    print(f"   ⚠️ [Attempt {attempt}] Synthesis produced empty answer.")
                    continue

                valid_batch = validator.validate([candidate])
                if valid_batch:
                    clean_dataset.append(candidate)
                    existing_questions.add(candidate.question.strip().lower())
                    question_passed = True

                    if output_file:
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_file, "a", encoding="utf-8") as f:
                            f.write(candidate.model_dump_json() + "\n")

                    print(f"   ✅ ACCEPTED! Valid Count: {len(clean_dataset)}/{total_target}")
                    break
                else:
                    print(f"   🔁 [Attempt {attempt}] Validation rejected. Retrying with wider context...")

            if not question_passed:
                print(f"   ❌ Question permanently skipped after {max_retries_per_question} attempts. Moving to next topic in catalog.")

        print(f"\n✨ Generation finished: Exactly {len(clean_dataset)}/{total_target} valid records obtained.")
        return clean_dataset

    def generate_balanced_dataset(
            self,
            retriever: RetrievedContext,
            validator: QAValidator,
            doc_distribution: Dict[str, int],
            total_target: int,
            output_file: Path | None = None,
            batch_size : int = 3,
    ) -> List[ValidatedQAPair]:

        if not doc_distribution:
            raise ValueError("The document distribution cannot be empty. Indexing must be carried out first.")

        total_chunks = sum(doc_distribution.values())
        doc_targets: Dict[str,int] = {}

        for doc_id, chunk_count in doc_distribution.items():
            ratio = chunk_count / total_chunks
            allocated = max(1, round(total_target * ratio))
            doc_targets[doc_id] = allocated
            print(f"  📊 {doc_id}: {chunk_count} chunk (%{ratio*100:.1f}) -> Goal: {allocated} Q/A")

        diff = total_target - sum(doc_targets.values())
        if diff != 0:
            top_doc = max(doc_targets, key=doc_targets.get)
            doc_targets[top_doc] = max(1, doc_targets[top_doc] + diff)

        total_accumulated : List[ValidatedQAPair] = []

        for doc_id, target, in doc_targets.items():
            print(f"\n▶️ [{doc_id}] Production is starting (Target: {target} Clean Q&A)...")
            doc_accumulated: List[ValidatedQAPair] = []
            attempts = 0
            max_attempts = math.ceil( target / batch_size) * 4 # Infinite loop barrier

            while len(doc_accumulated) < target and attempts < max_attempts:
                attempts += 1
                needed = min(batch_size, target - len(doc_accumulated))

                query = f"Key frameworks, trustworthy characteristics, risk management and requirements in {doc_id}"
                try:
                    contexts = retriever.retrieve_by_document(query, document_id=doc_id, top_k=5)
                except AttributeError:
                    contexts = retriever.retrieve(f"{doc_id}: {query}", top_k=5)

                if not contexts:
                    print(f"   ⚠️ Context could not be retrieved for {doc_id}, skipping.")
                    break

                profile = GenerationProfile(
                    depth=GenerationDepth.DEEP,
                    question_count=needed,
                    answer_length="Detailed and technical",
                )

                candidates = self.generate(contexts, profile)
                valid_batch = validator.validate(candidates)

                if valid_batch:
                    if output_file:
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_file, "a", encoding="utf-8") as f:
                            for item in valid_batch:
                                f.write(item.model_dump_json() + "\n")

                    doc_accumulated.extend(valid_batch)
                    print(f" +{len(valid_batch)} clean Q&As added. Progress: {len(doc_accumulated)}/{target}")
                else:
                    print("   ⚠️ Candidates have been flagged during validation (duplicates or quality filter).")

            total_accumulated.extend(doc_accumulated)
            print(f" [{doc_id}] Completed: {len(doc_accumulated)}/{target} records.")

        return total_accumulated