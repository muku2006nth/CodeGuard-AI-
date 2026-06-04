"""Semgrep integration — optional external scanner."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from app.models.finding import Severity, VulnerabilityCategory, VulnerabilityFinding
from app.security.language import file_extension

logger = logging.getLogger(__name__)

# Directory containing our custom Semgrep rules
_RULES_DIR = Path(__file__).resolve().parent / "semgrep_rules"

SEMGREP_RULE_MAP: dict[str, VulnerabilityCategory] = {
    "sql-injection": VulnerabilityCategory.SQL_INJECTION,
    "sqli": VulnerabilityCategory.SQL_INJECTION,
    "xss": VulnerabilityCategory.XSS,
    "command-injection": VulnerabilityCategory.COMMAND_INJECTION,
    "subprocess-shell": VulnerabilityCategory.COMMAND_INJECTION,
    "subprocess-call": VulnerabilityCategory.COMMAND_INJECTION,
    "os-system": VulnerabilityCategory.COMMAND_INJECTION,
    "os-popen": VulnerabilityCategory.COMMAND_INJECTION,
    "gitlab.bandit.b404": VulnerabilityCategory.COMMAND_INJECTION,
    "bandit.b404": VulnerabilityCategory.COMMAND_INJECTION,
    "path-traversal": VulnerabilityCategory.PATH_TRAVERSAL,
    "hardcoded-secret": VulnerabilityCategory.HARDCODED_SECRET,
    "hardcoded-password": VulnerabilityCategory.HARDCODED_SECRET,
    "secrets": VulnerabilityCategory.HARDCODED_SECRET,
    "eval": VulnerabilityCategory.CODE_INJECTION,
    "eval-injection": VulnerabilityCategory.CODE_INJECTION,
    "exec-injection": VulnerabilityCategory.CODE_INJECTION,
    "deserialization": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "pickle": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "yaml-unsafe": VulnerabilityCategory.UNSAFE_DESERIALIZATION,
    "crypto": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "weak-hash": VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
    "ssrf": VulnerabilityCategory.SSRF,
}


def _map_category(check_id: str, message: str) -> VulnerabilityCategory:
    combined = f"{check_id} {message}".lower()
    for key, cat in SEMGREP_RULE_MAP.items():
        if key in combined:
            return cat
    return VulnerabilityCategory.UNKNOWN


def _map_severity(level: str) -> Severity:
    level = (level or "").upper()
    if level in ("ERROR", "CRITICAL"):
        return Severity.CRITICAL
    if level == "WARNING":
        return Severity.HIGH
    if level == "INFO":
        return Severity.MEDIUM
    return Severity.MEDIUM


class SemgrepRunner:
    def __init__(self) -> None:
        # Use the custom rules directory shipped with the project
        self.rules_dir = str(_RULES_DIR)

    def is_available(self) -> bool:
        """Check if semgrep can be imported."""
        try:
            import semgrep  # noqa: F401
            return True
        except ImportError:
            return False

    def scan(self, code: str, language: str = "python") -> list[VulnerabilityFinding]:
        if not self.is_available():
            logger.info("Semgrep not installed — skipping")
            return []

        ext = file_extension(language)
        findings: list[VulnerabilityFinding] = []

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"snippet{ext}"
            path.write_text(code, encoding="utf-8")
            cmd = [
                sys.executable,
                "-c",
                "import semgrep.main; semgrep.main.main()",
                "--config",
                self.rules_dir,
                "--json",
                "--quiet",
                "--no-git-ignore",
                str(path),
            ]
            logger.info("Running Semgrep: %s", " ".join(cmd))
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                raw = proc.stdout.strip()
                if not raw:
                    logger.warning("Semgrep returned empty stdout. stderr: %s", proc.stderr[:500])
                    return []
                data = json.loads(raw)
            except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                logger.warning("Semgrep failed: %s", exc)
                return []

            for result in data.get("results", []):
                check_id = result.get("check_id", "unknown")
                extra = result.get("extra", {})
                message = extra.get("message", check_id)
                severity = _map_severity(extra.get("severity", "WARNING"))
                start = result.get("start", {})
                line = int(start.get("line", 1))
                snippet = (extra.get("lines", "") or "").strip()[:200]

                findings.append(
                    VulnerabilityFinding(
                        id=VulnerabilityFinding.new_id(),
                        category=_map_category(check_id, message),
                        severity=severity,
                        confidence=0.88,
                        line_number=line,
                        description=message,
                        remediation="Follow Semgrep rule guidance; apply secure coding pattern.",
                        code_snippet=snippet,
                        source="semgrep",
                        rule_id=check_id,
                    )
                )
        return findings
