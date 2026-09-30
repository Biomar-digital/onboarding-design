import { useState } from "react";
import { Link } from "react-router-dom";
import { Logo, TAGLINE } from "../components/Brand";
import { requestSignup, isBackendUnavailable } from "../lib/authApi";

// Self-service "request an account" form. Submitting creates a pending
// signup request; an admin reviews it in Admin → Signup requests and, on
// approval, sets a password and the account exists. Nothing is created here.
export function SignupRequest() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const result = await requestSignup(name.trim(), email.trim(), message.trim());
      if (!result.ok) {
        setError(result.error);
      } else {
        setSent(true);
      }
    } catch (err) {
      setError(
        isBackendUnavailable(err)
          ? "No live server behind this preview — account requests only work on a real deployment."
          : (err as Error).message,
      );
    } finally {
      setSubmitting(false);
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
          {sent ? (
            <>
              <h1 className="text-lg font-bold text-biomar-navy">Request sent</h1>
              <p className="mt-2 text-sm text-slate-500">
                An admin will review your request and set up your account. You'll
                be able to sign in with the password they give you.
              </p>
              <Link to="/login" className="btn-ghost mt-5 inline-block">
                ← Back to sign in
              </Link>
            </>
          ) : (
            <>
              <h1 className="text-lg font-bold text-biomar-navy">Request access</h1>
              <p className="mt-1 text-sm text-slate-500">
                Tell us who you are — an admin approves new accounts before they're
                created.
              </p>

              <form className="mt-5 space-y-3" onSubmit={submit}>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                    Full name
                  </span>
                  <input
                    required
                    className="input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                  />
                </label>
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
                  />
                </label>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
                    Note to the admin (optional)
                  </span>
                  <textarea
                    className="input h-20 resize-none"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="e.g. Joining as a junior graphic designer on 12 Oct"
                  />
                </label>

                {error && (
                  <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
                    {error}
                  </p>
                )}

                <button className="btn-primary w-full" disabled={submitting}>
                  {submitting ? "Sending…" : "Send request"}
                </button>
              </form>

              <p className="mt-4 text-center text-xs text-slate-400">
                Already have an account?{" "}
                <Link to="/login" className="font-semibold text-biomar-swoosh hover:underline">
                  Sign in
                </Link>
              </p>
            </>
          )}
        </div>
        <p className="mt-6 text-center text-xs text-white/60">{TAGLINE}</p>
      </div>
    </div>
  );
}
