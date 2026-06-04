interface Props {
  score: number;
  severity: string;
}

const severityColor: Record<string, string> = {
  LOW: "text-ok",
  MEDIUM: "text-warn",
  HIGH: "text-orange-400",
  CRITICAL: "text-danger",
};

export default function RiskGauge({ score, severity }: Props) {
  const color = score >= 80 ? "#f87171" : score >= 55 ? "#fb923c" : score >= 30 ? "#fbbf24" : "#4ade80";
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" className="-rotate-90">
        <circle cx="70" cy="70" r="54" fill="none" stroke="#334155" strokeWidth="12" />
        <circle
          cx="70"
          cy="70"
          r="54"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="-mt-20 text-center">
        <div className="text-3xl font-bold">{score}</div>
        <div className={`text-sm font-semibold ${severityColor[severity] || "text-slate-300"}`}>
          {severity}
        </div>
      </div>
    </div>
  );
}
