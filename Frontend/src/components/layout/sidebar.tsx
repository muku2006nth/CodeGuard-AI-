import { Link, useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import { 
  LayoutDashboard, 
  Code2, 
  FileText, 
  ShieldAlert, 
  History, 
  Settings, 
  BookOpen,
  Info
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useSystemStatus } from "@/hooks/useApi"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Code2, label: "Code Analysis", href: "/analyze" },
  { icon: FileText, label: "Reports", href: "/reports" },
  { icon: ShieldAlert, label: "Vulnerabilities", href: "/vulnerabilities" },
  { icon: History, label: "History", href: "/history" },
]

const bottomItems = [
  { icon: Settings, label: "Settings", href: "/settings" },
  { icon: BookOpen, label: "Documentation", href: "#" },
  { icon: Info, label: "About", href: "/about" },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card px-3 py-4">
      <div className="mb-8 flex items-center px-3">
        <ShieldAlert className="mr-2 h-6 w-6 text-primary" />
        <span className="text-lg font-bold tracking-tight">CodeGuard AI</span>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link key={item.href} to={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn("w-full justify-start", isActive ? "bg-accent text-accent-foreground" : "")}
              >
                <item.icon className="mr-3 h-4 w-4" />
                {item.label}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 h-8 w-1 rounded-r-full bg-primary"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                  />
                )}
              </Button>
            </Link>
          )
        })}
      </nav>

      <div className="mt-auto space-y-1 pt-4">
        {bottomItems.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link key={item.href} to={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn("w-full justify-start text-muted-foreground", isActive ? "text-foreground" : "")}
              >
                <item.icon className="mr-3 h-4 w-4" />
                {item.label}
              </Button>
            </Link>
          )
        })}
      </div>

      <div className="mt-8 pt-4 border-t">
        <SystemHealthPanel />
      </div>
    </div>
  )
}

function SystemHealthPanel() {
  const { data: status, isLoading } = useSystemStatus()

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="w-full justify-start text-xs font-medium text-muted-foreground hover:text-foreground">
          <div className="flex items-center w-full">
            <span className={cn("mr-2 h-2 w-2 rounded-full", isLoading ? "bg-muted" : status?.backend === "healthy" ? "bg-green-500" : "bg-red-500")} />
            System Health
            <span className="ml-auto opacity-50">View Details</span>
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent side="right" align="end" className="w-64 p-4 text-sm bg-card shadow-lg border-border">
        <h4 className="font-semibold mb-3">Service Status</h4>
        {isLoading ? (
          <p className="text-muted-foreground text-xs">Loading status...</p>
        ) : status ? (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>Backend API</span>
              <Badge variant={status.backend === "healthy" ? "default" : "destructive"} className="text-[10px] uppercase">{status.backend}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>Database</span>
              <Badge variant={status.database === "healthy" ? "default" : "destructive"} className="text-[10px] uppercase">{status.database}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>CodeBERT ML</span>
              <Badge variant={status.codebert === "loaded" ? "default" : "secondary"} className="text-[10px] uppercase">{status.codebert}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>Semgrep</span>
              <Badge variant={status.semgrep === "available" ? "default" : "secondary"} className="text-[10px] uppercase">{status.semgrep}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>RAG Engine</span>
              <Badge variant={status.rag === "available" ? "default" : "secondary"} className="text-[10px] uppercase">{status.rag}</Badge>
            </div>
          </div>
        ) : (
          <p className="text-red-500 text-xs">Unable to load system status.</p>
        )}
      </PopoverContent>
    </Popover>
  )
}
