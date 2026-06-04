"""Risk scoring engine — combines static findings and ML signal."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.finding import Severity, VulnerabilityFinding
from app.ml.base_model import MLPrediction

SEVERITY_WEIGHT = {
    Severity.LOW: 5,
    Severity.MEDIUM: 15,
    Severity.HIGH: 30,
    Severity.CRITICAL: 45,
}


@dataclass
class RiskResult:
    risk_score: int
    severity: Severity
    breakdown: dict[str, float]


class RiskEngine:
    def compute(
        self,
        findings: list[VulnerabilityFinding],
        ml: MLPrediction,
    ) -> RiskResult:
        if not findings and not ml.is_suspicious:
            return RiskResult(
                risk_score=max(0, int(ml.risk_probability * 20)),
                severity=Severity.LOW,
                breakdown={"ml": ml.risk_probability, "findings": 0},
            )

        finding_score = 0.0
        max_severity = Severity.LOW
        for f in findings:
            w = SEVERITY_WEIGHT.get(f.severity, 10)
            finding_score += w * f.confidence
            if list(Severity).index(f.severity) > list(Severity).index(max_severity):
                max_severity = f.severity

        ml_component = ml.risk_probability * 35
        raw = finding_score + ml_component
        risk_score = int(min(100, max(0, raw)))

        severity = self._score_to_severity(risk_score, max_severity)
        return RiskResult(
            risk_score=risk_score,
            severity=severity,
            breakdown={
                "finding_component": round(finding_score, 2),
                "ml_component": round(ml_component, 2),
                "ml_probability": ml.risk_probability,
            },
        )

    def _score_to_severity(self, score: int, max_finding: Severity) -> Severity:
        if score >= 80 or max_finding == Severity.CRITICAL:
            return Severity.CRITICAL
        if score >= 55 or max_finding == Severity.HIGH:
            return Severity.HIGH
        if score >= 30 or max_finding == Severity.MEDIUM:
            return Severity.MEDIUM
        return Severity.LOW
