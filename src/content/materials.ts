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
}

const SLICE = "/materials/slices";

const PLAYBOOK = "Design Hub Playbook";
const STRATEGIC = "Strategic Presentation";
const GLOBAL = "Global & Group Marketing";

// ── Confidential videos (private R2, streamed through the Worker) ────────────
export interface ModuleVideo {
  /** The object key in the R2 bucket, e.g. "task-manager-walkthrough.mp4". */
  key: string;
  /** Caption shown under the player. */
  title?: string;
  /** Optional poster image path (e.g. a /materials/... thumbnail). */
  poster?: string;
}

// Map each module to its videos by R2 key. Fill this in once the videos are
// uploaded to the "biomar-onboarding-media" bucket. Example:
//   "task-manager": [{ key: "task-manager-walkthrough.mp4", title: "Board walkthrough" }],
export const moduleVideos: Record<string, ModuleVideo[]> = {
  // (empty until videos are uploaded to R2 and keys are added here)
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
  // Process
  "process-overview": [
    { title: PLAYBOOK, file: `${SLICE}/process-overview--playbook.pptx` },
    { title: STRATEGIC, file: `${SLICE}/process-overview--strategic.pptx` },
  ],
  "the-brief": [
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
    { title: PLAYBOOK, file: `${SLICE}/files-naming--playbook.pptx` },
  ],
  "versioning-review": [
    { title: PLAYBOOK, file: `${SLICE}/versioning-review--playbook.pptx` },
  ],
  "export-close": [
    { title: PLAYBOOK, file: `${SLICE}/export-close--playbook.pptx` },
  ],
  // Brand
  "brand-guidelines": [
    { title: STRATEGIC, file: `${SLICE}/brand-guidelines--strategic.pptx` },
  ],
  "material-guide": [
    { title: STRATEGIC, file: `${SLICE}/material-guide--strategic.pptx` },
  ],
  // Tools
  communication: [
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
