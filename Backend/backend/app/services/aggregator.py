"""Finding aggregator — deduplicate and merge scanner results."""

from __future__ import annotations

from app.models.finding import VulnerabilityFinding


class FindingAggregator:
    def merge(self, *finding_lists: list[VulnerabilityFinding]) -> list[VulnerabilityFinding]:
        merged: list[VulnerabilityFinding] = []
        seen: dict[tuple[str, int, str], VulnerabilityFinding] = {}

        for findings in finding_lists:
            for f in findings:
                key = (f.category.value, f.line_number, f.code_snippet[:80].lower())
                existing = seen.get(key)
                if existing is None or f.confidence > existing.confidence:
                    seen[key] = f

        merged.extend(seen.values())
        merged.sort(key=lambda x: (x.line_number, -x.confidence))
        return merged
