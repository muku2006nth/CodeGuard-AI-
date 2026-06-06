import { useReports } from "@/hooks/useApi"
import { Loader2, AlertCircle, FileText } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { SeverityBadge } from "@/components/shared/severity-badge"
import { Link } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"

export function ReportsPage() {
  const { data: reports, isLoading, error } = useReports()

  return (
    <div className="flex flex-col gap-6 pb-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground mt-1">View and export detailed security reports.</p>
      </div>
      
      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading reports</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : "Could not connect to backend."}
          </AlertDescription>
        </Alert>
      ) : reports?.length === 0 ? (
        <div className="mt-8 flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
          <h3 className="text-lg font-medium">No reports yet</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm">
            Run a code analysis to generate your first security report.
          </p>
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="rounded-md border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Report ID</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Score</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Severity</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Findings</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Language</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {reports?.map((r) => (
                    <tr key={r.report_id} className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                      <td className="p-4 align-middle">
                        <Link to={`/results/${r.report_id}`} className="flex items-center gap-2 text-primary hover:underline">
                          <FileText className="h-4 w-4" />
                          <span className="font-mono">{r.report_id.slice(0, 8)}</span>
                        </Link>
                      </td>
                      <td className="p-4 align-middle font-medium">{r.risk_score}</td>
                      <td className="p-4 align-middle"><SeverityBadge severity={r.severity} /></td>
                      <td className="p-4 align-middle">{r.finding_count}</td>
                      <td className="p-4 align-middle capitalize">{r.language}</td>
                      <td className="p-4 align-middle text-muted-foreground">{new Date(r.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

