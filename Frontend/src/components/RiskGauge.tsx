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
    <div className="relative flex flex-col items-center justify-center w-[140px] h-[140px]">
      <svg width="140" height="140" className="-rotate-90 absolute inset-0">
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
      <div className="relative z-10 flex flex-col items-center justify-center text-center">
        <div className="text-3xl font-bold leading-none">{score}</div>
        <div className={`text-[10px] font-bold mt-1.5 tracking-wider uppercase ${severityColor[severity] || "text-slate-300"}`}>
          {severity}
        </div>
      </div>
    </div>
  );
}
