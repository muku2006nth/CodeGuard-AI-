import { Activity, ShieldAlert, FileText, CheckCircle2, Loader2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SeverityBadge } from "@/components/shared/severity-badge"
import { useDashboardData, useSystemStatus } from "@/hooks/useApi"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const COLORS: Record<string, string> = {
  Critical: '#ef4444', // text-red-500
  High: '#f97316',     // text-orange-500
  Medium: '#eab308',   // text-yellow-500
  Low: '#3b82f6'       // text-blue-500
}

export function DashboardPage() {
  const { data: dashboard, isLoading: isLoadingDash, error: dashError } = useDashboardData()
  const { data: systemStatus, isLoading: isLoadingSys } = useSystemStatus()

  if (isLoadingDash) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (dashError) {
    return (
      <Alert variant="destructive" className="mt-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error loading dashboard</AlertTitle>
        <AlertDescription>
          {dashError instanceof Error ? dashError.message : "Could not connect to backend."}
        </AlertDescription>
      </Alert>
    )
  }

  const activeEngines = systemStatus 
    ? [systemStatus.backend, systemStatus.codebert, systemStatus.semgrep].filter(s => s !== "mock" && s !== "unavailable" && s !== "offline").length
    : 0;

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
            <div className="text-2xl font-bold">{dashboard?.total_scans || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Total analysis runs</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Risk Score</CardTitle>
            <ShieldAlert className="h-4 w-4 text-severity-medium" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.average_risk_score || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Overall system risk</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Critical Findings</CardTitle>
            <ShieldAlert className="h-4 w-4 text-severity-critical" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.critical_findings || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Requires immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Engines</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-severity-low" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoadingSys ? "..." : `${activeEngines} / 3`}</div>
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
              {dashboard?.recent_scans && dashboard.recent_scans.length > 0 ? (
                dashboard.recent_scans.map((report) => (
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
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">No recent scans found.</p>
            )}
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
                <span className="text-4xl font-bold">
                  {(dashboard?.average_risk_score || 0) < 30 ? "A" : (dashboard?.average_risk_score || 0) < 60 ? "B" : "C"}
                </span>
                <p className="text-sm text-muted-foreground mt-2">Overall Grade</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground text-center mt-8 px-4">
              {dashboard?.critical_findings ? `Focus on resolving the ${dashboard.critical_findings} critical findings.` : "Your overall security posture is excellent. No critical findings."}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Scan Activity Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dashboard?.trend_data}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted-foreground)/0.2)" />
                  <XAxis dataKey="date" stroke="#ffffff" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#ffffff" fontSize={12} tickLine={false} axisLine={false} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  <Line type="monotone" dataKey="scans" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={dashboard?.severity_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {dashboard?.severity_distribution?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name] || 'hsl(var(--muted-foreground))'} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2">
                {['Critical', 'High', 'Medium', 'Low'].map(sev => (
                  <div key={sev} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <span className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[sev] }} />
                    {sev}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

