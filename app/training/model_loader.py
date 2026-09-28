from typing import Tuple
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

class ModelLoader:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-3B-Instruct"):
        self.model_id = model_id
        self.device = self._get_optimal_device()

    def _get_optimal_device(self) -> torch.device:

        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def load(self) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:

        torch_dtype = (
            torch.bfloat16 if torch.backends.mps.is_available() else torch.float32
        )

        tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code= True,
            use_fast= True,
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype = torch_dtype,
            device_map={"": self.device},
            trust_remote_code= True,
        )

        model.config.use_cache = False
        return model, tokenizer