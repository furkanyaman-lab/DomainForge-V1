import json
from pathlib import Path
from typing import Dict, Any
import pymupdf
import ollama

class FrameworkSummarizer:
    def __init__(
        self,
        model_name: str = "deepseek-r1:14b",
        output_dir: Path | str = "data/interim",
        ):
        self.model_name = model_name
        self.client = ollama.Client()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.summary_file = self.output_dir / "framework_summaries.json"

    def extract_toc_and_intro(self, pdf_path: Path, max_page: int = 6) -> str:
        doc = pymupdf.open(pdf_path)
        extracted_text = []

        for page_idx in range(min(max_page, len(doc))):
            text = doc[page_idx].get_text()
            extracted_text.append(f"--- PAGE {page_idx + 1} ---\n{text}")

        return "\n\n".join(extracted_text)

    def summarize_document(self, pdf_path: Path) -> Dict[str, Any]:

        print(f"  🔍 Extracting structural scope for: {pdf_path.name}...")
        intro_content = self.extract_toc_and_intro(pdf_path)

        prompt = f"""You are an expert Document Architecture Specialist.
Analyze the following introductory pages and Table of Contents (TOC) of '{pdf_path.name}':

{intro_content[:8000]}

TASK:
Extract the structural taxonomy, core functions, and high-level technical scope of this standard.
Return ONLY valid JSON matching this exact structure:
{{
  "title": "Full formal title of the framework",
  "core_sections": [
    "Section/Function name: Brief explanation of its scope and technical purpose"
  ],
  "key_topics": [
    "Key regulatory, technical, or risk areas covered"
  ]
}}
"""

        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            format="json",
            options = {"temperature": 0.1},
        )
        return json.loads(response["response"])

    def get_or_create_summaries(
        self, raw_data_dir: Path, force_refresh: bool = False
    ) -> Dict[str, Any]:
        if  self.summary_file.exists() and not force_refresh:
            print(f"  📂 Loaded existing framework scope from: {self.summary_file}")
            with open(self.summary_file, "r", encoding="utf-8") as f:
                return json.load(f)

        summaries = {}
        pdf_files = list(raw_data_dir.glob("*.pdf"))

        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {raw_data_dir}")

        for pdf in pdf_files:
            doc_id = pdf.stem
            summaries[doc_id] = self.summarize_document(pdf)

        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)

        print(f"  ✅ Framework summaries mapped and saved: {self.summary_file}")
        return summaries