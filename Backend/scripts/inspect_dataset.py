"""
Inspect DetectVul/devign from Hugging Face.

Run: python scripts/inspect_dataset.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.devign_data import CODE_COLUMN, HF_DATASET_ID, LABEL_COLUMN, load_hf_devign


def main():
    print(f"Loading {HF_DATASET_ID} from Hugging Face...\n")
    dataset = load_hf_devign()

    for split_name in ("train", "validation", "test"):
        if split_name not in dataset:
            continue
        split = dataset[split_name]
        labels = list(split[LABEL_COLUMN])
        dist = Counter(labels)

        print(f"=== {split_name} ===")
        print(f"  samples: {len(split)}")
        print(f"  class distribution (label={LABEL_COLUMN}):")
        for label, count in sorted(dist.items()):
            pct = 100.0 * count / len(split)
            name = "vulnerable" if label == 1 else "safe"
            print(f"    {label} ({name}): {count} ({pct:.1f}%)")
        print()

    train = dataset["train"]
    print("=== first train sample preview ===")
    print(f"  columns: {train.column_names}")
    print(f"  target: {train[0][LABEL_COLUMN]}")
    func = train[0][CODE_COLUMN]
    preview = func[:500] + ("..." if len(func) > 500 else "")
    print(f"  func ({len(func)} chars):\n{preview}\n")
    print("Ready for training: python src/train.py  (use Colab T4 for full run)")


if __name__ == "__main__":
    main()
