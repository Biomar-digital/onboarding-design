import { useState } from "react";
import { infoPanel } from "../content/infoPanel";

// The persistent reference panel. Collapsible so it can live alongside module
// content without crowding it, but is always one click away.
export function InfoPanel() {
  const [open, setOpen] = useState<string | null>("contacts");
  return (
    <aside className="space-y-3">
      <div className="flex items-center gap-2 px-1">
        <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
          Always-on info
        </span>
      </div>
      {infoPanel.map((group) => {
        const isOpen = open === group.id;
        return (
          <div key={group.id} className="card overflow-hidden">
            <button
              className="flex w-full items-center justify-between px-4 py-3 text-left"
              onClick={() => setOpen(isOpen ? null : group.id)}
            >
              <span className="flex items-center gap-2 text-sm font-semibold text-biomar-navy">
                <span aria-hidden>{group.icon}</span>
                {group.title}
              </span>
              <span
                className={`text-slate-300 transition ${isOpen ? "rotate-180" : ""}`}
              >
                ▾
              </span>
            </button>
            {isOpen && (
              <dl className="border-t border-slate-100 px-4 py-2">
                {group.rows.map((row, i) => (
                  <div key={i} className="py-1.5">
                    <dt className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                      {row.label}
                    </dt>
                    <dd className="text-sm text-slate-700">
                      {row.value}
                      {row.hint && (
                        <span className="ml-1 text-xs text-biomar-swoosh">
                          {row.hint}
                        </span>
                      )}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        );
      })}
    </aside>
  );
}
