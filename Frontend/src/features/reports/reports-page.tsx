export function ReportsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
      <p className="text-muted-foreground mt-1">View and export detailed security reports.</p>
      
      <div className="mt-8 flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
        <h3 className="text-lg font-medium">Coming Soon</h3>
        <p className="text-sm text-muted-foreground mt-2 max-w-sm">
          The reports module is currently under development. Soon you'll be able to export PDF and CSV reports for compliance audits.
        </p>
      </div>
    </div>
  )
}
