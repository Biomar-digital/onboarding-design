import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Logo } from "../components/Brand";
import * as authApi from "../lib/authApi";

// Public page opened from the invite link: the invited person chooses a
// password, the account is created and they're signed in.
export function SetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [invite, setInvite] = useState<{ email: string; name: string } | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!token) {
      setLoadError("This link is incomplete. Ask the Design Hub team for a new one.");
      return;
    }
    authApi
      .getInvite(token)
      .then((r) => (r.ok ? setInvite({ email: r.email, name: r.name }) : setLoadError(r.error)))
      .catch(() => setLoadError("Couldn't reach the server — please try again."));
  }, [token]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 8) return setError("Use at least 8 characters.");
    if (password !== confirm) return setError("The two passwords don't match.");
    setBusy(true);
    try {
      const r = await authApi.acceptInvite(token, password);
      if (!r.ok) {
        setError(r.error);
        setBusy(false);
        return;
      }
      // Signed in by the server; reload so the app picks up the session.
      window.location.assign("/");
    } catch {
      setError("Couldn't reach the server — please try again.");
      setBusy(false);
    }
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
          {loadError ? (
            <>
              <h1 className="text-lg font-bold text-biomar-navy">This link can't be used</h1>
              <p className="mt-2 text-sm text-slate-500">{loadError}</p>
              <Link to="/login" className="btn-primary mt-5 inline-block">
                Go to sign in
              </Link>
            </>
          ) : !invite ? (
            <p className="text-sm text-slate-400">Checking your link…</p>
          ) : (
            <>
              <h1 className="text-lg font-bold text-biomar-navy">
                Welcome, {invite.name.split(" ")[0]}
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Choose a password to start your Design Hub onboarding. You'll sign in with{" "}
                <span className="font-semibold text-biomar-navy">{invite.email}</span>.
              </p>
              <form className="mt-5 space-y-3" onSubmit={submit}>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                    New password
                  </span>
                  <input
                    type="password"
                    required
                    minLength={8}
                    className="input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    placeholder="At least 8 characters"
                  />
                </label>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                    Repeat password
                  </span>
                  <input
                    type="password"
                    required
                    className="input"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    autoComplete="new-password"
                  />
                </label>
                {error && (
                  <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>
                )}
                <button className="btn-primary w-full" disabled={busy}>
                  {busy ? "Creating your account…" : "Create password & sign in"}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
