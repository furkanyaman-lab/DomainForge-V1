import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.schemas import (
    PipelineConfig,
    PipelineManifest,
    GenerationProfile,
    QuestionDepth,
    TrainingProfile,
    LoRAProfile,
)

from app.ingestion.pdf_loader import load_pdfs
from app.rag.chunker import SemantikChunker
from app.rag.embedding import EmbeddingManager
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.generation.qa_generator import QAGenerator
from app.generation.qa_validator import QAValidator
from app.training.formatter import DatasetFormatter
from app.training.trainer import DomainTrainer
from app.evaluation.evaluator import ModelEvaluator

class DomainForgePipeline:
    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig

        self.raw_dir = BASE_DIR / self.config.raw_data_dir
        self.processed_dir = BASE_DIR / self.config.processed_dir
        self.final_dir = BASE_DIR / self.config.final_dir
        self.chroma_dir = BASE_DIR / self.config.chroma_dir
        self.models_dir = BASE_DIR / self.config.models_dir

        self.qa_dataset_file = self.processed_dir / "qa_dataset.jsonl"
        self.train_file = self.final_dir / "train.jsonl"
        self.eval_file = self.final_dir / "eval.jsonl"
        self.eval_result_file = self.final_dir / "eval_results.jsonl"

        self.embedding_manager = EmbeddingManager()

    def run_ingestion_and_indexing(self) -> int:
        """Stage 1: PDF Upload, Chunking and ChromaDB Indexing"""

        print("\n🔹 [STAGE 1/6] Ingestion & Vector Store Indexing...")

        documents = load_pdfs(self.raw_dir)
        print(f" Number of documents uploaded: {len(documents)}")

        chunker = SemantikChunker(
            model_name="all-MiniLM-L6-v2",
            threshold=getattr(self.config, "chunk_similarity_threshold", 0.85),
            max_chars=getattr(self.config, "chunk_max_chars", 1200),
        )

        chunks = chunker.chunk_corpus(documents)
        print(f" Number of semantic chunks generated: {len(chunks)}")

        vector_store = VectorStore(
            persist_dir=str(self.chroma_dir),
            embedding_manager=self.embedding_manager,
        )
        vector_store.add_chunks(chunks)
        print(" ChromaDB has been successfully updated.")
        return len(chunks)

    def run_generation_and_validation(self, count: int | None= None, model: str | None = None) -> int:
        """Stage 2: Context Extraction with RAG, Question-Answer Generation and Validation"""
        target_count = count or self.config.generation_question_count
        active_model = model or getattr(self.config, "model_name", None) or self.config.ollama_model
        print(f"\n🔹 [STAGE 2/6] Dynamic Top-Down Q/A Synthesis (Target: {target_count})...")

        vector_store = VectorStore(
            persist_dir= str(self.chroma_dir),
            embedding_manager= self.embedding_manager,
        )
        if vector_store.count() == 0:
            raise RuntimeError("ChromaDB is empty! Please run 'make ingest' first.")
        
        retriever = Retriever(vector_store)
        generator = QAGenerator(model_name=active_model, raw_dir=self.raw_dir)
        validator = QAValidator(
            embedding_manager=self.embedding_manager,
            similarity_threshold=self.config.similarity_threshold,
        )

        valid_dataset = generator.generate_topdown_dataset(
            retriever=retriever,
            validator=validator,
            total_target=target_count,
            output_file=self.qa_dataset_file,
        )
        return len(valid_dataset)

    def run_dataset_formatting(self) -> tuple[int, int]:
        """Stage 3: Conversion to ChatML Format and Separation of Train and Eval Sets"""
        print("\n🔹 [STAGE 3/6] Dataset Formatting (ChatML Split)...")
        formatter = DatasetFormatter()
        summary = formatter.process_and_export(
            input_qa_path=self.qa_dataset_file,
            output_dir=self.final_dir,
            train_ratio=self.config.train_ratio,
            seed=self.config.seed,
        )
        print(f" Train Set : {summary.train_count} count -> {summary.train_path}")
        print(f" Eval Set  : {summary.eval_count} count -> {summary.eval_path}")
        return summary.train_count, summary.eval_count

    def run_fine_tuning(self) -> None:
        """Stage 4: LoRA/PEFT Fine-tuning"""
        print("\n🔹 [STAGE 4/6] Fine-tuning the engine...")
        if self.config.skip_training:
            print(" [DRY-RUN] Training has been skipped (config.skip_training=True).")
            return

        print(" Fine-tuning is starting...")
        trainer_engine = DomainTrainer(
            train_profile=TrainingProfile(
                base_model_id=self.config.base_model_id,
                output_dir=str(self.models_dir),
            ),
            lora_profile=LoRAProfile(),
        )
        trainer = trainer_engine.build_trainer(
            train_path=str(self.train_file),
            eval_path=str(self.eval_file),
        )

        trainer.train()
        trainer.save_model(str(self.models_dir))
        print(f" Model saved successfully: {self.models_dir}")

    def run_evaluation(self) -> None:
        """Stage 5: Evaluation and Similarity Report"""
        print("\n🔹 [STAGE 5/6] Model Evaluation & Benchmarking...")
        eval_target = (
            self.eval_file
            if (self.eval_file.exists() and self.eval_file.stat().st_size > 0)
            else self.train_file
        )

        adapter = (
            self.models_dir
            if (self.models_dir.exists() and not self.config.skip_training)
            else None
        )

        evaluator = ModelEvaluator(
            base_model_id=self.config.base_model_id,
            adapter_path=Path(adapter),
            embedding_manager=self.embedding_manager,
        )
        summary = evaluator.evaluate(
            eval_path=eval_target,
            output_file=self.eval_result_file,
        )

        print(f" Record evaluated: {summary.total_samples}")
        print(f" Semantic similarity score: {summary.avg_semantic_sim_base}")
        print(f" Report sealed: {self.eval_result_file}")

    def execute_all(self, count: int | None = None, model: str | None = None) -> PipelineManifest:
        """It runs the entire pipeline from end to end and generates a manifest."""
        print("=" * 60)
        print("DOMAINFORGE V1 — PIPELINE ORCHESTRATION")
        print("=" * 60)

        chunks_count = self.run_ingestion_and_indexing()
        valid_qa_count = self.run_generation_and_validation(count=count, model=model)
        train_count, eval_count = self.run_dataset_formatting()
        self.run_fine_tuning()
        self.run_evaluation()

        manifest = PipelineManifest(
            executed_at=datetime.now(timezone.utc).isoformat(),
            stage= "all",
            status="COMPLETED",
            total_chunks=chunks_count,
            validated_qa_count=valid_qa_count,
            train_samples=train_count,
            eval_samples=eval_count,
            model_output_dir=str(self.models_dir),
            evaluation_summary_file=str(self.eval_result_file),
        )

        manifest_path = self.final_dir / "pipeline_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        print("\n" + "=" * 60)
        print(" PIPELINE COMPLETELY FINISHED!")
        print(f" Manifest File: {manifest_path}")
        print("=" * 60)
        return manifest

def main():
    parser = argparse.ArgumentParser(description="DomainForge V1 CLI Orchestrator")
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["ingest", "generate", "format", "train", "eval", "all"],
        help="Pipeline stage to execute",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model identifier",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of question-answer pairs to generate",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Actually triggers LoRA fine-tuning",
    )
    args = parser.parse_args()

    config = PipelineConfig(skip_training=not args.train)
    pipeline = DomainForgePipeline(config=config)

    if args.stage == "ingest":
        pipeline.run_ingestion_and_indexing()
    elif args.stage == "generate":
        pipeline.run_generation_and_validation(count=args.count, model=args.model)
    elif args.stage == "format":
        pipeline.run_dataset_formatting()
    elif args.stage == "train":
        pipeline.run_fine_tuning()
    elif args.stage == "eval":
        pipeline.run_evaluation()
    elif args.stage == "all":
        pipeline.execute_all(count=args.count, model=args.model)


if __name__ == "__main__":
    main()
