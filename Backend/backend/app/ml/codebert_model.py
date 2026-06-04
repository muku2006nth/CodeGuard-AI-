"""CodeBERT ML model — fine-tuned vulnerability detection.

Loads a trained CodeBERT checkpoint from CODEBERT_MODEL_PATH and runs
binary classification (label-1 = vulnerable) on source code snippets.

Activated by setting ML_PROVIDER=codebert in .env.
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.ml.base_model import BaseMLModel, MLPrediction
from app.utils.config import CODEBERT_MODEL_PATH, ML_SUSPICIOUS_THRESHOLD

logger = logging.getLogger(__name__)

MAX_LENGTH = 512


class CodeBERTModel(BaseMLModel):
    """Fine-tuned CodeBERT for vulnerability detection."""

    def __init__(self) -> None:
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.threshold = ML_SUSPICIOUS_THRESHOLD
        self._loaded = False

    def load(self) -> None:
        model_path = Path(CODEBERT_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(
                f"CodeBERT checkpoint not found at {model_path}. "
                "Train via colab/train_codebert.ipynb first."
            )

        logger.info("Loading CodeBERT model from %s ...", model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.model.to(self.device)
        self.model.eval()
        self._loaded = True
        logger.info("CodeBERT loaded successfully on %s", self.device)

    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, code: str, language: str = "unknown") -> MLPrediction:
        if not self._loaded:
            self.load()

        # Tokenize input code
        inputs = self.tokenizer(
            code,
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits  # shape: (1, 2)

        # Softmax to get probabilities
        probs = torch.softmax(logits, dim=1)
        risk_probability = float(probs[0, 1].cpu())  # label-1 = vulnerable

        # Clamp to avoid 0.0 / 1.0 extremes
        risk_probability = max(0.01, min(0.99, risk_probability))

        return MLPrediction(
            risk_probability=risk_probability,
            suspicious_score=risk_probability,
            is_suspicious=risk_probability >= self.threshold,
            provider="codebert",
        )
