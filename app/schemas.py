from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone

class Document(BaseModel):
    document_id: str
    source: str
    page: int
    text: str

class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    source: str
    page: int
    text: str

class RetrievedContext(BaseModel):
    """Represents a text chunk retrieved from the vector store with semantic similarity score and full provenance."""

    chunk_id: str = Field(
        ...,
        description="Unique identifier of the source chunk formatted as '{document_id}_p{page}_c{index}'",
        examples=["NIST.AI.100-1_p14_c2"],
    )
    document_id: str = Field(
        ...,
        description="Unique identifier or slug of the source document",
        examples=["NIST.AI.100-1"],
    )
    source: str = Field(
        ...,
        description="Original PDF filename including the extension",
        examples=["NIST.AI.100-1.pdf"],
    )
    page: int = Field(
        ...,
        ge=1,
        description="Original 1-based page number where the chunk is located",
        examples=[14],
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Raw textual content extracted from the retrieved chunk",
    )
    score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Cosine similarity score indicating relevance to the query (1.0 = identical, -1.0 = opposite)",
        examples=[0.8421],
    )

class QuestionDepth(str, Enum):
    FOUNDATIONAL = "foundational"
    TECHNICAL = "technical"
    COMPARATIVE = "comparative"

class GenerationProfile(BaseModel):
    question_count: int = Field(default=2, ge=1, le=10, description="Number of questions to be generated from each context")
    answer_length: str = Field(default="detailed", description="Answer length: concise, moderate, detailed")
    depth: QuestionDepth = Field(default=QuestionDepth.COMPARATIVE, description="The level of technical depth of the question")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="LLM temperature value (low = more faithful)")

class GeneratedQA(BaseModel):
    question: str = Field(..., min_length=10, description="Generated technical question")
    answer: str = Field(..., min_length=20, description="Response based solely on the provided context")
    source: str = Field(..., description="Name of the PDF source on which the answer is based")
    page: int = Field(..., ge=1, description="Source page number")
    chunk_id: str = Field(..., description="The chunk ID to which the context belongs")
    depth: str = Field(..., description="Target depth during production")
    retrieval_score: float = Field(..., description="Similarity score of the part used")

class ContextSourceReference(BaseModel):
    source: str
    page: int
    chunk_id: str

class SynthesizedQA(BaseModel):
    question : str = Field(..., min_length=15, description="A synthesised technical question")
    answer: str = Field(..., min_length=40, description="A comprehensive answer based on a comparison of sources")
    sources: List[ContextSourceReference] = Field(..., description="All the contexts on which the answer is based")
    depth: str


class ValidatedQA(BaseModel):
    question: str
    answer: str
    sources: List[ContextSourceReference]
    depth: str
    validated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc). isoformat())

class ChatMessage(BaseModel):
    role: str = Field(..., description="'system', 'user' or 'asisstant'")
    content: str

class TrainingExample(BaseModel):
    messages: List[ChatMessage]
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provenance, source chunks and depth information"
    )

class DatasetSplitSummary(BaseModel):
    total_count: int
    train_count: int
    eval_count: int
    train_path: str
    eval_path: str

class TrainingProfile(BaseModel):
    base_model_id: str = "Qwen/Qwen2.5-3B-Instruct"
    output_dir: str = "models/fine-tuned-governance"
    learning_rate: float = 2e-4
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    max_seq_length: int = 1024
    logging_steps: int = 2
    save_strategy: str = "no"
    warmup_steps: int = 5
    seed: int = 42

class LoRAProfile(BaseModel):
    r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = Field(
        default_factory=lambda:["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"] 
    )
    bias: str = "none"

class EvalSampleResult(BaseModel):
    question: str
    ground_truth: str
    base_response: str
    finetuned_response: str
    semantic_sim_base: float
    semantic_sim_ft: float
    token_f1_base: float
    token_f1_ft: float 
    sources: List[Dict[str, Any]] = Field(default_factory=list)

class EvaluationSummary(BaseModel):
    eval_model_id: str
    total_samples: int
    avg_semantic_sim_base: float
    avg_semantic_sim_ft: float
    avg_token_f1_base: float
    avg_token_f1_ft: float
    samples: List[EvalSampleResult]
    evaluated_at: str

class PipelineConfig(BaseModel):
    raw_data_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    final_dir: str = "data/final"
    chroma_dir: str = "data/chroma_db"
    models_dir: str = "models/fine-tuned-governance"

    # RAG & Generation
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 5
    generation_question_count: int = 3
    ollama_model: str = "deepseek-r1:14b"
    similarity_threshold: float = 0.85
    chunk_similarity_threshold: float = 0.85
    chunk_max_chars: int = 1200

    # Dataset Split
    train_ratio: float = 0.8
    seed: int = 42

    # Fine-Tuning & Evaluation
    base_model_id: str = "Qwen/Qwen2.5-3B-Instruct"
    skip_training: bool = False # -> For development/dry-run: True

class PipelineManifest(BaseModel):
    executed_at: str
    stage: str
    status: str
    ingested_documents: str
    total_chunks: int
    validated_qa_count: int
    train_samples: int
    eval_samples: int
    model_output_dir: str
    evaluation_summary_file: str | None = None

class GenerationDepth(str, Enum):
    FOUNDATIONAL = "foundational"
    TECHNICAL = "technical"
    COMPARATIVE = "comparative"

class ValidatedQAPair(BaseModel):

    question: str = Field(description="The technical governance question raised")
    answer: str = Field(description="A detailed and verified answer")
    sources: List[Dict[str, Any]] = Field(default_factory= List, description="Provenance information regarding the document, page and chunk on which the response is based")
    semantic_similarity: Optional[float] = Field( default=None, description="The semantic similarity or originality score calculated during the validation stage")