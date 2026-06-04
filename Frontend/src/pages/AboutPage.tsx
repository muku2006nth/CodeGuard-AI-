export default function AboutPage() {
  return (
    <div className="prose prose-invert max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">About</h1>
      <p className="text-slate-300 mb-4">
        AI Security Code Review Platform is a student-project AppSec tool combining static analysis
        with ML-assisted risk scoring.
      </p>
      <h2 className="text-lg font-semibold mt-6 mb-2">Architecture</h2>
      <ol className="list-decimal list-inside text-slate-400 space-y-1">
        <li>Regex engine — fast pattern detection</li>
        <li>Semgrep — multi-language rules (optional)</li>
        <li>Bandit — Python security linter (optional)</li>
        <li>Mock ML service — heuristic risk until CodeBERT is trained</li>
        <li>Risk engine — weighted score 0–100</li>
        <li>Explainer — remediation and secure examples</li>
      </ol>
      <h2 className="text-lg font-semibold mt-6 mb-2">Future CodeBERT</h2>
      <p className="text-slate-400">
        Train via <code className="text-accent">colab/train_codebert.ipynb</code>, implement{" "}
        <code className="text-accent">backend/app/ml/codebert_model.py</code>, set{" "}
        <code className="text-accent">ML_PROVIDER=codebert</code>. No frontend changes required.
      </p>
    </div>
  );
}
