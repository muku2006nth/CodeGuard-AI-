export function VulnerabilitiesPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">Vulnerabilities</h1>
      <p className="text-muted-foreground mt-1">Explore all detected vulnerabilities across your codebase.</p>
      
      <div className="mt-8 flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
        <h3 className="text-lg font-medium">Coming Soon</h3>
        <p className="text-sm text-muted-foreground mt-2 max-w-sm">
          The vulnerability knowledge base is being indexed. Check back later to browse by CWE/OWASP categories.
        </p>
      </div>
    </div>
  )
}
