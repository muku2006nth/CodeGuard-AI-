"""Analysis orchestrator — full security review pipeline."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

from app.ml.factory import get_ml_model
from app.models.finding import Severity, VulnerabilityFinding
from app.security.bandit_runner import BanditRunner
from app.security.explainer import Explainer
from app.security.language import detect_language
from app.security.regex_detector import RegexDetector
from app.security.risk_engine import RiskEngine
from app.security.semgrep_runner import SemgrepRunner
from app.services.aggregator import FindingAggregator
from app.ml.base_model import MLPrediction

try:
    from src.retriever import (
        SecurityRetriever,
        format_rag_context,
        format_chunks_as_dicts,
    )
    from src.pipeline import _generate_fix_llm, _severity_from_type
    from src.predict import CodeBERTClassifier, ClassificationResult

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AnalysisReport:
    report_id: str
    risk_score: int
    severity: Severity
    findings: list[VulnerabilityFinding]
    summary: str
    recommendations: list[str]
    ml_score: MLPrediction
    language: str
    latency_seconds: float = 0.0
    code: str = ""
    metadata: dict = field(default_factory=dict)
    # RAG-enriched fields
    rag_chunks: list[dict] = field(default_factory=list)
    rag_no_match: bool = True
    fixed_code: str = ""
    cve_refs: list[str] = field(default_factory=list)
    ai_explanation: str = ""

    def to_storage_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "risk_score": self.risk_score,
            "severity": self.severity.value,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "ml_score": self.ml_score.to_dict(),
            "language": self.language,
            "latency_seconds": self.latency_seconds,
            "metadata": self.metadata,
            "rag_chunks": self.rag_chunks,
            "rag_no_match": self.rag_no_match,
            "fixed_code": self.fixed_code,
            "cve_refs": self.cve_refs,
            "ai_explanation": self.ai_explanation,
        }


class SecurityAnalyzer:
    def __init__(self) -> None:
        self.regex = RegexDetector()
        self.semgrep = SemgrepRunner()
        self.bandit = BanditRunner()
        self.aggregator = FindingAggregator()
        self.risk_engine = RiskEngine()
        self.explainer = Explainer()
        self._ml = get_ml_model()

        # RAG components (optional — graceful degradation if unavailable)
        self._retriever = None
        self._classifier = None
        if RAG_AVAILABLE:
            try:
                self._retriever = SecurityRetriever()
                self._classifier = CodeBERTClassifier()
                logger.info("RAG pipeline initialized successfully.")
            except Exception as exc:
                logger.warning("RAG init failed — running without RAG: %s", exc)

    def analyze(
        self,
        code: str,
        language: str | None = None,
        filename: str | None = None,
    ) -> AnalysisReport:
        start = time.perf_counter()
        lang = detect_language(code, hint=language, filename=filename)

        regex_findings = self.regex.scan(code, lang)
        semgrep_findings = self.semgrep.scan(code, lang)
        bandit_findings = self.bandit.scan(code, lang)

        findings = self.aggregator.merge(
            regex_findings,
            semgrep_findings,
            bandit_findings,
        )

        ml_score = self._ml.predict(code, lang)
        risk = self.risk_engine.compute(findings, ml_score)
        findings = self.explainer.enrich(findings)

        summary = self.explainer.build_summary(
            findings,
            risk.risk_score,
            risk.severity.value,
            ml_score.risk_probability,
        )
        recommendations = self.explainer.build_recommendations(findings)

        # ---- RAG enrichment (non-blocking) ----
        rag_chunks: list[dict] = []
        rag_no_match = True
        fixed_code = ""
        cve_refs: list[str] = []
        ai_explanation = ""

        if self._retriever is not None and self._classifier is not None:
            try:
                # Classify with CodeBERT
                classification = self._classifier.classify(code)
                query = f"{classification.vuln_type} vulnerability in {lang}"
                rag_result = self._retriever.query_with_metadata(query, top_k=3)

                rag_no_match = rag_result.no_match
                rag_chunks = format_chunks_as_dicts(rag_result.chunks)

                # Collect CVE references from chunks
                for chunk in rag_result.chunks:
                    if chunk.cve_id and chunk.cve_id not in cve_refs:
                        cve_refs.append(chunk.cve_id)
                    if chunk.category and chunk.category not in cve_refs:
                        cve_refs.append(chunk.category)

                # Generate LLM fix if we have relevant chunks
                if not rag_no_match:
                    rag_context = format_rag_context(rag_result.chunks)
                    llm_out = _generate_fix_llm(
                        code, lang, classification, rag_context
                    )
                    fixed_code = llm_out.get("fixed_code", "")
                    ai_explanation = llm_out.get("explanation", "")
                    # Add LLM-discovered references
                    for ref in llm_out.get("references", []):
                        if ref not in cve_refs:
                            cve_refs.append(ref)

                logger.info(
                    "RAG: %d chunks, no_match=%s, vuln=%s",
                    len(rag_chunks), rag_no_match, classification.vuln_type,
                )
            except Exception as exc:
                logger.warning("RAG enrichment failed (non-fatal): %s", exc)

        return AnalysisReport(
            report_id=str(uuid.uuid4()),
            risk_score=risk.risk_score,
            severity=risk.severity,
            findings=findings,
            summary=summary,
            recommendations=recommendations,
            ml_score=ml_score,
            language=lang,
            latency_seconds=time.perf_counter() - start,
            code=code,
            metadata={
                "scanners": {
                    "regex": len(regex_findings),
                    "semgrep": len(semgrep_findings),
                    "bandit": len(bandit_findings),
                },
                "risk_breakdown": risk.breakdown,
            },
            rag_chunks=rag_chunks,
            rag_no_match=rag_no_match,
            fixed_code=fixed_code,
            cve_refs=cve_refs[:10],
            ai_explanation=ai_explanation,
        )
