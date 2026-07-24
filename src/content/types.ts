// ─────────────────────────────────────────────────────────────────────────────
// Content model for the BioMar Design Hub onboarding platform.
//
// Everything a learner sees is defined as data here and committed to GitHub —
// the repository is the source of truth ("GitHub as backend"). The Cloudflare
// Pages frontend reads this content; admin edits are published back as commits.
// ─────────────────────────────────────────────────────────────────────────────

/** A predefined onboarding profile (role + seniority) used to seed a route. */
export type ProfileId =
  | "graphic-junior"
  | "graphic-senior"
  | "motion"
  | "intern"
  | "external";

export type ModuleCategory =
  | "foundations"
  | "process"
  | "brand"
  | "tools"
  | "people";

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

export interface Module {
  id: string;
  category: ModuleCategory;
  title: string;
  /** One-line summary shown in cards and the agenda. */
  summary: string;
  estMinutes: number;
  /** Where this material comes from, so admins can trace it to source decks. */
  source: string;
  sections: LessonSection[];
  quiz: QuizQuestion[];
  exercises: Exercise[];
}

export interface AgendaPhase {
  id: string;
  title: string;
  /** e.g. "Week 1" / "Days 1–3". */
  timeframe: string;
  description: string;
  /** Ordered module ids that belong to this phase. */
  moduleIds: string[];
  /** Non-module milestones (meet people, first tasks). */
  milestones?: string[];
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
  /** Per-module progress the employee accrues. */
  progress: Record<
    string,
    { completed: boolean; quizScore: number | null }
  >;
}
