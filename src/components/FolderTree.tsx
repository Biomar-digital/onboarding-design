import { useEffect, useMemo, useState } from "react";
import type { FolderNode } from "../content/types";
import { folderTree } from "../content/folderStructure";
import {
  KIND_STYLE,
  branchKind,
  countDescendants,
  flatTree,
  keyOf,
  nodeAtPath,
} from "../content/folderMeta";

// Expandable tree of the whole shared drive. Level buttons open it a layer at a
// time, the filter opens only the branches that contain a match, and the panel
// on the right says what the selected folder is and where it sits.
export function FolderTree({ focus }: { focus: number[] | null }) {
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(["0"]));
  const [selected, setSelected] = useState<number[]>([0]);
  const [filter, setFilter] = useState("");
  const [copied, setCopied] = useState(false);

  const q = filter.trim().toLowerCase();

  // keys to show while filtering: every match plus its ancestors
  const visible = useMemo(() => {
    if (!q) return null;
    const keys = new Set<string>();
    for (const e of flatTree) {
      if (e.node.name.toLowerCase().includes(q)) {
        for (let i = 1; i <= e.idxPath.length; i++) keys.add(keyOf(e.idxPath.slice(0, i)));
      }
    }
    return keys;
  }, [q]);

  const matchCount = useMemo(
    () => (q ? flatTree.filter((e) => e.node.name.toLowerCase().includes(q)).length : 0),
    [q],
  );

  // jump here from the guide or the wizard
  useEffect(() => {
    if (!focus) return;
    setFilter("");
    setExpanded((cur) => {
      const next = new Set(cur);
      for (let i = 1; i < focus.length; i++) next.add(keyOf(focus.slice(0, i)));
      return next;
    });
    setSelected(focus);
    const t = setTimeout(
      () =>
        document
          .getElementById(`tree-node-${keyOf(focus)}`)
          ?.scrollIntoView({ block: "center", behavior: "smooth" }),
      80,
    );
    return () => clearTimeout(t);
  }, [focus]);

  const expandToLevel = (level: number) => {
    const next = new Set<string>();
    for (const e of flatTree) {
      if (e.idxPath.length <= level && e.node.children?.length) next.add(keyOf(e.idxPath));
    }
    setExpanded(next);
    setFilter("");
  };

  const toggle = (key: string) =>
    setExpanded((cur) => {
      const next = new Set(cur);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  const selNode = nodeAtPath(selected);
  const selNames = selected.map((_, i) => nodeAtPath(selected.slice(0, i + 1)).name);

  const copyPath = async () => {
    try {
      await navigator.clipboard.writeText(selNames.join(" / "));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* selecting the breadcrumb text works as a fallback */
    }
  };

  return (
    <section className="card overflow-hidden">
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 p-3">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Open</span>
        {[1, 2, 3].map((l) => (
          <button key={l} className="btn-ghost px-3 py-1 text-xs" onClick={() => expandToLevel(l)}>
            {l === 1 ? "Main folders" : l === 2 ? "+ 2nd level" : "+ 3rd level"}
          </button>
        ))}
        <button
          className="btn-ghost px-3 py-1 text-xs"
          onClick={() => {
            setExpanded(new Set(["0"]));
            setFilter("");
          }}
        >
          Collapse
        </button>
        <div className="relative ml-auto w-full sm:w-64">
          <input
            className="input py-1.5 text-sm"
            placeholder="Filter folders…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          {q && (
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[11px] text-slate-400">
              {matchCount} found
            </span>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_320px]">
        <div className="max-h-[34rem] overflow-y-auto p-2">
          <ul>
            {folderTree.map((n, i) => (
              <TreeRow
                key={i}
                node={n}
                idxPath={[i]}
                expanded={expanded}
                visible={visible}
                selectedKey={keyOf(selected)}
                onToggle={toggle}
                onSelect={setSelected}
                forceOpen={!!q}
              />
            ))}
          </ul>
          {q && matchCount === 0 && (
            <p className="px-3 py-6 text-center text-sm text-slate-400">No folders match “{filter}”.</p>
          )}
        </div>

        <aside className="border-t border-slate-100 bg-slate-50/60 p-4 lg:border-l lg:border-t-0">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Selected folder</p>
          <h3 className="mt-1 text-base font-bold text-biomar-navy">{selNode.name}</h3>
          <p className="mt-1 break-words text-xs text-slate-400">{selNames.join(" › ")}</p>
          {selNode.note ? (
            <p className="mt-3 rounded-lg border-l-4 border-biomar-swoosh bg-white px-3 py-2 text-sm text-slate-600">
              {selNode.note}
            </p>
          ) : (
            <p className="mt-3 text-sm text-slate-400">No note for this folder.</p>
          )}
          <p className="mt-3 text-xs text-slate-500">
            {selNode.children?.length
              ? `${selNode.children.length} folders inside · ${countDescendants(selNode)} in total below it`
              : "Nothing inside it on the map."}
          </p>
          <button className="btn-ghost mt-3 px-3 py-1.5 text-xs" onClick={copyPath}>
            {copied ? "Path copied ✓" : "Copy path"}
          </button>
        </aside>
      </div>
    </section>
  );
}

