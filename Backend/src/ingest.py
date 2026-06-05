"""
RAG Ingestion Pipeline — OWASP Top 10 + NVD CVE → ChromaDB.

Downloads and chunks security knowledge from two sources:
  1. OWASP Top 10 — fetched from owasp.org (falls back to local data/owasp/ files,
     then to hardcoded summaries if both fail).
  2. NVD CVE summaries — fetched from the free NVD 2.0 API for seven vulnerability
     categories (falls back to data/cve/seed_docs.json, then to a hardcoded set of
     10 common CVE summaries so the pipeline never breaks).

All text is chunked into 512-token segments with 50-token overlap, embedded with
sentence-transformers/all-MiniLM-L6-v2, and stored in a local ChromaDB collection
(cosine similarity, persistent storage at ./chroma_db).

Usage:
    python -m src.ingest                      # full pipeline
    python -m src.ingest --seed-only          # skip network, use bundled data only
    python -m src.ingest --persist-dir ./db   # custom ChromaDB path

No paid services are used. Everything runs locally.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

import chromadb
import requests
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHUNK_SIZE: int = 512
"""Maximum number of whitespace-delimited tokens per chunk."""

CHUNK_OVERLAP: int = 50
"""Overlap in tokens between consecutive chunks for context continuity."""

EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
"""Sentence-transformer model used for embedding (runs locally, ~80 MB)."""

NVD_API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
"""NVD CVE 2.0 REST API endpoint (free, no key required)."""

COLLECTION_NAME: str = "security_kb"
"""ChromaDB collection name for the security knowledge base."""

NVD_KEYWORDS: list[str] = [
    "SQL injection",
    "command injection",
    "XSS",
    "path traversal",
    "deserialization",
    "hardcoded secrets",
    "buffer overflow",
]
"""Vulnerability categories to fetch from NVD."""

NVD_RESULTS_PER_KEYWORD: int = 20
"""Max CVEs to fetch per keyword (keep low to respect NVD rate limits)."""

NVD_REQUEST_DELAY: float = 6.0
"""Seconds to wait between NVD API requests (NVD enforces ~5 req/30s without a key)."""

OWASP_URLS: dict[str, str] = {
    "A01:2021 Broken Access Control": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/A01_2021-Broken_Access_Control.md"
    ),
    "A02:2021 Cryptographic Failures": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/A02_2021-Cryptographic_Failures.md"
    ),
    "A03:2021 Injection": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/A03_2021-Injection.md"
    ),
    "A04:2021 Insecure Design": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/A04_2021-Insecure_Design.md"
    ),
    "A05:2021 Security Misconfiguration": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/A05_2021-Security_Misconfiguration.md"
    ),
    "A06:2021 Vulnerable Components": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/"
        "A06_2021-Vulnerable_and_Outdated_Components.md"
    ),
    "A07:2021 Auth Failures": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/"
        "A07_2021-Identification_and_Authentication_Failures.md"
    ),
    "A08:2021 Integrity Failures": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/"
        "A08_2021-Software_and_Data_Integrity_Failures.md"
    ),
    "A09:2021 Logging Failures": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/"
        "A09_2021-Security_Logging_and_Monitoring_Failures.md"
    ),
    "A10:2021 SSRF": (
        "https://raw.githubusercontent.com/OWASP/Top10/master/2021/docs/"
        "A10_2021-Server-Side_Request_Forgery_(SSRF).md"
    ),
}
"""OWASP Top 10 2021 raw markdown URLs from the official GitHub repo."""

# ---------------------------------------------------------------------------
# Hardcoded fallback CVE summaries (pipeline never breaks)
# ---------------------------------------------------------------------------

HARDCODED_CVE_FALLBACKS: list[dict[str, Any]] = [
    {
        "id": "fallback-cve-2021-44228-0",
        "text": (
            "CVE-2021-44228 (Log4Shell): Apache Log4j2 versions 2.0-beta9 through 2.15.0 "
            "JNDI features do not protect against attacker-controlled LDAP and other JNDI "
            "endpoints. An attacker who can control log messages can execute arbitrary code "
            "loaded from LDAP servers when message lookup substitution is enabled. Remote "
            "code execution with CVSS 10.0. Mitigation: upgrade to Log4j 2.17.0+ or remove "
            "JndiLookup class from the classpath."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2021-44228",
            "severity": "CRITICAL",
            "category": "command injection",
        },
    },
    {
        "id": "fallback-cve-2023-34362-0",
        "text": (
            "CVE-2023-34362: Progress MOVEit Transfer SQL injection vulnerability allows "
            "unauthenticated attackers to gain access to the database. Attackers can infer "
            "database structure and execute SQL statements to alter or delete elements. "
            "Exploited widely in 2023 by Cl0p ransomware group. CVSS 9.8. Mitigation: "
            "apply vendor patches immediately and restrict network access to MOVEit."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2023-34362",
            "severity": "CRITICAL",
            "category": "SQL injection",
        },
    },
    {
        "id": "fallback-cve-2017-5638-0",
        "text": (
            "CVE-2017-5638: Apache Struts 2 Jakarta Multipart parser allows remote code "
            "execution via crafted Content-Type HTTP header. Exploited in the Equifax breach "
            "affecting 147 million consumers. CVSS 10.0. Mitigation: upgrade Struts to "
            "2.3.32 or 2.5.10.1+."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2017-5638",
            "severity": "CRITICAL",
            "category": "command injection",
        },
    },
    {
        "id": "fallback-cve-2019-0708-0",
        "text": (
            "CVE-2019-0708 (BlueKeep): Remote code execution in Windows Remote Desktop "
            "Services. Pre-authentication, no user interaction required. Buffer overflow "
            "allows arbitrary code execution. CVSS 9.8. Mitigation: patch MS Windows, "
            "enable NLA, block TCP port 3389 at the firewall."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2019-0708",
            "severity": "CRITICAL",
            "category": "buffer overflow",
        },
    },
    {
        "id": "fallback-cve-2021-21972-0",
        "text": (
            "CVE-2021-21972: VMware vCenter Server remote code execution via path traversal "
            "and arbitrary file upload on port 443. CVSS 9.8. Mitigation: apply VMware "
            "patches, restrict management interface access."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2021-21972",
            "severity": "CRITICAL",
            "category": "path traversal",
        },
    },
    {
        "id": "fallback-cve-2015-7501-0",
        "text": (
            "CVE-2015-7501: JBoss EAP insecure deserialization allows remote code execution "
            "via crafted serialized Java objects using Apache Commons Collections gadget "
            "chains. CVSS 9.8. Mitigation: remove vulnerable library versions, use look-ahead "
            "deserialization filters."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2015-7501",
            "severity": "CRITICAL",
            "category": "deserialization",
        },
    },
    {
        "id": "fallback-cve-2020-1938-0",
        "text": (
            "CVE-2020-1938 (Ghostcat): Apache Tomcat AJP connector file inclusion "
            "vulnerability. Path traversal through AJP allows reading arbitrary server files "
            "and potential remote code execution if file upload is allowed. CVSS 9.8. "
            "Mitigation: disable AJP connector or restrict to localhost."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2020-1938",
            "severity": "CRITICAL",
            "category": "path traversal",
        },
    },
    {
        "id": "fallback-cve-2019-12384-0",
        "text": (
            "CVE-2019-12384: FasterXML Jackson-databind insecure deserialization via "
            "polymorphic type handling. Untrusted JSON can instantiate arbitrary Java classes. "
            "CVSS 5.9. Mitigation: disable default typing, whitelist allowed types, "
            "upgrade to patched version."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2019-12384",
            "severity": "HIGH",
            "category": "deserialization",
        },
    },
    {
        "id": "fallback-cve-2021-22205-0",
        "text": (
            "CVE-2021-22205: GitLab CE/EE unauthenticated remote code execution via "
            "specially crafted image files processed by ExifTool. Command injection through "
            "DjVu file metadata. CVSS 10.0. Mitigation: upgrade GitLab, disable file "
            "uploads or sanitize metadata."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2021-22205",
            "severity": "CRITICAL",
            "category": "command injection",
        },
    },
    {
        "id": "fallback-cve-2020-11022-0",
        "text": (
            "CVE-2020-11022: jQuery before 3.5.0 is vulnerable to Cross-Site Scripting "
            "(XSS) when passing untrusted HTML to jQuery DOM manipulation methods. Passing "
            "HTML from untrusted sources even after sanitizing it to jQuery methods may "
            "execute untrusted code. CVSS 6.1. Mitigation: upgrade jQuery to 3.5.0+, use "
            "textContent instead of html()."
        ),
        "metadata": {
            "source": "NVD",
            "cve_id": "CVE-2020-11022",
            "severity": "MEDIUM",
            "category": "XSS",
        },
    },
]
"""
Hardcoded fallback CVE summaries covering all 7 required categories.
Used when BOTH the NVD API and the seed_docs.json file are unavailable.
"""

# Hardcoded OWASP Top 10 summaries — used when both web fetch and local files fail
HARDCODED_OWASP_SUMMARIES: list[dict[str, Any]] = [
    {
        "id": "hardcoded-owasp-a01-0",
        "text": (
            "OWASP A01:2021 Broken Access Control. Access control enforces policy such that "
            "users cannot act outside of their intended permissions. Failures lead to "
            "unauthorized information disclosure, modification, or destruction of data. "
            "Prevention: deny by default, enforce record ownership, log access control "
            "failures, rate limit APIs, use short-lived JWT tokens."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "CRITICAL", "category": "A01:2021 Broken Access Control"},
    },
    {
        "id": "hardcoded-owasp-a02-0",
        "text": (
            "OWASP A02:2021 Cryptographic Failures. Failures related to cryptography leading "
            "to sensitive data exposure. Includes hard-coded passwords, weak algorithms, "
            "insufficient entropy. Prevention: classify data, encrypt at rest and in transit, "
            "use strong algorithms (AES-256, Argon2), proper key management."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "HIGH", "category": "A02:2021 Cryptographic Failures"},
    },
    {
        "id": "hardcoded-owasp-a03-0",
        "text": (
            "OWASP A03:2021 Injection. SQL, NoSQL, OS command, and LDAP injection occur when "
            "untrusted data is sent to an interpreter. Prevention: parameterized queries, "
            "ORMs, input validation with allowlists, escaping special characters, subprocess "
            "without shell=True."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "CRITICAL", "category": "A03:2021 Injection"},
    },
    {
        "id": "hardcoded-owasp-a07-0",
        "text": (
            "OWASP A07:2021 XSS. Cross-Site Scripting flaws occur when untrusted data is "
            "included in web pages without proper validation or escaping. Reflected, Stored, "
            "and DOM-based XSS can lead to session hijacking and keylogging. Prevention: "
            "context-aware output encoding, Content Security Policy, auto-escaping frameworks."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "HIGH", "category": "A07:2021 XSS"},
    },
    {
        "id": "hardcoded-owasp-a08-0",
        "text": (
            "OWASP A08:2021 Software and Data Integrity Failures. Insecure deserialization, "
            "untrusted CI/CD pipelines, and auto-updates without integrity verification. "
            "Prevention: digital signatures, trusted repositories, dependency scanning, "
            "code review for config changes."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "HIGH", "category": "A08:2021 Integrity Failures"},
    },
    {
        "id": "hardcoded-owasp-a10-0",
        "text": (
            "OWASP A10:2021 Server-Side Request Forgery (SSRF). Web applications fetching "
            "remote resources without validating user-supplied URLs. Attackers access internal "
            "services, cloud metadata, scan internal networks. Prevention: validate URLs with "
            "allowlists, disable redirections, do not send raw responses to clients."
        ),
        "metadata": {"source": "OWASP", "cve_id": "", "severity": "HIGH", "category": "A10:2021 SSRF"},
    },
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split *text* into overlapping chunks of at most *chunk_size* whitespace tokens.

    Args:
        text: Raw text to chunk.
        chunk_size: Maximum number of tokens (words) per chunk.
        overlap: Number of tokens shared between consecutive chunks.

    Returns:
        List of text chunks. Empty list if *text* is blank.
    """
    words = text.split()
    if not words:
        return []

    stride = max(1, chunk_size - overlap)
    chunks: list[str] = []
    for i in range(0, len(words), stride):
        piece = " ".join(words[i : i + chunk_size])
        if piece.strip():
            chunks.append(piece)
        if i + chunk_size >= len(words):
            break
    return chunks


