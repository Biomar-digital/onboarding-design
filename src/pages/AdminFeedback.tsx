import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import * as authApi from "../lib/authApi";

// Admin inbox for the "questions or feedback" boxes under each chapter.
export function AdminFeedback() {
  const [items, setItems] = useState<authApi.FeedbackRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"open" | "resolved" | "all">("open");

  const load = () =>
    authApi
      .listFeedback()
      .then((rows) => {
        setItems(rows);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const shown = useMemo(
    () =>
      (items ?? []).filter((i) =>
        filter === "all" ? true : filter === "open" ? !i.resolved : i.resolved,
      ),
    [items, filter],
  );
  const openCount = (items ?? []).filter((i) => !i.resolved).length;

  const toggle = async (item: authApi.FeedbackRow) => {
    setItems((cur) =>
      (cur ?? []).map((i) => (i.id === item.id ? { ...i, resolved: !i.resolved } : i)),
    );
    try {
      await authApi.resolveFeedback(item.id, !item.resolved);
    } catch {
      load();
    }
  };

  return (
    <div className="space-y-6">
      <Link to="/admin" className="text-sm text-slate-400 hover:text-biomar-swoosh">
        ← Back to admin
      </Link>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-biomar-navy">Feedback &amp; questions</h1>
          <p className="text-sm text-slate-500">
            What designers sent from the box under each chapter. {openCount} open.
          </p>
        </div>
        <div className="inline-flex gap-1 rounded-xl bg-white p-1 shadow-card ring-1 ring-slate-100">
          {(["open", "resolved", "all"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-lg px-3 py-1.5 text-sm font-semibold capitalize transition ${
                filter === f ? "bg-biomar-navy text-white" : "text-slate-500 hover:bg-slate-50"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="card p-4 text-sm text-red-600">{error}</div>}
      {!items && !error && <div className="card p-6 text-sm text-slate-400">Loading…</div>}
      {items && shown.length === 0 && (
        <div className="card p-8 text-center text-sm text-slate-500">
          {filter === "open" ? "No open messages 🎉" : "Nothing here."}
        </div>
      )}

      <div className="space-y-3">
        {shown.map((i) => (
          <article key={i.id} className={`card p-5 ${i.resolved ? "opacity-70" : ""}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-biomar-navy">
                  {i.name}{" "}
                  <span className="font-normal text-slate-400">· {i.email}</span>
                </div>
                <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  {i.sectionTitle && (
                    <span className="chip bg-biomar-ice text-biomar-blue">{i.sectionTitle}</span>
                  )}
                  <span>{new Date(i.createdAt).toLocaleString("en-GB")}</span>
                </div>
              </div>
              <button className="btn-ghost px-3 py-1.5 text-xs" onClick={() => toggle(i)}>
                {i.resolved ? "Reopen" : "Mark resolved ✓"}
              </button>
            </div>
            <p className="mt-3 whitespace-pre-wrap text-[15px] leading-relaxed text-slate-700">
              {i.message}
            </p>
          </article>
        ))}
      </div>
    </div>
  );
}
