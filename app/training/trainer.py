from pathlib import Path
import torch
from datasets import load_dataset
from peft import get_peft_model
from transformers import TrainingArguments, Trainer, DataCollatorForSeq2Seq

from app.schemas import TrainingProfile, LoRAProfile
from app.training.model_loader import ModelLoader
from app.training.lora_config import LoRAConfigFactory

class DomainTrainer:
    def __init__(
            self,
            train_profile: TrainingProfile | None = None,
            lora_profile: LoRAProfile | None = None,
        ):
            self.train_profile = train_profile or TrainingProfile()
            self.lora_profile = lora_profile or LoRAProfile()
            self.model_loader = ModelLoader(self.train_profile.base_model_id)

    def prepare_dataset(self, tokenizer, train_path: str, eval_path: str | None = None):

        data_files = {"train" : train_path}
        if eval_path and Path(eval_path).exists() and Path(eval_path).stat().st_size > 0:
            data_files["eval"] = eval_path

        dataset = load_dataset("json", data_files=data_files)

        def format_chat(sample):
            text = tokenizer.apply_chat_template(
                sample["messages"],
                tokenize = False,
                add_generation_prompt= False,

            )
            return {"text" : text}

        formatted_dataset = dataset.map(format_chat)

        def tokenize_func(examples):
            tokens = tokenizer(
                examples["text"],
                truncation = True,
                max_length = self.train_profile.max_seq_length,
                padding = False,
            )
            tokens["labels"] = tokens["input_ids"].copy()
            return tokens

        tokenized_dataset = formatted_dataset.map(
            tokenize_func,
            batched=True,
            remove_columns=dataset["train"].column_names,
        )
        return tokenized_dataset

    def build_trainer(self, train_path: str, eval_path: str | None = None) -> Trainer:

        model, tokenizer = self.model_loader.load()

        peft_config = LoRAConfigFactory.create(self.lora_profile)
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()

        tokenized_data = self.prepare_dataset(tokenizer, train_path, eval_path)

        is_mps = torch.backends.mps.is_available()

        training_args = TrainingArguments(
            output_dir=self.train_profile.output_dir,
            learning_rate=self.train_profile.learning_rate,
            num_train_epochs=self.train_profile.num_train_epochs,
            per_device_train_batch_size=self.train_profile.per_device_train_batch_size,
            gradient_accumulation_steps=self.train_profile.gradient_accumulation_steps,
            logging_steps=self.train_profile.logging_steps,
            save_strategy=self.train_profile.save_strategy,
            warmup_ratio=self.train_profile.warmup_ratio,
            seed=self.train_profile.seed,
            fp16=False,
            bf16=is_mps,
            report_to="none",
            use_mps_device=is_mps,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_data["train"],
            eval_dataset=tokenized_data.get("eval"),
            tokenizer=tokenizer,
            data_collator=DataCollatorForSeq2Seq(
                tokenizer, pad_to_multiple_of=8, return_tensors="pt"
            ),
        )

        return trainer

