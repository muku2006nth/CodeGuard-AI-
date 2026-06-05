import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import FindingsTable from "../components/FindingsTable";
import RiskGauge from "../components/RiskGauge";
import { downloadReportUrl, getReport } from "../services/api";
import type { AnalyzeResponse } from "../types/analysis";

export default function ResultsPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const location = useLocation();
  const [result, setResult] = useState<AnalyzeResponse | null>(
    (location.state as { result?: AnalyzeResponse })?.result ?? null
  );
  const [showJson, setShowJson] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId || result) return;
    getReport(reportId).then((r) => setResult(r.payload as AnalyzeResponse)).catch(console.error);
  }, [reportId, result]);

  if (!result) {
    return <p className="text-slate-400">Loading report…</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold">Analysis Results</h1>
          <p className="text-slate-500 font-mono text-sm">{result.report_id}</p>
        </div>
        <div className="flex gap-2">
          {(["json", "markdown", "pdf"] as const).map((fmt) => (
            <a
              key={fmt}
              href={downloadReportUrl(result.report_id, fmt)}
              className="text-sm border border-slate-600 px-3 py-1 rounded hover:border-accent"
              download
            >
              {fmt.toUpperCase()}
            </a>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-[200px_1fr] gap-6 bg-panel rounded-xl border border-slate-700 p-6">
        <RiskGauge score={result.risk_score} severity={result.severity} />
        <div>
          <p className="text-slate-300">{result.summary}</p>
          <p className="text-sm text-slate-500 mt-2">
            Language: {result.language} · ML provider: {result.ml_score.provider} · Suspicious:{" "}
            {(result.ml_score.risk_probability * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-2">Recommendations</h2>
        <ul className="list-disc list-inside text-slate-300 space-y-1">
          {result.recommendations.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Findings</h2>
        <FindingsTable findings={result.findings} />
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">Detailed Explanations</h2>
        <div className="space-y-3">
          {result.findings.map((f) => (
            <div key={f.id} className="border border-slate-700 rounded-lg p-4 bg-panel/50">
              <button
                className="w-full text-left font-semibold flex justify-between"
                onClick={() => setExpanded(expanded === f.id ? null : f.id)}
              >
                <span>
                  {f.category} — Line {f.line_number}
                </span>
                <span className="text-slate-500">{expanded === f.id ? "−" : "+"}</span>
              </button>
              {expanded === f.id && (
                <div className="mt-3 text-sm text-slate-300 space-y-2">
                  <p><strong>What:</strong> {f.what_is_wrong || f.description}</p>
                  <p><strong>Why:</strong> {f.why_dangerous}</p>
                  <p><strong>Impact:</strong> {f.real_world_impact}</p>
                  <p><strong>Fix:</strong> {f.remediation}</p>
                  <pre className="bg-surface p-2 rounded text-xs overflow-x-auto">{f.secure_example}</pre>
                  <pre className="bg-surface p-2 rounded text-xs text-danger/80">{f.code_snippet}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* AI-Generated Fix */}
      {result.ai_explanation && (
        <section>
          <h2 className="text-lg font-semibold mb-2">AI-Generated Fix</h2>
          <div className="border border-slate-700 rounded-lg p-4 bg-panel/50 space-y-3">
            <p className="text-slate-300 text-sm whitespace-pre-wrap">{result.ai_explanation}</p>
            {result.fixed_code && (
              <pre className="bg-surface p-3 rounded text-xs overflow-x-auto border border-slate-600">
                <code>{result.fixed_code}</code>
              </pre>
            )}
          </div>
        </section>
      )}

      {/* RAG References */}
      {result.cve_refs && result.cve_refs.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-2">RAG References</h2>
          <div className="flex flex-wrap gap-2">
            {result.cve_refs.map((ref, i) => (
              <span
                key={i}
                className="inline-block text-sm border border-blue-500/30 bg-blue-500/10 text-blue-400 px-3 py-1 rounded"
              >
                {ref}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* RAG Chunk Details */}
      {result.rag_chunks && result.rag_chunks.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-2">RAG Knowledge Chunks</h2>
          <div className="space-y-3">
            {result.rag_chunks.map((chunk, i) => (
              <div key={i} className="border border-slate-700 rounded-lg p-4 bg-panel/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs border border-slate-600 px-2 py-0.5 rounded">{chunk.source}</span>
                  {chunk.cve_id && (
                    <span className="text-xs border border-blue-500/30 bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">{chunk.cve_id}</span>
                  )}
                  <span className="text-xs border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded font-mono">
                    {(chunk.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-slate-300">
                  {chunk.text.length > 300 ? chunk.text.slice(0, 300) + "..." : chunk.text}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <button
          className="text-sm text-accent"
          onClick={() => setShowJson(!showJson)}
        >
          {showJson ? "Hide" : "Show"} JSON
        </button>
        {showJson && (
          <pre className="mt-2 bg-surface p-4 rounded text-xs overflow-auto max-h-96 border border-slate-700">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </section>

      <Link to="/analyze" className="text-accent text-sm">← New analysis</Link>
    </div>
  );
}
