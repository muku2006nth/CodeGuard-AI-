"""Evaluate fine-tuned CodeBERT on DetectVul/devign test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer

try:
    from src.devign_data import load_devign_splits
    from src.train import tokenize_dataset
except ImportError:
    from devign_data import load_devign_splits
    from train import tokenize_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/codebert-vuln")
    parser.add_argument("--output", default="results/metrics.json")
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit train split when loading (same as train.py smoke mode)",
    )
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("Note: evaluate.py runs on CPU locally — this is fine.")

    print("Loading DetectVul/devign test split from Hugging Face...")
    _, _, test_ds = load_devign_splits(
        max_samples=args.max_samples,
        cache_dir=args.cache_dir,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model)
    test_tok = tokenize_dataset(test_ds, tokenizer)

    trainer = Trainer(model=model)
    result = trainer.predict(test_tok)
    preds = np.argmax(result.predictions, axis=1)
    labels = result.label_ids

    metrics = {
        "dataset": "DetectVul/devign",
        "accuracy": float((preds == labels).mean()),
        "f1": float(f1_score(labels, preds, average="binary")),
        "classification_report": classification_report(labels, preds, output_dict=True),
        "confusion_matrix": confusion_matrix(labels, preds).tolist(),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"accuracy: {metrics['accuracy']:.1%}")
    print(f"F1: {metrics['f1']:.3f}")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
