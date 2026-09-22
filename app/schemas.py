from pydantic import BaseModel

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