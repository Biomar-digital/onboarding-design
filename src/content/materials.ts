// ─────────────────────────────────────────────────────────────────────────────
// Presentation materials.
//
// The original decks live in /public/materials and deploy as static assets, so
// each has a public URL on the Cloudflare site. They are shown *exactly* as the
// original PowerPoint via an embedded viewer (see components/DeckViewer.tsx),
// mapped here to the module they belong to.
// ─────────────────────────────────────────────────────────────────────────────

export interface Deck {
  id: string;
  title: string;
  /** Path under the site root (served from /public/materials). */
  file: string;
  slides: number;
}

export const decks: Record<string, Deck> = {
  playbook: {
    id: "playbook",
    title: "Design Hub Playbook",
    file: "/materials/design-hub-playbook.pptx",
    slides: 27,
  },
  strategic: {
    id: "strategic",
    title: "Design Hub 2026 — Strategic Presentation",
    file: "/materials/design-hub-strategic-2026.pptx",
    slides: 17,
  },
  global: {
    id: "global",
    title: "Global and Group Marketing",
    file: "/materials/global-and-group-marketing.pptx",
    slides: 18,
  },
  brief: {
    id: "brief",
    title: "Design Hub — Brief Template",
    file: "/materials/design-hub-brief-template.potx",
    slides: 1,
  },
};

export interface ModuleMaterial {
  deckId: keyof typeof decks;
  /** Human label of the slides relevant to this module (viewer shows full deck). */
  slides?: string;
}

// Which deck(s) back each module, and the slides worth focusing on.
export const moduleMaterials: Record<string, ModuleMaterial[]> = {
  // Foundations
  "what-is-biomar": [{ deckId: "strategic", slides: "Slide 4 — 2028 strategy house" }],
  "global-marketing": [{ deckId: "global", slides: "Slides 2–6, 15–16" }],
  "what-is-design-hub": [
    { deckId: "strategic", slides: "Slides 2–8, 11, 16" },
  ],
  // Process
  "process-overview": [
    { deckId: "playbook", slides: "Slide 3 — overall process" },
    { deckId: "strategic", slides: "Slides 9–10 — process & workflows" },
  ],
  "the-brief": [
    { deckId: "playbook", slides: "Slides 4–5" },
    { deckId: "brief", slides: "Brief template" },
  ],
  "email-tags-folders": [{ deckId: "playbook", slides: "Slide 6" }],
  "task-manager": [{ deckId: "playbook", slides: "Slides 7–12" }],
  "files-naming": [{ deckId: "playbook", slides: "Slides 13–17" }],
  "versioning-review": [{ deckId: "playbook", slides: "Slides 18–21" }],
  "export-close": [{ deckId: "playbook", slides: "Slides 22–24" }],
  // Brand
  "brand-guidelines": [{ deckId: "strategic", slides: "Slides 12–14" }],
  "material-guide": [{ deckId: "strategic", slides: "Slide 13 — additional guidelines" }],
  // Tools
  communication: [
    { deckId: "playbook", slides: "Slide 27 — ways of communicating" },
    { deckId: "strategic", slides: "Slide 15 — ways of working" },
    { deckId: "global", slides: "Slides 13–14 — channels" },
  ],
  // People
  "stakeholder-map": [
    { deckId: "playbook", slides: "Slides 25–26 — who's in charge" },
    { deckId: "global", slides: "Slides 7–9 — stakeholders" },
  ],
  "meet-managers": [{ deckId: "global", slides: "Slides 10–12 — meetings" }],
};
