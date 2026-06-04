import { Link, Outlet, useLocation } from "react-router-dom";

const nav = [
  { to: "/", label: "Dashboard" },
  { to: "/analyze", label: "Code Analysis" },
  { to: "/reports", label: "Reports" },
  { to: "/about", label: "About" },
];

export default function Layout() {
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-700 bg-panel/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-accent">
            AI Security Review
          </Link>
          <nav className="flex gap-4">
            {nav.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`text-sm ${
                  pathname === item.to ? "text-accent font-semibold" : "text-slate-400 hover:text-white"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-slate-700 py-4 text-center text-slate-500 text-sm">
        Student AppSec Platform — Regex · Semgrep · Bandit · ML (mock/CodeBERT)
      </footer>
    </div>
  );
}
