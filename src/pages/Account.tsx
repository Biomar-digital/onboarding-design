import { useState } from "react";
import { Link } from "react-router-dom";
import { useStore } from "../lib/store";
import { changePassword, isBackendUnavailable } from "../lib/authApi";

// Lets the signed-in user set their own password — the way to move off a
// temporary/bootstrap password an admin gave them.
export function Account() {
  const { currentUser, backendAvailable } = useStore();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setOk(false);
    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirm) {
      setError("New password and confirmation don't match.");
      return;
    }
    setSubmitting(true);
    try {
      const result = await changePassword(currentPassword, newPassword);
      if (!result.ok) setError(result.error);
      else {
        setOk(true);
        setCurrentPassword("");
        setNewPassword("");
        setConfirm("");
      }
    } catch (err) {
      setError(
        isBackendUnavailable(err)
          ? "No live server behind this preview — password changes only work on a real deployment."
          : (err as Error).message,
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-4">
      <Link
        to={currentUser?.role === "admin" ? "/admin" : "/"}
        className="text-sm text-slate-400 hover:text-biomar-swoosh"
      >
        ← Back
      </Link>

      <div className="card p-6">
        <h1 className="text-lg font-bold text-biomar-navy">Change password</h1>
        <p className="mt-1 text-sm text-slate-500">
          Signed in as {currentUser?.email}.
        </p>

        {backendAvailable === false && (
          <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
            No live server behind this preview — this only works on a real
            deployment.
          </p>
        )}

        <form className="mt-4 space-y-3" onSubmit={submit}>
          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Current password
            </span>
            <input
              type="password"
              required
              className="input"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              New password
            </span>
            <input
              type="password"
              required
              minLength={8}
              className="input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Confirm new password
            </span>
            <input
              type="password"
              required
              minLength={8}
              className="input"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
            />
          </label>

          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>
          )}
          {ok && (
            <p className="rounded-lg bg-biomar-ice/60 px-3 py-2 text-xs text-biomar-navy">
              Password updated ✓
            </p>
          )}

          <button className="btn-primary w-full" disabled={submitting}>
            {submitting ? "Saving…" : "Update password"}
          </button>
        </form>
      </div>
    </div>
  );
}
