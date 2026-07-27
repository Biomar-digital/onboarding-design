// ─────────────────────────────────────────────────────────────────────────────
// Cloudflare Worker entry (Workers + Static Assets).
//
// Cloudflare's unified model serves the built SPA from ./dist via the ASSETS
// binding and runs this Worker for anything that isn't a static file. We use
// it for the two API routes; everything else falls through to the static site
// (with single-page-application fallback for client-side routes).
//
//   POST /api/publish  → commit people/assignments back to GitHub
//   POST /api/suggest  → optional Claude-backed module suggestions
//   *                  → static assets (dist/) + SPA fallback
// ─────────────────────────────────────────────────────────────────────────────

// Minimal R2 shape (avoids needing @cloudflare/workers-types in this file).
interface R2Range {
  offset?: number;
  length?: number;
  suffix?: number;
}
interface R2Object {
  body: ReadableStream | null;
  size: number;
  httpEtag: string;
  range?: R2Range;
  writeHttpMetadata: (headers: Headers) => void;
}
interface R2Bucket {
  get: (
    key: string,
    opts?: { range?: R2Range; onlyIf?: Headers },
  ) => Promise<R2Object | null>;
  head: (key: string) => Promise<R2Object | null>;
}

export interface Env {
  ASSETS: { fetch: (request: Request) => Promise<Response> };
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string;
  GITHUB_BRANCH?: string;
  ANTHROPIC_API_KEY?: string;
  /** Private R2 bucket for confidential videos (bound in wrangler.jsonc). */
  MEDIA?: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/publish") {
      if (request.method !== "POST") return json({ error: "Use POST." }, 405);
      return handlePublish(request, env);
    }
    if (url.pathname === "/api/suggest") {
      if (request.method !== "POST") return json({ error: "Use POST." }, 405);
      return handleSuggest(request, env);
    }

    // Private video streaming from R2 (confidential — served through the Worker,
    // never a public bucket URL). Gate the site with Cloudflare Access so only
    // BioMar identities can reach this.
    if (url.pathname.startsWith("/media/video/")) {
      const key = decodeURIComponent(
        url.pathname.slice("/media/video/".length),
      );
      return handleVideo(request, env, key);
    }

    // Not an API route → static site (SPA fallback handled by the assets config).
    return env.ASSETS.fetch(request);
  },
};

// ── /api/publish ─────────────────────────────────────────────────────────────
const FILE_PATH = "src/content/people.generated.json";

async function handlePublish(request: Request, env: Env): Promise<Response> {
  if (!env.GITHUB_TOKEN || !env.GITHUB_REPO) {
    return json(
      {
        error:
          "Publishing not configured. Set GITHUB_TOKEN and GITHUB_REPO in the Worker's environment variables.",
      },
      501,
    );
  }

  let body: { people?: unknown };
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid JSON body." }, 400);
  }
  if (!Array.isArray(body.people)) {
    return json({ error: "Body must include a `people` array." }, 400);
  }

  const branch = env.GITHUB_BRANCH || "main";
  const api = `https://api.github.com/repos/${env.GITHUB_REPO}/contents/${FILE_PATH}`;
  const headers = {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "biomar-design-hub-onboarding",
    "Content-Type": "application/json",
  };

  // Current file SHA is required to update an existing file.
  let sha: string | undefined;
  const getRes = await fetch(`${api}?ref=${branch}`, { headers });
  if (getRes.ok) {
    const cur = (await getRes.json()) as { sha?: string };
    sha = cur.sha;
  }

  const content = toBase64(JSON.stringify(body.people, null, 2) + "\n");

  const putRes = await fetch(api, {
    method: "PUT",
    headers,
    body: JSON.stringify({
      message: "chore(onboarding): update people & assignments via admin",
      content,
      branch,
      sha,
    }),
  });

  if (!putRes.ok) {
    return json({ error: `GitHub API error: ${await putRes.text()}` }, putRes.status);
  }
  const data = (await putRes.json()) as { commit?: { sha?: string } };
  return json({ ok: true, commit: data.commit?.sha ?? null });
}

// ── /api/suggest ─────────────────────────────────────────────────────────────
interface SuggestBody {
  profileId?: string | null;
  notes?: string;
  catalog?: { id: string; title: string; category: string; summary: string }[];
}

async function handleSuggest(request: Request, env: Env): Promise<Response> {
  if (!env.ANTHROPIC_API_KEY) {
    return json({ error: "AI not configured (no ANTHROPIC_API_KEY)." }, 501);
  }

  let body: SuggestBody;
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
    'Respond ONLY as JSON: {"moduleIds": string[], "rationale": string}. ' +
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
    if (!res.ok) return json({ error: `Anthropic error: ${await res.text()}` }, 502);

    const data = (await res.json()) as { content?: { type: string; text?: string }[] };
    const text = data.content?.find((c) => c.type === "text")?.text?.trim() ?? "";
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) return json({ error: "No JSON in model output." }, 502);

    const parsed = JSON.parse(match[0]) as { moduleIds?: string[]; rationale?: string };
    const validIds = new Set(catalog.map((c) => c.id));
    const moduleIds = (parsed.moduleIds ?? []).filter((id) => validIds.has(id));
    return json({ moduleIds, rationale: parsed.rationale ?? "" });
  } catch (err) {
    return json({ error: (err as Error).message }, 500);
  }
}

// ── /media/video/:key — private R2 streaming with HTTP Range support ─────────
async function handleVideo(
  request: Request,
  env: Env,
  key: string,
): Promise<Response> {
  if (!env.MEDIA) {
    return json(
      {
        error:
          "Video storage not configured. Create an R2 bucket and bind it as MEDIA in wrangler.jsonc.",
      },
      501,
    );
  }
  if (!key || key.includes("..")) return json({ error: "Bad key." }, 400);

  const rangeHeader = request.headers.get("Range");
  let range: R2Range | undefined;
  if (rangeHeader) {
    const m = /bytes=(\d*)-(\d*)/.exec(rangeHeader);
    if (m) {
      const start = m[1] ? parseInt(m[1], 10) : undefined;
      const end = m[2] ? parseInt(m[2], 10) : undefined;
      if (start !== undefined && end !== undefined)
        range = { offset: start, length: end - start + 1 };
      else if (start !== undefined) range = { offset: start };
      else if (end !== undefined) range = { suffix: end };
    }
  }

  const obj = await env.MEDIA.get(key, range ? { range } : undefined);
  if (!obj) return json({ error: "Not found." }, 404);

  const headers = new Headers();
  obj.writeHttpMetadata(headers);
  headers.set("Accept-Ranges", "bytes");
  headers.set("etag", obj.httpEtag);
  headers.set("Cache-Control", "private, max-age=3600");
  if (!headers.has("Content-Type")) headers.set("Content-Type", "video/mp4");

  if (range && obj.range) {
    const offset = obj.range.offset ?? 0;
    const length = obj.range.length ?? obj.size - offset;
    const end = offset + length - 1;
    headers.set("Content-Range", `bytes ${offset}-${end}/${obj.size}`);
    headers.set("Content-Length", String(length));
    return new Response(obj.body, { status: 206, headers });
  }
  headers.set("Content-Length", String(obj.size));
  return new Response(obj.body, { status: 200, headers });
}

// ── helpers ──────────────────────────────────────────────────────────────────
function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

// UTF-8 safe base64 for the Workers runtime (no `unescape`).
function toBase64(str: string): string {
  const bytes = new TextEncoder().encode(str);
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}
