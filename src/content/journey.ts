import { chapters, chaptersById } from "./chapters";
import { modules } from "./modules";

// The didactic order of the whole onboarding, in one place. Everything that
// lists, groups, schedules or sorts modules reads from here.
//
//   Welcome → why the Hub exists → access & where things live → brand rules
//   (used in every piece from week one) → how work flows (Hub 2026, Playbook)
//   → wider marketing organisation → reference.
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

const chapterKeys = chapters.map((c) => c.id);
const [first, ...rest] = chapterKeys; // strategic first, then the setup block

export const journey: JourneySection[] = [
  {
    key: "welcome",
    icon: "👋",
    title: "Welcome",
    highlight: true,
    moduleIds: ["welcome"],
  },
  chapterSection(first),
  {
    key: "setup",
    icon: "🧰",
    title: "Set up: tools & where things live",
    description:
      "Get your access and learn where everything is stored before your first task.",
    moduleIds: SETUP_IDS,
  },
  ...rest.map(chapterSection),
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
