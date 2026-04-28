#!/usr/bin/env python3
"""
LoRA fine-tuning script for EVEZ self-improvement loop.
This script is intended to be run via GitHub Actions.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_int8_training
from datasets import load_dataset

def main():
    # Configuration
    base_model_name = os.environ.get("BASE_MODEL", "mistralai/Mistral-7B-v0.1")
    output_dir = os.environ.get("OUTPUT_DIR", "./model")
    data_path = os.environ.get("DATA_PATH", "./data/train.json")
    hf_token = os.environ.get("HF_TOKEN")  # For pushing to Hugging Face Hub

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.pad_token = tokenizer.eos_token  # Set pad token for batching

    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        load_in_8bit=True,  # Use 8-bit quantization for memory efficiency
        device_map="auto",
    )

    # Prepare model for int8 training if using 8-bit
    model = prepare_model_for_int8_training(model)

    # Configure LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # Adjust based on model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and prepare dataset
    # Assuming data is in JSON format with a "text" field
    dataset = load_dataset("json", data_files=data_path, split="train")

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

    # Data collator for language modeling
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        max_steps=1000,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_steps=500,
        evaluation_strategy="no",
        save_total_limit=2,
        push_to_hub=True,
        hub_token=hf_token,
        hub_model_id=os.environ.get("HF_MODEL_ID", "your-username/evez-model"),
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # Train
    trainer.train()

    # Save the model
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"Training complete. Model saved to {output_dir}")

if __name__ == "__main__":
    main()