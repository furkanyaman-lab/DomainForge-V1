from pydantic import BaseModel, Field

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