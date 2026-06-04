# Devign training data

Training data is **not stored in this repository**.

It is loaded at runtime from Hugging Face:

```python
from datasets import load_dataset
dataset = load_dataset("DetectVul/devign")
```

Inspect locally:

```bash
python scripts/inspect_dataset.py
```