function TreeRow({
  node,
  idxPath,
  expanded,
  visible,
  selectedKey,
  onToggle,
  onSelect,
  forceOpen,
}: {
  node: FolderNode;
  idxPath: number[];
  expanded: Set<string>;
  visible: Set<string> | null;
  selectedKey: string;
  onToggle: (key: string) => void;
  onSelect: (idxPath: number[]) => void;
  forceOpen: boolean;
}) {
  const key = keyOf(idxPath);
  if (visible && !visible.has(key)) return null;
  const hasChildren = !!node.children?.length;
  const open = hasChildren && (forceOpen || expanded.has(key));
  const isSelected = selectedKey === key;
  // top-level folders get a coloured bar to show which kind of branch they are
  const top = idxPath.length === 2 ? KIND_STYLE[branchKind(node.name)] : null;

  return (
    <li>
      <div
        id={`tree-node-${key}`}
        className={`flex items-center gap-1.5 rounded-lg py-1 pr-2 text-sm transition ${
          isSelected ? "bg-biomar-ice/80 ring-1 ring-biomar-swoosh/40" : "hover:bg-slate-50"
        } ${top ? `border-l-4 ${top.bar}` : ""}`}
        style={{ paddingLeft: 8 + (idxPath.length - 1) * 16 }}
      >
        <button
          className="grid h-5 w-5 shrink-0 place-items-center text-slate-400"
          onClick={() => hasChildren && onToggle(key)}
          aria-label={open ? "Collapse" : "Expand"}
          tabIndex={hasChildren ? 0 : -1}
        >
          {hasChildren ? (open ? "▾" : "▸") : ""}
        </button>
        <button
          className="flex min-w-0 flex-1 items-center gap-1.5 text-left"
          onClick={() => {
            onSelect(idxPath);
            if (hasChildren && !open) onToggle(key);
          }}
        >
          <span aria-hidden>{hasChildren ? (open ? "📂" : "📁") : "📄"}</span>
          <span className="truncate text-biomar-navy">{node.name}</span>
          {hasChildren && !open && (
            <span className="ml-auto shrink-0 text-[11px] text-slate-300">
              {countDescendants(node)}
            </span>
          )}
        </button>
      </div>
      {open && (
        <ul>
          {node.children!.map((c, i) => (
            <TreeRow
              key={i}
              node={c}
              idxPath={[...idxPath, i]}
              expanded={expanded}
              visible={visible}
              selectedKey={selectedKey}
              onToggle={onToggle}
              onSelect={onSelect}
              forceOpen={forceOpen}
            />
          ))}
        </ul>
      )}
    </li>
  );
}
