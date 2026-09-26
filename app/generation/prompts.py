import json
from typing import List
from app.schemas import RetrievedContext, GenerationProfile


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


SYSTEM_SYNTHETIC_GENERATOR = """You are a Principal AI Governance Architect and Lead Evaluator.
Your mission is to generate high-fidelity, technically rigorous synthetic Question/Answer pairs to create evaluation benchmarks and fine-tuning datasets for Trustworthy AI.

Strict Guidelines:
1. Strict Grounding: Every answer must be 100% derived from the provided context. Never use external knowledge.
2. Depth Awareness: Match the requested technical depth (Foundational, Technical, Comparative).
3. Precision: The answer must cite specific principles, mechanisms, or requirements mentioned in the text.
4. Output Format: You MUST respond ONLY with a raw valid JSON object. No conversational intro, no markdown codeblocks, just JSON."""

def buil_synthetic_qa_prompt(
        context: RetrievedContext,
        profile: GenerationProfile,
) -> str:

    schema_format = {
        "pairs" : [
            {
                "question" : "Technically challenging question based strictly on the text",
                "answer" : f"Clear, {profile.answer_length} answer fully verified by the text",
            }
        ]
    }

    return f"""{SYSTEM_SYNTHETIC_GENERATOR}

### Context Reference:
- Document: {context.source} (Page {context.page})
- Chunk ID: {context.chunk_id}
- Content:
{context.text}

### Instructions:
- Target Depth: {profile.depth.value.upper()}
- Question Count: {profile.question_count}
- Target Answer Length: {profile.answer_length}

Output must match this exact JSON structure:
{json.dumps(schema_format, indent=2)}

JSON Output:"""

SYSTEM_CROSS_SYNTHESIZER = """You are a Principal AI Governance Architect and Lead Benchmark Evaluator.
Your task is to synthesize MULTIPLE reference contexts to generate deep, multi-perspective Question/Answer pairs.

Strict Rules:
1. Cross-Context Synthesis: Connect, compare, or harmonize mechanisms across AT LEAST TWO different references provided.
2. Grounding & Zero Extrapolation: Base both the question and answer STRICTLY on the provided text. Do not mention or extrapolate external frameworks, laws, or acts (e.g., EU AI Act, GDPR) unless they are explicitly referenced inside the verified context blocks.
3. Natural Phrasing: NEVER include metadata like 'chunk_id', 'page number', or 'filename.pdf' inside the question or answer text.
4. Output Format: Respond ONLY with a valid raw JSON object matching the requested schema."""

def build_synthesized_qa_prompt(
        contexts: List[RetrievedContext],
        profile: GenerationProfile,
) -> str:
    
    blocks = []
    for i, c in enumerate(contexts, 1):
        blocks.append(
            f"[REF{i}] Document: {c.source} (Page {c.page}) | ID: {c.chunk_id} \n {c.text}"
        )
        combined_contexts = "\n\n".join(blocks)

        schema_format = {
            "pairs" : [
                {
                "question": "Deep technical question synthesizing governance mechanisms across references",
                "answer": "Comprehensive answer connecting the principles and controls without citing chunk IDs",
                "used_reference_numbers": [1, 2]
                }
            ]
        }

        return f"""{SYSTEM_CROSS_SYNTHESIZER}

### Verified References:
{combined_contexts}

### Directives:
- Target Depth: {profile.depth.value.upper()}
- Target Question Count: {profile.question_count}
- Answer Style: {profile.answer_length}

Output must match this exact Json structure:
{json.dumps(schema_format, indent=2)}

JSON Output:"""