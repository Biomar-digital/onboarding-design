import { useMemo, useState } from "react";
import { decks, moduleMaterials } from "../content/materials";

// Shows a module's presentation material exactly as the original PowerPoint,
// using Microsoft's Office Online viewer against the self-hosted .pptx files.
//
// The viewer requires the deck to be reachable at a public URL — that's the
// deployed Cloudflare site. On localhost it can't render (Microsoft can't fetch
// localhost), so we show a helpful note and a direct open/download link there.
export function DeckViewer({ moduleId }: { moduleId: string }) {
  const materials = moduleMaterials[moduleId] ?? [];
  const [active, setActive] = useState(0);

  if (materials.length === 0) return null;

  const isLocalhost =
    typeof window !== "undefined" &&
    /^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(window.location.hostname);

  const current = materials[active];
  const deck = decks[current.deckId];
  const fileUrl = useMemo(() => {
    if (typeof window === "undefined") return "";
    return new URL(deck.file, window.location.origin).toString();
  }, [deck.file]);

  const embedUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(
    fileUrl,
  )}`;

  return (
    <section className="card overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 px-4 py-3">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          📊 Material
        </h2>
        {materials.length > 1 && (
          <div className="flex flex-wrap gap-1">
            {materials.map((m, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={`chip transition ${
                  i === active
                    ? "bg-biomar-navy text-white"
                    : "bg-slate-100 text-slate-500 hover:bg-slate-200"
                }`}
              >
                {decks[m.deckId].title.split("—")[0].trim()}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between gap-2 px-4 py-2 text-xs">
        <span className="font-semibold text-biomar-navy">{deck.title}</span>
        {current.slides && (
          <span className="chip bg-biomar-ice text-biomar-blue">
            {current.slides}
          </span>
        )}
      </div>

      {isLocalhost ? (
        <div className="m-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
          The embedded PowerPoint viewer only works on the deployed site (the
          viewer needs a public URL it can reach).
          <div className="mt-3">
            <a
              className="btn-accent"
              href={deck.file}
              target="_blank"
              rel="noreferrer"
            >
              Open “{deck.title}”
            </a>
          </div>
        </div>
      ) : (
        <div className="bg-slate-100">
          <div className="relative w-full" style={{ aspectRatio: "16 / 9" }}>
            <iframe
              key={fileUrl}
              title={deck.title}
              src={embedUrl}
              className="absolute inset-0 h-full w-full"
              frameBorder={0}
              allowFullScreen
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between gap-2 px-4 py-2 text-xs text-slate-400">
        <span>Shown exactly as the original PowerPoint.</span>
        <a
          className="font-semibold text-biomar-swoosh hover:underline"
          href={deck.file}
          target="_blank"
          rel="noreferrer"
        >
          Open / download ↗
        </a>
      </div>
    </section>
  );
}
