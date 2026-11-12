import { useMemo, useState } from "react";
import {
  KIND_LABEL,
  KIND_STYLE,
  cellMatches,
  keyOf,
  matrixColumns,
  matrixRows,
  type BranchKind,
  type FlatEntry,
} from "../content/folderMeta";

// The two ideas behind the drive in one picture: rows say WHERE something
// belongs (a product, a market, the Digital Hub) and columns say WHAT it is
// (adverts, brochures, videos…). A dot means that folder exists there.
export function FolderMatrix({ onShow }: { onShow: (idxPath: number[]) => void }) {
  const [sel, setSel] = useState<{ row: number; col: string } | null>(null);

  const cells = useMemo(
    () =>
      matrixRows.map((r) =>
        Object.fromEntries(matrixColumns.map((c) => [c.key, cellMatches(r.idxPath, c.aliases)])),
      ) as Record<string, FlatEntry[]>[],
    [],
  );

  const groups: BranchKind[] = ["product", "market", "digital"];
  const selMatches = sel ? cells[sel.row][sel.col] : [];
  const selCol = sel ? matrixColumns.find((c) => c.key === sel.col) : null;

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-slate-100 p-4">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          🔲 Where × what
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Pick the <strong>row</strong> for where it belongs and the <strong>column</strong> for what it is.
          A dot means that folder exists there — click it to see the exact path. The same column names repeat
          in every row, so once you've learned one branch you know them all.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] border-collapse text-sm">
          <thead>
            <tr>
              <th className="sticky left-0 z-10 w-52 bg-white px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                Where ↓ / What →
              </th>
              {matrixColumns.map((c) => (
                <th
                  key={c.key}
                  title={c.hint}
                  className="px-1 py-2 text-center align-bottom text-[11px] font-semibold leading-tight text-biomar-navy"
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {groups.map((g) => {
              const rows = matrixRows.map((r, i) => ({ r, i })).filter((x) => x.r.kind === g);
              if (rows.length === 0) return null;
              return (
                <GroupRows
                  key={g}
                  kind={g}
                  rows={rows}
                  cells={cells}
                  sel={sel}
                  onSelect={setSel}
                  onShow={onShow}
                />
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="border-t border-slate-100 bg-slate-50/60 p-4 text-sm">
        {!sel ? (
          <p className="text-slate-400">Click a dot to see where that folder lives.</p>
        ) : (
          <div>
            <p className="font-semibold text-biomar-navy">
              {matrixRows[sel.row].name} · {selCol?.label}
              <span className="ml-2 font-normal text-slate-400">
                {selMatches.length} {selMatches.length === 1 ? "folder" : "folders"}
              </span>
            </p>
            <ul className="mt-2 space-y-1">
              {selMatches.slice(0, 12).map((m) => (
                <li key={keyOf(m.idxPath)} className="flex flex-wrap items-center gap-2">
                  <span className="min-w-0 break-words text-xs text-slate-500">
                    {m.names.slice(1).join(" › ")}
                  </span>
                  <button
                    className="shrink-0 text-xs font-semibold text-biomar-swoosh hover:underline"
                    onClick={() => onShow(m.idxPath)}
                  >
                    Show in tree →
                  </button>
                </li>
              ))}
              {selMatches.length > 12 && (
                <li className="text-xs text-slate-400">…and {selMatches.length - 12} more.</li>
              )}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}

function GroupRows({
  kind,
  rows,
  cells,
  sel,
  onSelect,
  onShow,
}: {
  kind: BranchKind;
  rows: { r: (typeof matrixRows)[number]; i: number }[];
  cells: Record<string, FlatEntry[]>[];
  sel: { row: number; col: string } | null;
  onSelect: (s: { row: number; col: string } | null) => void;
  onShow: (idxPath: number[]) => void;
}) {
  const st = KIND_STYLE[kind];
  return (
    <>
      <tr>
        <td colSpan={matrixColumns.length + 1} className={`px-3 py-1.5 text-[11px] font-bold uppercase tracking-widest ${st.text} ${st.soft}`}>
          {KIND_LABEL[kind]}
        </td>
      </tr>
      {rows.map(({ r, i }) => (
        <tr key={r.name} className="border-b border-slate-50 hover:bg-slate-50/60">
          <th className="sticky left-0 z-10 bg-white px-3 py-1.5 text-left text-sm font-medium text-biomar-navy">
            <button className="text-left hover:text-biomar-swoosh hover:underline" onClick={() => onShow(r.idxPath)}>
              {r.name}
            </button>
          </th>
          {matrixColumns.map((c) => {
            const n = cells[i][c.key].length;
            const active = sel?.row === i && sel.col === c.key;
            return (
              <td key={c.key} className="px-1 py-1 text-center">
                {n > 0 ? (
                  <button
                    onClick={() => onSelect(active ? null : { row: i, col: c.key })}
                    aria-label={`${r.name}: ${c.label} (${n})`}
                    className={`mx-auto grid h-7 w-7 place-items-center rounded-full text-[11px] font-bold text-white transition ${st.dot} ${
                      active ? `ring-4 ${st.ring} scale-110` : "opacity-80 hover:opacity-100"
                    }`}
                  >
                    {n > 1 ? n : ""}
                  </button>
                ) : (
                  <span className="text-slate-200">·</span>
                )}
              </td>
            );
          })}
        </tr>
      ))}
    </>
  );
}
