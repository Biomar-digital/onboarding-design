import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { modulesById } from "../content/modules";
import { toolGroups } from "../content/tools";
import { glossary } from "../content/glossary";
import type { LessonSection } from "../content/types";

// Global search (Ctrl/Cmd+K) across the person's modules and their sections,
// the tools map and the glossary.

interface Doc {
  kind: "module" | "section" | "tool" | "term";
  title: string;
  sub?: string;
  text: string;
  to?: string;
  href?: string;
  definition?: string;
}

const KIND_LABEL: Record<Doc["kind"], string> = {
  module: "Module",
  section: "Section",
  tool: "Tool",
  term: "Glossary",
};
const KIND_WEIGHT: Record<Doc["kind"], number> = { module: 3, section: 1, tool: 2, term: 4 };

function sectionText(s: LessonSection): string {
  return [
    ...(s.body ?? []),
    ...(s.bullets ?? []),
    ...(s.facts ?? []).map((f) => `${f.label}: ${f.value}`),
    s.note ?? "",
  ].join(" ");
}

function buildIndex(assignedIds: string[]): Doc[] {
  const docs: Doc[] = [];
  for (const id of assignedIds) {
    const m = modulesById[id];
    if (!m) continue;
    docs.push({ kind: "module", title: m.title, text: m.summary, to: `/module/${m.id}` });
    m.sections.forEach((s, i) => {
      if (!s.heading) return;
      docs.push({
        kind: "section",
        title: s.heading,
        sub: m.title,
        text: sectionText(s),
        to: `/module/${m.id}#section-${i}`,
      });
    });
  }
  for (const g of toolGroups)
    for (const t of g.tools)
      docs.push({
        kind: "tool",
        title: t.name,
        sub: g.title,
        text: t.purpose,
        href: t.url,
        to: t.url ? undefined : "/module/tools-map",
      });
  for (const g of glossary)
    docs.push({ kind: "term", title: g.term, text: g.definition, definition: g.definition });
  return docs;
}

function snippet(text: string, tokens: string[]): string {
  const lower = text.toLowerCase();
  const at = tokens.map((t) => lower.indexOf(t)).filter((i) => i >= 0).sort((a, b) => a - b)[0] ?? 0;
  const start = Math.max(0, at - 40);
  const out = text.slice(start, start + 130).trim();
  return (start > 0 ? "…" : "") + out + (start + 130 < text.length ? "…" : "");
}

export function SearchPalette({
  assignedIds,
  open,
  onClose,
}: {
  assignedIds: string[];
  open: boolean;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const index = useMemo(() => buildIndex(assignedIds), [assignedIds]);

  const tokens = useMemo(
    () => query.toLowerCase().split(/\s+/).filter(Boolean),
    [query],
  );
  const results = useMemo(() => {
    if (tokens.length === 0) return [];
    return index
      .map((d) => {
        const title = d.title.toLowerCase();
        const hay = `${title} ${(d.sub ?? "").toLowerCase()} ${d.text.toLowerCase()}`;
        if (!tokens.every((t) => hay.includes(t))) return null;
        const score =
          tokens.reduce(
            (n, t) => n + (title.includes(t) ? 5 : 0) + (d.text.toLowerCase().includes(t) ? 1 : 0),
            0,
          ) + KIND_WEIGHT[d.kind];
        return { d, score };
      })
      .filter((x): x is { d: Doc; score: number } => !!x)
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
      .map((x) => x.d);
  }, [index, tokens]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);
  useEffect(() => setActive(0), [query]);

  const go = (d: Doc) => {
    if (d.to) navigate(d.to);
    else if (d.href) window.open(d.href, "_blank", "noreferrer");
    else return; // glossary: the definition is already shown
    onClose();
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-biomar-navy/40 px-4 pt-[12vh] backdrop-blur-sm"
      onMouseDown={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Search"
    >
      <div
        className="w-full max-w-xl overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-slate-200"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-slate-100 px-4 py-3">
          <span aria-hidden>🔍</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
              else if (e.key === "ArrowDown") {
                e.preventDefault();
                setActive((a) => Math.min(a + 1, results.length - 1));
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setActive((a) => Math.max(a - 1, 0));
              } else if (e.key === "Enter" && results[active]) go(results[active]);
            }}
            placeholder="Search modules, sections, tools and terms…"
            className="w-full bg-transparent text-sm text-biomar-navy outline-none placeholder:text-slate-400"
          />
          <kbd className="rounded border border-slate-200 px-1.5 py-0.5 text-[10px] text-slate-400">Esc</kbd>
        </div>

        <div className="max-h-[50vh] overflow-y-auto">
          {tokens.length === 0 ? (
            <p className="px-4 py-6 text-center text-sm text-slate-400">
              Try “PROOF”, “logo”, “file naming” or “brief”.
            </p>
          ) : results.length === 0 ? (
            <p className="px-4 py-6 text-center text-sm text-slate-500">
              Nothing found for “{query}”.
            </p>
          ) : (
            <ul>
              {results.map((d, i) => (
                <li key={`${d.kind}-${d.title}-${i}`}>
                  <button
                    className={`block w-full px-4 py-2.5 text-left transition ${
                      i === active ? "bg-biomar-ice/70" : "hover:bg-slate-50"
                    }`}
                    onMouseEnter={() => setActive(i)}
                    onClick={() => go(d)}
                  >
                    <span className="flex items-center gap-2">
                      <span className="chip bg-biomar-ice text-[10px] uppercase text-biomar-blue">
                        {KIND_LABEL[d.kind]}
                      </span>
                      <span className="text-sm font-semibold text-biomar-navy">{d.title}</span>
                      {d.sub && <span className="truncate text-xs text-slate-400">in {d.sub}</span>}
                      {d.href && <span className="text-xs text-biomar-swoosh">↗</span>}
                    </span>
                    <span className="mt-0.5 block text-xs leading-snug text-slate-500">
                      {d.definition ?? snippet(d.text, tokens)}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
