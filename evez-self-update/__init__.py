"""Register EVEZ model with transformers."""

from transformers import AutoConfig, AutoModelForCausalLM
from .configuration_evez import EvezConfig
from .modeling_evez import EvezModel

AutoConfig.register("evez", EvezConfig)
AutoModelForCausalLM.register(EvezConfig, EvezModel)