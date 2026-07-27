import { toolGroups } from "../content/tools";

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
        <span className="font-semibold">Loop Link</span> and the tool owner.
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
                {group.tools.map((tool) => (
                  <div
                    key={tool.name}
                    className="flex items-start gap-3 px-4 py-2.5"
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
                      </div>
                      <div className="text-xs leading-snug text-slate-500">
                        {tool.purpose}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
