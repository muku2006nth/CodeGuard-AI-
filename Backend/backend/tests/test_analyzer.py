from app.services.analyzer import SecurityAnalyzer


VULNERABLE_SAMPLE = """
import os
password = "secret123"
cmd = input()
os.system(cmd)
"""

SAFE_SAMPLE = """
def add(a: int, b: int) -> int:
    return a + b
"""


def test_analyzer_finds_vulnerable_patterns():
    report = SecurityAnalyzer().analyze(VULNERABLE_SAMPLE, language="python")
    assert report.risk_score > 0
    assert len(report.findings) >= 1


def test_analyzer_safe_sample_lower_risk():
    vuln = SecurityAnalyzer().analyze(VULNERABLE_SAMPLE, language="python")
    safe = SecurityAnalyzer().analyze(SAFE_SAMPLE, language="python")
    assert safe.risk_score <= vuln.risk_score