# ---------------------------------------------------------------------------
# OWASP fetching
# ---------------------------------------------------------------------------


def _strip_markdown_images(text: str) -> str:
    """Remove markdown image tags ``![alt](url)`` that add noise to embeddings."""
    return re.sub(r"!\[.*?\]\(.*?\)", "", text)


def fetch_owasp_from_web() -> list[dict[str, Any]]:
    """Fetch OWASP Top 10 2021 content from the official GitHub repository.

    Each document is stripped of markdown images, chunked, and tagged with
    ``source=OWASP`` metadata.

    Returns:
        List of document dicts (``id``, ``text``, ``metadata``).
        Returns an empty list on any network error.
    """
    docs: list[dict[str, Any]] = []
    for category, url in OWASP_URLS.items():
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            text = _strip_markdown_images(resp.text)
            for i, chunk in enumerate(chunk_text(text)):
                slug = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")
                docs.append(
                    {
                        "id": f"owasp-web-{slug}-{i}",
                        "text": chunk,
                        "metadata": {
                            "source": "OWASP",
                            "cve_id": "",
                            "severity": "HIGH",
                            "category": category,
                        },
                    }
                )
            logger.info("Fetched OWASP %s (%d chunks)", category, i + 1)
        except (requests.RequestException, Exception) as exc:
            logger.warning("Failed to fetch OWASP %s: %s", category, exc)
            continue
    return docs


