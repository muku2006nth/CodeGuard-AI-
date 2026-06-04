import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { healthCheck, listReports } from "../services/api";
import type { ReportSummary } from "../types/analysis";

export default function Dashboard() {
  const [health, setHealth] = useState<{ status: string; ml_provider: string } | null>(null);
  const [reports, setReports] = useState<ReportSummary[]>([]);

  useEffect(() => {
    healthCheck().then(setHealth).catch(() => setHealth(null));
    listReports().then(setReports).catch(() => setReports([]));
  }, []);

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold mb-2">Security Review Dashboard</h1>
        <p className="text-slate-400 max-w-2xl">
          Analyze source code for vulnerability categories, risk scores, and remediation guidance.
          Comparable to lightweight SonarQube / Snyk for student projects.
        </p>
      </section>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-panel rounded-xl p-5 border border-slate-700">
          <h3 className="text-slate-400 text-sm">API Status</h3>
          <p className="text-2xl font-semibold mt-1">
            {health?.status === "ok" ? "Online" : "Offline"}
          </p>
          <p className="text-xs text-slate-500 mt-1">ML: {health?.ml_provider ?? "—"}</p>
        </div>
        <div className="bg-panel rounded-xl p-5 border border-slate-700">
          <h3 className="text-slate-400 text-sm">Reports</h3>
          <p className="text-2xl font-semibold mt-1">{reports.length}</p>
        </div>
        <Link
          to="/analyze"
          className="bg-accent/20 border border-accent rounded-xl p-5 flex items-center justify-center text-accent font-semibold hover:bg-accent/30"
        >
          Start New Analysis →
        </Link>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">Recent Reports</h2>
        {reports.length === 0 ? (
          <p className="text-slate-500">No reports yet. Run an analysis to get started.</p>
        ) : (
          <ul className="space-y-2">
            {reports.slice(0, 5).map((r) => (
              <li key={r.report_id}>
                <Link
                  to={`/results/${r.report_id}`}
                  className="block bg-panel border border-slate-700 rounded-lg px-4 py-3 hover:border-accent"
                >
                  <span className="font-mono text-xs text-slate-500">{r.report_id}</span>
                  <span className="ml-4">Score {r.risk_score}</span>
                  <span className="ml-4 text-warn">{r.severity}</span>
                  <span className="ml-4 text-slate-500">{r.finding_count} findings</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
