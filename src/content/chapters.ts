import type { Chapter } from "./types";

// Each chapter is exactly one source document. Order here is the order
// employees move through them. Within a chapter, modules.ts follows the
// document's own slide/page order end to end — nothing skipped, nothing
// reordered.
export const chapters: Chapter[] = [
  {
    id: "strategic",
    title: "Design Hub — Strategic Presentation",
    source: "Design Hub 2026 Strategic Presentation",
    icon: "🎯",
    description:
      "Who the Design Hub is, its strategic role and pillars, and how it has evolved.",
  },
  {
    id: "global",
    title: "Global & Group Marketing",
    source: "Global and Group Marketing",
    icon: "🌍",
    description:
      "The wider marketing organisation: team, stakeholders, meetings and the 2026 plan.",
  },
  {
    id: "dh2026",
    title: "Design Hub 2026",
    source: "Design Hub 2026",
    icon: "🧭",
    description:
      "How the Hub works day to day: reaching out, deadlines, tools and the end-to-end process.",
  },
  {
    id: "playbook",
    title: "Design Hub Playbook",
    source: "Design Hub Playbook",
    icon: "📘",
    description:
      "The extended reference: the brief, the task manager, files, versioning and closing tasks.",
  },
  {
    id: "brand-guidelines",
    title: "BioMar Brand Guidelines",
    source: "BioMar Brand Guidelines 2020",
    icon: "🎨",
    description:
      "The official visual identity: logo, typography, colour, shapes and photography.",
  },
];

export const chaptersById = Object.fromEntries(chapters.map((c) => [c.id, c]));
