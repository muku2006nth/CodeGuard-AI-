export interface Finding {
  id: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  line_number: number;
  description: string;
  remediation: string;
  code_snippet: string;
  source: string;
  rule_id?: string | null;
  what_is_wrong?: string;
  why_dangerous?: string;
  real_world_impact?: string;
  secure_example?: string;
}

export interface MLScore {
  risk_probability: number;
  suspicious_score: number;
  is_suspicious: boolean;
  provider: string;
}


export interface AnalyzeResponse {
  report_id: string;
  risk_score: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  findings: Finding[];
  summary: string;
  recommendations: string[];
  ml_score: MLScore;
  language: string;
  latency_seconds: number;

}

export interface ReportSummary {
  report_id: string;
  risk_score: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  finding_count: number;
  language: string;
  created_at: string;
}

export interface DashboardResponse {
  total_scans: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  average_risk_score: number;
  recent_scans: ReportSummary[];
  trend_data: { date: string; scans: number }[];
  severity_distribution: { name: string; value: number }[];
}

export interface StatisticsResponse {
  vulnerability_counts: Record<string, number>;
  risk_trends: { month: string; score: number }[];
  languages: Record<string, number>;
  top_categories: { category: string; count: number }[];
}

export interface SystemStatusResponse {
  backend: string;
  codebert: string;
  semgrep: string;

  database: string;
}

export interface HistoryResponse {
  scans: ReportSummary[];
}
