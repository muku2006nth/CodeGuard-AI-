import { Activity, ShieldAlert, FileText, CheckCircle2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MOCK_REPORTS } from "@/data/mock"
import { SeverityBadge } from "@/components/shared/severity-badge"

export function DashboardPage() {
  return (
    <div className="flex flex-col gap-8 pb-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Overview of your security posture across all projects.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Scans</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,248</div>
            <p className="text-xs text-muted-foreground mt-1">+12% from last month</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Risk Score</CardTitle>
            <ShieldAlert className="h-4 w-4 text-severity-medium" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42.5</div>
            <p className="text-xs text-muted-foreground mt-1">-5.2 from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Critical Findings</CardTitle>
            <ShieldAlert className="h-4 w-4 text-severity-critical" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">14</div>
            <p className="text-xs text-muted-foreground mt-1">Requires immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Engines</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-severity-low" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4 / 4</div>
            <p className="text-xs text-muted-foreground mt-1">Bandit, Semgrep, Regex, CodeBERT</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {MOCK_REPORTS.slice(0, 5).map((report) => (
                <div key={report.report_id} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                  <div className="flex items-center gap-4">
                    <div className="rounded-full bg-secondary p-2">
                      <FileText className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium leading-none">{report.report_id}</p>
                      <p className="text-xs text-muted-foreground mt-1">{report.language} • {new Date(report.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">{report.finding_count} findings</p>
                      <p className="text-xs text-muted-foreground mt-1">Score: {report.risk_score}</p>
                    </div>
                    <SeverityBadge severity={report.severity} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Security Posture</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <div className="relative h-48 w-48 rounded-full border-8 border-muted flex items-center justify-center">
              <div className="text-center">
                <span className="text-4xl font-bold">A-</span>
                <p className="text-sm text-muted-foreground mt-2">Overall Grade</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground text-center mt-8 px-4">
              Your overall security posture is good. Focus on resolving the 14 critical findings to reach grade A.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
