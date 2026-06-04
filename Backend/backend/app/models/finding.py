"""Domain models for vulnerability findings."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class VulnerabilityCategory(str, Enum):
    SQL_INJECTION = "SQL_INJECTION"
    NOSQL_INJECTION = "NOSQL_INJECTION"
    XSS = "XSS"
    CSRF = "CSRF"
    SSRF = "SSRF"
    OPEN_REDIRECT = "OPEN_REDIRECT"
    CLICKJACKING = "CLICKJACKING"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    CODE_INJECTION = "CODE_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    UNSAFE_DESERIALIZATION = "UNSAFE_DESERIALIZATION"
    BUFFER_OVERFLOW = "BUFFER_OVERFLOW"
    USE_AFTER_FREE = "USE_AFTER_FREE"
    DOUBLE_FREE = "DOUBLE_FREE"
    INTEGER_OVERFLOW = "INTEGER_OVERFLOW"
    NULL_POINTER = "NULL_POINTER"
    HARDCODED_SECRET = "HARDCODED_SECRET"
    API_KEY_EXPOSURE = "API_KEY_EXPOSURE"
    PRIVATE_KEY_EXPOSURE = "PRIVATE_KEY_EXPOSURE"
    JWT_SECRET_EXPOSURE = "JWT_SECRET_EXPOSURE"
    WEAK_CRYPTOGRAPHY = "WEAK_CRYPTOGRAPHY"
    WEAK_HASHING = "WEAK_HASHING"
    INSECURE_RANDOMNESS = "INSECURE_RANDOMNESS"
    BROKEN_AUTHENTICATION = "BROKEN_AUTHENTICATION"
    MISSING_AUTHORIZATION = "MISSING_AUTHORIZATION"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    RESOURCE_LEAK = "RESOURCE_LEAK"
    DOCKER_MISCONFIGURATION = "DOCKER_MISCONFIGURATION"
    KUBERNETES_MISCONFIGURATION = "KUBERNETES_MISCONFIGURATION"
    CLOUD_SECRET_EXPOSURE = "CLOUD_SECRET_EXPOSURE"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class VulnerabilityFinding:
    id: str
    category: VulnerabilityCategory
    severity: Severity
    confidence: float
    line_number: int
    description: str
    remediation: str
    code_snippet: str
    source: str = "regex"
    rule_id: str | None = None
    what_is_wrong: str = ""
    why_dangerous: str = ""
    real_world_impact: str = ""
    secure_example: str = ""

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())[:12]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["severity"] = self.severity.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VulnerabilityFinding:
        return cls(
            id=data["id"],
            category=VulnerabilityCategory(data["category"]),
            severity=Severity(data["severity"]),
            confidence=float(data["confidence"]),
            line_number=int(data["line_number"]),
            description=data["description"],
            remediation=data["remediation"],
            code_snippet=data.get("code_snippet", ""),
            source=data.get("source", "unknown"),
            rule_id=data.get("rule_id"),
            what_is_wrong=data.get("what_is_wrong", ""),
            why_dangerous=data.get("why_dangerous", ""),
            real_world_impact=data.get("real_world_impact", ""),
            secure_example=data.get("secure_example", ""),
        )
