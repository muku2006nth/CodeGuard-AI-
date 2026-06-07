// Vigil.dev — LandingPage.tsx
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

type TerminalLine = {
  text: string;
  type: 'prompt' | 'info' | 'warn' | 'crit' | 'ok' | 'dim' | 'blank' | 'divider' | 'notice';
  delay: number;
  highlight?: boolean;
};

const TERMINAL_SEQUENCE: TerminalLine[] = [
  { text: '$ vigil scan ./src/api/auth.py',         type: 'prompt',  delay: 0 },
  { text: '',                                         type: 'blank',   delay: 300 },
  { text: '[INFO]  Initialising engines...',          type: 'info',    delay: 400 },
  { text: '[INFO]  Regex engine       ✓ ready',       type: 'info',    delay: 350 },
  { text: '[INFO]  Semgrep engine     ✓ ready',       type: 'info',    delay: 350 },
  { text: '[INFO]  CodeBERT model     ✓ loaded',      type: 'info',    delay: 350 },
  { text: '',                                         type: 'blank',   delay: 200 },
  { text: 'Scanning auth.py...',                      type: 'dim',     delay: 400 },
  { text: '',                                         type: 'blank',   delay: 200 },
  { text: '[WARN]  Line 23 — SQL Injection',          type: 'warn',    delay: 500,  highlight: true },
  { text: '        engine: regex  |  confidence: 0.94', type: 'dim',   delay: 200 },
  { text: '',                                         type: 'blank',   delay: 150 },
  { text: '[WARN]  Line 41 — Hardcoded Secret',       type: 'warn',    delay: 450,  highlight: true },
  { text: '        engine: semgrep  |  confidence: 0.89', type: 'dim', delay: 200 },
  { text: '',                                         type: 'blank',   delay: 150 },
  { text: '[CRIT]  Line 67 — Command Injection',      type: 'crit',    delay: 500,  highlight: true },
  { text: '        engine: codebert  |  confidence: 0.97', type: 'dim', delay: 200 },
  { text: '',                                         type: 'blank',   delay: 300 },
  { text: '────────────────────────────────────',     type: 'divider', delay: 400 },
  { text: 'Risk Score    87 / 100',                   type: 'ok',      delay: 300 },
  { text: 'Severity      CRITICAL',                   type: 'crit',    delay: 250 },
  { text: 'Findings      3 vulnerabilities',          type: 'ok',      delay: 250 },
  { text: '────────────────────────────────────',     type: 'divider', delay: 200 },
  { text: '',                                         type: 'blank',   delay: 300 },
  { text: '--- Restarting simulation in 3s ---',      type: 'dim',     delay: 3000 }
];

