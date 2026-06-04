import { motion } from "framer-motion"

interface RiskGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export function RiskGauge({ score, size = 120, strokeWidth = 10 }: RiskGaugeProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (score / 100) * circumference

  // Color logic
  let strokeColor = "var(--severity-low)"
  if (score >= 80) strokeColor = "var(--severity-critical)"
  else if (score >= 55) strokeColor = "var(--severity-high)"
  else if (score >= 30) strokeColor = "var(--severity-medium)"

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90 transform">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--muted)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-bold tracking-tighter" style={{ color: strokeColor }}>
          {score}
        </span>
      </div>
    </div>
  )
}
