"""Report export — JSON, Markdown, PDF."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_json(report: dict[str, Any]) -> bytes:
    return json.dumps(report, indent=2).encode("utf-8")


def export_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Security Analysis Report",
        "",
        f"**Report ID:** {report.get('report_id')}",
        f"**Risk Score:** {report.get('risk_score')}/100",
        f"**Severity:** {report.get('severity')}",
        f"**Language:** {report.get('language')}",
        "",
        "## Summary",
        report.get("summary", ""),
        "",
        "## ML Score",
        f"- Risk probability: {report.get('ml_score', {}).get('risk_probability')}",
        f"- Suspicious: {report.get('ml_score', {}).get('is_suspicious')}",
        "",
        "## Recommendations",
    ]
    for rec in report.get("recommendations", []):
        lines.append(f"- {rec}")
    lines.extend(["", "## Findings", ""])
    for i, f in enumerate(report.get("findings", []), 1):
        lines.extend(
            [
                f"### {i}. {f.get('category')} (Line {f.get('line_number')})",
                f"- **Severity:** {f.get('severity')}",
                f"- **Confidence:** {f.get('confidence')}",
                f"- **Description:** {f.get('description')}",
                f"- **Remediation:** {f.get('remediation')}",
                "",
                "```",
                f.get("code_snippet", ""),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def export_pdf(report: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Security Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Report ID: {report.get('report_id')}", styles["Normal"]))
    story.append(Paragraph(f"Risk Score: {report.get('risk_score')}/100", styles["Normal"]))
    story.append(Paragraph(f"Severity: {report.get('severity')}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(report.get("summary", ""), styles["Normal"]))
    story.append(Spacer(1, 12))

    findings = report.get("findings", [])[:25]
    if findings:
        data = [["Category", "Line", "Severity", "Confidence"]]
        for f in findings:
            data.append(
                [
                    str(f.get("category", ""))[:30],
                    str(f.get("line_number", "")),
                    str(f.get("severity", "")),
                    f"{float(f.get('confidence', 0)):.0%}",
                ]
            )
        table = Table(data, colWidths=[180, 50, 80, 80])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]
            )
        )
        story.append(Paragraph("Findings", styles["Heading2"]))
        story.append(table)

    doc.build(story)
    return buffer.getvalue()
