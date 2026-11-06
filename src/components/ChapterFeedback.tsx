import { useState } from "react";
import * as authApi from "../lib/authApi";
import { useStore } from "../lib/store";

// A small "questions or feedback" box under each chapter. Messages go to the
// admins' Feedback inbox (Admin → Feedback).
export function ChapterFeedback({
  sectionKey,
  sectionTitle,
}: {
  sectionKey: string;
  sectionTitle: string;
}) {
  const { backendAvailable } = useStore();
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent">("idle");
  const [error, setError] = useState<string | null>(null);

  const send = async () => {
    setStatus("sending");
    setError(null);
    try {
      const r = await authApi.sendFeedback(sectionKey, sectionTitle, text);
      if (!r.ok) {
        setError(r.error);
        setStatus("idle");
        return;
      }
      setText("");
      setStatus("sent");
    } catch {
      setError("Couldn't reach the server — please try again.");
      setStatus("idle");
    }
  };

  if (status === "sent") {
    return (
      <div className="mt-4 flex items-center justify-between gap-3 rounded-xl bg-biomar-green/10 px-4 py-3 text-sm text-biomar-navy">
        <span>✓ Thanks — your message was sent to the team.</span>
        <button
          className="text-xs font-semibold text-biomar-swoosh hover:underline"
          onClick={() => {
            setStatus("idle");
            setOpen(true);
          }}
        >
          Send another
        </button>
      </div>
    );
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mt-4 flex w-full items-center gap-2 rounded-xl border border-dashed border-slate-200 px-4 py-2.5 text-left text-sm text-slate-500 transition hover:border-biomar-swoosh hover:bg-biomar-ice/40 hover:text-biomar-navy"
      >
        <span aria-hidden>💬</span> Questions or feedback about this chapter?
      </button>
    );
  }

  return (
    <div className="mt-4 rounded-xl border border-biomar-swoosh/30 bg-biomar-ice/30 p-4">
      <label className="block">
        <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-biomar-navy">
          Questions or feedback — {sectionTitle}
        </span>
        <textarea
          className="input min-h-[96px] resize-y"
          value={text}
          maxLength={2000}
          onChange={(e) => setText(e.target.value)}
          placeholder="Something unclear, missing or outdated? A question for the team? Write it here."
          autoFocus
        />
      </label>
      {backendAvailable === false && (
        <p className="mt-2 text-xs text-amber-700">
          Sending only works on the live site.
        </p>
      )}
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
      <div className="mt-3 flex items-center justify-between gap-3">
        <span className="text-xs text-slate-400">{text.trim().length}/2000</span>
        <div className="flex gap-2">
          <button className="btn-ghost px-3 py-1.5 text-xs" onClick={() => setOpen(false)}>
            Cancel
          </button>
          <button
            className="btn-primary px-3 py-1.5 text-xs"
            onClick={send}
            disabled={status === "sending" || text.trim().length < 3 || backendAvailable === false}
          >
            {status === "sending" ? "Sending…" : "Send to the team"}
          </button>
        </div>
      </div>
    </div>
  );
}
