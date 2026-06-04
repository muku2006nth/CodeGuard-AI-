"""Regex-based vulnerability pattern detector."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.finding import Severity, VulnerabilityCategory, VulnerabilityFinding


@dataclass
class _PatternRule:
    rule_id: str
    category: VulnerabilityCategory
    severity: Severity
    pattern: re.Pattern[str]
    description: str
    remediation: str
    confidence: float = 0.85


def _rules() -> list[_PatternRule]:
    flags = re.IGNORECASE | re.MULTILINE
    return [
        # SQL Injection
        _PatternRule(
            "regex-sqli-001",
            VulnerabilityCategory.SQL_INJECTION,
            Severity.CRITICAL,
            re.compile(
                r'execute\s*\(\s*["\'].*\+|cursor\.execute\s*\([^)]*\+|'
                r'["\']SELECT\s+.*["\']\s*\+|f["\']SELECT\s+',
                flags,
            ),
            "SQL query built via string concatenation or formatting.",
            "Use parameterized queries / prepared statements.",
            0.9,
        ),
        # NoSQL Injection
        _PatternRule(
            "regex-nosqli-001",
            VulnerabilityCategory.NOSQL_INJECTION,
            Severity.HIGH,
            re.compile(r'\$where|\{\s*["\']?\$gt|find\s*\(\s*\{[^}]*\+', flags),
            "Potential NoSQL injection via operator injection or string concat.",
            "Validate input; use typed query builders; avoid $where.",
            0.82,
        ),
        # XSS
        _PatternRule(
            "regex-xss-001",
            VulnerabilityCategory.XSS,
            Severity.HIGH,
            re.compile(
                r"innerHTML\s*=|document\.write\s*\(|dangerouslySetInnerHTML",
                flags,
            ),
            "DOM XSS sink: unsanitized HTML injection.",
            "Use textContent, sanitize HTML, or framework-safe APIs.",
            0.88,
        ),
        # Command Injection
        _PatternRule(
            "regex-cmd-001",
            VulnerabilityCategory.COMMAND_INJECTION,
            Severity.CRITICAL,
            re.compile(
                r"os\.system\s*\(|subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True|"
                r"Runtime\.getRuntime\(\)\.exec|child_process\.exec\s*\(",
                flags,
            ),
            "OS command execution with potential user-controlled input.",
            "Avoid shell=True; use argument lists; validate allowlists.",
            0.92,
        ),
        # Path Traversal
        _PatternRule(
            "regex-path-001",
            VulnerabilityCategory.PATH_TRAVERSAL,
            Severity.HIGH,
            re.compile(r"\.\./|\.\.\\|open\s*\(\s*\w+\s*\)|readFile\s*\(\s*\w+", flags),
            "Path traversal or file open with dynamic path.",
            "Canonicalize paths; restrict to base directory; validate input.",
            0.8,
        ),
        # Unsafe Deserialization
        _PatternRule(
            "regex-deser-001",
            VulnerabilityCategory.UNSAFE_DESERIALIZATION,
            Severity.CRITICAL,
            re.compile(
                r"pickle\.loads?\s*\(|yaml\.load\s*\(|marshal\.loads?\s*\(",
                flags,
            ),
            "Unsafe deserialization of untrusted data.",
            "Use yaml.safe_load; never unpickle untrusted bytes.",
            0.93,
        ),
        _PatternRule(
            "regex-codeinj-001",
            VulnerabilityCategory.CODE_INJECTION,
            Severity.CRITICAL,
            re.compile(r"\beval\s*\(|\bexec\s*\(", flags),
            "Dynamic code execution (eval/exec).",
            "Remove eval/exec; use safe parsers or explicit logic.",
            0.94,
        ),
        # Secrets
        _PatternRule(
            "regex-secret-001",
            VulnerabilityCategory.HARDCODED_SECRET,
            Severity.HIGH,
            re.compile(
                r'password\s*=\s*["\'][^"\']+["\']|api[_-]?key\s*=\s*["\'][^"\']+["\']|'
                r'token\s*=\s*["\'][^"\']+["\']|secret\s*=\s*["\'][^"\']+["\']',
                flags,
            ),
            "Hardcoded credential or secret in source.",
            "Load secrets from environment or secret manager.",
            0.87,
        ),
        _PatternRule(
            "regex-apikey-001",
            VulnerabilityCategory.API_KEY_EXPOSURE,
            Severity.CRITICAL,
            re.compile(r"AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{35}", flags),
            "Exposed cloud API key pattern.",
            "Rotate key; use IAM roles; never commit keys.",
            0.95,
        ),
        _PatternRule(
            "regex-privkey-001",
            VulnerabilityCategory.PRIVATE_KEY_EXPOSURE,
            Severity.CRITICAL,
            re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----", flags),
            "Private key material in source code.",
            "Remove key; store in HSM/vault; rotate immediately.",
            0.98,
        ),
        _PatternRule(
            "regex-jwt-001",
            VulnerabilityCategory.JWT_SECRET_EXPOSURE,
            Severity.HIGH,
            re.compile(r'jwt[_-]?secret\s*=\s*["\'][^"\']+["\']', flags),
            "Hardcoded JWT signing secret.",
            "Use strong rotating secrets from secure storage.",
            0.9,
        ),
        # Weak crypto
        _PatternRule(
            "regex-weakcrypto-001",
            VulnerabilityCategory.WEAK_CRYPTOGRAPHY,
            Severity.HIGH,
            re.compile(r"DES\.|RC4|ECB|MD5\s*\(|hashlib\.md5", flags),
            "Weak or deprecated cryptographic primitive.",
            "Use AES-GCM, SHA-256+, and modern libraries.",
            0.85,
        ),
        _PatternRule(
            "regex-weakhash-001",
            VulnerabilityCategory.WEAK_HASHING,
            Severity.MEDIUM,
            re.compile(r"hashlib\.(md5|sha1)\s*\(|SHA1\s*\(", flags),
            "Weak hash for security-sensitive use.",
            "Use bcrypt/argon2 for passwords; SHA-256+ for integrity.",
            0.82,
        ),
        _PatternRule(
            "regex-random-001",
            VulnerabilityCategory.INSECURE_RANDOMNESS,
            Severity.MEDIUM,
            re.compile(r"random\.(random|randint)|Math\.random\s*\(", flags),
            "Non-cryptographic RNG used in security context.",
            "Use secrets module or crypto.getRandomValues.",
            0.78,
        ),
        # Resource leak
        _PatternRule(
            "regex-leak-001",
            VulnerabilityCategory.RESOURCE_LEAK,
            Severity.MEDIUM,
            re.compile(r"open\s*\([^)]+\)(?!.*\bwith\b)", flags),
            "File opened without context manager (possible leak).",
            "Use `with open(...) as f:` to ensure closure.",
            0.7,
        ),
        # Buffer overflow hints (C)
        _PatternRule(
            "regex-bof-001",
            VulnerabilityCategory.BUFFER_OVERFLOW,
            Severity.CRITICAL,
            re.compile(r"\b(strcpy|strcat|gets|sprintf)\s*\(", flags),
            "Unsafe C string function prone to buffer overflow.",
            "Use strncpy, snprintf, or safe string libraries.",
            0.88,
        ),
    ]


class RegexDetector:
    def scan(self, code: str, language: str = "unknown") -> list[VulnerabilityFinding]:
        findings: list[VulnerabilityFinding] = []
        lines = code.splitlines()
        seen: set[tuple[str, int, str]] = set()

        for rule in _rules():
            for match in rule.pattern.finditer(code):
                line_no = code[: match.start()].count("\n") + 1
                snippet = lines[line_no - 1].strip() if 0 < line_no <= len(lines) else match.group(0)[:120]
                key = (rule.category.value, line_no, snippet[:80])
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    VulnerabilityFinding(
                        id=VulnerabilityFinding.new_id(),
                        category=rule.category,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        line_number=line_no,
                        description=rule.description,
                        remediation=rule.remediation,
                        code_snippet=snippet,
                        source="regex",
                        rule_id=rule.rule_id,
                    )
                )
        return findings