const LiveTerminal: React.FC = () => {
  const [visibleLines, setVisibleLines] = useState<number>(0);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const startSequence = () => {
    setVisibleLines(0);
    setIsFadingOut(false);
    
    let currentDelay = 0;
    
    TERMINAL_SEQUENCE.forEach((line, index) => {
      currentDelay += line.delay;
      const timeout = setTimeout(() => {
        setVisibleLines(index + 1);
        if (containerRef.current) {
          containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
        
        if (index === TERMINAL_SEQUENCE.length - 1) {
          const restartTimeout = setTimeout(() => {
            setIsFadingOut(true);
            const resetTimeout = setTimeout(() => {
              startSequence();
            }, 400);
            timeoutsRef.current.push(resetTimeout);
          }, 3000);
          timeoutsRef.current.push(restartTimeout);
        }
      }, currentDelay);
      timeoutsRef.current.push(timeout);
    });
  };

  useEffect(() => {
    startSequence();
    return () => {
      timeoutsRef.current.forEach(clearTimeout);
    };
  }, []);

  const renderLine = (line: TerminalLine, index: number) => {
    let content;
    
    if (line.type === 'prompt') {
      content = <><span style={{ color: '#8b949e' }}>$</span> <span style={{ color: '#ffffff' }}>{line.text.slice(2)}</span></>;
    } else if (line.type === 'info') {
      content = <><span style={{ color: '#00d4ff' }}>[INFO]</span><span style={{ color: '#ffffff' }}>{line.text.slice(6)}</span></>;
    } else if (line.type === 'warn' || line.type === 'notice') {
      content = <><span style={{ color: '#f0a500' }}>[WARN]</span><span style={{ color: '#f0a500' }}>{line.text.slice(6)}</span></>;
    } else if (line.type === 'crit') {
      content = <><span style={{ color: '#ff4444' }}>[CRIT]</span><span style={{ color: '#ff4444', fontWeight: 600 }}>{line.text.slice(6)}</span></>;
    } else if (line.type === 'ok') {
      if (line.text.startsWith('Risk Score')) {
        content = <><span style={{ color: '#8b949e' }}>Risk Score    </span><span style={{ color: '#ffffff' }}>{line.text.replace('Risk Score    ', '')}</span></>;
      } else if (line.text.startsWith('Findings')) {
        content = <><span style={{ color: '#8b949e' }}>Findings      </span><span style={{ color: '#ffffff' }}>{line.text.replace('Findings      ', '')}</span></>;
      } else {
        content = <span style={{ color: '#ffffff' }}>{line.text}</span>;
      }
    } else if (line.type === 'dim') {
      content = <span style={{ color: '#8b949e' }}>{line.text}</span>;
    } else if (line.type === 'divider') {
      content = <span style={{ color: '#1e2a3a' }}>{line.text}</span>;
    } else {
      content = <span>{line.text}</span>;
    }

    const highlightStyle = line.highlight ? {
      backgroundColor: line.type === 'crit' ? 'rgba(255,68,68,0.08)' : 'rgba(240,165,0,0.08)',
      borderLeft: `2px solid ${line.type === 'crit' ? '#ff4444' : '#f0a500'}`,
      padding: '4px 10px',
      borderRadius: '0 4px 4px 0',
      marginLeft: '-12px',
    } : {};

    return (
      <motion.div
        key={index}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.15 }}
        style={{
          minHeight: line.type === 'blank' ? '1.8em' : 'auto',
          whiteSpace: 'pre',
          ...highlightStyle
        }}
      >
        {content}
      </motion.div>
    );
  };

  return (
    <div style={{ background: '#0d1117', border: '1px solid #1e2a3a', borderRadius: '10px', overflow: 'hidden' }} className="w-full shadow-2xl">
      <div style={{ background: '#161b22', height: '36px' }} className="flex items-center px-4 w-full relative">
        <div className="flex gap-2">
          <div style={{ width: '12px', height: '12px', backgroundColor: '#ff5f57', borderRadius: '50%' }} />
          <div style={{ width: '12px', height: '12px', backgroundColor: '#febc2e', borderRadius: '50%' }} />
          <div style={{ width: '12px', height: '12px', backgroundColor: '#28c840', borderRadius: '50%' }} />
        </div>
        <div className="absolute left-0 right-0 text-center pointer-events-none" style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: '12px', color: '#8b949e' }}>
          vigil.dev — live scan
        </div>
      </div>
      <div 
        ref={containerRef}
        style={{ 
          padding: '20px 24px', 
          fontFamily: '"JetBrains Mono", monospace', 
          fontSize: '13px', 
          lineHeight: 1.8,
          height: '380px',
          overflowY: 'hidden',
          opacity: isFadingOut ? 0 : 1,
          transition: 'opacity 400ms ease-in-out'
        }}
      >
        {TERMINAL_SEQUENCE.slice(0, visibleLines).map((line, i) => renderLine(line, i))}
        {!isFadingOut && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.5, ease: "linear" }}
            style={{ color: '#00d4ff', marginLeft: '4px' }}
          >
            |
          </motion.span>
        )}
      </div>
    </div>
  );
};

const useCountUp = (end: number, duration: number = 2000) => {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const nodeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setHasAnimated(true);
          let startTimestamp: number | null = null;
          const step = (timestamp: number) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            setCount(Math.floor(progress * end));
            if (progress < 1) {
              window.requestAnimationFrame(step);
            }
          };
          window.requestAnimationFrame(step);
        }
      },
      { threshold: 0.1 }
    );
    if (nodeRef.current) observer.observe(nodeRef.current);
    return () => observer.disconnect();
  }, [end, duration, hasAnimated]);

  return { count, nodeRef };
};

