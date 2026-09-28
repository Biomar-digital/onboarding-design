import { useMemo, useState } from "react";
import type { FolderNode } from "../content/types";
import { folderTree } from "../content/folderStructure";

interface FlatEntry {
  node: FolderNode;
  /** Names from root to this node, inclusive — for display. */
  names: string[];
  /** Child indexes from root to this node, inclusive — unique even when two
   * siblings share a name (the source diagram has two different branches
   * both labeled "SALMON"), so this is what identifies a node unambiguously. */
  idxPath: number[];
}

function flatten(nodes: FolderNode[], names: string[] = [], idxPath: number[] = []): FlatEntry[] {
  const out: FlatEntry[] = [];
  nodes.forEach((n, i) => {
    const nextNames = [...names, n.name];
    const nextIdx = [...idxPath, i];
    out.push({ node: n, names: nextNames, idxPath: nextIdx });
    if (n.children?.length) out.push(...flatten(n.children, nextNames, nextIdx));
  });
  return out;
}

const keyOf = (idxPath: number[]) => idxPath.join(".");

// Interactive explorer of the real Design Hub folder tree (The Pond /
// Kontainer), with a type-ahead search across every folder at every depth.
export function FolderExplorer() {
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());
  const [focusKey, setFocusKey] = useState<string | null>(null);

  const flat = useMemo(() => flatten(folderTree), []);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return flat
      .filter((e) => e.node.name.toLowerCase().includes(q))
      .sort((a, b) => {
        const an = a.node.name.toLowerCase();
        const bn = b.node.name.toLowerCase();
        const aStarts = an.startsWith(q) ? 0 : 1;
        const bStarts = bn.startsWith(q) ? 0 : 1;
        if (aStarts !== bStarts) return aStarts - bStarts;
        return a.names.length - b.names.length;
      })
      .slice(0, 40);
  }, [query, flat]);

  const openResult = (entry: FlatEntry) => {
    // expand every ancestor along the index-path so the tree renders it visible
    setExpanded((prev) => {
      const next = new Set(prev);
      for (let i = 1; i < entry.idxPath.length; i++) {
        next.add(keyOf(entry.idxPath.slice(0, i)));
      }
      return next;
    });
    setFocusKey(keyOf(entry.idxPath));
    setQuery("");
  };

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-slate-100 p-4">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          🗂️ Buscar una carpeta
        </h2>
        <div className="relative mt-2">
          <input
            className="input"
            placeholder="Escribí un nombre… ej. “LARVIVA”, “brand guidelines”, “roll-up”"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {query && (
            <button
              className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-biomar-swoosh"
              onClick={() => setQuery("")}
            >
              ✕
            </button>
          )}
        </div>

        {query && (
          <div className="mt-3 max-h-80 space-y-1 overflow-y-auto">
            {results.length === 0 && (
              <p className="px-1 py-2 text-sm text-slate-400">
                Sin resultados para “{query}”.
              </p>
            )}
            {results.map((r) => (
              <button
                key={keyOf(r.idxPath)}
                onClick={() => openResult(r)}
                className="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-biomar-ice/50"
              >
                <span className="font-semibold text-biomar-navy">{r.node.name}</span>
                <span className="block truncate text-xs text-slate-400">
                  {r.names.slice(0, -1).join(" › ") || "raíz"}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {!query && (
        <div className="max-h-[32rem] overflow-y-auto p-3">
          <Tree
            nodes={folderTree}
            parentIdx={[]}
            expanded={expanded}
            setExpanded={setExpanded}
            focusKey={focusKey}
          />
        </div>
      )}
    </section>
  );
}

function Tree({
  nodes,
  parentIdx,
  expanded,
  setExpanded,
  focusKey,
}: {
  nodes: FolderNode[];
  parentIdx: number[];
  expanded: Set<string>;
  setExpanded: React.Dispatch<React.SetStateAction<Set<string>>>;
  focusKey: string | null;
}) {
  const depth = parentIdx.length;
  return (
    <ul className={depth === 0 ? "space-y-0.5" : "ml-4 space-y-0.5 border-l border-slate-100 pl-3"}>
      {nodes.map((n, i) => {
        const idxPath = [...parentIdx, i];
        const key = keyOf(idxPath);
        const hasChildren = !!n.children?.length;
        const isFocused = focusKey === key;
        const isOpen = expanded.has(key) || isFocused;
        return (
          <li key={key}>
            <div
              className={`flex items-start gap-1.5 rounded-lg px-1.5 py-1 ${
                isFocused ? "bg-biomar-swoosh/15 ring-1 ring-biomar-swoosh/40" : ""
              }`}
            >
              {hasChildren ? (
                <button
                  className="mt-0.5 grid h-4 w-4 shrink-0 place-items-center text-[10px] text-slate-400"
                  onClick={() =>
                    setExpanded((prev) => {
                      const next = new Set(prev);
                      if (next.has(key)) next.delete(key);
                      else next.add(key);
                      return next;
                    })
                  }
                >
                  {isOpen ? "▾" : "▸"}
                </button>
              ) : (
                <span className="mt-0.5 w-4 shrink-0 text-center text-[10px] text-slate-300">•</span>
              )}
              <div className="min-w-0">
                <span className="text-sm text-biomar-navy">
                  {hasChildren ? "📁" : "📄"} {n.name}
                </span>
                {n.note && <span className="block text-xs text-slate-400">{n.note}</span>}
              </div>
            </div>
            {hasChildren && isOpen && (
              <Tree
                nodes={n.children!}
                parentIdx={idxPath}
                expanded={expanded}
                setExpanded={setExpanded}
                focusKey={focusKey}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
}
