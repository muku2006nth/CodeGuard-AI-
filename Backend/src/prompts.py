"""LLM prompt templates for vulnerability fix generation."""

FIX_GENERATION_SYSTEM = """You are a senior application security engineer.
Given vulnerable source code, a vulnerability classification, and security reference context,
produce a concise, accurate fix and explanation.
Never invent CVE IDs not present in the provided context.
If no CVE context is relevant, say so and give generic secure-coding guidance."""

FIX_GENERATION_USER = """## Vulnerable code
```{language}
{code}
```

## Classification
- Type: {vuln_type}
- Confidence: {confidence:.1%}
- Severity hint: {severity_hint}

## Security context (RAG)
{rag_context}

## Instructions
Respond in this exact structure:

VULN_TYPE: <one line>
SEVERITY: CRITICAL|HIGH|MEDIUM|LOW
EXPLANATION: <2-4 sentences in plain English>
FIXED_CODE:
```{language}
<complete fixed code>
```
REFERENCES: <comma-separated CVE/OWASP IDs from context only, or "none">
"""

NO_CVE_CONTEXT = "No specific CVE/OWASP match above similarity threshold. Use general secure coding best practices."
