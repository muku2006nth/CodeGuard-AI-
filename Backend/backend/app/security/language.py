"""Language detection for static analysis routing."""

from __future__ import annotations

import re

LANGUAGE_PATTERNS: list[tuple[str, list[str]]] = [
    ("python", [r"\bdef\s+\w+", r"\bimport\s+\w+", r"\bfrom\s+\w+\s+import"]),
    ("javascript", [r"\bfunction\s+", r"\bconst\s+", r"=>", r"document\."]),
    ("typescript", [r"\binterface\s+", r":\s*\w+\s*;"]),
    ("java", [r"\bpublic\s+class\b", r"\bvoid\s+main\b"]),
    ("go", [r"\bpackage\s+main\b", r"\bfunc\s+main\b"]),
    ("php", [r"<\?php"]),
    ("ruby", [r"\bdef\s+\w+", r"\bend\b"]),
    ("c", [r"#include\s*<", r"\bprintf\s*\("]),
    ("cpp", [r"\bstd::", r"#include\s*<"]),
]


def detect_language(code: str, hint: str | None = None, filename: str | None = None) -> str:
    if hint:
        h = hint.strip().lower()
        return {"py": "python", "js": "javascript", "ts": "typescript"}.get(h, h)

    if filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        ext_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "java": "java",
            "go": "go",
            "php": "php",
            "rb": "ruby",
            "c": "c",
            "cpp": "cpp",
            "cs": "csharp",
        }
        if ext in ext_map:
            return ext_map[ext]

    scores: dict[str, int] = {}
    for lang, patterns in LANGUAGE_PATTERNS:
        scores[lang] = sum(1 for p in patterns if re.search(p, code))
    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]
    return "unknown"


def file_extension(language: str) -> str:
    return {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "go": ".go",
        "php": ".php",
        "ruby": ".rb",
        "c": ".c",
        "cpp": ".cpp",
        "csharp": ".cs",
    }.get(language, ".txt")
