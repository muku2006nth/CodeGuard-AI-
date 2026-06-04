import { ReportSummary, AnalyzeResponse, Finding } from "@/types"

export const MOCK_REPORTS: ReportSummary[] = [
  { report_id: "rep-1a2b3c", risk_score: 92, severity: "CRITICAL", finding_count: 4, language: "python", created_at: "2026-05-30T10:23:11Z" },
  { report_id: "rep-4d5e6f", risk_score: 75, severity: "HIGH", finding_count: 2, language: "javascript", created_at: "2026-05-31T14:45:22Z" },
  { report_id: "rep-7g8h9i", risk_score: 45, severity: "MEDIUM", finding_count: 1, language: "go", created_at: "2026-06-01T09:12:05Z" },
  { report_id: "rep-0j1k2l", risk_score: 12, severity: "LOW", finding_count: 0, language: "typescript", created_at: "2026-06-01T11:05:44Z" },
  { report_id: "rep-3m4n5o", risk_score: 88, severity: "CRITICAL", finding_count: 5, language: "java", created_at: "2026-06-01T15:30:10Z" },
]

export const MOCK_FINDINGS: Finding[] = [
  {
    id: "fnd-1",
    category: "SQL_INJECTION",
    severity: "CRITICAL",
    confidence: 0.95,
    line_number: 42,
    description: "Unsanitized user input in SQL query.",
    remediation: "Use parameterized queries or ORM.",
    code_snippet: "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')",
    source: "semgrep",
    rule_id: "python.lang.security.audit.sqli.sqli",
    what_is_wrong: "String interpolation directly into SQL query.",
    why_dangerous: "Allows attackers to modify the SQL logic.",
    real_world_impact: "Full database dump, modification or deletion.",
    secure_example: "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
  },
  {
    id: "fnd-2",
    category: "HARDCODED_SECRET",
    severity: "HIGH",
    confidence: 0.88,
    line_number: 12,
    description: "Hardcoded AWS Access Key.",
    remediation: "Move to environment variables or secret manager.",
    code_snippet: "AWS_SECRET = 'AKIAIOSFODNN7EXAMPLE'",
    source: "regex",
    what_is_wrong: "Secret key stored in plaintext in source code.",
    why_dangerous: "Source code might be leaked or exposed.",
    real_world_impact: "Unauthorized access to cloud infrastructure.",
    secure_example: "AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')"
  },
  {
    id: "fnd-3",
    category: "CODE_INJECTION",
    severity: "CRITICAL",
    confidence: 0.99,
    line_number: 105,
    description: "Use of eval() with user input.",
    remediation: "Avoid eval(). Use ast.literal_eval() or specific parsing logic.",
    code_snippet: "result = eval(user_provided_formula)",
    source: "bandit",
    rule_id: "B307",
    what_is_wrong: "eval() executes arbitrary code.",
    why_dangerous: "If user controls the input, they control the server.",
    real_world_impact: "Remote Code Execution (RCE).",
    secure_example: "result = ast.literal_eval(user_provided_formula)"
  },
  {
    id: "fnd-4",
    category: "INSECURE_RANDOMNESS",
    severity: "MEDIUM",
    confidence: 0.82,
    line_number: 56,
    description: "Use of pseudo-random generator for cryptographic purpose.",
    remediation: "Use secrets module instead of random.",
    code_snippet: "token = random.hex(16)",
    source: "semgrep",
    rule_id: "python.lang.security.audit.insecure-randomness",
    what_is_wrong: "random module is predictable.",
    why_dangerous: "Attackers can predict tokens or session IDs.",
    real_world_impact: "Session hijacking, password reset token prediction.",
    secure_example: "token = secrets.token_hex(16)"
  }
]

export const MOCK_ANALYSIS_RESPONSE: AnalyzeResponse = {
  report_id: "rep-mocked-123",
  risk_score: 92,
  severity: "CRITICAL",
  findings: MOCK_FINDINGS,
  summary: "Analysis complete: risk score 92/100 (CRITICAL). Found 4 issue(s) across 4 categories. ML suspicious probability: 85%.",
  recommendations: [
    "[CRITICAL] SQL_INJECTION: Use parameterized queries or ORM.",
    "[CRITICAL] CODE_INJECTION: Avoid eval(). Use ast.literal_eval() or specific parsing logic.",
    "[HIGH] HARDCODED_SECRET: Move to environment variables or secret manager.",
    "[MEDIUM] INSECURE_RANDOMNESS: Use secrets module instead of random."
  ],
  ml_score: {
    risk_probability: 0.85,
    suspicious_score: 0.85,
    is_suspicious: true,
    provider: "mock"
  },
  language: "python",
  latency_seconds: 1.2
}
