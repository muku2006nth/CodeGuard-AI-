import type { Finding } from "../types/analysis";

interface Props {
  findings: Finding[];
}

const sevClass: Record<string, string> = {
  LOW: "bg-slate-600",
  MEDIUM: "bg-warn/20 text-warn",
  HIGH: "bg-orange-500/20 text-orange-300",
  CRITICAL: "bg-danger/20 text-danger",
};

export default function FindingsTable({ findings }: Props) {
  if (!findings.length) {
    return <p className="text-slate-400">No findings detected by static scanners.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="w-full text-sm text-left">
        <thead className="bg-panel text-slate-400 uppercase text-xs">
          <tr>
            <th className="px-4 py-3">Line</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Severity</th>
            <th className="px-4 py-3">Confidence</th>
            <th className="px-4 py-3">Source</th>
            <th className="px-4 py-3">Description</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id} className="border-t border-slate-700 hover:bg-slate-800/50">
              <td className="px-4 py-3 font-mono">{f.line_number}</td>
              <td className="px-4 py-3">{f.category}</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-0.5 rounded text-xs ${sevClass[f.severity] || ""}`}>
                  {f.severity}
                </span>
              </td>
              <td className="px-4 py-3">{(f.confidence * 100).toFixed(0)}%</td>
              <td className="px-4 py-3">{f.source}</td>
              <td className="px-4 py-3 max-w-md truncate" title={f.description}>
                {f.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
