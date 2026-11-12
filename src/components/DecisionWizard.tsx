import { useState } from "react";
import { folderWizard } from "../content/folderWizard";
import { KIND_STYLE, examplePaths, resolveNames, type BranchKind } from "../content/folderMeta";

// What each wizard step adds to the path being built.
const PIECE: Record<string, { label: string; kind: BranchKind }> = {
  "enter-product-folder": { label: "Product folder · e.g. 2. LARVIVA", kind: "product" },
  "enter-subproduct-folder": { label: "Sub-product folder · e.g. 0. FISH", kind: "product" },
  "create-subfolder": { label: "New sub-product folder", kind: "product" },
  "enter-category-folder": { label: "Category folder · e.g. Adverts", kind: "product" },
  "create-category-folder": { label: "New category folder · e.g. Ads", kind: "product" },
  "create-project-folder": { label: "Project folder · 2026-07 EN_INICIO Plus Ad-A4", kind: "product" },
  "choose-specific-folder": { label: "Market, Digital Hub, Corporate, Global…", kind: "market" },
  "enter-design-assets": { label: "0. Design Assets", kind: "assets" },
};

// A real path to show once the wizard reaches its answer.
const EXAMPLE_FOR: Record<string, number> = {
  "enter-category-folder": 0,
  "create-category-folder": 0,
  "create-project-folder": 0,
  "choose-specific-folder": 1,
  "enter-design-assets": 3,
};

// Step-through "Where does this go?" wizard. Walks the WizardFlow one step at
// a time, keeping a breadcrumb trail so the user can go back or restart.
export function DecisionWizard({ onShow }: { onShow?: (idxPath: number[]) => void }) {
  const [path, setPath] = useState<string[]>([folderWizard.start]);
  const current = path[path.length - 1];
  const step = folderWizard.nodes[current];

  const go = (nextId: string) => setPath((p) => [...p, nextId]);
  const back = () => setPath((p) => (p.length > 1 ? p.slice(0, -1) : p));
  const restart = () => setPath([folderWizard.start]);

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          Where does this go?
        </h2>
        {path.length > 1 && (
          <button className="text-xs text-slate-400 hover:text-biomar-swoosh" onClick={restart}>
            ↺ Start over
          </button>
        )}
      </div>

      {/* breadcrumb of answers so far */}
      {path.length > 1 && (
        <ol className="mt-3 flex flex-wrap items-center gap-1 text-xs text-slate-400">
          {path.slice(0, -1).map((id, i) => (
            <li key={i} className="flex items-center gap-1">
              <span className="max-w-[16rem] truncate">{folderWizard.nodes[id].prompt}</span>
              <span className="text-slate-300">→</span>
            </li>
          ))}
        </ol>
      )}

      <div className="mt-4">
        {step.type === "question" ? (
          <QuestionStep prompt={step.prompt} onYes={() => go(step.yes!)} onNo={() => go(step.no!)} />
        ) : (
          <ActionStep
            prompt={step.prompt}
            options={step.options}
            isFinal={!!step.final}
            onContinue={step.next ? () => go(step.next!) : undefined}
            onRestart={step.restart ? restart : undefined}
          />
        )}
      </div>

      <PathSoFar path={path} onShow={onShow} />

      {path.length > 1 && (
        <button className="btn-ghost mt-4 text-xs" onClick={back}>
          ← Back
        </button>
      )}
    </section>
  );
}

function QuestionStep({
  prompt,
  onYes,
  onNo,
}: {
  prompt: string;
  onYes: () => void;
  onNo: () => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-center">
      <p className="text-base font-semibold text-biomar-navy">{prompt}</p>
      <div className="mt-4 flex justify-center gap-3">
        <button className="btn-primary min-w-24" onClick={onYes}>
          Yes
        </button>
        <button className="btn-ghost min-w-24" onClick={onNo}>
          No
        </button>
      </div>
    </div>
  );
}

function ActionStep({
  prompt,
  options,
  isFinal,
  onContinue,
  onRestart,
}: {
  prompt: string;
  options?: string[];
  isFinal: boolean;
  onContinue?: () => void;
  onRestart?: () => void;
}) {
  return (
    <div
      className={`rounded-xl border p-5 text-center ${
        isFinal
          ? "border-biomar-green/40 bg-biomar-green/10"
          : "border-biomar-swoosh/40 bg-biomar-ice/40"
      }`}
    >
      {isFinal && (
        <p className="mb-1 text-xs font-bold uppercase tracking-widest text-biomar-green">
          📁 That's the spot
        </p>
      )}
      <p className="text-base font-semibold text-biomar-navy">{prompt}</p>

      {options && (
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {options.map((o) => (
            <span key={o} className="chip bg-white text-biomar-navy ring-1 ring-slate-200">
              {o}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 flex justify-center gap-3">
        {onContinue && (
          <button className="btn-primary" onClick={onContinue}>
            Got it, continue →
          </button>
        )}
        {onRestart && (
          <button className="btn-primary" onClick={onRestart}>
            Start over
          </button>
        )}
      </div>
    </div>
  );
}

// The folder path taking shape as you answer, plus a real example at the end.
function PathSoFar({ path, onShow }: { path: string[]; onShow?: (idxPath: number[]) => void }) {
  const pieces = path.filter((id) => PIECE[id]);
  if (pieces.length === 0) return null;
  const last = path[path.length - 1];
  const exIndex = EXAMPLE_FOR[last];
  const example = exIndex === undefined ? null : examplePaths[exIndex];
  const idx = example ? resolveNames(example.segments.map((s) => s.name)) : null;

  return (
    <div className="mt-5 rounded-xl border border-slate-100 bg-slate-50/70 p-4">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Your path so far</p>
      <ol className="mt-2 flex flex-wrap items-center gap-1">
        <li className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">Design Hub 2.0</li>
        {pieces.map((id) => {
          const st = KIND_STYLE[PIECE[id].kind];
          return (
            <li key={id} className="flex items-center gap-1">
              <span className="text-slate-300">›</span>
              <span className={`rounded-md px-2 py-1 text-xs font-semibold ${st.soft} ${st.text}`}>
                {PIECE[id].label}
              </span>
            </li>
          );
        })}
      </ol>
      {example && (
        <p className="mt-3 text-xs text-slate-500">
          A real one: <strong className="text-biomar-navy">{example.segments.map((s) => s.name).join(" › ")}</strong>{" "}
          ({example.title.toLowerCase()})
          {idx && onShow && (
            <button className="ml-2 font-semibold text-biomar-swoosh hover:underline" onClick={() => onShow(idx)}>
              Show in tree →
            </button>
          )}
        </p>
      )}
    </div>
  );
}
