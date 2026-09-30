import { useState } from "react";
import { FolderExplorer } from "./FolderExplorer";
import { DecisionWizard } from "./DecisionWizard";

// Combines the two ways of learning the Design Hub's real folder structure:
// browsing/searching the actual tree, or walking the "where does this go?"
// decision wizard. Rendered in place of a module's plain sections (see
// ModuleView, same pattern as ToolsMap for the "tools-map" module).
export function FolderStructureExplorer() {
  const [tab, setTab] = useState<"wizard" | "explore">("wizard");

  return (
    <div className="space-y-4">
      <p className="rounded-xl border-l-4 border-biomar-swoosh bg-biomar-ice/50 px-4 py-3 text-sm text-biomar-navy">
        🗺️ This is the real folder tree of the Design Hub's shared drive, as
        it stands today. Use the wizard when you have something new to save and aren't
        sure where it goes, or explore/search directly if you already know
        what you're looking for.
      </p>

      <div className="inline-flex items-center gap-1 rounded-xl bg-white p-1 shadow-card ring-1 ring-slate-100">
        <TabButton active={tab === "wizard"} onClick={() => setTab("wizard")}>
          🧭 Where does this go?
        </TabButton>
        <TabButton active={tab === "explore"} onClick={() => setTab("explore")}>
          🗂️ Explore / search
        </TabButton>
      </div>

      {tab === "wizard" ? <DecisionWizard /> : <FolderExplorer />}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition ${
        active ? "bg-biomar-navy text-white" : "text-slate-500 hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
  );
}
