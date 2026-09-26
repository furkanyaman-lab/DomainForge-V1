from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

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
    question_count: int = Field(default=2, ge=1, le=5, description="Number of questions to be generated from each context")
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