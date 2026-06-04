"""
Load, chunk, and embed OWASP + CVE documents into ChromaDB (Day 3).
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import chromadb
import requests
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []
    stride = max(1, chunk_size - overlap)
    chunks = []
    for i in range(0, len(words), stride):
        piece = " ".join(words[i : i + chunk_size])
        if piece.strip():
            chunks.append(piece)
        if i + chunk_size >= len(words):
            break
    return chunks


def load_owasp_docs(owasp_dir: Path) -> list[dict]:
    docs = []
    if not owasp_dir.exists():
        return docs
    for path in owasp_dir.glob("**/*"):
        if path.suffix.lower() not in {".txt", ".md", ".html"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate(chunk_text(text)):
            docs.append(
                {
                    "id": f"owasp-{path.stem}-{i}",
                    "text": chunk,
                    "metadata": {
                        "source": "OWASP",
                        "category": path.stem,
                        "severity": "HIGH",
                    },
                }
            )
    return docs


def fetch_cve_summaries(keyword: str = "injection", max_results: int = 100) -> list[dict]:
    params = {"keywordSearch": keyword, "resultsPerPage": min(max_results, 2000)}
    resp = requests.get(NVD_API, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    docs = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "unknown")
        descriptions = cve.get("descriptions", [])
        desc = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")
        if not desc:
            continue
        for i, chunk in enumerate(chunk_text(desc)):
            docs.append(
                {
                    "id": f"{cve_id}-{i}",
                    "text": chunk,
                    "metadata": {
                        "source": "NVD",
                        "cve_id": cve_id,
                        "severity": "HIGH",
                        "category": keyword,
                    },
                }
            )
    return docs


def ingest_to_chroma(
    documents: list[dict],
    persist_dir: str = "data/chroma_db",
    collection_name: str = "security_kb",
):
    os.makedirs(persist_dir, exist_ok=True)
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [d["id"] for d in documents]
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    # Chroma has batch limits; ingest in batches
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=texts[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Ingest OWASP + CVE into ChromaDB")
    parser.add_argument("--owasp-dir", default="data/owasp")
    parser.add_argument("--cve-keyword", default="SQL injection")
    parser.add_argument("--cve-limit", type=int, default=100)
    parser.add_argument("--persist-dir", default="data/chroma_db")
    parser.add_argument("--seed-only", action="store_true", help="Use bundled seed docs only")
    args = parser.parse_args()

    documents = load_owasp_docs(Path(args.owasp_dir))

    if args.seed_only or not documents:
        seed_path = Path("data/cve/seed_docs.json")
        if seed_path.exists():
            with open(seed_path, encoding="utf-8") as f:
                documents.extend(json.load(f))

    if not args.seed_only:
        try:
            documents.extend(fetch_cve_summaries(args.cve_keyword, args.cve_limit))
        except requests.RequestException as e:
            print(f"NVD fetch failed ({e}); using seed/OWASP only.")

    if not documents:
        raise SystemExit("No documents to ingest. Add data/owasp/*.md or data/cve/seed_docs.json")

    count = ingest_to_chroma(documents, persist_dir=args.persist_dir)
    print(f"Ingested {count} chunks into {args.persist_dir}")


if __name__ == "__main__":
    main()
