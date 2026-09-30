import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useStore } from "../lib/store";
import {
  listSignupRequests,
  approveSignup,
  rejectSignup,
  isBackendUnavailable,
  type SignupRequestRow,
} from "../lib/authApi";
import type { Person } from "../content/types";

// Admin review queue for self-service "request access" submissions. Approving
// creates the login credential (server-side, via the Worker) and — unless
// linked to an existing designer — a new Person record here, which still
// needs a normal "Publish to GitHub" to become permanent.
export function AdminSignupRequests() {
  const { people, upsertPerson, publish } = useStore();
  const [requests, setRequests] = useState<SignupRequestRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    listSignupRequests()
      .then((r) => setRequests(r))
      .catch((err) =>
        setError(
          isBackendUnavailable(err)
            ? "No live server behind this preview — signup requests only work on a real deployment."
            : (err as Error).message,
        ),
      );
  };

  useEffect(load, []);

  const pending = requests?.filter((r) => r.status === "pending") ?? [];
  const handled = requests?.filter((r) => r.status !== "pending") ?? [];

  return (
    <div className="space-y-6">
      <Link to="/admin" className="text-sm text-slate-400 hover:text-biomar-swoosh">
        ← Back to admin
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-biomar-navy">Signup requests</h1>
        <p className="text-sm text-slate-500">
          Review who's asked for access. Approving sets their password and
          creates the account — nothing is created until you do.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {error}
        </div>
      )}

      {requests && (
        <div className="card p-5">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-widest text-slate-400">
            Pending ({pending.length})
          </h2>
          {pending.length === 0 ? (
            <p className="text-sm text-slate-400">Nothing waiting on you.</p>
          ) : (
            <div className="space-y-3">
              {pending.map((r) => (
                <RequestRow
                  key={r.id}
                  request={r}
                  people={people}
                  onApproved={(person) => {
                    upsertPerson(person);
                    load();
                  }}
                  onRejected={load}
                  publish={publish}
                />
              ))}
            </div>
          )}

          {handled.length > 0 && (
            <>
              <h2 className="mb-3 mt-6 text-sm font-bold uppercase tracking-widest text-slate-400">
                Handled
              </h2>
              <div className="space-y-1.5">
                {handled.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-sm"
                  >
                    <span>
                      <span className="font-semibold text-biomar-navy">{r.name}</span>{" "}
                      <span className="text-xs text-slate-400">{r.email}</span>
                    </span>
                    <span
                      className={`chip ${
                        r.status === "approved"
                          ? "bg-biomar-swoosh/15 text-biomar-swoosh"
                          : "bg-slate-100 text-slate-400"
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function randomPassword(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(9));
  return btoa(String.fromCharCode(...bytes)).replace(/[+/=]/g, "").slice(0, 12);
}

function RequestRow({
  request,
  people,
  onApproved,
  onRejected,
  publish,
}: {
  request: SignupRequestRow;
  people: Person[];
  onApproved: (person: Person) => void;
  onRejected: () => void;
  publish: () => Promise<{ ok: boolean; message: string }>;
}) {
  const [open, setOpen] = useState(false);
  const [linkTo, setLinkTo] = useState<string>("__new__");
  const [password, setPassword] = useState(randomPassword());
  const [role, setRole] = useState<"admin" | "employee">("employee");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<{ email: string; password: string } | null>(null);

  const approve = async () => {
    setBusy(true);
    setError(null);
    const person: Person =
      linkTo === "__new__"
        ? {
            id: `emp-${Date.now().toString(36)}`,
            name: request.name,
            email: request.email,
            role,
            profile: null,
            startDate: new Date().toISOString().slice(0, 10),
            assignedModuleIds: [],
            progress: {},
          }
        : people.find((p) => p.id === linkTo)!;

    const result = await approveSignup(request.id, person.id, password, role);
    setBusy(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    onApproved(person);
    setDone({ email: request.email, password });
    publish().catch(() => {});
  };

  const reject = async () => {
    if (!confirm(`Decline the request from ${request.name}?`)) return;
    setBusy(true);
    const result = await rejectSignup(request.id);
    setBusy(false);
    if (!result.ok) setError(result.error);
    else onRejected();
  };

  if (done) {
    return (
      <div className="rounded-xl border border-biomar-swoosh/30 bg-biomar-ice/40 p-4 text-sm">
        <p className="font-semibold text-biomar-navy">
          Account created for {request.name} ✓
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Share these with them — they can change the password after signing in.
        </p>
        <div className="mt-2 rounded-lg bg-white px-3 py-2 font-mono text-xs">
          {done.email} / {done.password}
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Don't forget to finish setting up their profile and module assignment
          on their designer page.
        </p>
      </div>
    );
  }

  const availablePeople = people.filter((p) => p.role === "employee");

  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-biomar-navy">{request.name}</p>
          <p className="text-xs text-slate-400">{request.email}</p>
          {request.message && (
            <p className="mt-1 text-xs text-slate-500">"{request.message}"</p>
          )}
          <p className="mt-1 text-[11px] text-slate-300">
            Requested {new Date(request.requestedAt).toLocaleDateString()}
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          <button className="btn-ghost text-xs" onClick={reject} disabled={busy}>
            Decline
          </button>
          <button
            className="btn-primary text-xs"
            onClick={() => setOpen((v) => !v)}
            disabled={busy}
          >
            {open ? "Cancel" : "Approve →"}
          </button>
        </div>
      </div>

      {open && (
        <div className="mt-4 space-y-3 border-t border-slate-100 pt-4">
          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Account
            </span>
            <select
              className="input"
              value={linkTo}
              onChange={(e) => setLinkTo(e.target.value)}
            >
              <option value="__new__">Create a new designer record</option>
              {availablePeople.map((p) => (
                <option key={p.id} value={p.id}>
                  Link to existing: {p.name}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Role
            </span>
            <select
              className="input"
              value={role}
              onChange={(e) => setRole(e.target.value as "admin" | "employee")}
            >
              <option value="employee">Employee (designer)</option>
              <option value="admin">Admin</option>
            </select>
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Initial password
            </span>
            <div className="flex gap-2">
              <input
                className="input font-mono"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
              />
              <button
                type="button"
                className="btn-ghost shrink-0 text-xs"
                onClick={() => setPassword(randomPassword())}
              >
                🎲 Generate
              </button>
            </div>
            <span className="mt-1 block text-[11px] text-slate-400">
              At least 8 characters. You'll share this with them directly.
            </span>
          </label>

          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>
          )}

          <button
            className="btn-accent w-full"
            onClick={approve}
            disabled={busy || password.length < 8}
          >
            {busy ? "Creating…" : "Create account"}
          </button>
        </div>
      )}
    </div>
  );
}
