import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

import { Badge } from "@/components/ui/badge"

export function SettingsPage() {
  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure analysis engines, ML providers, and preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analysis Engines</CardTitle>
          <CardDescription>Enable or disable specific static analysis tools.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Semgrep</Label>
              <p className="text-sm text-muted-foreground">Advanced semantic code analysis for deep vulnerability detection.</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between opacity-60">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label className="text-base">Bandit (Python)</Label>
                <Badge variant="secondary" className="text-[10px] uppercase font-semibold">Coming Soon</Badge>
              </div>
              <p className="text-sm text-muted-foreground">Python AST-based security analysis tool.</p>
            </div>
            <Switch disabled />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Regex Scanner</Label>
              <p className="text-sm text-muted-foreground">Fast, pattern-based secret and token detection.</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Machine Learning Provider</CardTitle>
          <CardDescription>Select the ML backend used for risk scoring.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">CodeBERT Engine</Label>
              <p className="text-sm text-muted-foreground">Fine-tuned Microsoft CodeBERT model (running locally).</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
