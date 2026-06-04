"""Explanation engine — enriches findings with educational content."""

from __future__ import annotations

from app.models.finding import VulnerabilityCategory, VulnerabilityFinding

EXPLANATIONS: dict[VulnerabilityCategory, dict[str, str]] = {
    VulnerabilityCategory.SQL_INJECTION: {
        "what": "User input is concatenated into SQL queries.",
        "why": "Attackers can alter query logic to read, modify, or delete data.",
        "impact": "Full database compromise, credential theft, data exfiltration.",
        "fix": "Use parameterized queries with bound parameters.",
        "example": 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
    },
    VulnerabilityCategory.XSS: {
        "what": "Untrusted data is written into the DOM as HTML.",
        "why": "Browsers execute attacker-controlled scripts in victim sessions.",
        "impact": "Session hijacking, credential theft, defacement.",
        "fix": "Encode output; use CSP; prefer safe DOM APIs.",
        "example": "element.textContent = userInput;",
    },
    VulnerabilityCategory.COMMAND_INJECTION: {
        "what": "Shell commands include unsanitized user input.",
        "why": "Attackers execute arbitrary OS commands on the server.",
        "impact": "Remote code execution, ransomware deployment, lateral movement.",
        "fix": "Use subprocess with list args; shell=False; strict allowlists.",
        "example": 'subprocess.run(["ping", "-c", "1", host], check=True)',
    },
    VulnerabilityCategory.PATH_TRAVERSAL: {
        "what": "File paths include ../ sequences or unvalidated names.",
        "why": "Attackers read or write files outside intended directories.",
        "impact": "Exposure of /etc/passwd, config files, source code.",
        "fix": "Resolve paths; enforce base directory; reject .. segments.",
        "example": 'safe = (BASE / Path(name).name).resolve(); assert BASE in safe.parents',
    },
    VulnerabilityCategory.HARDCODED_SECRET: {
        "what": "Credentials or tokens are embedded in source code.",
        "why": "Secrets in repos are scraped by bots and abused at scale.",
        "impact": "Account takeover, cloud resource abuse, compliance violations.",
        "fix": "Use environment variables or secret managers.",
        "example": 'api_key = os.environ["API_KEY"]',
    },
    VulnerabilityCategory.UNSAFE_DESERIALIZATION: {
        "what": "Untrusted serialized objects are deserialized.",
        "why": "Gadget chains can lead to arbitrary code execution.",
        "impact": "Full server compromise via malicious payloads.",
        "fix": "Never deserialize untrusted data; use JSON with schema validation.",
        "example": "data = json.loads(payload); validate(data, schema)",
    },
    VulnerabilityCategory.CODE_INJECTION: {
        "what": "Dynamic execution of code from strings (eval/exec).",
        "why": "Any input can become executable attacker code.",
        "impact": "Complete application compromise.",
        "fix": "Remove eval/exec; parse with safe libraries.",
        "example": "# Use ast.literal_eval only for literals, or structured parsers",
    },
    VulnerabilityCategory.WEAK_CRYPTOGRAPHY: {
        "what": "Deprecated or broken crypto primitives are used.",
        "why": "Ciphertext can be broken with modern attacks.",
        "impact": "Decryption of sensitive data, forged signatures.",
        "fix": "Use AES-GCM, ChaCha20-Poly1305, SHA-256+.",
        "example": "from cryptography.fernet import Fernet",
    },
    VulnerabilityCategory.INSECURE_RANDOMNESS: {
        "what": "Predictable RNG used for security-sensitive values.",
        "why": "Tokens and session IDs can be guessed.",
        "impact": "Session fixation, token brute-force success.",
        "fix": "Use secrets.token_urlsafe or os.urandom.",
        "example": "token = secrets.token_urlsafe(32)",
    },
    VulnerabilityCategory.RESOURCE_LEAK: {
        "what": "Resources are not reliably closed on all paths.",
        "why": "Exhaustion leads to denial of service.",
        "impact": "File descriptor exhaustion, memory growth, outages.",
        "fix": "Use context managers (with statements).",
        "example": "with open(path) as f: data = f.read()",
    },
}

DEFAULT_EXPLANATION = {
    "what": "A security anti-pattern was detected in this code region.",
    "why": "It may violate secure coding standards and enable exploitation.",
    "impact": "Impact depends on context; treat as security debt until reviewed.",
    "fix": "Review OWASP guidelines and apply defense in depth.",
    "example": "# Apply principle of least privilege and input validation",
}


class Explainer:
    def enrich(self, findings: list[VulnerabilityFinding]) -> list[VulnerabilityFinding]:
        for f in findings:
            tpl = EXPLANATIONS.get(f.category, DEFAULT_EXPLANATION)
            f.what_is_wrong = tpl["what"]
            f.why_dangerous = tpl["why"]
            f.real_world_impact = tpl["impact"]
            if not f.remediation:
                f.remediation = tpl["fix"]
            f.secure_example = tpl["example"]
        return findings

    def build_summary(
        self,
        findings: list[VulnerabilityFinding],
        risk_score: int,
        severity: str,
        ml_prob: float,
    ) -> str:
        if not findings and ml_prob < 0.5:
            return (
                "No significant static security issues detected. "
                "ML risk signal is low. Continue secure coding practices."
            )
        cats = sorted({f.category.value for f in findings})
        return (
            f"Analysis complete: risk score {risk_score}/100 ({severity}). "
            f"Found {len(findings)} issue(s) across {len(cats)} categories. "
            f"ML suspicious probability: {ml_prob:.0%}."
        )

    def build_recommendations(self, findings: list[VulnerabilityFinding]) -> list[str]:
        recs: list[str] = []
        seen: set[str] = set()
        for f in findings:
            key = f.category.value
            if key in seen:
                continue
            seen.add(key)
            recs.append(f"[{f.severity.value}] {f.category.value}: {f.remediation}")
        if not recs:
            recs.append("No critical findings — maintain input validation and dependency updates.")
        return recs[:15]
