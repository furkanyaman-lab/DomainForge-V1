import json
from typing import List, Dict, Any
from app.schemas import RetrievedContext


SYSTEM_GOVERNANCE_EXPERT = """You are a specialized AI Governance, Ethics, and Risk Management technical expert.
Your responses must be strictly grounded in the provided contextual references.
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


def build_question_catalog_prompt(framework_summaries: Dict[str, Any], target_count: int) -> str:
    doc_keys = list(framework_summaries.keys())
    
    return f"""You are a Principal Regulatory and AI Governance Architect.
Analyze the structural summaries and core pillars of the following {len(doc_keys)} governance framework(s):

{json.dumps(framework_summaries, indent=2)}

AVAILABLE FRAMEWORKS:
{', '.join(doc_keys)}

TASK:
Generate EXACTLY {target_count} rigorous, specific, and technically demanding governance questions.

STRICT BALANCING & COVERAGE RULES:
1. BALANCED COVERAGE: Distribute questions EQUALLY across all available frameworks ({', '.join(doc_keys)}):
   - Produce focused questions targeting unique technical controls, ethical principles, or compliance responsibilities of each individual framework.
   - Produce comparative / cross-framework questions that explore alignments, trade-offs, or regulatory gaps between the frameworks.
2. TECHNICAL DEPTH: Focus on concrete governance mechanisms, auditing requirements, operational testing, data provenance, bias mitigation, and human oversight.
3. NO SHALLOW QUESTIONS: Do NOT create generic questions (e.g., 'What are the main goals of framework X?').
4. FORMAT: Return ONLY valid JSON in this exact structure:
{{
  "catalog": [
    "Rigorous, technically precise governance question here...",
    ...
  ]
}}
"""

def build_targeted_synthesis_prompt(question: str, contexts: List[RetrievedContext]) -> str:
    context_str = "\n\n".join([
        f"--- CONTEXT BLOCK {i+1} (Document: {c.document_id}, Page: {c.page}) ---\n{c.text}"
        for i, c in enumerate(contexts)
    ])
    
    return f"""You are an authoritative AI Governance and Compliance Advisor.
Synthesize a comprehensive, authoritative, and technically grounded answer to the specific question below using ONLY the provided references.

QUESTION:
{question}

CONTEXT REFERENCES:
{context_str}

STRICT WRITING RULES:
1. Ground every claim directly in the provided context references.
2. CITATION CLEANLINESS: DO NOT include in-text bracketed markers such as '(Reference [1])', '[Reference 2]', or chunk identifiers in the body of your answer. Write in natural, executive-level regulatory prose.
3. If comparing frameworks, explain differences and complementary aspects with technical precision.
4. Return ONLY valid JSON:
{{
  "answer": "Polished, exhaustive technical answer without raw reference tags...",
  "used_references_numbers": [1, 2]
}}
"""

def build_balanced_gap_catalog_prompt(
    framework_summaries: Dict[str, Any],
    coverage_summary: Dict[str, int],
    target_count: int,
) -> str:
    doc_keys = list(framework_summaries.keys())

    return f"""You are a Principal AI Governance Architect.
Review the structural blueprints of the following frameworks:
{json.dumps(framework_summaries, indent=2)}

CURRENT DATASET COVERAGE (Completed counts per framework):
{json.dumps(coverage_summary, indent=2)}

AVAILABLE FRAMEWORKS:
{', '.join(doc_keys)}

TASK:
Generate EXACTLY {target_count} technical governance questions to BALANCE the overall dataset.

CRITICAL INSTRUCTIONS:
1. GAP FILLING: Strongly prioritize frameworks and topics that have the lowest counts or are missing in CURRENT DATASET COVERAGE.
2. TECHNICAL DEPTH: Focus on concrete technical controls, auditing, operational risk mitigations, human-in-the-loop oversight, and compliance nuances.
3. NO SHALLOW QUESTIONS: Avoid generic questions (e.g., 'What are the principles of X?').
4. FORMAT: Return ONLY valid JSON in this exact structure:
{{
  "catalog": [
    "Targeted question addressing an under-represented governance area...",
    ...
  ]
}}
"""