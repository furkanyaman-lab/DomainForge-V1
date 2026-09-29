import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import torch
from peft import PeftModel
from sentence_transformers import util  

from app.schemas import EvalSampleResult, EvaluationSummary
from app.rag.embedding import EmbeddingManager
from app.training.model_loader import ModelLoader

class ModelEvaluator:

    def __init__(
            self,
            base_model_id: str = "Qwen/Qwen2.5-3B-Instruct",
            adapter_path: str | Path | None = None,
            embedding_manager: EmbeddingManager | None = None,
            max_new_tokens: int = 300,
            temperature: float = 0.2, 
            ):
        self.base_model_id = base_model_id
        self.adapter_path = Path(adapter_path) if adapter_path else None
        self.embedding_manager = embedding_manager
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

    def generate(self, model, tokenizer, question: str) -> str:

        messages = [
            {"role": "system", "content" : " You are an expert AI Governance Advisor."},
            {"role": "user", "content": question},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize= False, add_generatation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens = self.max_new_tokens,
                temperature = self.temperature,
                do_sample = self.temperature > 0.0,
                pad_token_id = tokenizer.pad_token_id,
            )

        gen_tokens = outputs[0][inputs["inputs_ids"].shape[1]:]
        return tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    def evaluate(self, eval_path: Path, output_file: Path | None = None) -> EvaluationSummary:

        if not eval_path.exists():
            raise FileNotFoundError(f"Evaluation data not found: {eval_path}")

        loader = ModelLoader(self.base_model_id)
        model, tokenizer = loader.load()

        if self.adapter_path and self.adapter_path.exists():
            print(f"LoRA Adapter is being integrated: {self.adapter_path}")
            model = PeftModel.from_pretrained(model, str(self.adapter_path))

        model.eval()

        with open(eval_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        results: List[EvalSampleResult] = []

        for item in records:
            question = item["messages"][1]["content"]
            ground_truth = item["messages"][2]["content"]

            response = self.generate(model, tokenizer, question)

            sim_score = 0.0
            if self.embedding_manager:
                emb_res = self.embedding_manager.model.encode(
                    response, convert_to_tensor=True, normalize_embeddings=True
                )

                emb_gt = self.embedding_manager.model.encode(
                    ground_truth, convert_to_tensor=True, normalize_embeddings=True
                )

                sim_score = round(float(util.cos_sim(emb_res, emb_gt)[0][0]), 4)

            results.append(
                EvalSampleResult(
                    question=question,
                    ground_truth=ground_truth,
                    base_response=response,
                    finetuned_response=response if self.adapter_path else "[Adapter Not Loaded - Baseline Mode]",
                    semantic_sim_base=sim_score,
                    semantic_sim_ft=sim_score if self.adapter_path else 0.0,
                    token_f1_base=0.0,
                    token_f1_ft=0.0,
                    sources=item.get("metadata", {}).get("sources", []),
                )
            )

            avg_sim = round(sum(r.semantic_sim_base for r in results) / len(results), 4)

            summary = EvaluationSummary(
                eval_model_id=self.base_model_id,
                total_samples=len(results),
                avg_semantic_sim_base=avg_sim,
                avg_semantic_sim_ft=avg_sim if self.adapter_path else 0.0,
                avg_token_f1_base=0.0,
                avg_token_f1_ft=0.0,
                samples=results,
                evaluated_at= datetime.now(timezone.utc).isoformat()
            )

            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(summary.model_dump_json(indent=2))

            return summary