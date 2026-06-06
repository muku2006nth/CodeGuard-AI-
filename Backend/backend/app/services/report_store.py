"""Supabase report persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.security.auth import supabase, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, ClientOptions

class ReportStore:
    def __init__(self) -> None:
        pass

    def _get_client(self, token: str | None = None):
        if token and SUPABASE_URL and SUPABASE_KEY:
            return create_client(
                SUPABASE_URL,
                SUPABASE_KEY,
                options=ClientOptions(headers={'Authorization': f'Bearer {token}'})
            )
        return supabase

    def save(self, report: dict[str, Any], user_id: str, token: str | None = None) -> str:
        report_id = report["report_id"]
        report["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save to Supabase
        client = self._get_client(token)
        if client:
            data = {
                "user_id": user_id,
                "report_id": report_id,
                "risk_score": report.get("risk_score", 0),
                "severity": report.get("severity", "LOW"),
                "finding_count": len(report.get("findings", [])),
                "language": report.get("language", "unknown"),
                "created_at": report["created_at"],
                "payload": report
            }
            client.table("reports").insert(data).execute()
        
        return report_id

    def get(self, report_id: str, user_id: str, token: str | None = None) -> dict[str, Any] | None:
        client = self._get_client(token)
        if client:
            response = client.table("reports").select("payload").eq("report_id", report_id).eq("user_id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]["payload"]
        return None

    def list_reports(self, user_id: str, limit: int = 50, token: str | None = None) -> list[dict[str, Any]]:
        client = self._get_client(token)
        if client:
            response = client.table("reports").select("report_id, risk_score, severity, finding_count, language, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            if response.data:
                return response.data
        return []
