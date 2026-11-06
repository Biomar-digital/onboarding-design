import { glossaryLookup, glossaryRegex } from "../content/glossary";

// Renders text with glossary terms underlined; hovering or focusing shows the
// definition. Each term is highlighted only the first time it appears on a
// page (tracked by the `seen` set the page passes in), so text stays calm.
export function GlossaryText({ text, seen }: { text: string; seen?: Set<string> }) {
  const parts: (string | { match: string; term: string; definition: string })[] = [];
  let last = 0;
  glossaryRegex.lastIndex = 0;
  for (let m = glossaryRegex.exec(text); m; m = glossaryRegex.exec(text)) {
    const entry = glossaryLookup.get(m[1]);
    if (!entry) continue;
    if (seen?.has(entry.term)) continue;
    seen?.add(entry.term);
    parts.push(text.slice(last, m.index));
    parts.push({ match: m[1], term: entry.term, definition: entry.definition });
    last = m.index + m[1].length;
  }
  if (parts.length === 0) return <>{text}</>;
  parts.push(text.slice(last));

  return (
    <>
      {parts.map((p, i) =>
        typeof p === "string" ? (
          p
        ) : (
          <span
            key={i}
            tabIndex={0}
            className="group relative cursor-help border-b border-dotted border-biomar-swoosh outline-none"
          >
            {p.match}
            <span
              role="tooltip"
              className="pointer-events-none invisible absolute left-0 top-full z-30 mt-1 w-64 rounded-lg bg-biomar-navy px-3 py-2 text-left text-xs font-normal leading-snug text-white shadow-lg group-hover:visible group-focus:visible"
            >
              <span className="mb-0.5 block font-semibold text-biomar-swoosh">{p.term}</span>
              {p.definition}
            </span>
          </span>
        ),
      )}
    </>
  );
}
