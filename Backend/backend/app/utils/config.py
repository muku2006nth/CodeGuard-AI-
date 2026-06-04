"""Application configuration from environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/utils/config.py -> repo root is parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent

load_dotenv(REPO_ROOT / ".env")

ML_PROVIDER = os.getenv("ML_PROVIDER", "mock").lower()
_codebert_env = os.getenv("CODEBERT_MODEL_PATH", "models/codebert-vuln")
CODEBERT_MODEL_PATH = str(REPO_ROOT / _codebert_env) if not Path(_codebert_env).is_absolute() else _codebert_env
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(REPO_ROOT / "data" / "reports")))
MAX_CODE_BYTES = int(os.getenv("MAX_CODE_BYTES", "512000"))
ML_SUSPICIOUS_THRESHOLD = float(os.getenv("ML_SUSPICIOUS_THRESHOLD", "0.65"))
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")


def ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR
