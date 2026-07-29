import { useMemo } from "react";
import type { ModuleMaterial, ModuleResource } from "../content/types";

// Shows a module's own slice of its source document — exactly as the
// original file, nothing edited. PDFs render natively in the browser (works
// everywhere). PPTX files render via Microsoft's Office Online viewer, which
// needs a public URL it can fetch — so on localhost we show an open/download
// link instead.
export function DeckViewer({
  material,
  resources,
}: {
  material?: ModuleMaterial;
  resources?: ModuleResource[];
}) {
  const isLocalhost =
    typeof window !== "undefined" &&
    /^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(window.location.hostname);

  const fileUrl = useMemo(() => {
    if (!material || typeof window === "undefined") return "";
    return new URL(material.file, window.location.origin).toString();
  }, [material]);

  if (!material && (!resources || resources.length === 0)) return null;

  const embedUrl = material
    ? `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`
    : "";

  return (
    <section className="card overflow-hidden">
      {material && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 px-4 py-3">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
              {material.type === "pdf" ? "📄 Material" : "📊 Material"}
            </h2>
            <span className="chip bg-biomar-ice text-biomar-blue">
              {material.range}
            </span>
          </div>

          {material.type === "pdf" ? (
            <iframe
              key={material.file}
              title="Material"
              src={`${material.file}#view=FitH`}
              className="h-[80vh] w-full border-0 bg-slate-100"
            />
          ) : isLocalhost ? (
            <div className="m-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
              The embedded PowerPoint viewer only works on the deployed site
              (it needs a public URL it can reach).
              <div className="mt-3">
                <a className="btn-accent" href={material.file} target="_blank" rel="noreferrer">
                  Open material
                </a>
              </div>
            </div>
          ) : (
            <div className="bg-slate-100">
              <div className="relative w-full" style={{ aspectRatio: "16 / 9" }}>
                <iframe
                  key={fileUrl}
                  title="Material"
                  src={embedUrl}
                  className="absolute inset-0 h-full w-full"
                  frameBorder={0}
                  allowFullScreen
                />
              </div>
            </div>
          )}

          <div className="flex items-center justify-between gap-2 px-4 py-2 text-xs text-slate-400">
            <span>Shown exactly as the original document.</span>
            <a
              className="font-semibold text-biomar-swoosh hover:underline"
              href={material.file}
              target="_blank"
              rel="noreferrer"
            >
              Open / download ↗
            </a>
          </div>
        </>
      )}

      {resources && resources.length > 0 && (
        <div
          className={`flex flex-wrap gap-2 px-4 py-3 ${material ? "border-t border-slate-100" : ""}`}
        >
          {resources.map((r) => (
            <a
              key={r.file}
              href={r.file}
              target="_blank"
              rel="noreferrer"
              className="btn-ghost text-xs"
            >
              📎 {r.title} — download
            </a>
          ))}
        </div>
      )}
    </section>
  );
}
