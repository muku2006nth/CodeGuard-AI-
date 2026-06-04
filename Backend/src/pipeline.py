"""
Main orchestrator: CodeBERT -> RAG -> LLM (Day 4).
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

from src.predict import CodeBERTClassifier, ClassificationResult
from src.prompts import FIX_GENERATION_SYSTEM, FIX_GENERATION_USER, NO_CVE_CONTEXT
from src.retriever import SecurityRetriever, format_rag_context

load_dotenv()


@dataclass
class ReviewResult:
    vuln_type: str
    severity: str
    confidence: float
    is_vulnerable: bool
    cve_refs: list[str] = field(default_factory=list)
    explanation: str = ""
    fixed_code: str = ""
    original_code: str = ""
    language: str = "python"
    latency_seconds: float = 0.0
    rag_chunks_used: int = 0


def detect_language(code: str, hint: str | None = None) -> str:
    if hint:
        return hint.lower()
    if "def " in code or "import " in code:
        return "python"
    if "function " in code or "const " in code or "=>" in code:
        return "javascript"
    if "public class" in code or "void main" in code:
        return "java"
    if "#include" in code:
        return "c"
    return "python"


def _severity_from_type(vuln_type: str, confidence: float) -> str:
    critical = {"SQL Injection", "Command Injection", "Buffer Overflow"}
    high = {"Cross-Site Scripting (XSS)", "Path Traversal", "Use After Free"}
    if "Safe" in vuln_type:
        return "LOW"
    if vuln_type in critical and confidence >= 0.9:
        return "CRITICAL"
    if vuln_type in critical or vuln_type in high:
        return "HIGH"
    return "MEDIUM"


def _parse_llm_response(text: str, language: str) -> dict:
    out = {
        "vuln_type": "Unknown",
        "severity": "MEDIUM",
        "explanation": text.strip(),
        "fixed_code": "",
        "references": [],
    }

    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("VULN_TYPE:"):
            out["vuln_type"] = line.split(":", 1)[1].strip()
        elif upper.startswith("SEVERITY:"):
            out["severity"] = line.split(":", 1)[1].strip().upper()
        elif upper.startswith("EXPLANATION:"):
            out["explanation"] = line.split(":", 1)[1].strip()

    ref_match = re.search(r"REFERENCES:\s*(.+)", text, re.IGNORECASE)
    if ref_match:
        refs = [r.strip() for r in ref_match.group(1).split(",") if r.strip()]
        out["references"] = [r for r in refs if r.lower() != "none"]

    code_match = re.search(
        rf"FIXED_CODE:\s*```{language}\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not code_match:
        code_match = re.search(r"FIXED_CODE:\s*```\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if code_match:
        out["fixed_code"] = code_match.group(1).strip()

    return out


def _generate_fix_llm(
    code: str,
    language: str,
    classification: ClassificationResult,
    rag_context: str,
) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "vuln_type": classification.vuln_type,
            "severity": _severity_from_type(classification.vuln_type, classification.confidence),
            "explanation": (
                "Set GROQ_API_KEY in .env to enable LLaMA3 fix generation. "
                "Classification and RAG context are still available."
            ),
            "fixed_code": code,
            "references": [],
        }

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError:
        return {
            "vuln_type": classification.vuln_type,
            "severity": _severity_from_type(classification.vuln_type, classification.confidence),
            "explanation": "Install langchain-groq for LLM fix generation.",
            "fixed_code": code,
            "references": [],
        }

    severity_hint = _severity_from_type(classification.vuln_type, classification.confidence)
    user_prompt = FIX_GENERATION_USER.format(
        language=language,
        code=code,
        vuln_type=classification.vuln_type,
        confidence=classification.confidence,
        severity_hint=severity_hint,
        rag_context=rag_context or NO_CVE_CONTEXT,
    )

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0.2)
    response = llm.invoke(
        [SystemMessage(content=FIX_GENERATION_SYSTEM), HumanMessage(content=user_prompt)]
    )
    return _parse_llm_response(response.content, language)


class CodeReviewPipeline:
    def __init__(self):
        self.classifier = CodeBERTClassifier()
        self.retriever = SecurityRetriever()

    def review(self, code: str, language: str | None = None) -> ReviewResult:
        start = time.perf_counter()
        lang = detect_language(code, language)

        classification = self.classifier.classify(code)
        query = f"{classification.vuln_type} vulnerability in {lang}"
        chunks = self.retriever.query(query, top_k=3)
        rag_context = format_rag_context(chunks)

        llm_out = _generate_fix_llm(code, lang, classification, rag_context)

        cve_refs = list(llm_out.get("references", []))
        for c in chunks:
            if c.cve_id and c.cve_id not in cve_refs:
                cve_refs.append(c.cve_id)
            if c.category and c.category not in cve_refs:
                cve_refs.append(c.category)

        severity = llm_out.get("severity") or _severity_from_type(
            classification.vuln_type, classification.confidence
        )

        return ReviewResult(
            vuln_type=llm_out.get("vuln_type", classification.vuln_type),
            severity=severity,
            confidence=classification.confidence,
            is_vulnerable=classification.is_vulnerable,
            cve_refs=cve_refs[:10],
            explanation=llm_out.get("explanation", ""),
            fixed_code=llm_out.get("fixed_code", code),
            original_code=code,
            language=lang,
            latency_seconds=time.perf_counter() - start,
            rag_chunks_used=len(chunks),
        )


def review_code(code: str, language: str | None = None) -> ReviewResult:
    return CodeReviewPipeline().review(code, language=language)
