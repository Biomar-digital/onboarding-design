import { useState } from "react";
import * as authApi from "../lib/authApi";
import type { Person } from "../content/types";

// Admin: create a one-time "set your password" link for a person and send it
// from your own mail app (or automatically, if a mail provider is configured).
export function InviteCard({ person }: { person: Person }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invite, setInvite] = useState<authApi.InviteResult | null>(null);
  const [copied, setCopied] = useState(false);

  const create = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await authApi.inviteUser(person.email.trim(), person.id, person.role);
      if (!r.ok) setError(r.error);
      else setInvite(r.invite);
    } catch {
      setError("Couldn't reach the server.");
    }
    setBusy(false);
  };

  const first = person.name.split(" ")[0];
  const subject = "Set your password — BioMar Design Hub onboarding";
  const body = invite
    ? `Hi ${first},\n\nYou've been added to the BioMar Design Hub onboarding. Use this link to choose your password and sign in:\n\n${invite.link}\n\nThe link works once and expires in ${invite.expiresInDays} days. If it expires, let me know and I'll send you a new one.\n\nPowered by Partnership. Driven by Innovation.`
    : "";
  const mailto = `mailto:${encodeURIComponent(person.email.trim())}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* the field is selectable as a fallback */
    }
  };

  return (
    <div className="card p-5">
      <h2 className="flex items-center gap-2 text-sm font-bold text-biomar-navy">
        <span>✉️</span> Access invite
      </h2>
      <p className="mt-1 text-xs text-slate-500">
        Creates a one-time link so {first} can choose a password and sign in. It expires in 7 days.
      </p>

      {!person.email.trim() ? (
        <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
          Add and save an email for this person first.
        </p>
      ) : (
        <button className="btn-primary mt-3 w-full" onClick={create} disabled={busy}>
          {busy ? "Creating…" : invite ? "Create a new link" : "Create invite link"}
        </button>
      )}
      {error && <p className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>}

      {invite && (
        <div className="mt-3 space-y-2">
          {invite.emailSent ? (
            <p className="rounded-lg bg-biomar-green/10 px-3 py-2 text-xs text-biomar-navy">
              ✓ Email sent to {person.email}.
            </p>
          ) : (
            <p className="text-xs text-slate-500">
              {invite.emailError ? `Automatic email failed (${invite.emailError}). ` : ""}
              Send it from your own mail:
            </p>
          )}
          <input
            readOnly
            value={invite.link}
            onFocus={(e) => e.currentTarget.select()}
            className="input text-xs"
          />
          <div className="flex gap-2">
            <button className="btn-ghost flex-1 px-3 py-1.5 text-xs" onClick={() => copy(invite.link)}>
              {copied ? "Copied ✓" : "Copy link"}
            </button>
            <a className="btn-accent flex-1 px-3 py-1.5 text-center text-xs" href={mailto}>
              Open email draft
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
