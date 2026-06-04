export function HistoryPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">Scan History</h1>
      <p className="text-muted-foreground mt-1">Timeline of all analysis runs on this repository.</p>
      
      <div className="mt-8 flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
        <h3 className="text-lg font-medium">Coming Soon</h3>
        <p className="text-sm text-muted-foreground mt-2 max-w-sm">
          Historical trends and diffs between scans will be available here.
        </p>
      </div>
    </div>
  )
}
