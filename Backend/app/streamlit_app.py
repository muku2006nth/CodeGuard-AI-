"""Streamlit UI dashboard (Day 6)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.github_fetcher import fetch_github_file
from src.pipeline import review_code

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔒", layout="wide")

SEVERITY_COLORS = {
    "CRITICAL": "#dc2626",
    "HIGH": "#ea580c",
    "MEDIUM": "#ca8a04",
    "LOW": "#16a34a",
}


def highlight_code(code: str, language: str) -> str:
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        try:
            lexer = guess_lexer(code)
        except Exception:
            lexer = get_lexer_by_name("text")
    formatter = HtmlFormatter(style="monokai", noclasses=True)
    return highlight(code, lexer, formatter)


def severity_badge(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity.upper(), "#6b7280")
    return f'<span style="background:{color};color:white;padding:6px 14px;border-radius:6px;font-weight:bold;">{severity}</span>'


if "history" not in st.session_state:
    st.session_state.history = []

st.title("AI Code Reviewer")
st.caption("CodeBERT classification · ChromaDB RAG · LLaMA3 fix suggestions")

tab_paste, tab_github = st.tabs(["Paste code", "GitHub URL"])

code_input = ""
language_hint = None

with tab_paste:
    language_hint = st.selectbox(
        "Language (optional)",
        ["auto", "python", "javascript", "java", "c"],
        index=0,
    )
    code_input = st.text_area("Source code", height=280, placeholder="Paste vulnerable code here...")

with tab_github:
    github_url = st.text_input("GitHub file URL", placeholder="https://github.com/user/repo/blob/main/file.py")
    if st.button("Fetch from GitHub", type="secondary") and github_url:
        try:
            code_input, language_hint = fetch_github_file(github_url)
            st.success(f"Fetched {len(code_input)} characters")
            st.code(code_input[:2000] + ("..." if len(code_input) > 2000 else ""))
        except Exception as e:
            st.error(str(e))

col_left, col_right = st.columns([1, 1])

with col_left:
    submit = st.button("Run security review", type="primary", use_container_width=True)

if submit and code_input.strip():
    lang = None if language_hint in (None, "auto") else language_hint
    with st.spinner("Analyzing..."):
        result = review_code(code_input, language=lang)

    st.session_state.history.insert(
        0,
        {
            "vuln_type": result.vuln_type,
            "severity": result.severity,
            "confidence": result.confidence,
            "latency": result.latency_seconds,
        },
    )
    st.session_state.history = st.session_state.history[:5]

    with col_right:
        st.markdown(severity_badge(result.severity), unsafe_allow_html=True)
        st.metric("Confidence", f"{result.confidence:.1%}")
        st.metric("Latency", f"{result.latency_seconds:.2f}s")
        if result.cve_refs:
            st.subheader("References")
            for ref in result.cve_refs:
                if ref.upper().startswith("CVE-"):
                    st.markdown(f"- [{ref}](https://nvd.nist.gov/vuln/detail/{ref})")
                else:
                    st.markdown(f"- {ref}")

    st.subheader("Explanation")
    st.write(result.explanation)

    st.subheader("Original vs fixed")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original**")
        st.markdown(highlight_code(result.original_code, result.language), unsafe_allow_html=True)
    with c2:
        st.markdown("**Suggested fix**")
        st.markdown(highlight_code(result.fixed_code, result.language), unsafe_allow_html=True)

elif submit:
    st.warning("Enter code or fetch from GitHub first.")

st.divider()
st.subheader("Review history (last 5)")
if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.caption("No reviews yet.")
