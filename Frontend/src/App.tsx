import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { AppLayout } from "@/components/layout/app-layout"
import { DashboardPage } from "@/features/dashboard/dashboard-page"
import { AnalysisPage } from "@/features/analysis/analysis-page"
import { ReportsPage } from "@/features/reports/reports-page"
import { VulnerabilitiesPage } from "@/features/vulnerabilities/vulnerabilities-page"
import { HistoryPage } from "@/features/history/history-page"
import { SettingsPage } from "@/features/settings/settings-page"

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="analyze" element={<AnalysisPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="vulnerabilities" element={<VulnerabilitiesPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </Router>
  )
}
