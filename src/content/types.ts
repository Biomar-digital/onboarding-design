// ─────────────────────────────────────────────────────────────────────────────
// Content model for the BioMar Design Hub onboarding platform.
//
// Everything a learner sees is defined as data here and committed to GitHub —
// the repository is the source of truth ("GitHub as backend"). The Cloudflare
// Pages frontend reads this content; admin edits are published back as commits.
//
// Structure: each source document (a deck or PDF) is a Chapter. A Chapter is
// split into Modules ("items") that follow the document's original order and
// together cover it end to end — no reordering across topics, no skipping.
// A few reference modules aren't sourced from a single document (e.g. the
// tools map, curated from a list) — those have chapterId: null and render as
// standalone reference material rather than inside a chapter.
// ─────────────────────────────────────────────────────────────────────────────

/** A predefined onboarding profile (role + seniority) used to seed a route. */
export type ProfileId =
  | "graphic-junior"
  | "graphic-senior"
  | "motion"
  | "intern"
  | "external";

export interface Chapter {
  id: string;
  /** Display title. */
  title: string;
  /** The original document this chapter is sourced from. */
  source: string;
  icon: string;
  description: string;
}

export interface QuizQuestion {
  id: string;
  /** "single" = one correct option, "multi" = several, "boolean" = true/false. */
  type: "single" | "multi" | "boolean";
  prompt: string;
  options: string[];
  /** Indexes into `options` that are correct. */
  correct: number[];
  /** Shown after answering, right or wrong, to reinforce the concept. */
  explanation: string;
}

export interface Exercise {
  id: string;
  title: string;
  /** A hands-on task the designer does in the real tools to cement the module. */
  prompt: string;
  /** What "done" looks like, so they can self-check. */
  successCriteria: string[];
}

export interface LessonSection {
  heading?: string;
  /** Paragraphs of body copy. */
  body?: string[];
  /** Optional bullet list. */
  bullets?: string[];
  /** Optional key/value callouts (e.g. a cheat-sheet row). */
  facts?: { label: string; value: string }[];
  /** Optional highlighted note. */
  note?: string;
}

/** The original-document material shown for a module — exact, unedited. */
export interface ModuleMaterial {
  /** Path under the site root (served from /public/materials). */
  file: string;
  /** "pptx" → embedded Office viewer; "pdf" → native in-browser viewer. */
  type: "pptx" | "pdf";
  /** Human label, e.g. "Slides 1–3" or "Pages 9–14". */
  range: string;
}

/** A supplementary downloadable file attached to a module (e.g. a template). */
export interface ModuleResource {
  title: string;
  file: string;
}

export interface Module {
  id: string;
  /** The chapter (source document) this belongs to, in original order. Null = standalone reference, not tied to one document. */
  chapterId: string | null;
  title: string;
  /** One-line summary shown in cards and the agenda. */
  summary: string;
  estMinutes: number;
  /** The exact original material for this module (slides/pages, unedited). */
  material?: ModuleMaterial;
  /** Supplementary files (e.g. a template) referenced alongside the material. */
  resources?: ModuleResource[];
  sections: LessonSection[];
  quiz: QuizQuestion[];
  exercises: Exercise[];
}

export interface Profile {
  id: ProfileId;
  label: string;
  description: string;
  /** Module ids the AI recommends for this profile by default. */
  recommendedModuleIds: string[];
}

export interface InfoPanelGroup {
  id: string;
  title: string;
  icon: string;
  /** Reference rows always visible in the persistent info panel. */
  rows: { label: string; value: string; hint?: string }[];
}

export type Role = "admin" | "employee";

export interface Person {
  id: string;
  name: string;
  email: string;
  role: Role;
  profile: ProfileId | null;
  startDate: string;
  /** Modules assigned to this person (after admin approval). */
  assignedModuleIds: string[];
  /** Admin-set calendar: moduleId → "YYYY-MM-DD". Optional per module. */
  schedule?: Record<string, string>;
  /** Per-module progress the employee accrues. */
  progress: Record<
    string,
    { completed: boolean; quizScore: number | null }
  >;
}
