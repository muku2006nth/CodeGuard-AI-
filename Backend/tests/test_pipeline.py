"""Pipeline integration tests."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import detect_language, review_code
from src.retriever import SecurityRetriever


def test_detect_language_python():
    assert detect_language("def foo():\n    pass") == "python"


def test_detect_language_javascript():
    assert detect_language("const x = () => document.write(user);") == "javascript"


@pytest.mark.skipif(
    not Path("data/chroma_db").exists(),
    reason="ChromaDB not ingested — run: python src/ingest.py --seed-only",
)
def test_retriever_sql_injection():
    retriever = SecurityRetriever()
    chunks = retriever.query("SQL injection vulnerability", top_k=3)
    assert len(chunks) >= 1


def test_review_sql_injection_sample():
    sample = Path(__file__).parent / "sample_code" / "sql_injection.py"
    code = sample.read_text(encoding="utf-8")
    result = review_code(code, language="python")
    assert result.vuln_type
    assert 0 <= result.confidence <= 1
    assert result.latency_seconds >= 0
