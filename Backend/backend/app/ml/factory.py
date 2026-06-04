"""ML model factory — swap providers via ML_PROVIDER env var."""

from __future__ import annotations

from functools import lru_cache

from app.ml.base_model import BaseMLModel
from app.ml.mock_model import MockMLModel
from app.utils.config import ML_PROVIDER


@lru_cache(maxsize=1)
def get_ml_model() -> BaseMLModel:
    provider = ML_PROVIDER
    if provider == "codebert":
        from app.ml.codebert_model import CodeBERTModel

        model: BaseMLModel = CodeBERTModel()
    else:
        model = MockMLModel()
    model.load()
    return model
