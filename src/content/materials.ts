// ─────────────────────────────────────────────────────────────────────────────
// Presentation materials.
//
// Each module shows ONLY its own slides. The source decks are split per module
// into small .pptx files under /public/materials/slices (media purged so each
// slice stays light), and shown exactly as the original PowerPoint via the
// embedded Office viewer (see components/DeckViewer.tsx).
// ─────────────────────────────────────────────────────────────────────────────

export interface ModuleMaterial {
  /** Deck name shown as the tab / label. */
  title: string;
  /** Path under the site root (served from /public/materials). */
  file: string;
  /** "pptx" → embedded Office viewer (default); "pdf" → native PDF viewer. */
  type?: "pptx" | "pdf";
}

const SLICE = "/materials/slices";

const PLAYBOOK = "Design Hub Playbook";
const STRATEGIC = "Strategic Presentation";
const GLOBAL = "Global & Group Marketing";
const DH2026 = "Design Hub 2026";

// ── Videos (Vimeo) ───────────────────────────────────────────────────────────
export interface ModuleVideo {
  /** Vimeo video id, or an id/hash pair for unlisted videos ("123456789/abcdef1234"). */
  vimeo: string;
  /** Caption shown under the player. */
  title?: string;
}

// Map each module to its Vimeo videos. Accepts a bare id ("123456789") or, for
// unlisted/private videos, the "id/privacyHash" form from the Vimeo URL
// (e.g. vimeo.com/123456789/abcdef1234 → "123456789/abcdef1234"). Example:
//   "task-manager": [{ vimeo: "123456789/abcdef1234", title: "Board walkthrough" }],
export const moduleVideos: Record<string, ModuleVideo[]> = {
  "what-is-biomar": [
    { vimeo: "1213275191/e9194f1235", title: "BioMar — intro" },
  ],
};

export const moduleMaterials: Record<string, ModuleMaterial[]> = {
  // Foundations
  "what-is-biomar": [
    { title: STRATEGIC, file: `${SLICE}/what-is-biomar--strategic.pptx` },
  ],
  "global-marketing": [
    { title: GLOBAL, file: `${SLICE}/global-marketing--global.pptx` },
  ],
  "what-is-design-hub": [
    { title: STRATEGIC, file: `${SLICE}/what-is-design-hub--strategic.pptx` },
  ],
  // Process — start with Design Hub 2026 (how we work), then the Playbook (extended).
  "process-overview": [
    { title: DH2026, file: `${SLICE}/process-overview--dh2026.pptx` },
    { title: PLAYBOOK, file: `${SLICE}/process-overview--playbook.pptx` },
    { title: STRATEGIC, file: `${SLICE}/process-overview--strategic.pptx` },
  ],
  "tasks-vs-projects": [
    { title: DH2026, file: `${SLICE}/tasks-vs-projects--dh2026.pptx` },
  ],
  "deadlines-priorities": [
    { title: DH2026, file: `${SLICE}/deadlines-priorities--dh2026.pptx` },
  ],
  "the-brief": [
    { title: DH2026, file: `${SLICE}/the-brief--dh2026.pptx` },
    { title: PLAYBOOK, file: `${SLICE}/the-brief--playbook.pptx` },
    { title: "Brief Template", file: `/materials/design-hub-brief-template.potx` },
  ],
  "email-tags-folders": [
    { title: PLAYBOOK, file: `${SLICE}/email-tags-folders--playbook.pptx` },
  ],
  "task-manager": [
    { title: PLAYBOOK, file: `${SLICE}/task-manager--playbook.pptx` },
  ],
  "files-naming": [
    { title: DH2026, file: `${SLICE}/files-naming--dh2026.pptx` },
    { title: PLAYBOOK, file: `${SLICE}/files-naming--playbook.pptx` },
  ],
  "versioning-review": [
    { title: DH2026, file: `${SLICE}/versioning-review--dh2026.pptx` },
    { title: PLAYBOOK, file: `${SLICE}/versioning-review--playbook.pptx` },
  ],
  "export-close": [
    { title: PLAYBOOK, file: `${SLICE}/export-close--playbook.pptx` },
  ],
  // Brand
  "brand-guidelines": [
    {
      title: "BioMar Brand Guidelines 2020",
      file: `/materials/brand-guidelines-2020.pdf`,
      type: "pdf",
    },
    { title: STRATEGIC, file: `${SLICE}/brand-guidelines--strategic.pptx` },
  ],
  "material-guide": [
    { title: STRATEGIC, file: `${SLICE}/material-guide--strategic.pptx` },
  ],
  // Tools
  "incopy-indesign": [
    { title: DH2026, file: `${SLICE}/incopy-indesign--dh2026.pptx` },
  ],
  communication: [
    { title: DH2026, file: `${SLICE}/communication--dh2026.pptx` },
    { title: PLAYBOOK, file: `${SLICE}/communication--playbook.pptx` },
    { title: STRATEGIC, file: `${SLICE}/communication--strategic.pptx` },
    { title: GLOBAL, file: `${SLICE}/communication--global.pptx` },
  ],
  // People
  "stakeholder-map": [
    { title: PLAYBOOK, file: `${SLICE}/stakeholder-map--playbook.pptx` },
    { title: GLOBAL, file: `${SLICE}/stakeholder-map--global.pptx` },
  ],
  "meet-managers": [
    { title: GLOBAL, file: `${SLICE}/meet-managers--global.pptx` },
  ],
};
