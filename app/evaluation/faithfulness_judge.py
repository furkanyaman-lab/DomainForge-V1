import json
import os
import re
from typing import Any, Dict
import requests

FAITHFULNESS_PROMPT = """You are an expert AI Governance and Regulatory Auditor.
Your task is to evaluate the REGULATORY COMPLIANCE, FACTUAL ACCURACY, and CONTRADICTIONS of a Generated Response compared against an authoritative Ground Truth reference.

Ground Truth Reference Context:
{ground_truth}

Model Generated Response:
{model_response}

Evaluation Criteria:
1. Contradictions & Falsifications: Does the response state anything that directly contradicts official regulatory principles (NIST AI RMF, OECD, UNESCO)?
2. Fictitious Citations: Did the model invent non-existent regulatory clauses, invalid sub-categories (e.g., GOVERN-9.9), or broken syntax?
3. Domain Validity (Extrapolation): Technical elaborations (e.g., referencing STIX/TAXII, CI/CD gates, OECD taxonomies, or industry-standard schemas) are ALLOWED and VALID as long as they align with the spirit of the Ground Truth and do not fabricate regulatory facts.

Scoring Guidelines:
- 1.0: Accurate, fully aligned with regulatory intent, zero contradictions, valid domain extension.
- 0.7 - 0.9: Highly compliant, minor unverified technical details but sound governance logic.
- 0.4 - 0.6: Partially correct, but contains misaligned interpretations or weak governance controls.
- 0.0 - 0.3: Severe hallucinations (invented standards, broken logic, dangerous governance contradictions).

Respond strictly in valid JSON:
{{
  "score": <float between 0.0 and 1.0>,
  "hallucinated_claims": [<list of actual contradictions or invented standard codes; empty list if technically sound>],
  "cited_standards_valid": <true or false>,
  "reasoning": "<concise 1-2 sentence audit verdict>"
}}
"""

class FaithfulnessJudge:

    def __init__(
        self,
        model_name: str = "nvidia/nemotron-3-super-120b-a12b:free",
    ):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = model_name

        if not self.api_key:
            print(" ERROR: OPENROUTER_API_KEY not found in environment!")

    def verify(self, model_response: str, ground_truth: str) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "score": 0.0,
                "hallucinated_claims": ["Missing OPENROUTER_API_KEY"],
                "cited_standards_valid": False,
                "reasoning": "Missing API key",
            }

        prompt = FAITHFULNESS_PROMPT.format(
            ground_truth=ground_truth, model_response=model_response
        )

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                },
                timeout=45,
            )
            response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]
            match = re.search(r"\{.*\}", content, re.DOTALL)

            if not match:
                raise ValueError("Valid JSON block not found in model response")

            data = json.loads(match.group(0))
            score = data.get("score", data.get("faithfulness_score", 0.0))
            data["score"] = round(float(score), 4)
            return data

        except Exception as e:
            return {
                "score": 0.0,
                "hallucinated_claims": [str(e)],
                "cited_standards_valid": False,
                "reasoning": str(e),
            }