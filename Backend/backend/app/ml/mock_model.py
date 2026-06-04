"""Heuristic ML service — used until CodeBERT is trained and plugged in."""

from __future__ import annotations

import re

from app.ml.base_model import BaseMLModel, MLPrediction
from app.utils.config import ML_SUSPICIOUS_THRESHOLD

DANGEROUS_PATTERNS: list[tuple[str, float]] = [
    (r"os\.system\s*\(", 0.35),
    (r"eval\s*\(|exec\s*\(", 0.4),
    (r"pickle\.loads?\s*\(", 0.35),
    (r"password\s*=\s*['\"]", 0.25),
    (r"SELECT\s+.*\+", 0.3),
    (r"innerHTML\s*=", 0.28),
    (r"subprocess\..*shell\s*=\s*True", 0.32),
    (r"-----BEGIN.*PRIVATE KEY-----", 0.45),
    (r"AKIA[0-9A-Z]{16}", 0.4),
    (r"\.\./", 0.2),
    (r"yaml\.load\s*\(", 0.25),
    (r"\b(strcpy|gets)\s*\(", 0.3),
]


class MockMLModel(BaseMLModel):
    """Temporary risk estimator based on pattern heuristics."""

    def __init__(self, threshold: float | None = None):
        self.threshold = threshold or ML_SUSPICIOUS_THRESHOLD
        self._loaded = False

    def load(self) -> None:
        self._loaded = True

    def predict(self, code: str, language: str = "unknown") -> MLPrediction:
        if not self._loaded:
            self.load()

        score = 0.05
        for pattern, weight in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                score += weight

        # Longer code with many risky tokens gets slightly higher score
        lines = code.splitlines()
        if len(lines) > 100:
            score += 0.05

        risk_probability = min(0.99, max(0.01, score))
        suspicious_score = risk_probability
        is_suspicious = risk_probability >= self.threshold

        return MLPrediction(
            risk_probability=risk_probability,
            suspicious_score=suspicious_score,
            is_suspicious=is_suspicious,
            provider="mock",
        )
