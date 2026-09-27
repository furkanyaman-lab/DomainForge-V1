
import torch
from datetime import datetime, timezone
from typing import List, Tuple
from sentence_transformers import util

from app.schemas import SynthesizedQA, ValidatedQA, RetrievedContext
from app.rag.embedding import EmbeddingManager

class QAValidator:
    def __init__(
            self,
            embedding_manager: EmbeddingManager,
            similarity_threshold: float = 0.85,
            ):
            self.embedding_manager = embedding_manager
            self.similarity_threshold = similarity_threshold
            self.seen_embeddings = []

            self.forbidden_markers = [
                "chunk_", ".pdf", "page number", "context block", "reference 1"
            ]

    def check(self, qa: SynthesizedQA) -> tuple[bool, str]:

        if len(qa.question.strip()) < 25:
            return False, "The question is very short (< 25 characters)"
        if len(qa.answer.strip()) < 50:
            return False, "The answer is very short (< 50 characters)"
        
        combined_text = f"{qa.question} {qa.answer}".lower()
        for marker in self.forbidden_markers:
            if marker in combined_text:
                return False, f"Leak of a banned synthetic expression: '{marker}'"

        q_emb = self.embedding_manager.model.encode(
            qa.question, convert_to_tensor=True, normalize_embeddings=True
        )

        if len(self.seen_embeddings) > 0:
            seen_tensor = torch.stack(self.seen_embeddings)
            cos_scores = util.cos_sim(q_emb, seen_tensor)[0]
            max_sim = float(cos_scores.max())
            if max_sim >= self.similarity_threshold:
                return False, f"Duplicate question ({max_sim:.2f} >= {self.similarity_threshold})"

        self.seen_embeddings.append(q_emb)
        return True, "Passed"

    def validate(self, qa_list : List[SynthesizedQA]) -> List[ValidatedQA]:

        valid_records : List[ValidatedQA] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for qa in qa_list:
            is_valid, reason = self.check(qa)
            if is_valid:
                valid_records.append(
                    ValidatedQA(
                        question=qa.question,
                        answer=qa.answer,
                        sources=qa.sources,
                        depth=qa.depth,
                        validated_at=now_iso,
                    )
                )
                print(f"✅ [ PASSED ] {qa.question[:50]}...")
            else:
                print(f"❌ [ELIMINATED] Reason: {reason} | Question: {qa.question[:50]}...")
        return valid_records