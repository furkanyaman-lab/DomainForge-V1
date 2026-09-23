from pathlib import Path
from typing import List, Optional, Union
import chromadb
from chromadb.config import Settings

from app.schemas import Chunk
from app.rag.embedding import EmbeddingManager

class VectorStore:
    def __init__(
        self,
        persist_dir: Union[str, Path] = "data/vectorstore",
        collection_name: str = "domainforge_governance",
        embedding_manager: Optional[EmbeddingManager] = None,

        ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name
        self.embedding_manager = embedding_manager or EmbeddingManager()

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection = self.client.get_or_create_collection(
            name= self.collection_name,
            metadata={"hnsw:space" : "cosine"},
        )

    def add_chunks(self, chunks: List[Chunk], batch_size: int = 256 ) -> None:
        current_count = self.collection.count()
        if current_count > 0:
            print(f"[VECTOR STORE] Collection is already full ({current_count} records). Indexing skipped.")

        if not chunks:
            print("[VECTOR STORE] No chunks found to add.")

        total_chunks = len(chunks)
        print(f"[VECTOR STORE] {total_chunks} chunks are being indexed to disk...")

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]

            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.text for chunk in batch]
            metadatas = [
                {
                    "chunk_id" : chunk.chunk_id,
                    "document_id" : chunk.document_id,
                    "source" : chunk.source,
                    "page" : chunk.page,
                }
                for chunk in batch
            ]

            embeddings = self.embedding_manager.generate_embeddings(documents)

            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        print(f"[VECTOR STORE] Indexing completed and saved. Total: {self.collection.count()}")

    def count(self) -> int:
        return self.collection.count()    