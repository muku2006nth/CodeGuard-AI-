"""Load DetectVul/devign from Hugging Face (no local CSV/JSON required)."""

from __future__ import annotations

from datasets import Dataset, DatasetDict, load_dataset

HF_DATASET_ID = "DetectVul/devign"
CODE_COLUMN = "func"
LABEL_COLUMN = "target"


def load_hf_devign(cache_dir: str | None = None) -> DatasetDict:
    return load_dataset(HF_DATASET_ID, cache_dir=cache_dir)


def _split_to_dataset(split, max_rows: int | None = None) -> Dataset:
    if max_rows is not None and max_rows < len(split):
        split = split.select(range(max_rows))
    labels = [int(x) for x in split[LABEL_COLUMN]]
    return Dataset.from_dict(
        {
            "text": split[CODE_COLUMN],
            "label": labels,
        }
    )


def load_devign_splits(
    max_samples: int | None = None,
    cache_dir: str | None = None,
) -> tuple[Dataset, Dataset, Dataset]:
    """
    Return (train, validation, test) as Hugging Face Datasets with text/label columns.

    When max_samples is set (smoke tests), only the train split is truncated.
    Validation and test use up to min(500, split size) for speed.
    """
    raw = load_hf_devign(cache_dir=cache_dir)

    if "validation" in raw:
        val_key = "validation"
    elif "val" in raw:
        val_key = "val"
    else:
        raise KeyError(f"No validation split in {HF_DATASET_ID}: {list(raw.keys())}")

    if max_samples is not None:
        train = _split_to_dataset(raw["train"], max_rows=max_samples)
        val_cap = min(500, len(raw[val_key]))
        test_cap = min(500, len(raw["test"]))
        val = _split_to_dataset(raw[val_key], max_rows=val_cap)
        test = _split_to_dataset(raw["test"], max_rows=test_cap)
    else:
        train = _split_to_dataset(raw["train"])
        val = _split_to_dataset(raw[val_key])
        test = _split_to_dataset(raw["test"])

    return train, val, test
