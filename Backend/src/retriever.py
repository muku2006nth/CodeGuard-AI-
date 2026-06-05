"""
RAG Retriever — Semantic search over the OWASP + CVE knowledge base.

Loads a pre-populated ChromaDB collection (created by ``src.ingest``) and
provides a query interface that returns the top-*k* most relevant security
knowledge chunks for a given vulnerability type string.

Key behaviours:
  * Cosine similarity via ``all-MiniLM-L6-v2`` (runs locally, no paid APIs).
  * Similarity threshold (default 0.7, configurable via ``RAG_SIMILARITY_THRESHOLD``
    env var): if the best match scores below threshold, returns an empty list
    with ``no_match=True`` so callers can adapt their behaviour.
  * Returns structured dicts per chunk with ``text``, ``source``, ``cve_id``,
    ``severity``, ``score`` — ready for downstream LLM prompt construction.

Usage::

    from src.retriever import SecurityRetriever, format_rag_context

    retriever = SecurityRetriever()
    result = retriever.query("SQL injection in Python")
    for chunk in result["chunks"]:
        print(chunk["cve_id"], chunk["score"])

No paid services are used. Everything runs locally.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
"""Sentence-transformer model for query embedding (must match ingest model)."""

COLLECTION_NAME: str = "security_kb"
"""ChromaDB collection name (must match ``src.ingest.COLLECTION_NAME``)."""

DEFAULT_PERSIST_DIR: str = "data/chroma_db"
"""Default ChromaDB storage path."""

DEFAULT_SIMILARITY_THRESHOLD: float = 0.7
"""Minimum cosine similarity score for a chunk to be considered relevant."""

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class RetrievedChunk:
    """A single retrieved knowledge-base chunk with metadata and relevance score.

    Attributes:
        text: The chunk content.
        score: Cosine similarity score in ``[0, 1]``.
        source: Origin of the data (``"OWASP"`` or ``"NVD"``).
        cve_id: CVE identifier if applicable, otherwise empty string.
        severity: CVSS severity level (``CRITICAL``, ``HIGH``, ``MEDIUM``, ``LOW``).
        category: Vulnerability category label.
    """

    text: str
    score: float
    source: str
    cve_id: str | None = None
    severity: str = "UNKNOWN"
    category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize this chunk to the canonical downstream dict format.

        Returns:
            Dict with keys: ``text``, ``source``, ``cve_id``, ``severity``, ``score``.
        """
        return {
            "text": self.text,
            "source": self.source,
            "cve_id": self.cve_id or "",
            "severity": self.severity,
            "score": round(self.score, 4),
        }


# ---------------------------------------------------------------------------
# Query result
# ---------------------------------------------------------------------------


