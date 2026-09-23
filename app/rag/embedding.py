from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(
            self, texts: Union[str, List[str]], batch_size: int = 64
            ) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        embeddings: np.ndarray = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 50,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()