"""
UniXCoder fine-tuning on DetectVul/devign
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import torch
from datasets import Dataset
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

try:
    from src.devign_data import load_devign_splits
except ImportError:
    from devign_data import load_devign_splits

MODEL_NAME = "microsoft/unixcoder-base"


def tokenize_dataset(dataset: Dataset, tokenizer, max_length: int = 512) -> Dataset:
    def _tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )

    tokenized = dataset.map(_tokenize, batched=True)
    tokenized = tokenized.rename_column("label", "labels")
    tokenized.set_format(
        "torch",
        columns=["input_ids", "attention_mask", "labels"],
    )
    return tokenized


def compute_metrics(eval_pred):
    logits, labels = eval_pred

    preds = np.argmax(logits, axis=1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        preds,
        average="binary",
        zero_division=0,
    )

    accuracy = accuracy_score(labels, preds)

    return {
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune UniXCoder on DetectVul/devign"
    )

    parser.add_argument(
        "--dataset",
        default="DetectVul/devign",
    )

    parser.add_argument(
        "--output",
        default="models/unixcoder-vuln",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=1e-5,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
    )

    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--allow-cpu",
        action="store_true",
    )

    parser.add_argument(
        "--cache-dir",
        default=None,
    )

    args = parser.parse_args()

    if not torch.cuda.is_available():
        if not args.allow_cpu:
            print("CUDA available: False")
            print("Use Google Colab T4 GPU.")
            sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Using device: {device}")
    print("Loading dataset from Hugging Face: DetectVul/devign")

    train_ds, val_ds, test_ds = load_devign_splits(
        max_samples=args.max_samples,
        cache_dir=args.cache_dir,
    )

    print(
        f"train={len(train_ds)} "
        f"validation={len(val_ds)} "
        f"test={len(test_ds)}"
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
    )

    train_tok = tokenize_dataset(
        train_ds,
        tokenizer,
        args.max_length,
    )

    val_tok = tokenize_dataset(
        val_ds,
        tokenizer,
        args.max_length,
    )

    test_tok = tokenize_dataset(
        test_ds,
        tokenizer,
        args.max_length,
    )

    use_fp16 = torch.cuda.is_available()

    training_args = TrainingArguments(
        output_dir=args.output,

        num_train_epochs=args.epochs,

        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,

        learning_rate=args.lr,

        weight_decay=0.01,
        warmup_ratio=0.1,

        eval_strategy="epoch",
        save_strategy="epoch",

        load_best_model_at_end=True,
        metric_for_best_model="eval_f1",
        greater_is_better=True,

        logging_steps=50,

        fp16=use_fp16,

        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=val_tok,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)

    results = trainer.predict(test_tok)

    preds = np.argmax(
        results.predictions,
        axis=1,
    )

    labels = results.label_ids

    accuracy = accuracy_score(
        labels,
        preds,
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        preds,
        average="binary",
        zero_division=0,
    )

    print("\n===== TEST RESULTS =====")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print(f"\nModel saved to {args.output}")


if __name__ == "__main__":
    main()