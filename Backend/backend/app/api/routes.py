"""FastAPI route handlers."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app import __version__
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    FindingResponse,
    HealthResponse,
    MLScoreResponse,
    ReportDetailResponse,
    ReportSummary,
    UploadResponse,
)
from app.services.analyzer import SecurityAnalyzer
from app.services.report_export import export_json, export_markdown, export_pdf
from app.services.report_store import ReportStore
from app.utils.config import MAX_CODE_BYTES, ML_PROVIDER

router = APIRouter()
_analyzer = SecurityAnalyzer()
_store = ReportStore()


def _report_to_response(report_dict: dict) -> AnalyzeResponse:
    ml = report_dict.get("ml_score", {})
    findings = [
        FindingResponse(**f) if isinstance(f, dict) else f
        for f in report_dict.get("findings", [])
    ]
    return AnalyzeResponse(
        report_id=report_dict["report_id"],
        risk_score=report_dict["risk_score"],
        severity=report_dict["severity"],
        findings=findings,
        summary=report_dict["summary"],
        recommendations=report_dict["recommendations"],
        ml_score=MLScoreResponse(
            risk_probability=ml.get("risk_probability", 0),
            suspicious_score=ml.get("suspicious_score", 0),
            is_suspicious=ml.get("is_suspicious", False),
            provider=ml.get("provider", "mock"),
        ),
        language=report_dict.get("language", "unknown"),
        latency_seconds=report_dict.get("latency_seconds", 0),
    )


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", version=__version__, ml_provider=ML_PROVIDER)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest):
    code = body.code
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        raise HTTPException(status_code=413, detail="Code exceeds size limit")

    report = _analyzer.analyze(
        code,
        language=body.language,
        filename=body.filename,
    )
    stored = report.to_storage_dict()
    _store.save(stored)
    return _report_to_response(stored)


@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    language: str | None = Query(None),
):
    content = await file.read()
    if len(content) > MAX_CODE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds size limit")
    try:
        code = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text") from exc

    report = _analyzer.analyze(code, language=language, filename=file.filename)
    stored = report.to_storage_dict()
    _store.save(stored)
    return UploadResponse(
        report_id=stored["report_id"],
        filename=file.filename or "upload.txt",
        message="Analysis complete",
    )


@router.get("/report/{report_id}", response_model=ReportDetailResponse)
def get_report(report_id: str):
    data = _store.get(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetailResponse(report_id=report_id, payload=data)


@router.get("/reports", response_model=list[ReportSummary])
def list_reports():
    items = _store.list_reports()
    return [ReportSummary(**item) for item in items]


@router.get("/report/{report_id}/download")
def download_report(report_id: str, format: str = "json"):
    data = _store.get(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")

    fmt = format.lower()
    if fmt == "json":
        return Response(
            content=export_json(data),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{report_id}.json"'},
        )
    if fmt == "markdown" or fmt == "md":
        return Response(
            content=export_markdown(data),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{report_id}.md"'},
        )
    if fmt == "pdf":
        return Response(
            content=export_pdf(data),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report_id}.pdf"'},
        )
    raise HTTPException(status_code=400, detail="format must be json, markdown, or pdf")
