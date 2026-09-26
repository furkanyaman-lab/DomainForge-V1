import json
from typing import List
import ollama

from app.schemas import GenerationProfile, SynthesizedQA, ContextSourceReference, RetrievedContext
from app.generation.prompts import build_synthesized_qa_prompt

class QAGenerator:
    def __init__(self, model_name: str = "deepseek-r1:14b"):
        self.model_name = model_name
        self.client = ollama.Client()

    def generate(
            self, contexts: list[RetrievedContext], profile: GenerationProfile
    ) -> List[SynthesizedQA]:
        prompt = build_synthesized_qa_prompt(contexts, profile)

        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            format="json",
            options={"temperature" : profile.temperature},
        )

        data = json.loads(response["response"])
        pairs = data.get("pairs", [])

        results: List[SynthesizedQA] = []
        for p in pairs:
            used_refs = p.get("used_references_numbers", list(range(1, len(contexts)+ 1)))
            source_refs = []

            for ref_idx in used_refs:
                if 1 <= ref_idx <= len(contexts):
                    c = contexts[ref_idx - 1]
                    source_refs.append(
                        ContextSourceReference(source=c.source, page=c.page, chunk_id=c.chunk_id)
                    )

            results.append(
                SynthesizedQA(
                    question=p["question"],
                    answer=p["answer"],
                    sources=source_refs if source_refs else[
                        ContextSourceReference(
                            source=contexts[0].source,
                            page=contexts[0].page,
                            chunk_id=contexts[0].chunk_id
                        )
                    ],
                    depth= profile.depth.value,
                )
            )
        return results