export default function LandingPage() {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToEngine = () => {
    document.getElementById('engine-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  const statSamples = useCountUp(27318, 1500);

  return (
    <div style={{ backgroundColor: '#08090c', minHeight: '100vh', fontFamily: '"Inter", sans-serif', color: '#ffffff' }}>
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        .custom-scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #08090c; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 4px; }
      `}} />

      <nav 
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{ 
          background: 'rgba(8,9,12,0.85)', 
          backdropFilter: 'blur(12px)',
          borderBottom: scrolled ? '1px solid #1e2a3a' : '1px solid transparent'
        }}
      >
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#00d4ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 8v4" stroke="#00d4ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="12" cy="16" r="1" fill="#00d4ff"/>
            </svg>
            <span style={{ fontWeight: 600, fontSize: '20px' }}>Vigil.dev</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#" className="transition-colors hover:text-white" style={{ color: '#8b949e', fontWeight: 500 }}>Documentation</a>
            <button onClick={() => navigate('/login')} className="transition-opacity hover:opacity-80" style={{ color: '#ffffff', fontWeight: 500 }}>Sign In</button>
            <button 
              onClick={() => navigate('/login')}
              style={{ backgroundColor: '#00d4ff', color: '#08090c', fontWeight: 600, padding: '10px 20px', borderRadius: '6px' }}
              className="transition-transform hover:scale-105 active:scale-95"
            >
              Get Started →
            </button>
          </div>

          <button className="md:hidden p-2 text-white">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12h18M3 6h18M3 18h18" strokeLinecap="round"/></svg>
          </button>
        </div>
      </nav>

      <main className="pt-32 pb-24 overflow-hidden">
        <section className="max-w-7xl mx-auto px-6 pt-12 pb-24">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="w-full lg:w-[60%] flex flex-col items-start">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '13px', marginBottom: '16px' }}>
                  // AI-Powered Security Analysis
                </div>
                <h1 style={{ fontWeight: 700, fontSize: 'clamp(36px, 5vw, 56px)', lineHeight: 1.1, marginBottom: '24px' }}>
                  Your Code Has Secrets.<br />Vigil Finds Them.
                </h1>
                <p style={{ color: '#8b949e', fontSize: '18px', maxWidth: '480px', lineHeight: 1.6, marginBottom: '40px' }}>
                  Hybrid vulnerability detection combining machine learning, static analysis, and pattern matching. Paste your code. Get a security report in seconds.
                </p>
                <div className="flex flex-col sm:flex-row items-center gap-6 mb-8">
                  <button 
                    onClick={() => navigate('/login')}
                    style={{ backgroundColor: '#00d4ff', color: '#08090c', fontWeight: 600, padding: '14px 28px', borderRadius: '6px', fontSize: '16px' }}
                    className="w-full sm:w-auto transition-transform hover:scale-105 active:scale-95"
                  >
                    Start Scanning Free
                  </button>
                  <button 
                    onClick={scrollToEngine}
                    style={{ color: '#ffffff', fontWeight: 500, fontSize: '16px' }}
                    className="transition-opacity hover:opacity-70"
                  >
                    View the engine →
                  </button>
                </div>
                <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#8b949e', fontSize: '13px' }} className="flex flex-wrap items-center gap-3">
                  <span>27,318 training samples</span>
                  <span style={{ color: '#3d444d' }}>·</span>
                  <span>3-engine pipeline</span>
                  <span style={{ color: '#3d444d' }}>·</span>
                  <span>&lt; 3s scan time</span>
                </div>
              </motion.div>
            </div>
            <div className="w-full lg:w-[40%] mt-12 lg:mt-0 lg:rotate-[1.5deg] origin-center">
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
                <LiveTerminal />
              </motion.div>
            </div>
          </div>
        </section>

        <div style={{ borderTop: '1px solid #1e2a3a', borderBottom: '1px solid #1e2a3a', padding: '24px 0', overflow: 'hidden' }} className="w-full bg-[#08090c] relative">
          <div className="absolute left-0 top-0 bottom-0 w-8 sm:w-32 bg-gradient-to-r from-[#08090c] to-transparent z-10 pointer-events-none"></div>
          <div className="absolute right-0 top-0 bottom-0 w-8 sm:w-32 bg-gradient-to-l from-[#08090c] to-transparent z-10 pointer-events-none"></div>
          <div className="flex w-max">
            <motion.div 
              animate={{ x: ["0%", "-50%"] }} 
              transition={{ repeat: Infinity, ease: "linear", duration: 30 }}
              className="flex items-center gap-6 whitespace-nowrap px-6"
            >
              {[...Array(2)].map((_, i) => (
                <React.Fragment key={i}>
                  <span style={{ color: '#8b949e', fontSize: '14px', marginLeft: i === 1 ? '24px' : '0' }}>Detecting vulnerabilities across</span>
                  {[
                    'SQL Injection', 'Command Injection', 'Path Traversal', 'Hardcoded Secrets', 
                    'Weak Cryptography', 'Unsafe Deserialization', 'Code Injection'
                  ].map((type, j) => (
                    <span key={`${i}-${j}`} style={{ background: '#0f1117', border: '1px solid #1e2a3a', color: '#8b949e', padding: '6px 14px', borderRadius: '999px', fontSize: '12px', fontFamily: '"JetBrains Mono", monospace' }}>
                      {type}
                    </span>
                  ))}
                </React.Fragment>
              ))}
            </motion.div>
          </div>
        </div>

        <section className="max-w-7xl mx-auto px-6 py-32">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4 }}>
            <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '13px', marginBottom: '8px' }}>// three-stage pipeline</div>
            <h2 style={{ fontSize: '32px', fontWeight: 600, marginBottom: '64px' }}>How Vigil works</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { num: '01', title: 'Paste Your Code', desc: 'Drop any Python, JavaScript, or C function directly into the editor or upload a file.' },
                { num: '02', title: 'Three Engines Run in Parallel', desc: 'Regex, Semgrep, and CodeBERT analyse simultaneously. Each engine contributes its signal to the risk score.' },
                { num: '03', title: 'Read Your Report', desc: 'Line-level findings, confidence scores, severity rating, and an executive summary — ready in under 3 seconds.' }
              ].map((step, i) => (
                <div key={i} className="relative group mt-8 md:mt-0">
                  <div style={{ background: '#0d1117', border: '1px solid #1e2a3a', padding: '40px 32px', height: '100%', position: 'relative', transition: 'border-color 200ms ease', overflow: 'hidden' }} className="hover:border-[#00d4ff] rounded-lg">
                    <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: '120px', fontWeight: 700, color: '#1e2a3a', position: 'absolute', top: '-20px', right: '-10px', opacity: 0.3, pointerEvents: 'none' }}>
                      {step.num}
                    </div>
                    <div className="relative z-10">
                      <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '16px' }}>{step.title}</h3>
                      <p style={{ color: '#8b949e', lineHeight: 1.6 }}>{step.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </section>

        <section id="engine-section" className="max-w-7xl mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4 }}>
            <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '13px', marginBottom: '8px' }}>// under the hood</div>
            <h2 style={{ fontSize: '32px', fontWeight: 600, marginBottom: '64px' }}>The detection engine</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-16">
              <div>
                <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '12px', marginBottom: '12px' }}>LAYER 01</div>
                <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px' }}>Pattern Matching</h3>
                <p style={{ color: '#8b949e', lineHeight: 1.6, marginBottom: '24px', minHeight: '96px' }}>
                  Deterministic rules targeting known vulnerability signatures. Zero false negatives on patterns it knows. Runs in microseconds.
                </p>
                <div className="flex flex-wrap gap-2">
                  {['SQL Injection', 'Command Injection', 'Hardcoded Secrets'].map(tag => (
                    <span key={tag} style={{ background: '#161b22', color: '#8b949e', padding: '4px 10px', borderRadius: '4px', fontSize: '12px', fontFamily: '"JetBrains Mono", monospace' }}>{tag}</span>
                  ))}
                </div>
              </div>
              <div>
                <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '12px', marginBottom: '12px' }}>LAYER 02</div>
                <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px' }}>Static Analysis</h3>
                <p style={{ color: '#8b949e', lineHeight: 1.6, marginBottom: '24px', minHeight: '96px' }}>
                  Understands your code's syntax tree, not just its text. Catches context-aware vulnerabilities across multi-line patterns.
                </p>
                <div className="flex flex-wrap gap-2">
                  {['Path Traversal', 'Deserialization', 'Dangerous Functions'].map(tag => (
                    <span key={tag} style={{ background: '#161b22', color: '#8b949e', padding: '4px 10px', borderRadius: '4px', fontSize: '12px', fontFamily: '"JetBrains Mono", monospace' }}>{tag}</span>
                  ))}
                </div>
              </div>
              <div>
                <div style={{ fontFamily: '"JetBrains Mono", monospace', color: '#00d4ff', fontSize: '12px', marginBottom: '12px' }}>LAYER 03</div>
                <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px' }}>Machine Learning</h3>
                <p style={{ color: '#8b949e', lineHeight: 1.6, marginBottom: '24px', minHeight: '96px' }}>
                  Fine-tuned transformer model trained on 27,318 labeled vulnerability samples from the Devign research dataset. Detects what rules cannot.
                </p>
                <div className="flex flex-wrap gap-2">
                  {['Semantic Patterns', 'Novel Vulnerabilities', 'Code Injection'].map(tag => (
                    <span key={tag} style={{ background: '#161b22', color: '#8b949e', padding: '4px 10px', borderRadius: '4px', fontSize: '12px', fontFamily: '"JetBrains Mono", monospace' }}>{tag}</span>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: '14px', color: '#8b949e', textAlign: 'center', lineHeight: 1.8 }} className="hidden md:block mt-12 bg-[#0d1117] border border-[#1e2a3a] rounded-lg p-8">
              <div className="flex justify-center items-center gap-4 text-left">
                <div className="flex flex-col gap-6">
                  <motion.div initial={{ x: -10, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="flex items-center gap-2">
                    <span className="text-white font-semibold w-20 text-right">Regex</span> <span className="text-[#1e2a3a]">──┐</span>
                  </motion.div>
                  <motion.div initial={{ x: -10, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.2 }} className="flex items-center gap-2">
                    <span className="text-white font-semibold w-20 text-right">Semgrep</span> <span className="text-[#1e2a3a]">──┤</span>
                  </motion.div>
                  <motion.div initial={{ x: -10, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.3 }} className="flex items-center gap-2">
                    <span className="text-white font-semibold w-20 text-right">CodeBERT</span> <span className="text-[#1e2a3a]">──┘</span>
                  </motion.div>
                </div>
                <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.5 }} className="text-[#1e2a3a] text-xl px-2">→</motion.div>
                <motion.div initial={{ scale: 0.95, opacity: 0 }} whileInView={{ scale: 1, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.6 }} className="border border-[#1e2a3a] bg-[#161b22] px-6 py-3 rounded text-white font-semibold relative overflow-hidden group">
                  <motion.div 
                    initial={{ left: '-100%' }}
                    whileInView={{ left: '200%' }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.7, duration: 1.5, ease: "linear" }}
                    className="absolute top-0 bottom-0 w-20 bg-gradient-to-r from-transparent via-[rgba(0,212,255,0.2)] to-transparent skew-x-12"
                  ></motion.div>
                  Risk Assessment Engine
                </motion.div>
                <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.8 }} className="text-[#1e2a3a] text-xl px-2">→</motion.div>
                <motion.div initial={{ x: 10, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.9 }} className="flex gap-3 font-semibold">
                  <span className="text-[#ff4444]">CRITICAL</span><span className="text-[#1e2a3a]">/</span><span className="text-[#f0a500]">HIGH</span><span className="text-[#1e2a3a]">/</span><span className="text-[#28c840]">LOW</span>
                </motion.div>
              </div>
            </div>
            <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: '13px', color: '#8b949e', lineHeight: 1.8 }} className="block md:hidden border border-[#1e2a3a] p-4 mt-8 rounded bg-[#0d1117]">
              Regex →<br/>
              Semgrep → Risk Engine → SCORE<br/>
              CodeBERT →
            </div>
          </motion.div>
        </section>

        <section className="max-w-7xl mx-auto px-6 py-32" ref={statSamples.nodeRef}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-0 md:divide-x divide-[#1e2a3a] border-y border-[#1e2a3a] py-12">
            <div className="flex flex-col items-center justify-center text-center px-4">
              <div style={{ fontSize: '48px', fontWeight: 700, marginBottom: '8px' }}>{statSamples.count.toLocaleString()}</div>
              <div style={{ color: '#8b949e', fontSize: '16px' }}>Vulnerability samples trained on</div>
            </div>
            <div className="flex flex-col items-center justify-center text-center px-4 border-l border-[#1e2a3a] md:border-l-0">
              <div style={{ fontSize: '48px', fontWeight: 700, marginBottom: '8px' }}>7+</div>
              <div style={{ color: '#8b949e', fontSize: '16px' }}>Vulnerability classes detected</div>
            </div>
            <div className="flex flex-col items-center justify-center text-center px-4 pt-8 md:pt-0 border-t border-[#1e2a3a] md:border-t-0 col-span-2 md:col-span-1">
              <div style={{ fontSize: '48px', fontWeight: 700, marginBottom: '8px' }}>3</div>
              <div style={{ color: '#8b949e', fontSize: '16px' }}>Detection engines</div>
            </div>
            <div className="flex flex-col items-center justify-center text-center px-4 pt-8 md:pt-0 border-t border-[#1e2a3a] md:border-t-0 border-l border-[#1e2a3a] md:border-l-0 col-span-2 md:col-span-1">
              <div style={{ fontSize: '48px', fontWeight: 700, marginBottom: '8px' }}>&lt; 3s</div>
              <div style={{ color: '#8b949e', fontSize: '16px' }}>Time to full report</div>
            </div>
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-6 py-16">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            whileInView={{ opacity: 1, y: 0 }} 
            viewport={{ once: true }} 
            transition={{ duration: 0.4 }}
            style={{ background: '#0d1117', border: '1px solid #1e2a3a', borderRadius: '12px', padding: '80px 40px' }}
            className="text-center max-w-[800px] mx-auto flex flex-col items-center"
          >
            <h2 style={{ fontSize: 'clamp(28px, 4vw, 40px)', fontWeight: 700, marginBottom: '16px' }}>Start finding vulnerabilities today.</h2>
            <p style={{ color: '#8b949e', fontSize: '18px', marginBottom: '40px' }}>Free to use. No credit card. Paste your first file in 30 seconds.</p>
            <button 
              onClick={() => navigate('/login')}
              style={{ backgroundColor: '#00d4ff', color: '#08090c', fontWeight: 600, padding: '16px 36px', borderRadius: '6px', fontSize: '18px' }}
              className="transition-transform hover:scale-105 active:scale-95"
            >
              Open Vigil →
            </button>
          </motion.div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #1e2a3a', backgroundColor: '#08090c', padding: '64px 0 24px' }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8 mb-16">
            <div>
              <div style={{ fontWeight: 600, fontSize: '20px', color: '#ffffff', marginBottom: '16px' }}>Vigil.dev</div>
              <p style={{ color: '#8b949e', fontSize: '14px', maxWidth: '240px' }}>Find vulnerabilities before attackers do.</p>
            </div>
            <div className="flex flex-col gap-4">
              <button onClick={() => navigate('/login')} className="text-left w-fit transition-colors hover:text-white" style={{ color: '#8b949e', fontSize: '14px' }}>Sign In</button>
              <button onClick={() => navigate('/login')} className="text-left w-fit transition-colors hover:text-white" style={{ color: '#8b949e', fontSize: '14px' }}>Get Started</button>
              <button onClick={scrollToEngine} className="text-left w-fit transition-colors hover:text-white" style={{ color: '#8b949e', fontSize: '14px' }}>How It Works</button>
            </div>
            <div>
              <p style={{ color: '#8b949e', fontSize: '14px', fontFamily: '"JetBrains Mono", monospace', whiteSpace: 'nowrap' }}>
                Built with CodeBERT · Semgrep · Regex · FastAPI
              </p>
            </div>
          </div>
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 pt-8" style={{ borderTop: '1px solid #1e2a3a' }}>
            <span style={{ color: '#3d444d', fontSize: '12px' }}>© 2026 Vigil.dev</span>
            <span style={{ color: '#3d444d', fontSize: '12px' }}>Made by Mukunth</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
