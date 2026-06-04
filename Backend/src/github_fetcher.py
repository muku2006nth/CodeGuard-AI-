"""Fetch source files from GitHub URLs (Day 5)."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

import requests

RAW_PATTERN = re.compile(
    r"github\.com/(?P<user>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)"
)
GITHUB_API = "https://api.github.com/repos/{user}/{repo}/contents/{path}"


def parse_github_url(url: str) -> tuple[str, str, str, str] | None:
    url = url.strip().rstrip("/")
    if "raw.githubusercontent.com" in url:
        # https://raw.githubusercontent.com/user/repo/branch/path
        parts = urlparse(url)
        segments = [s for s in parts.path.split("/") if s]
        if len(segments) >= 4:
            user, repo, branch = segments[0], segments[1], segments[2]
            path = "/".join(segments[3:])
            return user, repo, branch, path
        return None

    match = RAW_PATTERN.search(url)
    if match:
        return (
            match.group("user"),
            match.group("repo"),
            match.group("branch"),
            match.group("path"),
        )
    return None


def fetch_github_file(url: str, max_bytes: int = 512_000) -> tuple[str, str]:
    parsed = parse_github_url(url)
    if not parsed:
        raise ValueError("Invalid GitHub file URL. Use blob/... or raw.githubusercontent.com/...")

    user, repo, branch, path = parsed
    raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"

    headers = {"Accept": "application/vnd.github.raw"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get(raw_url, headers=headers, timeout=30)
    if resp.status_code == 404:
        api_url = GITHUB_API.format(user=user, repo=repo, path=path)
        params = {"ref": branch}
        resp = requests.get(api_url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data.get("encoding") == "base64":
            import base64

            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        else:
            raise ValueError("Could not decode GitHub file content")
    else:
        resp.raise_for_status()
        content = resp.text

    if len(content.encode("utf-8")) > max_bytes:
        raise ValueError(f"File exceeds {max_bytes} byte limit")

    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    lang_map = {"py": "python", "js": "javascript", "ts": "typescript", "java": "java", "c": "c", "cpp": "cpp"}
    language = lang_map.get(ext, "text")
    return content, language
