import { useQuery } from "@tanstack/react-query";
import {
  getDashboardData,
  getStatistics,
  getSystemStatus,
  getHistory,
  listReports,
  getReport,
} from "../services/api";

export function useDashboardData() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardData,
  });
}

export function useStatistics() {
  return useQuery({
    queryKey: ["statistics"],
    queryFn: getStatistics,
  });
}

export function useSystemStatus() {
  return useQuery({
    queryKey: ["systemStatus"],
    queryFn: getSystemStatus,
  });
}

export function useHistory() {
  return useQuery({
    queryKey: ["history"],
    queryFn: getHistory,
  });
}

export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: listReports,
  });
}

export function useReport(reportId: string | undefined) {
  return useQuery({
    queryKey: ["report", reportId],
    queryFn: () => getReport(reportId!),
    enabled: !!reportId,
  });
}
