"""Hugging Face compatible model wrapper for EVEZ."""

import torch
from transformers import PreTrainedModel, AutoModelForCausalLM, AutoTokenizer
from .configuration_evez import EvezConfig
from .control.deployer import main as deployer_main  # Not ideal but for simplicity; better to import runtime


class EvezModel(PreTrainedModel):
    config_class = EvezConfig

    def __init__(self, config):
        super().__init__(config)
        # Load base model
        self.base_model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        # Import EVEZ runtime (adjust path as needed)
        # For now, we'll simulate by using the base model directly
        # In practice, you would inject your EVEZ runtime here
        self.runtime = None  # Placeholder for actual EVEZ runtime

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        # Forward pass to base model
        return self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **kwargs,
        )

    def generate(self, input_ids=None, attention_mask=None, **kwargs):
        # This is where EVEZ runtime takes over
        if self.runtime is not None:
            # Decode input to prompt
            prompt = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
            # Run through EVEZ runtime (agent orchestration, etc.)
            output_text = self.runtime.run(prompt)
            # Encode back to token ids
            output_ids = self.tokenizer.encode(output_text, return_tensors="pt")
            return output_ids
        else:
            # Fallback to base model generation
            return self.base_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                **kwargs,
            )

