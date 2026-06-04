"""Analysis orchestrator — full security review pipeline."""

from __future__ import annotations

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
        )
