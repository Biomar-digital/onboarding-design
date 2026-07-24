import { useNavigate } from "react-router-dom";
import { useStore } from "../lib/store";
import { Logo, TAGLINE } from "../components/Brand";
import { completionStats } from "../lib/progress";

// Demo sign-in: pick a user. In production this screen is replaced by
// Cloudflare Access (Zero Trust) — BioMar SSO gates the whole site and the
// signed-in identity maps to a person record. See DEPLOYMENT.md.
export function Login() {
  const { people, login } = useStore();
  const navigate = useNavigate();
  const admins = people.filter((p) => p.role === "admin");
  const employees = people.filter((p) => p.role === "employee");

  const go = (id: string, role: string) => {
    login(id);
    navigate(role === "admin" ? "/admin" : "/");
  };

  return (
    <div className="grid min-h-full place-items-center bg-gradient-to-b from-biomar-navy to-biomar-blue px-4 py-16">
      <div className="w-full max-w-lg">
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
            Choose who you are to continue. (Demo sign-in — production uses
            BioMar SSO via Cloudflare Access.)
          </p>

          <p className="mt-5 text-xs font-bold uppercase tracking-widest text-slate-400">
            Admin
          </p>
          <div className="mt-2 space-y-2">
            {admins.map((p) => (
              <button
                key={p.id}
                onClick={() => go(p.id, p.role)}
                className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-left transition hover:border-biomar-swoosh hover:bg-biomar-ice"
              >
                <span>
                  <span className="block text-sm font-semibold text-biomar-navy">
                    {p.name}
                  </span>
                  <span className="block text-xs text-slate-400">
                    {p.email}
                  </span>
                </span>
                <span className="chip bg-biomar-navy text-white">Admin</span>
              </button>
            ))}
          </div>

          <p className="mt-5 text-xs font-bold uppercase tracking-widest text-slate-400">
            Employees
          </p>
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
                    <span className="block text-sm font-semibold text-biomar-navy">
                      {p.name}
                    </span>
                    <span className="block text-xs text-slate-400">
                      {p.email}
                    </span>
                  </span>
                  <span className="chip bg-biomar-ice text-biomar-blue">
                    {pct}% done
                  </span>
                </button>
              );
            })}
          </div>
        </div>
        <p className="mt-6 text-center text-xs text-white/60">{TAGLINE}</p>
      </div>
    </div>
  );
}
