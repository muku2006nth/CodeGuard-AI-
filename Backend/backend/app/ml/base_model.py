"""ML model abstraction — plug-and-play interface for risk scoring."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MLPrediction:
    risk_probability: float
    suspicious_score: float
    is_suspicious: bool
    provider: str = "mock"

    def to_dict(self) -> dict:
        return {
            "risk_probability": round(self.risk_probability, 4),
            "suspicious_score": round(self.suspicious_score, 4),
            "is_suspicious": self.is_suspicious,
            "provider": self.provider,
        }


class BaseMLModel(ABC):
    """Interface for ML risk estimators. CodeBERT implements this later."""

    @abstractmethod
    def load(self) -> None:
        """Load model weights and tokenizer."""

    @abstractmethod
    def predict(self, code: str, language: str = "unknown") -> MLPrediction:
        """Return binary risk signals — not vulnerability categories."""

    def is_loaded(self) -> bool:
        return True
