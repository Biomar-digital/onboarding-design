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

function nodeAt(idxPath: number[]): FolderNode {
  let level = folderTree;
  let node: FolderNode = folderTree[0];
  for (const i of idxPath) {
    node = level[i];
    level = node.children ?? [];
  }
  return node;
}

const keyOf = (idxPath: number[]) => idxPath.join(".");

// Drill-down explorer of the real Design Hub folder tree (The Pond /
// Kontainer): click into a folder to see what's inside it, use the
// breadcrumb to step back out, or search across every folder at every depth.
export function FolderExplorer() {
  const [query, setQuery] = useState("");
  const [navPath, setNavPath] = useState<number[]>([0]); // start inside the root ("Design Hub 2.0")
  const [highlightKey, setHighlightKey] = useState<string | null>(null);

  const flat = useMemo(() => flatten(folderTree), []);
  const currentNode = useMemo(() => nodeAt(navPath), [navPath]);
  const breadcrumb = useMemo(
    () => navPath.map((_, i) => nodeAt(navPath.slice(0, i + 1))),
    [navPath],
  );

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

  const enter = (idxPath: number[]) => {
    setNavPath(idxPath);
    setHighlightKey(null);
    setQuery("");
  };

  const openResult = (entry: FlatEntry) => {
    const hasChildren = !!entry.node.children?.length;
    if (hasChildren) {
      // step inside the folder itself
      setNavPath(entry.idxPath);
      setHighlightKey(null);
    } else {
      // it's a file — land in its parent folder and point it out
      setNavPath(entry.idxPath.slice(0, -1));
      setHighlightKey(keyOf(entry.idxPath));
    }
    setQuery("");
  };

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-slate-100 p-4">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          🗂️ Search a folder
        </h2>
        <div className="relative mt-2">
          <input
            className="input"
            placeholder="Type a name… e.g. “LARVIVA”, “brand guidelines”, “roll-up”"
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
              <p className="px-1 py-2 text-sm text-slate-400">No results for “{query}”.</p>
            )}
            {results.map((r) => (
              <button
                key={keyOf(r.idxPath)}
                onClick={() => openResult(r)}
                className="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-biomar-ice/50"
              >
                <span className="font-semibold text-biomar-navy">
                  {r.node.children?.length ? "📁" : "📄"} {r.node.name}
                </span>
                <span className="block truncate text-xs text-slate-400">
                  {r.names.slice(0, -1).join(" › ") || "root"}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {!query && (
        <div>
          {/* breadcrumb */}
          <div className="flex flex-wrap items-center gap-1 border-b border-slate-100 bg-slate-50 px-4 py-2 text-xs">
            {breadcrumb.map((n, i) => {
              const isLast = i === breadcrumb.length - 1;
              return (
                <span key={i} className="flex items-center gap-1">
                  <button
                    onClick={() => enter(navPath.slice(0, i + 1))}
                    disabled={isLast}
                    className={
                      isLast
                        ? "font-semibold text-biomar-navy"
                        : "text-slate-500 hover:text-biomar-swoosh hover:underline"
                    }
                  >
                    {n.name}
                  </button>
                  {!isLast && <span className="text-slate-300">›</span>}
                </span>
              );
            })}
            {navPath.length > 1 && (
              <button
                onClick={() => enter(navPath.slice(0, -1))}
                className="btn-ghost ml-auto px-2 py-1 text-[11px]"
              >
                ← Up one level
              </button>
            )}
          </div>

          {currentNode.note && (
            <p className="border-b border-slate-100 bg-biomar-ice/30 px-4 py-2 text-xs text-slate-500">
              {currentNode.note}
            </p>
          )}

          {/* contents of the current folder */}
          <div className="max-h-[28rem] overflow-y-auto p-2">
            {(currentNode.children ?? []).length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-slate-400">
                This folder has nothing inside it on the map.
              </p>
            ) : (
              <ul className="space-y-0.5">
                {currentNode.children!.map((n, i) => {
                  const idxPath = [...navPath, i];
                  const key = keyOf(idxPath);
                  const hasChildren = !!n.children?.length;
                  const isHighlighted = highlightKey === key;
                  return (
                    <li key={key}>
                      <button
                        onClick={() => hasChildren && enter(idxPath)}
                        className={`flex w-full items-start gap-2 rounded-lg px-3 py-2 text-left transition ${
                          isHighlighted
                            ? "bg-biomar-swoosh/15 ring-1 ring-biomar-swoosh/40"
                            : hasChildren
                              ? "hover:bg-biomar-ice/50"
                              : "cursor-default"
                        }`}
                      >
                        <span className="mt-0.5 shrink-0">{hasChildren ? "📁" : "📄"}</span>
                        <span className="min-w-0 flex-1">
                          <span className="block text-sm text-biomar-navy">{n.name}</span>
                          {n.note && (
                            <span className="block text-xs text-slate-400">{n.note}</span>
                          )}
                        </span>
                        {hasChildren && (
                          <span className="shrink-0 text-xs text-slate-300">
                            {n.children!.length} ›
                          </span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
