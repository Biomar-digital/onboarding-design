import type { Profile } from "./types";
import { modules } from "./modules";

const allIds = modules.map((m) => m.id);
const without = (...ids: string[]) => allIds.filter((id) => !ids.includes(id));

// Profiles seed the AI recommendation. The admin picks a profile, the app
// suggests these modules, and the admin adjusts before approving.
export const profiles: Profile[] = [
  {
    id: "graphic-junior",
    label: "Graphic Designer — Junior",
    description:
      "New graphic designer. Needs the full journey: foundations, the complete process, brand and people.",
    recommendedModuleIds: allIds,
  },
  {
    id: "graphic-senior",
    label: "Graphic Designer — Senior",
    description:
      "Experienced designer joining the Hub. Knows the craft; needs BioMar process, brand and stakeholders — lighter on generic foundations.",
    recommendedModuleIds: without("meet-managers"),
  },
  {
    id: "motion",
    label: "Multimedia / Motion Designer",
    description:
      "Video & motion focus. Emphasizes process, versioning (video feedback), brand and people; still needs foundations.",
    recommendedModuleIds: without("material-guide"),
  },
  {
    id: "intern",
    label: "Intern / Short-term",
    description:
      "Short engagement. A focused core: what the Hub is, the process backbone, brand basics and who to ask.",
    recommendedModuleIds: [
      "what-is-design-hub",
      "process-overview",
      "the-brief",
      "task-manager",
      "files-naming",
      "brand-guidelines",
      "stakeholder-map",
    ],
  },
  {
    id: "external",
    label: "External Partner / Contractor",
    description:
      "Works with the Hub from outside. Needs brand rules, file/versioning conventions and the review workflow — not internal people or platforms.",
    recommendedModuleIds: [
      "what-is-design-hub",
      "the-brief",
      "files-naming",
      "versioning-review",
      "export-close",
      "brand-guidelines",
      "material-guide",
    ],
  },
];

export const profilesById = Object.fromEntries(
  profiles.map((p) => [p.id, p]),
);
