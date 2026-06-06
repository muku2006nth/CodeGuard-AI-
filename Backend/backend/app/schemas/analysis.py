"""Pydantic schemas for API request/response."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=200_000)
    language: str | None = None
    filename: str | None = None


class MLScoreResponse(BaseModel):
    risk_probability: float
    suspicious_score: float
    is_suspicious: bool
    provider: str = "mock"


class FindingResponse(BaseModel):
    id: str
    category: str
    severity: str
    confidence: float
    line_number: int
    description: str
    remediation: str
    code_snippet: str
    source: str
    rule_id: str | None = None
    what_is_wrong: str = ""
    why_dangerous: str = ""
    real_world_impact: str = ""
    secure_example: str = ""





class AnalyzeResponse(BaseModel):
    report_id: str
    risk_score: int = Field(ge=0, le=100)
    severity: str
    findings: list[FindingResponse]
    summary: str
    recommendations: list[str]
    ml_score: MLScoreResponse
    language: str
    latency_seconds: float



class ReportSummary(BaseModel):
    report_id: str
    risk_score: int
    severity: str
    finding_count: int
    language: str
    created_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    ml_provider: str


class UploadResponse(BaseModel):
    report_id: str
    filename: str
    language: str = "unknown"
    latency_seconds: float = 0.0


class ReportDetailResponse(BaseModel):
    report_id: str
    payload: dict[str, Any]


class DashboardResponse(BaseModel):
    total_scans: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    average_risk_score: float
    recent_scans: list[ReportSummary]
    trend_data: list[dict[str, Any]]
    severity_distribution: list[dict[str, Any]]


class StatisticsResponse(BaseModel):
    vulnerability_counts: dict[str, int]
    risk_trends: list[dict[str, Any]]
    languages: dict[str, int]
    top_categories: list[dict[str, Any]]


class SystemStatusResponse(BaseModel):
    backend: str
    codebert: str
    semgrep: str

    database: str