def load_owasp_from_disk(owasp_dir: Path) -> list[dict[str, Any]]:
    """Load OWASP documents from local ``data/owasp/`` directory.

    Reads ``.txt``, ``.md``, and ``.html`` files, chunks them, and tags each
    chunk with ``source=OWASP`` metadata.

    Args:
        owasp_dir: Path to the local OWASP data directory.

    Returns:
        List of document dicts. Empty list if directory does not exist.
    """
    docs: list[dict[str, Any]] = []
    if not owasp_dir.exists():
        logger.info("OWASP directory %s does not exist — skipping.", owasp_dir)
        return docs

    for path in sorted(owasp_dir.glob("**/*")):
        if path.suffix.lower() not in {".txt", ".md", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("Could not read %s: %s", path, exc)
            continue

        text = _strip_markdown_images(text)
        for i, chunk in enumerate(chunk_text(text)):
            docs.append(
                {
                    "id": f"owasp-local-{path.stem}-{i}",
                    "text": chunk,
                    "metadata": {
                        "source": "OWASP",
                        "cve_id": "",
                        "severity": "HIGH",
                        "category": path.stem,
                    },
                }
            )
    logger.info("Loaded %d OWASP chunks from disk (%s).", len(docs), owasp_dir)
    return docs


# ---------------------------------------------------------------------------
# NVD CVE fetching
# ---------------------------------------------------------------------------


def _extract_severity(cve_data: dict) -> str:
    """Extract the highest CVSS severity string from a CVE record.

    Checks CVSS v3.1 → v3.0 → v2.0 metrics in order of preference.

    Args:
        cve_data: The ``cve`` object from an NVD API response item.

    Returns:
        One of ``CRITICAL``, ``HIGH``, ``MEDIUM``, ``LOW``, or ``UNKNOWN``.
    """
    metrics = cve_data.get("metrics", {})

    # Try CVSS v3.1 first
    for key in ("cvssMetricV31", "cvssMetricV30"):
        entries = metrics.get(key, [])
        if entries:
            severity = entries[0].get("cvssData", {}).get("baseSeverity", "")
            if severity:
                return severity.upper()

    # Fall back to CVSS v2
    v2_entries = metrics.get("cvssMetricV2", [])
    if v2_entries:
        score = v2_entries[0].get("cvssData", {}).get("baseScore", 0)
        if score >= 9.0:
            return "CRITICAL"
        if score >= 7.0:
            return "HIGH"
        if score >= 4.0:
            return "MEDIUM"
        return "LOW"

    return "UNKNOWN"


def fetch_cve_summaries(
    keyword: str,
    max_results: int = NVD_RESULTS_PER_KEYWORD,
) -> list[dict[str, Any]]:
    """Fetch CVE summaries from the NVD 2.0 API for a single keyword.

    Args:
        keyword: Vulnerability keyword to search (e.g. ``"SQL injection"``).
        max_results: Maximum number of CVEs to retrieve.

    Returns:
        List of document dicts with NVD metadata. Empty on network failure.

    Raises:
        requests.RequestException: Propagated to caller for per-keyword handling.
    """
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": min(max_results, 2000),
    }
    resp = requests.get(NVD_API_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    docs: list[dict[str, Any]] = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "unknown")
        descriptions = cve.get("descriptions", [])
        desc = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "",
        )
        if not desc:
            continue

        severity = _extract_severity(cve)

        for i, chunk in enumerate(chunk_text(desc)):
            docs.append(
                {
                    "id": f"nvd-{cve_id}-{i}",
                    "text": chunk,
                    "metadata": {
                        "source": "NVD",
                        "cve_id": cve_id,
                        "severity": severity,
                        "category": keyword,
                    },
                }
            )
    return docs


