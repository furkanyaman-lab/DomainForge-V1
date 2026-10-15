import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import torch
from peft import PeftModel
from sentence_transformers import util  
from enum import Enum

from app.schemas import EvalSampleResult, EvaluationSummary
from app.rag.embedding import EmbeddingManager
from app.training.model_loader import ModelLoader

class ModelEvaluator:

    def __init__(
            self,
            base_model_id: str = "Qwen/Qwen2.5-3B-Instruct",
            adapter_path: str | Path | None = None,
            embedding_manager: EmbeddingManager | None = None,
            max_new_tokens: int = 300,
            temperature: float = 0.2, 
            ):
        self.base_model_id = base_model_id
        self.adapter_path = Path(adapter_path) if adapter_path else None
        self.embedding_manager = embedding_manager
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

    def generate(self, model, tokenizer, question: str) -> str:

        messages = [
            {"role": "system", "content" : " You are an expert AI Governance Advisor."},
            {"role": "user", "content": question},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize= False, add_generatation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens = self.max_new_tokens,
                temperature = self.temperature,
                do_sample = self.temperature > 0.0,
                pad_token_id = tokenizer.pad_token_id,
            )

        gen_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    def evaluate(self, eval_path: Path, output_file: Path | None = None) -> EvaluationSummary:

        if not eval_path.exists():
            raise FileNotFoundError(f"Evaluation data not found: {eval_path}")

        loader = ModelLoader(self.base_model_id)
        model, tokenizer = loader.load()

        adapter_dir = Path(self.adapter_path) if self.adapter_path else None
        has_adapter = False

        if adapter_dir and adapter_dir.exists():
            print(f"✅ LoRA adapter is being successfully integrated: {adapter_dir}")
            model = PeftModel.from_pretrained(model, str(adapter_dir))
            has_adapter = True
        else:
            print(f"⚠️ WARNING: Adapter not found or invalid path: {adapter_dir}")

        model.eval()

        with open(eval_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        total_records = len(records)
        print(f"Total number of records to be processed: {total_records}")

        results: List[EvalSampleResult] = []

        for idx, item in enumerate(records,1):
            question = item["messages"][1]["content"]
            ground_truth = item["messages"][2]["content"]
            
            if has_adapter:
                with model.disable_adapter():
                    base_resp = self.generate(model, tokenizer, question)

                ft_resp = self.generate(model, tokenizer, question)
            else:
                base_resp = self.generate(model, tokenizer, question)
                ft_resp = "[Adapter Not Loaded - Baseline Mode]"

            sim_base, sim_ft = 0.0, 0.0
            if self.embedding_manager:
                emb_base = self.embedding_manager.model.encode(
                    base_resp, convert_to_tensor=True, normalize_embeddings=True
                )

                emb_gt = self.embedding_manager.model.encode(
                    ground_truth, convert_to_tensor=True, normalize_embeddings=True
                )

                sim_base = round(float(util.cos_sim(emb_base, emb_gt)[0][0]), 4)

                if has_adapter:
                    emb_ft = self.embedding_manager.model.encode(
                    ft_resp, convert_to_tensor=True, normalize_embeddings=True
                )
                    sim_ft = round(float(util.cos_sim(emb_ft, emb_gt)[0][0]), 4)

            results.append(
                EvalSampleResult(
                    question=question,
                    ground_truth=ground_truth,
                    base_response=base_resp,
                    finetuned_response=ft_resp if self.adapter_path else "[Adapter Not Loaded - Baseline Mode]",
                    semantic_sim_base=sim_base,
                    semantic_sim_ft=sim_ft if self.adapter_path else 0.0,
                    token_f1_base=0.0,
                    token_f1_ft=0.0,
                    sources=item.get("metadata", {}).get("sources", []),
                )
            )
            print(f"[{idx}/{total_records}] Base: {sim_base} | Fine-Tuned: {sim_ft}")

        avg_base = round(sum(r.semantic_sim_base for r in results) / len(results), 4) if results else 0.0
        avg_ft = round(sum(r.semantic_sim_ft for r in results) / len(results), 4) if results else 0.0
        
        summary = EvaluationSummary(
                eval_model_id=self.base_model_id,
                total_samples=len(results),
                avg_semantic_sim_base=avg_base,
                avg_semantic_sim_ft=avg_ft if self.adapter_path else 0.0,
                avg_token_f1_base=0.0,
                avg_token_f1_ft=0.0,
                samples=results,
                evaluated_at= datetime.now(timezone.utc).isoformat()
            )

        print("\n" + "=" * 50)
        print(f"📊 COMPARISON REPORT ({total_records} samples)")
        print(f"Average Similarity of Raw Base Model       : {avg_base}")
        print(f"Fine-Tuned Model Average Similarity    : {avg_ft}")
        print(f"Net Improvement (Delta)                    : +{round(avg_ft - avg_base, 4)}")
        print("=" * 50)

        if output_file:
            json_target = (
                output_file.with_suffix(".json")
                if output_file.with_suffix == ".jsonl"
                else output_file
            )
            json_target.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                    f.write(summary.model_dump_json(indent=2))
            print(f"Report sealed: {json_target}")

        return summary