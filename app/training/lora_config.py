from peft import LoraConfig, TaskType
from app.schemas import LoRAProfile

class LoRAConfigFactory:
    @staticmethod
    def create(profile: LoRAProfile | None = None) -> LoraConfig:
        if profile is None:
            profile = LoRAProfile()

        return LoraConfig(
            r=profile.r,
            lora_alpha=profile.lora_alpha,
            lora_dropout=profile.lora_dropout,
            target_modules=profile.target_modules,
            bias=profile.bias,
            task_type=TaskType.CAUSAL_LM,

        )