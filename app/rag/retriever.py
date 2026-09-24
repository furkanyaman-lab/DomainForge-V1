from typing import List, Optional

from app.schemas import RetrievedContext
from app.rag.embedding import EmbeddingManager
from app.rag.vector_store import VectorStore

class Retriever:
    def __init__(
            self,
            vector_store: VectorStore,
            embedding_manager: Optional[EmbeddingManager] = None,
            top_k: int = 4,
            ):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager or vector_store.embedding_manager
        self.top_k = top_k

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedContext]:
        k =top_k or self.top_k
        query_embedding = self.embedding_manager.generate_embeddings([query], is_query=True)

        results = self.vector_store.collection.query(
            query_embeddings = query_embedding,
            n_results = k,
            include = ["documents", "metadatas", "distances"],
        )

        retrieved_contexts : List[RetrievedContext] = []

        if not results or not results["documents"] or not results["documents"][0]:
            return retrieved_contexts

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc_text, meta, dist in zip(documents,metadatas,distances):
            similarity_score = float(1.0 - dist)

            retrieved_contexts.append(
                RetrievedContext(
                    chunk_id=meta["chunk_id"],
                    document_id=meta["document_id"],
                    source=meta["source"],
                    page=meta["page"],
                    text=doc_text,
                    score= round(similarity_score, 4),
                )
            )

        return retrieved_contexts