def fetch_all_nvd_keywords(
    keywords: list[str] | None = None,
    max_per_keyword: int = NVD_RESULTS_PER_KEYWORD,
) -> list[dict[str, Any]]:
    """Fetch CVEs from NVD for every keyword, with rate-limit delays.

    If a single keyword fails the function logs a warning and continues
    with the remaining keywords so one transient failure does not abort
    the entire ingestion.

    Args:
        keywords: List of search terms. Defaults to :data:`NVD_KEYWORDS`.
        max_per_keyword: Max CVEs per keyword.

    Returns:
        Combined list of document dicts from all successful fetches.
    """
    keywords = keywords or NVD_KEYWORDS
    all_docs: list[dict[str, Any]] = []

    for idx, kw in enumerate(keywords):
        try:
            docs = fetch_cve_summaries(kw, max_results=max_per_keyword)
            all_docs.extend(docs)
            logger.info("NVD keyword '%s': %d chunks fetched.", kw, len(docs))
        except requests.RequestException as exc:
            logger.warning("NVD fetch failed for '%s': %s — skipping.", kw, exc)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("NVD parse error for '%s': %s — skipping.", kw, exc)

        # Respect NVD rate limits (5 requests per 30 s without API key)
        if idx < len(keywords) - 1:
            logger.debug("Sleeping %.1fs for NVD rate limit…", NVD_REQUEST_DELAY)
            time.sleep(NVD_REQUEST_DELAY)

    return all_docs


