import { Badge } from "@/components/ui/badge"
import { SEVERITY_COLORS } from "@/lib/constants"
import { cn } from "@/lib/utils"

interface SeverityBadgeProps {
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const colorClass = SEVERITY_COLORS[severity] || SEVERITY_COLORS.MEDIUM;
  
  return (
    <Badge 
      variant="outline" 
      className={cn("px-2 py-0.5 font-medium border text-[10px]", colorClass, className)}
    >
      {severity}
    </Badge>
  )
}
