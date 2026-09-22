
from pathlib import Path

import fitz

from app.schemas import Document

def load_pdf(path: str | Path) -> list[Document]:
    """Read a PDF page by page and return Document objects."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".pdf": # If the file is not a PDF, raise a ValueError
        raise ValueError("File must be a PDF")

    documents = []
    document_id = path.stem

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            documents.append(
                Document(
                    document_id=document_id,
                    source=path.name,
                    page=page_number,
                    text=page.get_text("text"),
                )
            )

    return documents

def load_pdfs(directory: str | Path):
    """Read all PDFs in a directory."""
    directory = Path(directory)
    documents = []
    filename = directory.name

    for pdf in sorted(directory.glob("*.pdf")):
        documents.extend(load_pdf(pdf))

    return documents, filename
