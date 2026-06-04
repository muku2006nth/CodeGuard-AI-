"""Semantic search over OWASP + CVE knowledge base (Day 3)."""

from __future__ import annotations

import os
from dataclasses import dataclass

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "security_kb"


@dataclass
class RetrievedChunk:
    text: str
    score: float
    source: str
    cve_id: str | None
    category: str | None


class SecurityRetriever:
    def __init__(
        self,
        persist_dir: str | None = None,
        similarity_threshold: float | None = None,
    ):
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
        self.threshold = float(
            similarity_threshold or os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7")
        )
        embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )

    def query(self, text: str, top_k: int = 3) -> list[RetrievedChunk]:
        if self.collection.count() == 0:
            return []

        results = self.collection.query(query_texts=[text], n_results=top_k)
        chunks: list[RetrievedChunk] = []

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            # Chroma cosine distance: lower is better; convert to similarity
            score = 1.0 - float(dist) if dist is not None else 0.0
            if score < self.threshold:
                continue
            meta = meta or {}
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    score=score,
                    source=meta.get("source", "unknown"),
                    cve_id=meta.get("cve_id"),
                    category=meta.get("category"),
                )
            )

        return sorted(chunks, key=lambda c: c.score, reverse=True)


def format_rag_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        from src.prompts import NO_CVE_CONTEXT

        return NO_CVE_CONTEXT

    lines = []
    for c in chunks:
        ref = c.cve_id or c.category or c.source
        lines.append(f"[{ref}] (score: {c.score:.2f})\n{c.text}")
    return "\n\n".join(lines)
