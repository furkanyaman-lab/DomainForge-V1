
import torch
from datetime import datetime, timezone
from typing import List, Tuple
from sentence_transformers import util

from app.schemas import SynthesizedQA, ValidatedQA
from app.rag.embedding import EmbeddingManager

class QAValidator:
    """This class validates the generated Q&A pairs for similarity, superficiality and hallucinations."""
    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        similarity_threshold: float = 0.85,
    ):
        self.embedding_manager = embedding_manager
        self.similarity_threshold = similarity_threshold
        self.seen_embeddings: List[torch.Tensor] = []

        self.forbidden_markers = [
            "chunk_", ".pdf", "page number", "context block", "reference 1", "reference [", "references ["
        ]

        self.negative_grounding_markers = [
            "provided references do not",
            "provided references establish",
            "referenced material",
            "not specify concrete",
            "do not specify",
            "not present in the provided",
            "does not specify a statistical",
            "additional standards, regulatory guidance, or domain-specific",
        ]

    def load_history(self, existing_items: List[SynthesizedQA]) -> None:
        if not existing_items:
            return

        questions = [item.question.strip() for item in existing_items if item.question.strip()]
        if not questions:
            return

        print(f"  🧠 [Validator Memory] {len(questions)} past records are being loaded into memory...")

        with torch.no_grad():
            embeddings = self.embedding_manager.model.encode(
                questions,
                convert_to_tensor=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

        if embeddings.ndim == 1:
            self.seen_embeddings.append(embeddings)
        else:
            for emb in embeddings:
                self.seen_embeddings.append(emb)

        print(f"  ✅ [Validator Memory] {len(self.seen_embeddings)} previous embeddings are ready for similarity checks.")

    def check(self, qa: SynthesizedQA) -> tuple[bool, str]:
        if len(qa.question.strip()) < 25:
            return False, "The question is very short (< 25 characters)"
        if len(qa.answer.strip()) < 50:
            return False, "The answer is very short (< 50 characters)"
        
        answer_lower = qa.answer.lower()
        combined_text = f"{qa.question} {qa.answer}".lower()
        
        for marker in self.forbidden_markers:
            if marker in combined_text:
                return False, f"Leak of a banned synthetic expression: '{marker}'"

        for neg_marker in self.negative_grounding_markers:
            if neg_marker in answer_lower:
                return False, f"Negative grounding escape detected: '{neg_marker}'"

        with torch.no_grad():
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

    def validate(self, qa_list: List[SynthesizedQA]) -> List[ValidatedQA]:
        valid_records: List[ValidatedQA] = []
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