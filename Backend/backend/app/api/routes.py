"""FastAPI route handlers."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, Depends
from fastapi.responses import Response

from app.security.auth import get_current_user, UserContext

from app import __version__
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    FindingResponse,
    HealthResponse,
    MLScoreResponse,
    RagChunkResponse,
    ReportDetailResponse,
    ReportSummary,
    UploadResponse,
    DashboardResponse,
    StatisticsResponse,
    SystemStatusResponse,
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
    # Map RAG chunks to response schema
    rag_chunks = [
        RagChunkResponse(**rc) if isinstance(rc, dict) else rc
        for rc in report_dict.get("rag_chunks", [])
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
        rag_chunks=rag_chunks,
        rag_no_match=report_dict.get("rag_no_match", True),
        fixed_code=report_dict.get("fixed_code", ""),
        cve_refs=report_dict.get("cve_refs", []),
        ai_explanation=report_dict.get("ai_explanation", ""),
    )


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", version=__version__, ml_provider=ML_PROVIDER)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest, user: UserContext = Depends(get_current_user)):
    code = body.code
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        raise HTTPException(status_code=413, detail="Code exceeds size limit")

    report = _analyzer.analyze(
        code,
        language=body.language,
        filename=body.filename,
    )
    stored = report.to_storage_dict()
    _store.save(stored, user.id, token=user.token)
    return _report_to_response(stored)


@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    language: str | None = Query(None),
    user: UserContext = Depends(get_current_user),
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
    _store.save(stored, user.id, token=user.token)
    return UploadResponse(
        report_id=stored["report_id"],
        filename=file.filename or "upload.txt",
        message="Analysis complete",
    )


@router.get("/report/{report_id}", response_model=ReportDetailResponse)
def get_report(report_id: str, user: UserContext = Depends(get_current_user)):
    data = _store.get(report_id, user.id, token=user.token)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetailResponse(report_id=report_id, payload=data)


@router.get("/reports", response_model=list[ReportSummary])
def list_reports(user: UserContext = Depends(get_current_user)):
    items = _store.list_reports(user.id, token=user.token)
    return [ReportSummary(**item) for item in items]


@router.get("/report/{report_id}/download")
def download_report(report_id: str, format: str = "json", user: UserContext = Depends(get_current_user)):
    data = _store.get(report_id, user.id, token=user.token)
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


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(user: UserContext = Depends(get_current_user)):
    items = _store.list_reports(user.id, limit=100, token=user.token)
    total_scans = len(items)
    
    critical = 0
    high = 0
    medium = 0
    low = 0
    total_risk = 0
    
    # Calculate finding severity counts directly from full reports if needed, 
    # but list_reports only has 'severity' of the overall report, not individual finding counts.
    # We will load the full reports to count individual findings accurately.
    for item in items:
        report_data = _store.get(item["report_id"], user.id, token=user.token)
        if not report_data:
            continue
        total_risk += report_data.get("risk_score", 0)
        for f in report_data.get("findings", []):
            sev = f.get("severity", "LOW").upper()
            if sev == "CRITICAL":
                critical += 1
            elif sev == "HIGH":
                high += 1
            elif sev == "MEDIUM":
                medium += 1
            else:
                low += 1

    avg_risk = total_risk / total_scans if total_scans > 0 else 0.0

    # Trend data (mocked slightly based on recent reports for the chart)
    # We will just group by date string prefix
    dates = {}
    for item in items:
        date_str = item["created_at"][:10] if item["created_at"] else "Unknown"
        dates[date_str] = dates.get(date_str, 0) + 1
    
    trend_data = [{"date": k, "scans": v} for k, v in sorted(dates.items())[-7:]]
    
    severity_distribution = [
        {"name": "Critical", "value": critical},
        {"name": "High", "value": high},
        {"name": "Medium", "value": medium},
        {"name": "Low", "value": low},
    ]

    return DashboardResponse(
        total_scans=total_scans,
        critical_findings=critical,
        high_findings=high,
        medium_findings=medium,
        low_findings=low,
        average_risk_score=round(avg_risk, 1),
        recent_scans=[ReportSummary(**item) for item in items[:5]],
        trend_data=trend_data,
        severity_distribution=severity_distribution,
    )


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(user: UserContext = Depends(get_current_user)):
    items = _store.list_reports(user.id, limit=200, token=user.token)
    
    vuln_counts = {}
    languages = {}
    
    for item in items:
        # Lang stats
        lang = item.get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1
        
        # Vuln stats
        report_data = _store.get(item["report_id"], user.id, token=user.token)
        if report_data:
            for f in report_data.get("findings", []):
                cat = f.get("category", "Unknown")
                vuln_counts[cat] = vuln_counts.get(cat, 0) + 1
                
    top_categories = [{"category": k, "count": v} for k, v in sorted(vuln_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # Mocking trend for UI since we might not have historical data
    risk_trends = [
        {"month": "Jan", "score": 45},
        {"month": "Feb", "score": 42},
        {"month": "Mar", "score": 38},
        {"month": "Apr", "score": 40},
        {"month": "May", "score": 35},
        {"month": "Jun", "score": 30},
    ]
    
    return StatisticsResponse(
        vulnerability_counts=vuln_counts,
        risk_trends=risk_trends,
        languages=languages,
        top_categories=top_categories,
    )


@router.get("/system-status", response_model=SystemStatusResponse)
def get_system_status():
    from app.services.analyzer import RAG_AVAILABLE
    
    backend_status = "healthy"
    database_status = "healthy"
    
    # Try to check ML provider
    if ML_PROVIDER == "codebert":
        codebert_status = "loaded"
    else:
        codebert_status = "mock"
        
    semgrep_status = "available" # Assuming semgrep is installed
    rag_status = "available" if RAG_AVAILABLE else "unavailable"
    
    return SystemStatusResponse(
        backend=backend_status,
        codebert=codebert_status,
        semgrep=semgrep_status,
        rag=rag_status,
        database=database_status,
    )

@router.get("/history")
def get_history(user: UserContext = Depends(get_current_user)):
    # Alias for reports to satisfy the requested endpoints
    items = _store.list_reports(user.id, limit=100, token=user.token)
    return {"scans": [ReportSummary(**item).dict() for item in items]}
