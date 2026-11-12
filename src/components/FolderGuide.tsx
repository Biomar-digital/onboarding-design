import {
  KIND_STYLE,
  examplePaths,
  branchRows,
  resolveNames,
  type BranchKind,
} from "../content/folderMeta";

// "How it works": the whole drive explained in one page for someone new —
// three questions decide the branch, the same pieces repeat inside it, and
// four real paths show the pattern.
export function FolderGuide({
  onShow,
  onTab,
}: {
  onShow: (idxPath: number[]) => void;
  onTab: (tab: "tree" | "wizard") => void;
}) {
  const products = branchRows.filter((r) => r.kind === "product");
  const markets = branchRows.filter((r) => r.kind === "market");

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h2 className="text-lg font-bold text-biomar-navy">The drive in one idea</h2>
        <p className="mt-2 text-[15px] leading-relaxed text-slate-700">
          The Design Hub drive has around 500 folders, but it follows one logic. First decide <strong>where</strong>{" "}
          something belongs (a product, a market, the Digital Hub or the shared assets); then say <strong>what it is</strong>{" "}
          (an advert, a brochure, a video…). The same “what” folders repeat in every “where”, so once you know one
          branch you know them all.
        </p>
      </section>

      <section>
        <h3 className="mb-2 px-1 text-xs font-bold uppercase tracking-widest text-slate-400">
          Step 1 — three questions decide the branch
        </h3>
        <div className="grid gap-3 md:grid-cols-3">
          <QuestionCard
            n={1}
            kind="product"
            question="Is it about a product?"
            answer="Go to that product's folder."
            chips={products.map((p) => p.name)}
          />
          <QuestionCard
            n={2}
            kind="market"
            question="Is it for a market, the Digital Hub, Corporate or Global?"
            answer="Go to that market's folder."
            chips={[...markets.map((m) => m.name), "00. Digital Hub (SoMe)"]}
            note="Sustainability and R&D have their own folders too."
          />
          <QuestionCard
            n={3}
            kind="assets"
            question="Is it an asset — a logo, photo, template or guideline?"
            answer="Go to Design Assets, the shared libraries."
            chips={["BioMar Logos", "Photo Library", "Video Library", "Icon Library", "BioMar Brand Guidelines"]}
          />
        </div>
      </section>

      <section className="card p-6">
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">
          Step 2 — inside the branch, the same pieces repeat
        </h3>
        <ol className="mt-4 grid gap-2 md:grid-cols-4">
          <Piece n="A" title="Product or market" example="2. LARVIVA · ASIA" text="The branch you picked." />
          <Piece n="B" title="Sub-product or country" example="0. FISH · China" text="If it exists. If not, create it." />
          <Piece n="C" title="Category" example="Adverts · Brochures · SoMe · Presentations" text="What kind of piece it is. Create it if missing." />
          <Piece n="D" title="Project folder" example="2026-07 EN_INICIO Plus Ad-A4" text="If it fits no category, make a folder named with the convention." />
        </ol>
        <p className="mt-4 rounded-lg bg-biomar-ice/50 px-3 py-2 text-xs text-biomar-navy">
          Naming convention: <strong>Year-Month Language_Market Brand/Product-FileType</strong> — see “File naming” in the
          side panel.
        </p>
      </section>

      <section>
        <h3 className="mb-2 px-1 text-xs font-bold uppercase tracking-widest text-slate-400">
          Step 3 — four real paths
        </h3>
        <div className="grid gap-3 md:grid-cols-2">
          {examplePaths.map((ex) => {
            const idx = resolveNames(ex.segments.map((s) => s.name));
            const st = KIND_STYLE[ex.kind];
            return (
              <article key={ex.title} className="card p-4">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold text-biomar-navy">{ex.title}</h4>
                  {idx && (
                    <button
                      className="shrink-0 text-xs font-semibold text-biomar-swoosh hover:underline"
                      onClick={() => onShow(idx)}
                    >
                      Show in tree →
                    </button>
                  )}
                </div>
                <ol className="mt-3 flex flex-wrap items-stretch gap-1">
                  {ex.segments.map((s, i) => (
                    <li key={i} className="flex items-center gap-1">
                      <span
                        className={`rounded-lg px-2 py-1 ${i === 0 ? "bg-slate-100 text-slate-600" : `${st.soft} ${st.text}`}`}
                      >
                        <span className="block text-[10px] font-semibold uppercase tracking-wide opacity-70">
                          {s.role}
                        </span>
                        <span className="block text-xs font-semibold">{s.name}</span>
                      </span>
                      {i < ex.segments.length - 1 && <span className="text-slate-300">›</span>}
                    </li>
                  ))}
                </ol>
              </article>
            );
          })}
        </div>
      </section>

      <section className="card flex flex-wrap items-center justify-between gap-3 p-5">
        <p className="text-sm text-slate-600">Ready to try it yourself?</p>
        <div className="flex flex-wrap gap-2">
          <button className="btn-primary px-4 py-2 text-sm" onClick={() => onTab("wizard")}>
            🧭 Where does this go?
          </button>
          <button className="btn-ghost px-4 py-2 text-sm" onClick={() => onTab("tree")}>
            🌳 Open the tree
          </button>
        </div>
      </section>
    </div>
  );
}

function QuestionCard({
  n,
  kind,
  question,
  answer,
  chips,
  note,
}: {
  n: number;
  kind: BranchKind;
  question: string;
  answer: string;
  chips: string[];
  note?: string;
}) {
  const st = KIND_STYLE[kind];
  return (
    <article className={`card border-t-4 p-4 ${st.bar}`}>
      <span className={`grid h-7 w-7 place-items-center rounded-full text-sm font-bold text-white ${st.dot}`}>{n}</span>
      <h4 className="mt-2 text-sm font-bold text-biomar-navy">{question}</h4>
      <p className="mt-1 text-sm text-slate-600">→ {answer}</p>
      <div className="mt-3 flex flex-wrap gap-1">
        {chips.map((c) => (
          <span key={c} className={`rounded-md px-2 py-0.5 text-[11px] font-medium ${st.soft} ${st.text}`}>
            {c}
          </span>
        ))}
      </div>
      {note && <p className="mt-2 text-xs text-slate-400">{note}</p>}
    </article>
  );
}

function Piece({ n, title, example, text }: { n: string; title: string; example: string; text: string }) {
  return (
    <li className="relative rounded-xl border border-slate-100 bg-slate-50/60 p-3">
      <span className="grid h-6 w-6 place-items-center rounded-full bg-biomar-navy text-xs font-bold text-white">{n}</span>
      <p className="mt-2 text-sm font-bold text-biomar-navy">{title}</p>
      <p className="mt-0.5 text-xs font-medium text-biomar-swoosh">{example}</p>
      <p className="mt-1 text-xs text-slate-500">{text}</p>
    </li>
  );
}
