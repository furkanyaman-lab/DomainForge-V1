from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.query_instruction = "Represent this sentence for searching relevant passages: "


    def generate_embeddings(
            self, texts: Union[str, List[str]], is_query: bool = False, batch_size: int = 64
            ) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        if is_query and "bge" in self.model_name.lower():
            texts = [f"{self.query_instruction}{t}" for t in texts]

        embeddings: np.ndarray = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 50,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()