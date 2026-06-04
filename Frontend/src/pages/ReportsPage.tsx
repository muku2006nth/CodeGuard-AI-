import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listReports } from "../services/api";
import type { ReportSummary } from "../types/analysis";

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);

  useEffect(() => {
    listReports().then(setReports).catch(() => setReports([]));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Reports</h1>
      {reports.length === 0 ? (
        <p className="text-slate-500">No saved reports.</p>
      ) : (
        <table className="w-full text-sm border border-slate-700 rounded-lg overflow-hidden">
          <thead className="bg-panel text-slate-400">
            <tr>
              <th className="text-left px-4 py-2">ID</th>
              <th className="text-left px-4 py-2">Score</th>
              <th className="text-left px-4 py-2">Severity</th>
              <th className="text-left px-4 py-2">Findings</th>
              <th className="text-left px-4 py-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.report_id} className="border-t border-slate-700">
                <td className="px-4 py-2">
                  <Link to={`/results/${r.report_id}`} className="text-accent font-mono text-xs">
                    {r.report_id.slice(0, 8)}…
                  </Link>
                </td>
                <td className="px-4 py-2">{r.risk_score}</td>
                <td className="px-4 py-2">{r.severity}</td>
                <td className="px-4 py-2">{r.finding_count}</td>
                <td className="px-4 py-2 text-slate-500">{r.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
