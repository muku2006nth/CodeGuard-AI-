"""
Main orchestrator: CodeBERT → RAG → LLM fix generation.

Pipeline flow:
  1. **Language detection** — heuristic identification of source language.
  2. **Classification** — CodeBERT/UniXCoder predicts vulnerability type + confidence.
  3. **RAG retrieval** — query ChromaDB for the top 3 most relevant OWASP/CVE chunks
     matching the detected vulnerability type. If no match exceeds the similarity
     threshold (default 0.7), the ``no_match`` flag is set and the LLM receives
     a generic secure-coding prompt instead.
  4. **LLM fix generation** — Groq LLaMA-3 generates an explanation and fixed code,
     grounded in the RAG context.

All components degrade gracefully: missing API keys, empty ChromaDB, or network
errors produce informative fallback responses rather than exceptions.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

from src.predict import CodeBERTClassifier, ClassificationResult
from src.prompts import FIX_GENERATION_SYSTEM, FIX_GENERATION_USER, NO_CVE_CONTEXT
from src.retriever import (
    SecurityRetriever,
    format_rag_context,
    format_chunks_as_dicts,
)

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ReviewResult:
    """Complete result of a code vulnerability review.

    Attributes:
        vuln_type: Human-readable vulnerability type label.
        severity: ``CRITICAL`` | ``HIGH`` | ``MEDIUM`` | ``LOW``.
        confidence: Model confidence in ``[0, 1]``.
        is_vulnerable: Whether the code is classified as vulnerable.
        cve_refs: List of CVE/OWASP IDs referenced in the analysis.
        explanation: Plain-English explanation of the vulnerability.
        fixed_code: Suggested fixed version of the code.
        original_code: The input code that was analysed.
        language: Detected or hinted programming language.
        latency_seconds: Wall-clock time for the full pipeline.
        rag_chunks_used: Number of RAG chunks that passed similarity threshold.
        rag_no_match: ``True`` when no knowledge-base chunk was relevant.
        rag_chunks: Raw chunk dicts passed to the LLM (for debugging/audit).
    """

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
    rag_no_match: bool = False
    rag_chunks: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def detect_language(code: str, hint: str | None = None) -> str:
    """Detect the programming language of *code* using simple heuristics.

    Args:
        code: Source code string.
        hint: Optional explicit language hint (returned as-is if provided).

    Returns:
        Lowercase language name.
    """
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
    """Derive a severity rating from the vulnerability type and model confidence.

    Args:
        vuln_type: Vulnerability category label from the classifier.
        confidence: Model confidence score.

    Returns:
        One of ``CRITICAL``, ``HIGH``, ``MEDIUM``, ``LOW``.
    """
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
    """Parse the structured LLM response into a dict.

    Expected format::

        VULN_TYPE: <one line>
        SEVERITY: CRITICAL|HIGH|MEDIUM|LOW
        EXPLANATION: <text>
        FIXED_CODE:
        ```<language>
        <code>
        ```
        REFERENCES: <comma-separated>

    Args:
        text: Raw LLM response text.
        language: Programming language for code fence matching.

    Returns:
        Dict with keys: ``vuln_type``, ``severity``, ``explanation``,
        ``fixed_code``, ``references``.
    """
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
        code_match = re.search(
            r"FIXED_CODE:\s*```\s*(.*?)```", text, re.DOTALL | re.IGNORECASE
        )
    if code_match:
        out["fixed_code"] = code_match.group(1).strip()

    return out


# ---------------------------------------------------------------------------
# LLM fix generation
# ---------------------------------------------------------------------------


def _generate_fix_llm(
    code: str,
    language: str,
    classification: ClassificationResult,
    rag_context: str,
) -> dict:
    """Call Groq LLaMA-3 to generate a vulnerability explanation and fix.

    Degrades gracefully:
      * Missing ``GROQ_API_KEY`` → returns classification-only result.
      * Missing ``langchain-groq`` package → returns install hint.

    Args:
        code: The vulnerable source code.
        language: Programming language.
        classification: Output from CodeBERT classifier.
        rag_context: Formatted RAG context string for the prompt.

    Returns:
        Parsed LLM response dict.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "vuln_type": classification.vuln_type,
            "severity": _severity_from_type(
                classification.vuln_type, classification.confidence
            ),
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
            "severity": _severity_from_type(
                classification.vuln_type, classification.confidence
            ),
            "explanation": "Install langchain-groq for LLM fix generation.",
            "fixed_code": code,
            "references": [],
        }

    severity_hint = _severity_from_type(
        classification.vuln_type, classification.confidence
    )
    user_prompt = FIX_GENERATION_USER.format(
        language=language,
        code=code,
        vuln_type=classification.vuln_type,
        confidence=classification.confidence,
        severity_hint=severity_hint,
        rag_context=rag_context or NO_CVE_CONTEXT,
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile", api_key=api_key, temperature=0.2
    )
    response = llm.invoke(
        [
            SystemMessage(content=FIX_GENERATION_SYSTEM),
            HumanMessage(content=user_prompt),
        ]
    )
    return _parse_llm_response(response.content, language)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class CodeReviewPipeline:
    """End-to-end code vulnerability review pipeline.

    Orchestrates:  CodeBERT classification → RAG retrieval → LLM fix generation.

    The pipeline is initialized once (loads model + ChromaDB) and can be
    called repeatedly via :meth:`review`.
    """

    def __init__(self) -> None:
        self.classifier = CodeBERTClassifier()
        self.retriever = SecurityRetriever()

    def review(self, code: str, language: str | None = None) -> ReviewResult:
        """Run the full review pipeline on a code snippet.

        Steps:
          1. Detect language.
          2. Classify with CodeBERT → get ``vuln_type`` + ``confidence``.
          3. Query RAG retriever with ``"{vuln_type} vulnerability in {lang}"``.
          4. If ``no_match`` (top score < threshold), pass generic context.
          5. Generate fix via Groq LLaMA-3 with RAG context.
          6. Assemble :class:`ReviewResult`.

        Args:
            code: Source code to review.
            language: Optional language hint (auto-detected if omitted).

        Returns:
            :class:`ReviewResult` with classification, RAG chunks, and LLM output.
        """
        start = time.perf_counter()
        lang = detect_language(code, language)

        # ---- Step 1: Classification ----
        classification = self.classifier.classify(code)
        logger.info(
            "Classification: %s (confidence=%.3f, vulnerable=%s)",
            classification.vuln_type,
            classification.confidence,
            classification.is_vulnerable,
        )

        # ---- Step 2: RAG Retrieval ----
        query = f"{classification.vuln_type} vulnerability in {lang}"
        rag_result = self.retriever.query_with_metadata(query, top_k=3)
        chunks = rag_result.chunks
        no_match = rag_result.no_match

        if no_match:
            logger.info(
                "RAG: no match above threshold for '%s' — using generic context.",
                query,
            )

        # Format RAG context for the LLM prompt
        rag_context = format_rag_context(chunks)

        # Serialize chunks for the result (audit trail)
        rag_chunk_dicts = format_chunks_as_dicts(chunks)

        logger.info(
            "RAG: %d chunks retrieved (no_match=%s).", len(chunks), no_match
        )

        # ---- Step 3: LLM Fix Generation ----
        llm_out = _generate_fix_llm(code, lang, classification, rag_context)

        # ---- Step 4: Assemble references ----
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
            rag_no_match=no_match,
            rag_chunks=rag_chunk_dicts,
        )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def review_code(code: str, language: str | None = None) -> ReviewResult:
    """One-shot convenience wrapper around :class:`CodeReviewPipeline`.

    Creates a fresh pipeline instance per call. For repeated use, prefer
    instantiating ``CodeReviewPipeline`` once and calling ``.review()``
    directly to avoid reloading models.

    Args:
        code: Source code to review.
        language: Optional language hint.

    Returns:
        :class:`ReviewResult`.
    """
    return CodeReviewPipeline().review(code, language=language)
