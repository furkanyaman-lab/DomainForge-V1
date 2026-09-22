import re
from typing import List
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F

from app.schemas   import Document, Chunk

class SemantikChunker:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        threshold: float = 0.85,
        max_chars: int = 1200,
    ):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.max_chars = max_chars

    def _split_sentences(self, text:str) -> List[str]:
        return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text)if s.strip()]

    def chunk_document(self, doc: Document) -> List[Chunk]:
        sentences = self._split_sentences(doc.text)
        if not sentences:
            return[]

        embeddings = self.model.encode(sentences, convert_to_tensor=True)
        similarities = F.cosine_similarity(embeddings[:-1], embeddings[1:], dim=1)

        chunks: List[Chunk] = []
        current_sentences: List[str] = [sentences[0]]

        for sim, next_sentence in zip(similarities, sentences[1:]):
            current_text = " ".join(current_sentences)

            if sim.item() < self.threshold or len(current_text) >= self.max_chars:
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc.document_id}_p{doc.page}_c{len(chunks)}",
                        document_id= doc.document_id,
                        source=doc.source,
                        page=doc.page,
                        text=current_text,
                    )
                )
                current_sentences = []

            current_sentences.append(next_sentence)

        if current_sentences:
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.document_id}_p{doc.page}_c{len(chunks)}",
                    document_id=doc.document_id,
                    source=doc.source,
                    page=doc.page,
                    text= " ".join(current_sentences),
                )
            )
        return chunks

    def chunk_corpus(self, docs: List[Document]) -> List[Chunk]:
        return [chunk for doc in docs for chunk in self.chunk_document(doc)]
