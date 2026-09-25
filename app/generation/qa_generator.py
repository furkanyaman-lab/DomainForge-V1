import json
from typing import List
import ollama

from app.schemas import GenerationProfile, GeneratedQA, RetrievedContext
from app.generation.prompts import buil_synthetic_qa_prompt

class QAGenerator:
    def __init__(self, model_name: str = "deepseek-r1:14b"):
        self.model_name = model_name
        self.client = ollama.Client()

    def generate(
            self, context: RetrievedContext, profile: GenerationProfile
    ) -> List[GeneratedQA]:
        prompt = buil_synthetic_qa_prompt(context, profile)

        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            format="json",
            options={"temperature" : profile.temperature},
        )

        data = json.loads(response["response"])
        pairs = data.get("pairs", [])

        return [
            GeneratedQA(
                question=p["question"],
                answer=p["answer"],
                source= context.source,
                page=context.page,
                chunk_id= context.chunk_id,
                depth=profile.depth.value,
                retrieval_score=context.score,
            )
            for p in pairs
        ]
    def generate_batch(
            self, contexts: List[RetrievedContext], profile: GenerationProfile
    ) -> List[GeneratedQA]:
        return [qa for ctx in contexts for qa in self.generate(ctx, profile)]