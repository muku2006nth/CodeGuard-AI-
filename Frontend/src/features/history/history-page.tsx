import { useHistory } from "@/hooks/useApi"
import { Loader2, AlertCircle, Clock, ShieldAlert } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { SeverityBadge } from "@/components/shared/severity-badge"
import { Link } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"

export function HistoryPage() {
  const { data: history, isLoading, error } = useHistory()

  return (
    <div className="flex flex-col gap-6 pb-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Scan History</h1>
        <p className="text-muted-foreground mt-1">Timeline of all analysis runs on this repository.</p>
      </div>
      
      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading history</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : "Could not connect to backend."}
          </AlertDescription>
        </Alert>
      ) : history?.scans?.length === 0 ? (
        <div className="mt-8 flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
          <h3 className="text-lg font-medium">No history found</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm">
            Run an analysis to start building your scan history.
          </p>
        </div>
      ) : (
        <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
          {history?.scans?.map((scan) => (
            <div key={scan.report_id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-100 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                <Clock className="w-4 h-4" />
              </div>
              <Card className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4 flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <Link to={`/results/${scan.report_id}`} className="font-semibold text-primary hover:underline">
                      Scan {scan.report_id.slice(0, 8)}
                    </Link>
                    <span className="text-xs text-muted-foreground">{new Date(scan.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex gap-4 text-sm mt-2">
                    <div className="flex items-center gap-1">
                      <ShieldAlert className="w-4 h-4 text-muted-foreground" />
                      <span>{scan.finding_count} findings</span>
                    </div>
                    <div>Score: <strong>{scan.risk_score}</strong></div>
                    <SeverityBadge severity={scan.severity} />
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

