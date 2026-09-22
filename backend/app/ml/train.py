"""
Fine-tunes DistilBERT to classify request payloads as SAFE or ATTACK.

Usage:
    python -m app.ml.train

Reads:  ml_data/dataset.json   (list of {"text": ..., "label": 0|1})
Writes: model/final/           (tokenizer + weights, loaded by app.ml.detector)
"""
import json
import os

from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

DATASET_PATH = os.environ.get("DATASET_PATH", "ml_data/dataset.json")
OUTPUT_DIR = os.environ.get("TRAIN_OUTPUT_DIR", "model")
FINAL_MODEL_DIR = os.path.join(OUTPUT_DIR, "final")


def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total samples: {len(data)}")

    dataset = Dataset.from_list(data)
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=128)

    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.train_test_split(test_size=0.2, seed=42)

    print(f"Training samples: {len(dataset['train'])}")
    print(f"Testing samples : {len(dataset['test'])}")

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=2,
        id2label={0: "SAFE", 1: "ATTACK"},
        label2id={"SAFE": 0, "ATTACK": 1},
    )

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=8,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
    )

    print("\nStarting training...\n")
    trainer.train()

    os.makedirs(FINAL_MODEL_DIR, exist_ok=True)
    trainer.save_model(FINAL_MODEL_DIR)
    tokenizer.save_pretrained(FINAL_MODEL_DIR)

    print("\n======================================")
    print("TRAINING COMPLETE")
    print("Model saved to:", FINAL_MODEL_DIR)
    print("======================================")


if __name__ == "__main__":
    main()
