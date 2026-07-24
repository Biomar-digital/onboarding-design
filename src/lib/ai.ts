import type { ProfileId } from "../content/types";
import { profilesById } from "../content/profiles";
import { modules, modulesById } from "../content/modules";

export interface Suggestion {
  moduleIds: string[];
  rationale: string;
  source: "ai" | "rules";
}

// Deterministic, explainable baseline the admin always gets instantly.
export function recommendByProfile(
  profileId: ProfileId | null,
  notes = "",
): Suggestion {
  if (!profileId) {
    return {
      moduleIds: modules
        .filter((m) => m.category === "foundations")
        .map((m) => m.id),
      rationale:
        "No profile selected — starting with the Foundations modules everyone needs.",
      source: "rules",
    };
  }
  const profile = profilesById[profileId];
  let ids = [...profile.recommendedModuleIds];

  // Light keyword nudges from the free-text notes.
  const n = notes.toLowerCase();
  const add = (id: string) => {
    if (modulesById[id] && !ids.includes(id)) ids.push(id);
  };
  if (/(video|motion|animation)/.test(n)) add("versioning-review");
  if (/(print|packaging|production)/.test(n)) {
    add("material-guide");
    add("export-close");
  }
  if (/(brand|guideline)/.test(n)) add("brand-guidelines");

  // Keep canonical module order.
  const order = modules.map((m) => m.id);
  ids = ids.sort((a, b) => order.indexOf(a) - order.indexOf(b));

  return {
    moduleIds: ids,
    rationale: `Based on the "${profile.label}" profile${
      notes ? " and your notes" : ""
    }: ${profile.description}`,
    source: "rules",
  };
}

// Optional AI pass via a Cloudflare Pages Function. Falls back to the rules
// baseline if the endpoint isn't configured.
export async function suggestWithAI(
  profileId: ProfileId | null,
  notes: string,
): Promise<Suggestion> {
  const baseline = recommendByProfile(profileId, notes);
  try {
    const res = await fetch("/api/suggest", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        profileId,
        notes,
        catalog: modules.map((m) => ({
          id: m.id,
          title: m.title,
          category: m.category,
          summary: m.summary,
        })),
      }),
    });
    if (!res.ok) return baseline;
    const data = (await res.json()) as {
      moduleIds?: string[];
      rationale?: string;
    };
    if (!data.moduleIds?.length) return baseline;
    const valid = data.moduleIds.filter((id) => modulesById[id]);
    const order = modules.map((m) => m.id);
    return {
      moduleIds: valid.sort((a, b) => order.indexOf(a) - order.indexOf(b)),
      rationale: data.rationale ?? baseline.rationale,
      source: "ai",
    };
  } catch {
    return baseline;
  }
}
