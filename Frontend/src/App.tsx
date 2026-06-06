import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom"
import { AppLayout } from "@/components/layout/app-layout"
import { DashboardPage } from "@/features/dashboard/dashboard-page"
import { AnalysisPage } from "@/features/analysis/analysis-page"
import { ReportsPage } from "@/features/reports/reports-page"
import { VulnerabilitiesPage } from "@/features/vulnerabilities/vulnerabilities-page"
import { HistoryPage } from "@/features/history/history-page"
import { SettingsPage } from "@/features/settings/settings-page"
import { LoginPage } from "@/features/auth/login-page"
import { AuthCallback } from "@/features/auth/auth-callback"
import { Toaster } from "@/components/ui/sonner"
import { AuthProvider, useAuth } from "@/components/auth/auth-provider"

function ProtectedRoute() {
  const { session, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-muted/40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="analyze" element={<AnalysisPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="vulnerabilities" element={<VulnerabilitiesPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>
        </Routes>
        <Toaster />
      </Router>
    </AuthProvider>
  )
}
