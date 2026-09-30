import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useStore } from "../lib/store";
import { Logo, TAGLINE } from "../components/Brand";
import { completionStats } from "../lib/progress";

export function Login() {
  const { login, backendAvailable } = useStore();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showDemo, setShowDemo] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const result = await login(email.trim(), password);
    setSubmitting(false);
    if (!result.ok) {
      setError(result.message ?? "Sign-in failed.");
      return;
    }
    navigate("/");
  };

  return (
    <div className="grid min-h-full place-items-center bg-gradient-to-b from-biomar-navy to-biomar-blue px-4 py-16">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <div className="rounded-2xl bg-white px-6 py-4 shadow-card">
            <Logo />
          </div>
        </div>
        <div className="card p-6">
          <h1 className="text-lg font-bold text-biomar-navy">
            Welcome to Design Hub Onboarding
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Sign in with your BioMar email and password.
          </p>

          <form className="mt-5 space-y-3" onSubmit={submit}>
            <label className="block">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                Email
              </span>
              <input
                type="email"
                required
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@biomar.com"
                autoComplete="username"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                Password
              </span>
              <input
                type="password"
                required
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </label>

            {error && (
              <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
                {error}
              </p>
            )}
            {backendAvailable === false && !error && (
              <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
                No live server behind this preview, so sign-in here won't work
                — use demo mode below instead.
              </p>
            )}

            <button className="btn-primary w-full" disabled={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="mt-4 text-center text-xs text-slate-400">
            New here?{" "}
            <Link to="/signup" className="font-semibold text-biomar-swoosh hover:underline">
              Request access
            </Link>
          </p>

          {backendAvailable === false && (
            <div className="mt-5 border-t border-slate-100 pt-4 text-center">
              <button
                className="text-xs text-slate-400 underline hover:text-biomar-swoosh"
                onClick={() => setShowDemo((v) => !v)}
              >
                {showDemo ? "Hide" : "⚙ No server detected — use demo sign-in"}
              </button>
              {showDemo && <DemoPicker />}
            </div>
          )}
        </div>
        <p className="mt-6 text-center text-xs text-white/60">{TAGLINE}</p>
      </div>
    </div>
  );
}

// Only shown when there's no live Worker behind this URL (e.g. a static
// Artifact preview) — lets you click through the app without real accounts.
function DemoPicker() {
  const { people, demoLogin } = useStore();
  const navigate = useNavigate();
  const admins = people.filter((p) => p.role === "admin");
  const employees = people.filter((p) => p.role === "employee");

  const go = (id: string, role: string) => {
    demoLogin(id);
    navigate(role === "admin" ? "/admin" : "/");
  };

  return (
    <div className="mt-3 text-left">
      <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Admin</p>
      <div className="mt-2 space-y-2">
        {admins.map((p) => (
          <button
            key={p.id}
            onClick={() => go(p.id, p.role)}
            className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-left transition hover:border-biomar-swoosh hover:bg-biomar-ice"
          >
            <span>
              <span className="block text-sm font-semibold text-biomar-navy">{p.name}</span>
              <span className="block text-xs text-slate-400">{p.email}</span>
            </span>
            <span className="chip bg-biomar-navy text-white">Admin</span>
          </button>
        ))}
      </div>

      <p className="mt-4 text-xs font-bold uppercase tracking-widest text-slate-400">Employees</p>
      <div className="mt-2 space-y-2">
        {employees.map((p) => {
          const { pct } = completionStats(p);
          return (
            <button
              key={p.id}
              onClick={() => go(p.id, p.role)}
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-left transition hover:border-biomar-swoosh hover:bg-biomar-ice"
            >
              <span>
                <span className="block text-sm font-semibold text-biomar-navy">{p.name}</span>
                <span className="block text-xs text-slate-400">{p.email}</span>
              </span>
              <span className="chip bg-biomar-ice text-biomar-blue">{pct}% done</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
