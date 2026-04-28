"""Configuration for EVEZ model."""

from transformers import PretrainedConfig
import os


class EvezConfig(PretrainedConfig):
    model_type = "evez"

    def __init__(
        self,
        base_model="mistralai/Mistral-7B-v0.1",
        **kwargs,
    ):
        self.base_model = base_model
        super().__init__(**kwargs)

