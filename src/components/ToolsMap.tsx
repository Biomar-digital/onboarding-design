import { toolGroups, PLATFORMS_ACCESSES_URL } from "../content/tools";

// Visual, on-brand map of the Design Hub toolkit — a grid of category cards,
// each with its tools and a one-line purpose. No credentials (those live in
// Loop Link). Rendered for the "tools-map" module in place of a plain list.
const HEX: Record<string, string> = {
  "biomar-navy": "#1F3E77",
  "biomar-blue": "#16356E",
  "biomar-swoosh": "#0471AD",
  "biomar-green": "#97D130",
  "biomar-sand": "#EAB318",
  "biomar-orange": "#DD6928",
  "biomar-gray": "#575756",
};

export function ToolsMap() {
  return (
    <div className="space-y-4">
      <p className="rounded-xl border-l-4 border-biomar-swoosh bg-biomar-ice/50 px-4 py-3 text-sm text-biomar-navy">
        🔐 Logins & passwords are never stored here — request access through{" "}
        <a
          href={PLATFORMS_ACCESSES_URL}
          target="_blank"
          rel="noreferrer"
          className="font-semibold text-biomar-swoosh underline"
        >
          Loop Link — Platforms & Accesses ↗
        </a>{" "}
        and the tool owner.
        This map is only about <em>what each tool is for</em>.
      </p>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {toolGroups.map((group) => {
          const color = HEX[group.accent] ?? "#1F3E77";
          return (
            <section
              key={group.title}
              className="flex flex-col overflow-hidden rounded-2xl bg-white shadow-card ring-1 ring-slate-100"
            >
              <header
                className="flex items-center gap-2 px-4 py-2.5 text-white"
                style={{ backgroundColor: color }}
              >
                <span aria-hidden className="text-base">
                  {group.icon}
                </span>
                <h3 className="text-sm font-bold">{group.title}</h3>
              </header>
              <div className="flex-1 divide-y divide-slate-100">
                {group.tools.map((tool) => {
                  const Row = tool.url ? "a" : "div";
                  return (
                  <Row
                    key={tool.name}
                    {...(tool.url
                      ? { href: tool.url, target: "_blank", rel: "noreferrer" }
                      : {})}
                    className={`flex items-start gap-3 px-4 py-2.5 ${
                      tool.url ? "hover:bg-biomar-ice/40" : ""
                    }`}
                  >
                    <span
                      aria-hidden
                      className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-base"
                      style={{ backgroundColor: `${color}14` }}
                    >
                      {tool.icon}
                    </span>
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-biomar-navy">
                        {tool.name}
                        {tool.url && <span className="ml-1 text-biomar-swoosh">↗</span>}
                      </div>
                      <div className="text-xs leading-snug text-slate-500">
                        {tool.purpose}
                      </div>
                    </div>
                  </Row>
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
