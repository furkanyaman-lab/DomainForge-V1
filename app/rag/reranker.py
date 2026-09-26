from typing import List
from sentence_transformers import CrossEncoder
from app.schemas import RetrievedContext

class Reranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)

    def rerank(
            self, query: str, contexts: List[RetrievedContext], top_n: int = 5
    ) -> List[RetrievedContext]:
        if not contexts:
            return []

        pairs = [[query, ctx.text]for ctx in contexts]
        scores = self.model.predict(pairs)

        for ctx, score in zip(contexts, scores):
            ctx.score = round(float(score), 4)

        ranked = sorted(contexts, key=lambda x: x.score, reverse=True)
        return ranked[:top_n]