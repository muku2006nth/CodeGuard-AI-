import type { AnalyzeResponse, ReportSummary } from "../types/analysis";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function analyzeCode(
  code: string,
  language?: string
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language }),
  });
}

export async function uploadFile(file: File, language?: string): Promise<{ report_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const url = new URL(`${API_BASE}/upload`, window.location.origin);
  if (language) url.searchParams.set("language", language);
  const res = await fetch(url.toString(), { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function getReport(reportId: string): Promise<{ report_id: string; payload: AnalyzeResponse & Record<string, unknown> }> {
  return request(`/report/${reportId}`);
}

export async function listReports(): Promise<ReportSummary[]> {
  return request<ReportSummary[]>("/reports");
}

export function downloadReportUrl(reportId: string, format: "json" | "markdown" | "pdf"): string {
  return `${API_BASE}/report/${reportId}/download?format=${format}`;
}

export async function healthCheck(): Promise<{ status: string; ml_provider: string }> {
  return request("/health");
}