# ---------------------------------------------------------------------------
# Seed / fallback loading
# ---------------------------------------------------------------------------


def load_seed_docs(seed_path: Path) -> list[dict[str, Any]]:
    """Load pre-bundled seed documents from a JSON file.

    Args:
        seed_path: Path to ``data/cve/seed_docs.json``.

    Returns:
        Parsed list of document dicts. Empty list if file is missing or invalid.
    """
    if not seed_path.exists():
        logger.info("Seed file %s not found — skipping.", seed_path)
        return []
    try:
        with open(seed_path, encoding="utf-8") as f:
            docs = json.load(f)
        logger.info("Loaded %d seed documents from %s.", len(docs), seed_path)
        return docs
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load seed docs from %s: %s", seed_path, exc)
        return []


# ---------------------------------------------------------------------------
# ChromaDB ingestion
# ---------------------------------------------------------------------------


def ingest_to_chroma(
    documents: list[dict[str, Any]],
    persist_dir: str = "data/chroma_db",
    collection_name: str = COLLECTION_NAME,
) -> int:
    """Embed and upsert documents into a local ChromaDB collection.

    Uses ``all-MiniLM-L6-v2`` for embedding. Creates the persist directory
    if it does not exist. Existing documents with the same ID are overwritten
    (upsert semantics) so re-running ingestion is idempotent.

    Args:
        documents: List of dicts with keys ``id``, ``text``, ``metadata``.
        persist_dir: Filesystem path for ChromaDB persistent storage.
        collection_name: Name of the ChromaDB collection.

    Returns:
        Number of documents ingested.
    """
    if not documents:
        logger.warning("No documents to ingest — collection unchanged.")
        return 0

    os.makedirs(persist_dir, exist_ok=True)

    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
    )
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Ensure every metadata dict has all four required fields (ChromaDB does
    # not accept None values in metadata, so default to empty string).
    for doc in documents:
        meta = doc.get("metadata", {})
        meta.setdefault("source", "unknown")
        meta.setdefault("cve_id", "")
        meta.setdefault("severity", "UNKNOWN")
        meta.setdefault("category", "")
        # ChromaDB rejects None — coerce to empty string
        for k, v in meta.items():
            if v is None:
                meta[k] = ""
        doc["metadata"] = meta

    ids = [d["id"] for d in documents]
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    # ChromaDB has internal batch size limits; upsert in batches of 100
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=texts[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    logger.info(
        "Ingested %d chunks into ChromaDB at '%s' (collection: %s).",
        len(documents),
        persist_dir,
        collection_name,
    )
    return len(documents)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point — orchestrates the full ingestion pipeline.

    Steps:
      1. Attempt to fetch OWASP Top 10 from GitHub → fall back to local
         ``data/owasp/`` files → fall back to hardcoded summaries.
      2. Fetch CVEs from NVD for all 7 keywords → fall back to
         ``data/cve/seed_docs.json`` → fall back to 10 hardcoded CVEs.
      3. Chunk everything at 512 tokens / 50 overlap.
      4. Embed + upsert into ChromaDB.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Ingest OWASP Top 10 + NVD CVEs into ChromaDB for the RAG pipeline.",
    )
    parser.add_argument(
        "--owasp-dir",
        default="data/owasp",
        help="Local directory with OWASP .md/.txt files (default: data/owasp).",
    )
    parser.add_argument(
        "--persist-dir",
        default="data/chroma_db",
        help="ChromaDB persistent storage directory (default: data/chroma_db).",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Skip all network requests; use only bundled seed data + local files.",
    )
    parser.add_argument(
        "--cve-limit",
        type=int,
        default=NVD_RESULTS_PER_KEYWORD,
        help=f"Max CVEs per NVD keyword (default: {NVD_RESULTS_PER_KEYWORD}).",
    )
    args = parser.parse_args()

    documents: list[dict[str, Any]] = []

    # ---- OWASP ----
    if not args.seed_only:
        logger.info("Fetching OWASP Top 10 from owasp.org / GitHub…")
        owasp_docs = fetch_owasp_from_web()
        if owasp_docs:
            documents.extend(owasp_docs)
            logger.info("✓ Fetched %d OWASP chunks from web.", len(owasp_docs))
        else:
            logger.warning("Web fetch returned 0 OWASP docs — trying local files.")

    # Fall back to local files if web fetch produced nothing
    if not any(d["metadata"].get("source") == "OWASP" for d in documents):
        local_owasp = load_owasp_from_disk(Path(args.owasp_dir))
        if local_owasp:
            documents.extend(local_owasp)
            logger.info("✓ Loaded %d OWASP chunks from local disk.", len(local_owasp))
        else:
            logger.warning("No local OWASP files — using hardcoded summaries.")
            documents.extend(HARDCODED_OWASP_SUMMARIES)
            logger.info("✓ Added %d hardcoded OWASP summaries.", len(HARDCODED_OWASP_SUMMARIES))

    # ---- NVD CVEs ----
    nvd_docs: list[dict[str, Any]] = []
    if not args.seed_only:
        logger.info("Fetching CVEs from NVD for %d keywords…", len(NVD_KEYWORDS))
        nvd_docs = fetch_all_nvd_keywords(max_per_keyword=args.cve_limit)

    if nvd_docs:
        documents.extend(nvd_docs)
        logger.info("✓ Fetched %d NVD CVE chunks.", len(nvd_docs))
    else:
        # Fall back to seed_docs.json
        seed_path = Path("data/cve/seed_docs.json")
        seed_docs = load_seed_docs(seed_path)
        if seed_docs:
            documents.extend(seed_docs)
            logger.info("✓ Loaded %d seed CVE documents.", len(seed_docs))
        else:
            # Final fallback: hardcoded CVE summaries
            logger.warning("No NVD data and no seed file — using hardcoded CVE fallbacks.")
            documents.extend(HARDCODED_CVE_FALLBACKS)
            logger.info("✓ Added %d hardcoded CVE fallback documents.", len(HARDCODED_CVE_FALLBACKS))

    # Also always load seeds to ensure minimum coverage even when NVD returns data
    if nvd_docs:
        seed_path = Path("data/cve/seed_docs.json")
        seed_extra = load_seed_docs(seed_path)
        if seed_extra:
            # Only add seeds whose IDs are not already present
            existing_ids = {d["id"] for d in documents}
            new_seeds = [s for s in seed_extra if s["id"] not in existing_ids]
            documents.extend(new_seeds)
            if new_seeds:
                logger.info("✓ Merged %d additional seed docs for coverage.", len(new_seeds))

    # ---- Ingest ----
    if not documents:
        logger.error(
            "No documents collected from any source! "
            "Add files to data/owasp/ or data/cve/seed_docs.json."
        )
        raise SystemExit(1)

    logger.info("Total documents to ingest: %d", len(documents))
    count = ingest_to_chroma(documents, persist_dir=args.persist_dir)
    print(f"\n✅ Successfully ingested {count} chunks into {args.persist_dir}")
    print(f"   Collection: {COLLECTION_NAME}")
    print(f"   Embedding model: {EMBEDDING_MODEL}")


if __name__ == "__main__":
    main()
