import { supabase } from "@/lib/supabase";
import type { AnalyzeResponse, ReportSummary } from "../types/analysis";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers = new Headers(init?.headers);
  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
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

  const { data: { session } } = await supabase.auth.getSession();
  const headers = new Headers();
  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  const res = await fetch(url.toString(), { method: "POST", body: form, headers });
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
  // Return the URL. However, the browser opening this directly won't have the Bearer token.
  // The user would need to use a fetch with blob to download protected files.
  // For now we will append the session token to the query string if possible, or we just leave it and expect an update to the download method.
  return `${API_BASE}/report/${reportId}/download?format=${format}`;
}

export async function healthCheck(): Promise<{ status: string; ml_provider: string }> {
  return request("/health");
}

export async function getDashboardData(): Promise<import("../types/analysis").DashboardResponse> {
  return request("/dashboard");
}

export async function getStatistics(): Promise<import("../types/analysis").StatisticsResponse> {
  return request("/statistics");
}

export async function getSystemStatus(): Promise<import("../types/analysis").SystemStatusResponse> {
  return request("/system-status");
}

export async function getHistory(): Promise<import("../types/analysis").HistoryResponse> {
  return request("/history");
}
