"""Bandit integration for Python security analysis."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.models.finding import Severity, VulnerabilityCategory, VulnerabilityFinding

logger = logging.getLogger(__name__)

BANDIT_TEST_MAP: dict[str, VulnerabilityCategory] = {
    "B101": VulnerabilityCategory.CODE_INJECTION,
    "B102": VulnerabilityCategory.CODE_INJECTION,
    "B103": VulnerabilityCategory.HARDCODED_SECRET,
    "B104": VulnerabilityCategory.MISSING_AUTHORIZATION,
    "B105": VulnerabilityCategory.HARDCODED_SECRET,
    "B106": VulnerabilityCategory.HARDCODED_SECRET,
    "B107": VulnerabilityCategory.HARDCODED_SECRET,
    "B108": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B201": VulnerabilityCategory.COMMAND_INJECTION,
    "B301": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B302": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B303": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B304": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B305": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B306": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B307": VulnerabilityCategory.CODE_INJECTION,
    "B308": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B310": VulnerabilityCategory.SSRF,
    "B311": VulnerabilityCategory.INSECURE_RANDOMNESS,
    "B312": VulnerabilityCategory.INSECURE_RANDOMNESS,
    "B313": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "B501": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B502": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B503": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B504": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B505": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B506": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B507": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "B601": VulnerabilityCategory.COMMAND_INJECTION,
    "B602": VulnerabilityCategory.COMMAND_INJECTION,
    "B603": VulnerabilityCategory.COMMAND_INJECTION,
    "B604": VulnerabilityCategory.COMMAND_INJECTION,
    "B605": VulnerabilityCategory.COMMAND_INJECTION,
    "B606": VulnerabilityCategory.COMMAND_INJECTION,
    "B607": VulnerabilityCategory.COMMAND_INJECTION,
    "B608": VulnerabilityCategory.SQL_INJECTION,
    "B609": VulnerabilityCategory.COMMAND_INJECTION,
}


def _bandit_severity(confidence: str, issue_text: str) -> Severity:
    c = (confidence or "").upper()
    if c == "HIGH":
        return Severity.CRITICAL
    if c == "MEDIUM":
        return Severity.HIGH
    if "hardcoded" in issue_text.lower():
        return Severity.HIGH
    return Severity.MEDIUM


class BanditRunner:
    def is_available(self) -> bool:
        return shutil.which("bandit") is not None

    def scan(self, code: str, language: str = "python") -> list[VulnerabilityFinding]:
        if language != "python":
            return []
        if not self.is_available():
            logger.info("Bandit not installed — skipping")
            return []

        findings: list[VulnerabilityFinding] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snippet.py"
            path.write_text(code, encoding="utf-8")
            cmd = ["bandit", "-f", "json", "-q", str(path)]
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )
                raw = proc.stdout.strip() or proc.stderr.strip()
                if not raw:
                    return []
                data = json.loads(raw)
            except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                logger.warning("Bandit failed: %s", exc)
                return []

            for item in data.get("results", []):
                test_id = item.get("test_id", "B000")
                issue = item.get("issue_text", "Bandit security issue")
                line = int(item.get("line_number", 1))
                conf = item.get("issue_confidence", "MEDIUM")
                snippet = (item.get("code", "") or "").strip()

                findings.append(
                    VulnerabilityFinding(
                        id=VulnerabilityFinding.new_id(),
                        category=BANDIT_TEST_MAP.get(test_id, VulnerabilityCategory.UNKNOWN),
                        severity=_bandit_severity(conf, issue),
                        confidence=0.86 if conf.upper() == "HIGH" else 0.75,
                        line_number=line,
                        description=issue,
                        remediation=f"Address Bandit {test_id}: follow secure Python guidelines.",
                        code_snippet=snippet,
                        source="bandit",
                        rule_id=test_id,
                    )
                )
        return findings
