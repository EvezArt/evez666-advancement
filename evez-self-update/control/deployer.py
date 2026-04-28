#!/usr/bin/env python3
"""
Deploy script for EVEZ model.
Pushes the fine-tuned model to Hugging Face Hub.
"""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig

def main():
    # Configuration
    base_model_name = os.environ.get("BASE_MODEL", "mistralai/Mistral-7B-v0.1")
    adapter_model_dir = os.environ.get("ADAPTER_MODEL_DIR", "./model")  # where LoRA adapter is saved
    hf_token = os.environ.get("HF_TOKEN")
    hf_model_id = os.environ.get("HF_MODEL_ID", "your-username/evez-model")

    # Load base model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        load_in_8bit=True,
        device_map="auto",
    )

    # Load the LoRA adapter
    model = PeftModel.from_pretrained(base_model, adapter_model_dir)
    model = model.merge_and_unload()  # Optional: merge LoRA weights for faster inference

    # Save merged model
    merged_model_dir = "./merged_model"
    model.save_pretrained(merged_model_dir)
    tokenizer.save_pretrained(merged_model_dir)

    # Push to Hugging Face Hub
    model.push_to_hub(hf_model_id, token=hf_token)
    tokenizer.push_to_hub(hf_model_id, token=hf_token)

    print(f"Model pushed to {hf_model_id}")

if __name__ == "__main__":
    main()