@dataclass
class QueryResult:
    """Container for a retrieval query result.

    Attributes:
        chunks: List of :class:`RetrievedChunk` objects that passed the
            similarity threshold, sorted by descending score.
        no_match: ``True`` when the top match scored below the threshold,
            meaning the knowledge base has no confident answer for this query.
    """

    chunks: list[RetrievedChunk] = field(default_factory=list)
    no_match: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for JSON-friendly downstream use.

        Returns:
            ``{"chunks": [...], "no_match": bool}``
        """
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "no_match": self.no_match,
        }


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------


class SecurityRetriever:
    """Semantic retriever backed by a local ChromaDB + MiniLM-L6-v2.

    The retriever connects to an existing ChromaDB persistent collection on
    init. If the collection is empty (ingestion hasn't been run), queries
    return an empty result with ``no_match=True`` rather than raising.

    Args:
        persist_dir: Path to ChromaDB storage. Falls back to
            ``CHROMA_PERSIST_DIR`` env var → ``"data/chroma_db"``.
        similarity_threshold: Minimum cosine similarity. Falls back to
            ``RAG_SIMILARITY_THRESHOLD`` env var → ``0.7``.
    """

    def __init__(
        self,
        persist_dir: str | None = None,
        similarity_threshold: float | None = None,
    ) -> None:
        self.persist_dir: str = (
            persist_dir
            or os.getenv("CHROMA_PERSIST_DIR", DEFAULT_PERSIST_DIR)
        )
        self.threshold: float = float(
            similarity_threshold
            if similarity_threshold is not None
            else os.getenv("RAG_SIMILARITY_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD))
        )

        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
        )
        client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "SecurityRetriever initialized (persist=%s, threshold=%.2f, docs=%d).",
            self.persist_dir,
            self.threshold,
            self.collection.count(),
        )

    # ----- public API -----

    def query(
        self,
        vulnerability_type: str,
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        """Query the knowledge base for chunks relevant to *vulnerability_type*.

        This method preserves backward compatibility with the existing
        ``pipeline.py`` which expects ``List[RetrievedChunk]`` directly.

        Args:
            vulnerability_type: Free-text vulnerability description
                (e.g. ``"SQL injection vulnerability in Python"``).
            top_k: Maximum number of chunks to return.

        Returns:
            List of :class:`RetrievedChunk` objects sorted by descending
            similarity score. Empty list if no chunk passes the threshold
            or the collection is empty.
        """
        result = self.query_with_metadata(vulnerability_type, top_k=top_k)
        return result.chunks

    def query_with_metadata(
        self,
        vulnerability_type: str,
        top_k: int = 3,
    ) -> QueryResult:
        """Query the knowledge base and return a :class:`QueryResult` with ``no_match`` flag.

        This is the full-featured query method. Use this when you need to
        know whether the knowledge base had *any* relevant match.

        Args:
            vulnerability_type: Free-text vulnerability description.
            top_k: Maximum number of chunks to return.

        Returns:
            :class:`QueryResult` with ``chunks`` and ``no_match`` flag.
        """
        if self.collection.count() == 0:
            logger.warning("ChromaDB collection is empty — returning no_match.")
            return QueryResult(chunks=[], no_match=True)

        results = self.collection.query(
            query_texts=[vulnerability_type],
            n_results=min(top_k, self.collection.count()),
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        chunks: list[RetrievedChunk] = []
        for doc, meta, dist in zip(docs, metas, distances):
            # ChromaDB cosine distance: similarity = 1 - distance
            score = 1.0 - float(dist) if dist is not None else 0.0
            if score < self.threshold:
                continue

            meta = meta or {}
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    score=score,
                    source=meta.get("source", "unknown"),
                    cve_id=meta.get("cve_id") or None,
                    severity=meta.get("severity", "UNKNOWN"),
                    category=meta.get("category") or None,
                )
            )

        chunks.sort(key=lambda c: c.score, reverse=True)

        # Determine no_match: if zero chunks passed threshold, flag it
        no_match = len(chunks) == 0
        if no_match:
            logger.info(
                "No match above threshold %.2f for query: '%s'",
                self.threshold,
                vulnerability_type[:80],
            )

        return QueryResult(chunks=chunks, no_match=no_match)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_rag_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a text block suitable for LLM prompts.

    Each chunk is rendered as::

        [CVE-ID or Category] (score: 0.xx, severity: HIGH)
        <chunk text>

    If *chunks* is empty, returns the ``NO_CVE_CONTEXT`` fallback string
    from ``src.prompts``.

    Args:
        chunks: List of :class:`RetrievedChunk` objects.

    Returns:
        Formatted multi-line string for injection into LLM prompts.
    """
    if not chunks:
        from src.prompts import NO_CVE_CONTEXT

        return NO_CVE_CONTEXT

    lines: list[str] = []
    for c in chunks:
        ref = c.cve_id or c.category or c.source
        severity = c.severity or "UNKNOWN"
        lines.append(
            f"[{ref}] (score: {c.score:.2f}, severity: {severity})\n{c.text}"
        )
    return "\n\n".join(lines)


def format_chunks_as_dicts(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    """Convert a list of chunks to the canonical dict format for API responses.

    Returns:
        List of dicts, each with keys: ``text``, ``source``, ``cve_id``,
        ``severity``, ``score``.
    """
    return [c.to_dict() for c in chunks]


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    query_text = " ".join(sys.argv[1:]) or "SQL injection vulnerability in Python"
    print(f"\nQuerying: '{query_text}'\n")

    retriever = SecurityRetriever()
    result = retriever.query_with_metadata(query_text)

    if result.no_match:
        print("❌ No match above similarity threshold.")
    else:
        for i, chunk in enumerate(result.chunks, 1):
            d = chunk.to_dict()
            print(f"--- Chunk {i} ---")
            print(f"  Score:    {d['score']}")
            print(f"  Source:   {d['source']}")
            print(f"  CVE ID:   {d['cve_id']}")
            print(f"  Severity: {d['severity']}")
            print(f"  Text:     {d['text'][:200]}…")
            print()

    print(f"\nFormatted RAG context:\n{format_rag_context(result.chunks)}")
