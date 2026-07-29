import type { Profile } from "./types";
import { modules } from "./modules";

const allIds = modules.map((m) => m.id);
const without = (...ids: string[]) => allIds.filter((id) => !ids.includes(id));
const only = (...ids: string[]) => ids;

// Profiles seed the AI recommendation. The admin picks a profile, the app
// suggests these modules, and the admin adjusts before approving.
export const profiles: Profile[] = [
  {
    id: "graphic-junior",
    label: "Graphic Designer — Junior",
    description:
      "New graphic designer. Needs every chapter, start to finish — strategy, marketing org, process, playbook and brand guidelines.",
    recommendedModuleIds: allIds,
  },
  {
    id: "graphic-senior",
    label: "Graphic Designer — Senior",
    description:
      "Experienced designer joining the Hub. Knows the craft; needs BioMar process, brand and stakeholders — lighter on strategic/organisational context.",
    recommendedModuleIds: without(
      "strategic-01",
      "strategic-04",
      "global-01",
      "dh2026-06",
    ),
  },
  {
    id: "motion",
    label: "Multimedia / Motion Designer",
    description:
      "Video & motion focus. Emphasizes process, feedback formats (incl. video), brand and people; still needs the full strategic/organisational picture.",
    recommendedModuleIds: without("dh2026-06"),
  },
  {
    id: "intern",
    label: "Intern / Short-term",
    description:
      "Short engagement. A focused core: what the Hub is, the process backbone, brand basics and who to ask.",
    recommendedModuleIds: only(
      "strategic-01",
      "strategic-02",
      "dh2026-01",
      "dh2026-03",
      "playbook-01",
      "playbook-02",
      "playbook-05",
      "brand-guidelines-01",
    ),
  },
  {
    id: "external",
    label: "External Partner / Contractor",
    description:
      "Works with the Hub from outside. Needs brand rules, file/versioning conventions and the review workflow — not internal org structure.",
    recommendedModuleIds: only(
      "strategic-01",
      "playbook-01",
      "playbook-03",
      "playbook-04",
      "brand-guidelines-01",
      "brand-guidelines-02",
      "brand-guidelines-03",
      "brand-guidelines-04",
    ),
  },
];

export const profilesById = Object.fromEntries(
  profiles.map((p) => [p.id, p]),
);
