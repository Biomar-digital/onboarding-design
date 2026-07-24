// Cloudflare Pages Function — POST /api/suggest
//
// Optional AI pass for the admin's "Suggest modules" button. Given a profile,
// free-text notes and the module catalog, it asks Claude which modules to
// assign and why. The frontend always has a deterministic rules fallback, so
// this endpoint is purely additive — if ANTHROPIC_API_KEY isn't set it returns
// 501 and the UI uses the rules baseline.
//
// Env var: ANTHROPIC_API_KEY

interface Env {
  ANTHROPIC_API_KEY?: string;
}

interface Body {
  profileId?: string | null;
  notes?: string;
  catalog?: { id: string; title: string; category: string; summary: string }[];
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { env, request } = context;
  if (!env.ANTHROPIC_API_KEY) {
    return json({ error: "AI not configured (no ANTHROPIC_API_KEY)." }, 501);
  }

  let body: Body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid JSON." }, 400);
  }
  const catalog = body.catalog ?? [];

  const system =
    "You design onboarding routes for new designers joining BioMar's Design Hub. " +
    "Given a profile and notes, choose which onboarding modules to assign from the catalog. " +
    "Prefer completeness for juniors, focus for seniors/externals. " +
    "Respond ONLY as JSON: {\"moduleIds\": string[], \"rationale\": string}. " +
    "moduleIds MUST be a subset of the catalog ids.";

  const user = JSON.stringify({
    profileId: body.profileId ?? null,
    notes: body.notes ?? "",
    catalog,
  });

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-5",
        max_tokens: 1024,
        system,
        messages: [{ role: "user", content: user }],
      }),
    });
    if (!res.ok) {
      return json({ error: `Anthropic error: ${await res.text()}` }, 502);
    }
    const data = (await res.json()) as {
      content?: { type: string; text?: string }[];
    };
    const text =
      data.content?.find((c) => c.type === "text")?.text?.trim() ?? "";
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) return json({ error: "No JSON in model output." }, 502);
    const parsed = JSON.parse(match[0]) as {
      moduleIds?: string[];
      rationale?: string;
    };
    const validIds = new Set(catalog.map((c) => c.id));
    const moduleIds = (parsed.moduleIds ?? []).filter((id) => validIds.has(id));
    return json({ moduleIds, rationale: parsed.rationale ?? "" });
  } catch (err) {
    return json({ error: (err as Error).message }, 500);
  }
};

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}
