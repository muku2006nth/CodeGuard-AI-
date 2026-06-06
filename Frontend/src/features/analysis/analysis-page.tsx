import { useState, useEffect } from "react"
import { Play, Code2, AlertTriangle, ShieldCheck, Bug, Search, Brain, Circle, Database } from "lucide-react"
import Editor from "@monaco-editor/react"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { RiskGauge } from "@/components/shared/risk-gauge"
import { SeverityBadge } from "@/components/shared/severity-badge"
import { AnalyzeResponse, Finding } from "@/types"
import { analyzeCode } from "@/services/api"
export function AnalysisPage() {
  const [code, setCode] = useState<string>("# Write or paste your code here\n\nimport os\n\ndef get_user_data(user_id):\n    # TODO: fetch from db\n    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n    return query\n")
  const [language, setLanguage] = useState<string>("python")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [results, setResults] = useState<AnalyzeResponse | null>(null)
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null)

  useEffect(() => {
    if (!isAnalyzing) return

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < 5 ? prev + 1 : prev))
    }, 700)

    return () => clearInterval(interval)
  }, [isAnalyzing])

  const handleAnalyze = async () => {
    if (!code.trim()) return
    
    setIsAnalyzing(true)
    setCurrentStep(0)
    setResults(null)
    setSelectedFinding(null)
    
    try {
      const data = await analyzeCode(code, language)
      setResults(data)
    } catch (error) {
      console.error("Error analyzing code:", error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="flex h-full flex-col gap-6 overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Code Analysis</h1>
          <p className="text-muted-foreground mt-1">Run AI-powered security scans on your source code.</p>
        </div>
        <div className="flex items-center gap-4">
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
              <SelectItem value="typescript">TypeScript</SelectItem>
              <SelectItem value="go">Go</SelectItem>
              <SelectItem value="java">Java</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleAnalyze} disabled={isAnalyzing} className="min-w-[120px]">
            {isAnalyzing ? (
              <span className="flex items-center gap-2">
                <Search className="h-4 w-4 animate-spin" />
                Analyzing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Play className="h-4 w-4" />
                Analyze Code
              </span>
            )}
          </Button>
        </div>
      </div>

      <ResizablePanelGroup 
        direction="horizontal" 
        className="h-[calc(100vh-180px)] rounded-lg border"
      >
        <ResizablePanel defaultSize={50} minSize={30}>
          {/* Editor Pane */}
          <Card className="flex h-full flex-col overflow-hidden border-0 rounded-none border-r border-border/50">
            <div className="flex items-center justify-between border-b bg-muted/30 px-4 py-2">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Code2 className="h-4 w-4" />
                Source Code
              </div>
            </div>
            <div className="flex-1">
              <Editor
                height="100%"
                language={language}
                theme="vs-dark"
                value={code}
                onChange={(value) => setCode(value || "")}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: "'JetBrains Mono', monospace",
                  padding: { top: 16 },
                  scrollBeyondLastLine: false,
                }}
              />
            </div>
          </Card>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel defaultSize={50} minSize={30}>
          {/* Results Pane */}
          <Card className="flex h-full flex-col overflow-hidden border-0 rounded-none bg-card">
            {!results && !isAnalyzing ? (
              <div className="flex h-full flex-col items-center justify-center text-center p-8">
                <div className="rounded-full bg-muted p-4 mb-4">
                  <ShieldCheck className="h-12 w-12 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Ready to Analyze</h3>
                <p className="text-muted-foreground max-w-sm">
                  Write or paste your code in the editor, then click Analyze to detect security vulnerabilities, hardcoded secrets, and logical flaws.
                </p>
              </div>
            ) : isAnalyzing ? (
              <div className="flex h-full flex-col items-center justify-center text-center p-8">
                <div className="relative">
                  <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                  <div className="h-16 w-16 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                </div>
                <h3 className="text-xl font-semibold mt-6 mb-2">Running Analysis Pipeline</h3>
                <div className="space-y-3 mt-5 text-left text-sm text-muted-foreground">
                  {/* Step 1: Regex Scanner */}
                  {currentStep > 0 ? (
                    <p className="flex items-center gap-2.5 text-emerald-500 font-medium transition-colors duration-200">
                      <CheckCircle /> Regex Scanner (Completed)
                    </p>
                  ) : (
                    <p className="flex items-center gap-2.5 text-primary font-medium">
                      <Search className="h-4 w-4 animate-spin text-primary" /> Regex Scanner (Running...)
                    </p>
                  )}

                  {/* Step 2: Semgrep SAST */}
                  {currentStep > 1 ? (
                    <p className="flex items-center gap-2.5 text-emerald-500 font-medium transition-colors duration-200">
                      <CheckCircle /> Semgrep SAST (Completed)
                    </p>
                  ) : currentStep === 1 ? (
                    <p className="flex items-center gap-2.5 text-primary font-medium">
                      <Search className="h-4 w-4 animate-spin text-primary" /> Semgrep SAST (Running...)
                    </p>
                  ) : (
                    <p className="flex items-center gap-2.5 opacity-40">
                      <Circle className="h-3.5 w-3.5 border border-muted-foreground rounded-full" /> Semgrep SAST (Pending)
                    </p>
                  )}

                  {/* Step 3: CodeBERT ML Model */}
                  {currentStep > 2 ? (
                    <p className="flex items-center gap-2.5 text-emerald-500 font-medium transition-colors duration-200">
                      <CheckCircle /> CodeBERT ML Model (Completed)
                    </p>
                  ) : currentStep === 2 ? (
                    <p className="flex items-center gap-2.5 text-primary font-medium">
                      <Search className="h-4 w-4 animate-spin text-primary" /> CodeBERT ML Model (Running...)
                    </p>
                  ) : (
                    <p className="flex items-center gap-2.5 opacity-40">
                      <Brain className="h-4 w-4" /> CodeBERT ML Model (Pending)
                    </p>
                  )}

                  {/* Step 4: RAG Knowledge Retrieval */}
                  {currentStep > 3 ? (
                    <p className="flex items-center gap-2.5 text-emerald-500 font-medium transition-colors duration-200">
                      <CheckCircle /> RAG Knowledge Retrieval (Completed)
                    </p>
                  ) : currentStep === 3 ? (
                    <p className="flex items-center gap-2.5 text-primary font-medium">
                      <Database className="h-4 w-4 animate-pulse text-primary" /> RAG Knowledge Retrieval (Running...)
                    </p>
                  ) : (
                    <p className="flex items-center gap-2.5 opacity-40">
                      <Database className="h-4 w-4" /> RAG Knowledge Retrieval (Pending)
                    </p>
                  )}

                  {/* Step 6: Risk Assessment Engine */}
                  {currentStep === 5 ? (
                    <p className="flex items-center gap-2.5 text-primary font-medium">
                      <Search className="h-4 w-4 animate-spin text-primary" /> Risk Assessment Engine (Running...)
                    </p>
                  ) : (
                    <p className="flex items-center gap-2.5 opacity-40">
                      <Bug className="h-4 w-4" /> Risk Assessment Engine (Pending)
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex h-full flex-col">
                <div className="border-b p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h2 className="text-2xl font-bold tracking-tight">Analysis Results</h2>
                      <p className="text-sm text-muted-foreground mt-1">
                        Completed in {results?.latency_seconds}s • Found {results?.findings.length} issues
                      </p>
                      <div className="flex gap-2 mt-4 flex-wrap">
                        <SeverityBadge severity={results?.severity || "MEDIUM"} />
                        <Badge variant="outline" className="bg-muted">Risk Score: {results?.risk_score}/100</Badge>
                        <Badge variant="outline" className={results?.ml_score.is_suspicious ? "bg-red-500/10 text-red-500 border-red-500/30" : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"}>
                          Model Prediction: {results?.ml_score.is_suspicious ? "Vulnerable" : "Safe"}
                        </Badge>

                      </div>
                    </div>
                    <div className="flex gap-8">
                      <RiskGauge score={results?.risk_score || 0} size={100} strokeWidth={8} label="Risk Score" type="risk" />
                      <RiskGauge score={Math.round((results?.ml_score.risk_probability || 0) * 100)} size={100} strokeWidth={8} label="ML Confidence" type="confidence" />
                    </div>
                  </div>
                </div>
                
                <Tabs defaultValue="findings" className="flex-1 flex flex-col overflow-hidden">
                  <div className="px-6 pt-4">
                    <TabsList className="w-full justify-start rounded-none border-b bg-transparent p-0">
                      <TabsTrigger value="findings" className="rounded-none border-b-2 border-transparent px-4 py-2 data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none">
                        Findings ({results?.findings.length})
                      </TabsTrigger>

                      <TabsTrigger value="summary" className="rounded-none border-b-2 border-transparent px-4 py-2 data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none">
                        Executive Summary
                      </TabsTrigger>
                    </TabsList>
                  </div>
                  
                  {/* ===== Findings Tab ===== */}
                  <TabsContent value="findings" className="flex-1 overflow-hidden m-0">
                    <ScrollArea className="h-full">
                      <div className="p-6 space-y-6">
                        {results?.findings.map((finding) => (
                          <Card 
                            key={finding.id} 
                            className={`cursor-pointer transition-colors hover:bg-muted/50 ${selectedFinding?.id === finding.id ? 'border-primary' : ''}`}
                            onClick={() => setSelectedFinding(finding)}
                          >
                            <CardHeader className="p-4 pb-2">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <SeverityBadge severity={finding.severity} />
                                  <CardTitle className="text-sm">{finding.category}</CardTitle>
                                </div>
                                <span className="text-xs text-muted-foreground font-mono">Line {finding.line_number}</span>
                              </div>
                            </CardHeader>
                            <CardContent className="p-4 pt-0">
                              <p className="text-sm text-muted-foreground mb-3">{finding.description}</p>
                              {selectedFinding?.id === finding.id && (
                                <div className="mt-5 space-y-6 border-t border-border/40 pt-5">
                                  <div className="bg-slate-900/20 rounded-lg p-3 border border-border/20">
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">What is wrong?</h4>
                                    <p className="text-sm leading-relaxed">{finding.what_is_wrong}</p>
                                  </div>
                                  <div className="bg-slate-900/20 rounded-lg p-3 border border-border/20">
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Remediation</h4>
                                    <p className="text-sm leading-relaxed">{finding.remediation}</p>
                                  </div>
                                  <div className="space-y-2">
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Secure Example</h4>
                                    <pre className="mt-1 rounded-md bg-muted p-3 text-xs font-mono">
                                      <code>{finding.secure_example}</code>
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </ScrollArea>
                  </TabsContent>


                  {/* ===== Executive Summary Tab ===== */}
                  <TabsContent value="summary" className="flex-1 overflow-hidden m-0">
                    <ScrollArea className="h-full">
                      <div className="p-6 space-y-6">
                        <div>
                          <h3 className="text-lg font-semibold mb-2">Analysis Overview</h3>
                          <p className="text-muted-foreground leading-relaxed">{results?.summary}</p>
                        </div>
                        <Separator />
                        <div>
                          <h3 className="text-lg font-semibold mb-3">Key Recommendations</h3>
                          <ul className="space-y-3">
                            {results?.recommendations.map((rec, i) => (
                              <li key={i} className="flex gap-3">
                                <AlertTriangle className="h-5 w-5 text-severity-high shrink-0" />
                                <span className="text-sm">{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </Card>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  )
}

function CheckCircle() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-primary"
    >
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
