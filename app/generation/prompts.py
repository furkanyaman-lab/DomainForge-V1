from typing import List
from app.schemas import RetrievedContext

SYSTEM_GOVERNANCE_EXPERT = """You are a specialized AI Governance, Ethics, and Risk Management technical expert.
Your responses must be strictly grounded in the provided contextual references (such as NIST AI RMF, UNESCO Recommendations, and OECD AI Principles).
Do not fabricate information, extrapolate without evidence, or use outside unverified facts."""

def format_retrieved_context(contexts: List[RetrievedContext]) -> str:

    blocks = []
    for ctx in contexts:
        block = (
            f"[CONTEXT BLOCK START]\n"
            f"Source: {ctx.source}\n"
            f"Page: {ctx.page}\n"
            f"Chunk ID: {ctx.chunk_id}\n"
            f"Content: {ctx.text}\n"
            f"[CONTEXT BLOCK END]" 
        )
        blocks.append(block)
    return "\n\n".join(blocks)

def build_rag_qa_prompt(query: str, contexts: List[RetrievedContext]) -> str:

    context_str = format_retrieved_context(contexts)
    return f"""{SYSTEM_GOVERNANCE_EXPERT}

### Verified Reference Context:
{context_str}

### User Question:
{query}

### Grounded Answer:"""