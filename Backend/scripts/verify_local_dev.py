"""
Verify local development environment (CPU-only is expected).

Run: python scripts/verify_local_dev.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

OK = "[OK]"
WARN = "[!!]"
FAIL = "[XX]"


def main():
    print("AI Code Reviewer — local dev check\n")
    print("Workflow: Local PC (dev) + Google Colab T4 (training)\n")
    print("Dataset: Hugging Face DetectVul/devign (no CSV / train.json)\n")

    try:
        import torch

        cuda = torch.cuda.is_available()
        print(f"{OK} PyTorch {torch.__version__} | CUDA: {cuda}")
        if cuda:
            print(f"    GPU: {torch.cuda.get_device_name(0)} (training can run locally)")
        else:
            print("    No GPU — use Colab for full training (expected on most laptops)")
    except ImportError:
        print(f"{FAIL} PyTorch not installed — pip install -r requirements.txt")

    try:
        from datasets import load_dataset

        print(f"{OK} datasets library installed")
        print("    Run: python scripts/inspect_dataset.py")
    except ImportError:
        print(f"{FAIL} datasets not installed")

    model_dir = ROOT / "models" / "codebert-vuln"
    has_model = (model_dir / "config.json").exists()
    if has_model:
        print(f"{OK} Fine-tuned model at models/codebert-vuln/")
    else:
        print(f"{WARN} No fine-tuned model — train on Colab, download codebert-vuln.zip")

    chroma = ROOT / "data" / "chroma_db"
    if chroma.exists():
        print(f"{OK} ChromaDB at data/chroma_db/")
    else:
        print(f"{WARN} ChromaDB missing — run: python src/ingest.py --seed-only")

    groq = os.getenv("GROQ_API_KEY", "")
    if groq and groq != "your_groq_api_key_here":
        print(f"{OK} GROQ_API_KEY set (LLM fixes enabled)")
    else:
        print(f"{WARN} GROQ_API_KEY not set — classifier + RAG work; fixes need Groq")

    metrics = ROOT / "results" / "metrics.json"
    if metrics.exists():
        import json

        with open(metrics, encoding="utf-8") as f:
            m = json.load(f)
        if m.get("accuracy"):
            print(f"{OK} metrics.json accuracy={m['accuracy']:.1%}")
        else:
            print(f"{WARN} metrics.json exists but no accuracy yet (train on Colab first)")

    print("\nNext steps:")
    print("  1. python scripts/inspect_dataset.py")
    print("  2. python src/ingest.py --seed-only")
    print("  3. Colab: colab/train_codebert.ipynb (GPU)")
    print("  4. streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
