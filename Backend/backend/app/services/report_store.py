"""In-memory + filesystem report persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.utils.config import ensure_reports_dir


class ReportStore:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._dir = ensure_reports_dir()

    def save(self, report: dict[str, Any]) -> str:
        report_id = report["report_id"]
        report["created_at"] = datetime.now(timezone.utc).isoformat()
        self._cache[report_id] = report
        path = self._dir / f"{report_id}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report_id

    def get(self, report_id: str) -> dict[str, Any] | None:
        if report_id in self._cache:
            return self._cache[report_id]
        path = self._dir / f"{report_id}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self._cache[report_id] = data
            return data
        return None

    def list_reports(self, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for path in sorted(self._dir.glob("*.json"), reverse=True)[:limit]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append(
                    {
                        "report_id": data["report_id"],
                        "risk_score": data.get("risk_score", 0),
                        "severity": data.get("severity", "LOW"),
                        "finding_count": len(data.get("findings", [])),
                        "language": data.get("language", "unknown"),
                        "created_at": data.get("created_at", ""),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue
        return items
