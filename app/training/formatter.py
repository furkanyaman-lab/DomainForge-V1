import json
import random
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple
from app.schemas import ValidatedQA, TrainingExample, ChatMessage, DatasetSplitSummary

SYSTEM_INSTRUCTION = (
    "You are an expert AI Governance Advisor. Provide rigorous, balanced, "
    "and technically grounded answers based on international AI governance "
    "frameworks and technical standards."
)

class DatasetFormatter:

    def __init__(self, system_prompt: str = SYSTEM_INSTRUCTION):
        self.system_prompt = system_prompt

    def to_training_example(self, qa: ValidatedQA) -> TrainingExample:

        messages = [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=qa.question),
            ChatMessage(role="assistant", content=qa.answer),
        ]

        metadata = {
            "depth": qa.depth,
            "validated_at" : qa.validated_at,
            "sources": [src.model_dump() for src in qa.sources],
        }

        return TrainingExample(messages=messages, metadata=metadata)


    def _get_primary_source(self, example: TrainingExample) -> str:
        sources = example.metadata.get("sources", [])
        if sources and isinstance(sources, list) and len(sources) > 0:
            first_src = sources[0]
            if isinstance(first_src, dict) and "source" in first_src:
                return first_src["source"]
            return "UNKNOWN"
    def split_dataset(
            self,
            examples: List[TrainingExample],
            train_ratio: float= 0.8,
            seed: int = 42,
    ) -> Tuple[List[TrainingExample], List[TrainingExample]]:
        try:
            if not examples or len(examples) == 0:
                raise ValueError("The dataset to be split is empty! There are no records in the 'examples' list.")

            if len(examples) == 1:
                return examples, []

            random.seed(seed)

            grouped_by_source = defaultdict(list)
            for ex in examples:
                src_key = self._get_primary_source(ex)
                grouped_by_source[src_key].append(ex)

            train_data: List[TrainingExample] = []
            eval_data: List[TrainingExample] = []

            eval_ratio = 1 - train_ratio

            for src_name, group_items in grouped_by_source.items():
                items = list(group_items)
                random.shuffle(items)

                group_len = len(items)
                if group_len == 1:
                    train_data.append(items[0])
                    continue

                n_eval = int(round(group_len * eval_ratio))
                n_eval = max(1, min(n_eval, group_len - 1))

                eval_data.extend(items[:n_eval])
                train_data.extend(items[n_eval:])

            random.shuffle(train_data)
            random.shuffle(eval_data)

            if not train_data:
                raise ValueError("The partitioning operation failed: the 'train_data' list was empty.")

            return train_data, eval_data

        except Exception as e:
            raise ValueError(f"An error occurred during the dataset split: {str(e)}") from e

    def export_jsonl(self, examples: List[TrainingExample], output_path: Path) -> None :
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                for item in examples:
                    f.write(item.model_dump_json() + "\n")
        except Exception as e:
            raise  IOError(f"Unable to write the JSONL file ({output_path}): {str(e)}") from e
        
    def process_and_export(
            self,
            input_qa_path: Path,
            output_dir: Path,
            train_ratio: float = 0.8,
            seed: int = 42
    ) -> DatasetSplitSummary:

        try:
            if not input_qa_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_qa_path}")

            validated_records: List[ValidatedQA] = []
            with open(input_qa_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line_str = line.strip()
                    if line_str:
                        try:
                            validated_records.append(ValidatedQA.model_validate_json(line_str))
                        except Exception as parse_err:
                            raise ValueError(f"Line {line_num} is not a valid ValidatedQA JSON: {parse_err}")

            if not validated_records:
                raise ValueError(f"No valid record was found in the input file: {input_qa_path}")

            examples = [self.to_training_example(qa) for qa in validated_records]

            train_set, eval_set = self.split_dataset(examples, train_ratio=train_ratio, seed=seed)

            train_file = output_dir / "train.jsonl"
            eval_file = output_dir / "eval.jsonl"

            self.export_jsonl(train_set, train_file)
            self.export_jsonl(eval_set, eval_file)

            return DatasetSplitSummary(
                total_count=len(examples),
                train_count=len(train_set),
                eval_count=len(eval_set),
                train_path=str(train_file),
                eval_path=str(eval_file),
            )

        except Exception as e:
            raise RuntimeError(f"DatasetFormatter processing error: {str(e)}") from e