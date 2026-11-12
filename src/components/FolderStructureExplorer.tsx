import { useState } from "react";
import { FolderExplorer } from "./FolderExplorer";
import { DecisionWizard } from "./DecisionWizard";
import { FolderGuide } from "./FolderGuide";
import { FolderTree } from "./FolderTree";

type Tab = "guide" | "tree" | "wizard" | "search";

// Several ways of learning the Design Hub's real folder structure, from
// "understand the logic" to "find a specific folder". Rendered in place of a
// module's plain sections (see ModuleView, same pattern as ToolsMap).
export function FolderStructureExplorer() {
  const [tab, setTab] = useState<Tab>("guide");
  const [focus, setFocus] = useState<number[] | null>(null);

  // jump to a folder in the tree from any other view
  const showInTree = (idxPath: number[]) => {
    setFocus([...idxPath]);
    setTab("tree");
  };

  return (
    <div className="space-y-4">
      <p className="rounded-xl border-l-4 border-biomar-swoosh bg-biomar-ice/50 px-4 py-3 text-sm text-biomar-navy">
        🗺️ This is the real folder tree of the Design Hub's shared drive. Start with{" "}
        <strong>How it works</strong> to understand the logic, then use the tree to look around, or the wizard when you
        have something to save.
      </p>

      <div className="flex flex-wrap items-center gap-1 rounded-xl bg-white p-1 shadow-card ring-1 ring-slate-100">
        <TabButton active={tab === "guide"} onClick={() => setTab("guide")}>
          🧩 How it works
        </TabButton>
        <TabButton active={tab === "tree"} onClick={() => setTab("tree")}>
          🌳 Tree
        </TabButton>
        <TabButton active={tab === "wizard"} onClick={() => setTab("wizard")}>
          🧭 Where does this go?
        </TabButton>
        <TabButton active={tab === "search"} onClick={() => setTab("search")}>
          🔎 Search &amp; browse
        </TabButton>
      </div>

      {tab === "guide" && (
        <FolderGuide onShow={showInTree} onTab={(t) => setTab(t)} />
      )}
      {tab === "tree" && <FolderTree focus={focus} />}
      {tab === "wizard" && <DecisionWizard onShow={showInTree} />}
      {tab === "search" && <FolderExplorer />}
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
