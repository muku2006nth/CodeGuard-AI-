"""FastAPI backend — POST /review (Day 5)."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.github_fetcher import fetch_github_file
from src.pipeline import review_code

app = FastAPI(
    title="AI Code Reviewer",
    description="CodeBERT + RAG + LLaMA3 vulnerability review API",
    version="0.1.0",
)

MAX_CODE_BYTES = 512_000


class ReviewRequest(BaseModel):
    code: str | None = Field(None, max_length=200_000)
    language: str | None = None
    github_url: str | None = None

    @model_validator(mode="after")
    def require_code_or_url(self):
        if not self.code and not self.github_url:
            raise ValueError("Provide either 'code' or 'github_url'")
        if self.code and self.github_url:
            raise ValueError("Provide only one of 'code' or 'github_url'")
        return self


class ReviewResponse(BaseModel):
    vuln_type: str
    severity: str
    confidence: float
    is_vulnerable: bool
    cve_refs: list[str]
    explanation: str
    fixed_code: str
    language: str
    latency_seconds: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
def review(body: ReviewRequest):
    try:
        if body.github_url:
            code, language = fetch_github_file(body.github_url, max_bytes=MAX_CODE_BYTES)
        else:
            assert body.code is not None
            if len(body.code.encode("utf-8")) > MAX_CODE_BYTES:
                raise HTTPException(status_code=413, detail="Code exceeds size limit")
            code, language = body.code, body.language

        result = review_code(code, language=language)
        return ReviewResponse(
            vuln_type=result.vuln_type,
            severity=result.severity,
            confidence=result.confidence,
            is_vulnerable=result.is_vulnerable,
            cve_refs=result.cve_refs,
            explanation=result.explanation,
            fixed_code=result.fixed_code,
            language=result.language,
            latency_seconds=round(result.latency_seconds, 3),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
