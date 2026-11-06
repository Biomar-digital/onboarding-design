import { chaptersById } from "./chapters";
import { modules } from "./modules";

// The didactic order of the whole onboarding, in one place. Everything that
// lists, groups, schedules or sorts modules reads from here.
//
//   Welcome → Strategic (why the Hub exists) → Design Hub 2026 (how it works)
//   → Brand Guidelines → Global & Group Marketing → set-up (tools & drive)
//   → Playbook → reference.
export interface JourneySection {
  key: string;
  icon: string;
  title: string;
  description?: string;
  /** Source document name, for chapter sections. */
  source?: string;
  /** Welcome gets the highlighted treatment. */
  highlight?: boolean;
  moduleIds: string[];
}

const chapterSection = (id: string): JourneySection => {
  const c = chaptersById[id];
  return {
    key: c.id,
    icon: c.icon,
    title: c.title,
    description: c.description,
    source: c.source,
    moduleIds: modules.filter((m) => m.chapterId === c.id).map((m) => m.id),
  };
};

const SETUP_IDS = ["tools-map", "folder-structure"];

export const journey: JourneySection[] = [
  {
    key: "welcome",
    icon: "👋",
    title: "Welcome",
    highlight: true,
    moduleIds: ["welcome"],
  },
  chapterSection("strategic"),
  chapterSection("dh2026"),
  chapterSection("brand-guidelines"),
  chapterSection("global"),
  {
    key: "setup",
    icon: "🧰",
    title: "Set up: tools & where things live",
    description:
      "Get your access and learn where everything is stored before your first task.",
    moduleIds: SETUP_IDS,
  },
  chapterSection("playbook"),
  {
    key: "reference",
    icon: "📎",
    title: "Reference material",
    description: "Not tied to a single document — always here to check back on.",
    moduleIds: modules
      .filter(
        (m) =>
          m.chapterId === null &&
          m.id !== "welcome" &&
          !SETUP_IDS.includes(m.id),
      )
      .map((m) => m.id),
  },
].filter((s) => s.moduleIds.length > 0);

/** Every module id in learning order. */
export const journeyOrder: string[] = journey.flatMap((s) => s.moduleIds);
