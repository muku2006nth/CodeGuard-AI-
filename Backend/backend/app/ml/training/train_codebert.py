"""
Fine-tune CodeBERT on DetectVul/devign.

Run from repo root:
  python -m app.ml.training.train_codebert --output ../../models/codebert-vuln

Or from Colab after cd into backend.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset, load_dataset
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "microsoft/codebert-base"
HF_DATASET = "DetectVul/devign"


def load_splits(max_samples: int | None = None):
    raw = load_dataset(HF_DATASET)
    val_key = "validation" if "validation" in raw else "val"

    def to_ds(split, cap: int | None = None):
        if cap and cap < len(split):
            split = split.select(range(cap))
        return Dataset.from_dict(
            {
                "text": split["func"],
                "labels": [int(x) for x in split["target"]],
            }
        )

    train_cap = max_samples
    val_cap = min(500, len(raw[val_key])) if max_samples else None
    test_cap = min(500, len(raw["test"])) if max_samples else None

    train = to_ds(raw["train"], train_cap)
    val = to_ds(raw[val_key], val_cap)
    test = to_ds(raw["test"], test_cap)
    return train, val, test


def tokenize(ds: Dataset, tokenizer, max_length: int) -> Dataset:
    def _tok(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )

    out = ds.map(_tok, batched=True)
    out.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
    return out


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    p, r, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": p,
        "recall": r,
        "f1": f1,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="models/codebert-vuln")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("WARNING: CUDA not available — training will be very slow on CPU.")

    output = Path(args.output)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {HF_DATASET}...")
    train_ds, val_ds, test_ds = load_splits(args.max_samples)
    print(f"train={len(train_ds)} val={len(val_ds)} test={len(test_ds)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    train_tok = tokenize(train_ds, tokenizer, args.max_length)
    val_tok = tokenize(val_ds, tokenizer, args.max_length)
    test_tok = tokenize(test_ds, tokenizer, args.max_length)

    training_args = TrainingArguments(
        output_dir=str(output / "checkpoints"),
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
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=val_tok,
        compute_metrics=compute_metrics,
    )

    print("Training...")
    trainer.train()

    trainer.save_model(str(output))
    tokenizer.save_pretrained(str(output))

    print("Evaluating on test split...")
    pred = trainer.predict(test_tok)
    preds = np.argmax(pred.predictions, axis=1)
    labels = pred.label_ids

    accuracy = float(accuracy_score(labels, preds))
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    cm = confusion_matrix(labels, preds).tolist()
    report = classification_report(labels, preds, output_dict=True)

    metrics = {
        "model": MODEL_NAME,
        "dataset": HF_DATASET,
        "accuracy": accuracy,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": cm,
        "classification_report": report,
    }

    metrics_path = results_dir / "metrics.json"
    eval_path = results_dir / "evaluation_report.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    eval_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("\n===== TEST METRICS =====")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1       : {f1:.4f}")
    print(f"Confusion matrix: {cm}")
    print(f"Saved model to {output}")
    print(f"Saved metrics to {metrics_path}")


if __name__ == "__main__":
    # Allow running as script from backend/
    backend_root = Path(__file__).resolve().parents[3]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    main()
