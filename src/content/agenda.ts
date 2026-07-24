import type { AgendaPhase } from "./types";

// The recommended onboarding journey. The employee view walks phases top to
// bottom; a phase's modules are only the ones actually assigned to that person.
export const agenda: AgendaPhase[] = [
  {
    id: "phase-1",
    title: "Foundations",
    timeframe: "Week 1 · Days 1–3",
    description:
      "Understand the company, where Global Marketing sits, and what the Design Hub is for before touching any tool.",
    moduleIds: ["what-is-biomar", "global-marketing", "what-is-design-hub"],
    milestones: [
      "Get accesses via Loop Link",
      "Meet your immediate Design Hub team",
    ],
  },
  {
    id: "phase-2",
    title: "The Process",
    timeframe: "Week 1–2",
    description:
      "Learn the backbone every request flows through: brief, board, files, versioning, review and closeout.",
    moduleIds: [
      "process-overview",
      "the-brief",
      "email-tags-folders",
      "task-manager",
      "files-naming",
      "versioning-review",
      "export-close",
    ],
    milestones: ["Shadow a live task end-to-end"],
  },
  {
    id: "phase-3",
    title: "Brand & Guidelines",
    timeframe: "Week 2",
    description:
      "Internalize the visual system you protect and the practical production rules.",
    moduleIds: ["brand-guidelines", "material-guide"],
    milestones: ["Find the Brand Guidelines on The Pond"],
  },
  {
    id: "phase-4",
    title: "Tools & Ways of Working",
    timeframe: "Week 2–3",
    description: "Get fluent in the platforms and the communication rhythms.",
    moduleIds: ["platforms", "communication"],
    milestones: ["Confirm access to every core platform"],
  },
  {
    id: "phase-5",
    title: "People & Integration",
    timeframe: "Week 3–4",
    description:
      "Learn who owns what and start meeting the marketing managers.",
    moduleIds: ["stakeholder-map", "meet-managers"],
    milestones: [
      "Meet the first two marketing managers",
      "Save the stakeholder map somewhere you'll actually use it",
    ],
  },
  {
    id: "phase-6",
    title: "First Tasks",
    timeframe: "Week 4+",
    description:
      "Take your first real, low-risk tasks with support, then widen scope.",
    moduleIds: [],
    milestones: [
      "Complete a first small task end-to-end",
      "Run one full review round with a requester",
    ],
  },
];
