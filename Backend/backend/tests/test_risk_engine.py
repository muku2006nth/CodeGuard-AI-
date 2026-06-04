from app.ml.base_model import MLPrediction
from app.models.finding import Severity, VulnerabilityCategory, VulnerabilityFinding
from app.security.risk_engine import RiskEngine


def test_low_risk_empty_findings():
    ml = MLPrediction(0.1, 0.1, False, "mock")
    result = RiskEngine().compute([], ml)
    assert result.risk_score < 30
    assert result.severity == Severity.LOW


def test_high_risk_with_critical_finding():
    f = VulnerabilityFinding(
        id="x",
        category=VulnerabilityCategory.SQL_INJECTION,
        severity=Severity.CRITICAL,
        confidence=0.95,
        line_number=1,
        description="sqli",
        remediation="fix",
        code_snippet="bad",
    )
    ml = MLPrediction(0.8, 0.8, True, "mock")
    result = RiskEngine().compute([f], ml)
    assert result.risk_score >= 50
