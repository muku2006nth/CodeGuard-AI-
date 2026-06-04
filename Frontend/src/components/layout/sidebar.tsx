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
    </div>
  )
}
