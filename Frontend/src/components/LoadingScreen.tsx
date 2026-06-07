// Vigil.dev — LoadingScreen.tsx
import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldAlert } from "lucide-react";

interface LoadingScreenProps {
  onComplete: () => void;
  message?: string;
  skipBoot?: boolean;
}

const BOOT_LINES = [
  { prefix: "[SYS]", text: "Mounting file system...", status: "OK" },
  { prefix: "[SYS]", text: "Loading CodeBERT weights...", status: "OK" },
  { prefix: "[SYS]", text: "Initialising Regex engine...", status: "OK" },
  { prefix: "[SYS]", text: "Initialising Semgrep engine...", status: "OK" },
  { prefix: "[SYS]", text: "Connecting to Supabase...", status: "OK" },
  { prefix: "[SYS]", text: "Verifying auth tokens...", status: "OK" },
];

function generateHex() {
  return "0x" + Math.floor(Math.random() * 0xffffffff).toString(16).padStart(8, "0");
}

export default function LoadingScreen({ onComplete, message, skipBoot = false }: LoadingScreenProps) {
  const [phase, setPhase] = useState<1 | 2 | 3 | 4>(skipBoot ? 2 : 1);
  const [bootLineIndex, setBootLineIndex] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [hexPairs, setHexPairs] = useState<{ left: string; right: string }[]>([
    { left: generateHex(), right: generateHex() },
    { left: generateHex(), right: generateHex() },
  ]);
  const [isSlidingUp, setIsSlidingUp] = useState(false);

  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const addTimeout = (fn: () => void, delay: number) => {
      const id = setTimeout(fn, delay);
      timeoutsRef.current.push(id);
      return id;
    };

    if (phase === 1 && !skipBoot) {
      let delay = 0;
      for (let i = 0; i <= BOOT_LINES.length; i++) {
        addTimeout(() => setBootLineIndex(i), delay);
        delay += 160;
      }
      addTimeout(() => setPhase(2), delay + 400);
    } 
    else if (phase === 2) {
      let currentProgress = 0;
      const duration = 1200;
      const interval = 20;
      const step = (100 / duration) * interval;
      
      const progressInterval = setInterval(() => {
        currentProgress = Math.min(100, currentProgress + step);
        setProgress(Math.floor(currentProgress));
        if (currentProgress >= 100) clearInterval(progressInterval);
      }, interval);

      intervalRef.current = setInterval(() => {
        setHexPairs([
          { left: generateHex(), right: generateHex() },
          { left: generateHex(), right: generateHex() },
        ]);
      }, 80);

      addTimeout(() => {
        clearInterval(progressInterval);
        if (intervalRef.current) clearInterval(intervalRef.current);
        setProgress(100);
        
        addTimeout(() => setPhase(3), 200);
      }, duration);
    }
    else if (phase === 3) {
      addTimeout(() => {
        setIsSlidingUp(true);
        addTimeout(() => {
          onComplete();
        }, 500);
      }, 700);
    }

    return () => {
      timeoutsRef.current.forEach(clearTimeout);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [phase, skipBoot, onComplete]);

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <motion.div
      initial={{ y: 0 }}
      animate={{ y: isSlidingUp ? "-100%" : 0 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center overflow-hidden font-mono text-sm select-none"
      style={{ backgroundColor: "#08090c" }}
    >
      <AnimatePresence mode="wait">
        {phase === 1 && (
          <motion.div
            key="phase1"
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-2xl px-6"
          >
            <div className="mb-2">
              <div className="text-[18px] text-white" style={{ letterSpacing: "0.15em" }}>
                VIGIL.DEV SECURITY ENGINE
              </div>
              <div className="text-[13px] text-[#8b949e]">v2.1.0 — build 20260607</div>
            </div>
            <div className="text-[#1e2a3a] mb-4">─────────────────────────────────────</div>
            
            <div className="space-y-1">
              {BOOT_LINES.map((line, i) => (
                <div
                  key={i}
                  className="flex transition-opacity duration-[120ms]"
                  style={{ opacity: bootLineIndex >= i ? 1 : 0 }}
                >
                  <span className="text-[#8b949e] w-16">{line.prefix}</span>
                  <span className="text-white flex-1">{line.text}</span>
                  <span className="text-[#00d4ff]">{line.status}</span>
                </div>
              ))}
            </div>

            <div className="text-[#1e2a3a] mt-4 mb-1">─────────────────────────────────────</div>
            <div
              className="flex transition-opacity duration-[120ms]"
              style={{ opacity: bootLineIndex >= BOOT_LINES.length ? 1 : 0 }}
            >
              <span className="text-[#00d4ff] w-24">[READY]</span>
              <span className="text-white">All systems operational</span>
            </div>
          </motion.div>
        )}

        {phase === 2 && (
          <motion.div
            key="phase2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center"
          >
            <div className="relative flex items-center justify-center mb-6">
              <svg width="140" height="140" className="-rotate-90">
                <circle
                  cx="70"
                  cy="70"
                  r={radius}
                  fill="none"
                  stroke="#1e2a3a"
                  strokeWidth="2"
                />
                <circle
                  cx="70"
                  cy="70"
                  r={radius}
                  fill="none"
                  stroke="#00d4ff"
                  strokeWidth="2"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  className="transition-all duration-[20ms] ease-linear"
                />
              </svg>
              <div
                className={`absolute text-2xl text-white transition-colors ${
                  progress === 100 ? "text-[#00d4ff]" : ""
                }`}
              >
                {progress}
              </div>
            </div>

            <div className="text-[#8b949e] text-[12px] mb-6" style={{ letterSpacing: "0.2em" }}>
              {message || "ANALYSING THREAT MATRIX..."}
            </div>

            <div className="text-[#3d444d] space-y-1 font-mono text-center">
              {hexPairs.map((pair, i) => (
                <div key={i}>
                  {pair.left} → {pair.right}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {phase >= 3 && (
          <motion.div
            key="phase3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="flex items-center"
          >
            <ShieldAlert className="mr-3 h-8 w-8 text-[#00d4ff]" />
            <span className="font-sans text-[32px] font-bold text-white tracking-tight">
              ViGiL.dev
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
