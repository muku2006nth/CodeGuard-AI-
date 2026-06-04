import Editor from "@monaco-editor/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeCode, uploadFile } from "../services/api";

const DEFAULT_CODE = `import os

def run_cmd(user_input):
    # Vulnerable: command injection
    os.system(user_input)

password = "hardcoded_secret"
`;

export default function AnalyzePage() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const runAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCode(code, language);
      navigate(`/results/${result.report_id}`, { state: { result } });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const onFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const { report_id } = await uploadFile(file, language);
      navigate(`/results/${report_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Code Analysis</h1>
      <div className="flex flex-wrap gap-3 items-center">
        <label className="text-sm text-slate-400">
          Language
          <select
            className="ml-2 bg-panel border border-slate-600 rounded px-2 py-1"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="go">Go</option>
            <option value="c">C</option>
          </select>
        </label>
        <label className="cursor-pointer bg-panel border border-slate-600 px-3 py-1 rounded text-sm hover:border-accent">
          Upload File
          <input type="file" className="hidden" accept=".py,.js,.ts,.java,.go,.c,.cpp,.txt" onChange={onFileUpload} />
        </label>
        <button
          onClick={runAnalyze}
          disabled={loading}
          className="bg-accent text-surface font-semibold px-4 py-1.5 rounded disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>
      {error && <p className="text-danger text-sm">{error}</p>}
      <div className="border border-slate-700 rounded-lg overflow-hidden h-[480px]">
        <Editor
          height="100%"
          language={language}
          theme="vs-dark"
          value={code}
          onChange={(v) => setCode(v || "")}
          options={{ minimap: { enabled: false }, fontSize: 14 }}
        />
      </div>
    </div>
  );
}
