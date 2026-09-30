// ─────────────────────────────────────────────────────────────────────────────
// Cloudflare Worker entry (Workers + Static Assets).
//
// Cloudflare's unified model serves the built SPA from ./dist via the ASSETS
// binding and runs this Worker for anything that isn't a static file. We use
// it for the API routes; everything else falls through to the static site
// (with single-page-application fallback for client-side routes).
//
//   POST /api/publish            → commit people/assignments back to GitHub
//   POST /api/suggest            → optional Claude-backed module suggestions
//   POST /api/auth/login         → email+password sign-in, sets a session cookie
//   POST /api/auth/logout        → clears the session
//   GET  /api/auth/me            → who the current session belongs to, if any
//   POST /api/auth/signup-request        → request an account (self-service)
//   GET  /api/auth/signup-requests       → admin: list pending requests
//   POST /api/auth/signup-requests/:id/approve → admin: create the account
//   POST /api/auth/signup-requests/:id/reject  → admin: decline the request
//   POST /api/auth/change-password       → the signed-in user sets a new password
//   POST /api/admin/reset-password       → admin: set someone else's password
//   *                            → static assets (dist/) + SPA fallback
//
// Credentials live in Cloudflare KV (binding: AUTH_KV) — see worker/auth.ts and
// DEPLOYMENT.md for how to provision it. Everything else stays "GitHub as
// backend" as before.
// ─────────────────────────────────────────────────────────────────────────────

import type { AuthEnv } from "./auth";
import {
  ensureBootstrapAdmin,
  getUser,
  putUser,
  hashPassword,
  verifyPassword,
  createSession,
  getSessionUser,
  destroySession,
  sessionCookieHeader,
  clearCookieHeader,
  createSignupRequest,
  listSignupRequests,
  getSignupRequest,
  putSignupRequest,
} from "./auth";

export interface Env extends AuthEnv {
  ASSETS: { fetch: (request: Request) => Promise<Response> };
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string;
  GITHUB_BRANCH?: string;
  ANTHROPIC_API_KEY?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/api/publish") {
      if (request.method !== "POST") return json({ error: "Use POST." }, 405);
      return handlePublish(request, env);
    }
    if (path === "/api/suggest") {
      if (request.method !== "POST") return json({ error: "Use POST." }, 405);
      return handleSuggest(request, env);
    }
    if (path.startsWith("/api/auth/") || path.startsWith("/api/admin/")) {
      return handleAuthRoute(path, request, env);
    }

    // Not an API route → static site (SPA fallback handled by the assets config).
    return env.ASSETS.fetch(request);
  },
};

// ── auth routes ──────────────────────────────────────────────────────────────
async function handleAuthRoute(path: string, request: Request, env: Env): Promise<Response> {
  if (!env.AUTH_KV) {
    return json(
      { error: "Login isn't configured yet. Bind a KV namespace named AUTH_KV in this Worker (see DEPLOYMENT.md)." },
      501,
    );
  }

  if (path === "/api/auth/login" && request.method === "POST") return handleLogin(request, env);
  if (path === "/api/auth/logout" && request.method === "POST") return handleLogout(request, env);
  if (path === "/api/auth/me" && request.method === "GET") return handleMe(request, env);
  if (path === "/api/auth/signup-request" && request.method === "POST")
    return handleSignupRequest(request, env);
  if (path === "/api/auth/signup-requests" && request.method === "GET")
    return handleListSignupRequests(request, env);
  if (path === "/api/auth/change-password" && request.method === "POST")
    return handleChangePassword(request, env);
  if (path === "/api/admin/reset-password" && request.method === "POST")
    return handleAdminResetPassword(request, env);

  const approveMatch = path.match(/^\/api\/auth\/signup-requests\/([^/]+)\/approve$/);
  if (approveMatch && request.method === "POST") return handleApprove(approveMatch[1], request, env);

  const rejectMatch = path.match(/^\/api\/auth\/signup-requests\/([^/]+)\/reject$/);
  if (rejectMatch && request.method === "POST") return handleReject(rejectMatch[1], request, env);

  return json({ error: "Not found." }, 404);
}

async function handleLogin(request: Request, env: Env): Promise<Response> {
  const body = (await safeJson(request)) as { email?: string; password?: string } | null;
  const email = body?.email?.trim().toLowerCase();
  const password = body?.password ?? "";
  if (!email || !password) return json({ error: "Email and password are required." }, 400);

  await ensureBootstrapAdmin(env, email);

  const user = await getUser(env, email);
  if (!user || !(await verifyPassword(password, user))) {
    return json({ error: "Incorrect email or password." }, 401);
  }

  const token = await createSession(env, user.email);
  return json(
    { ok: true, email: user.email, personId: user.personId, role: user.role },
    200,
    { "Set-Cookie": sessionCookieHeader(token) },
  );
}

async function handleLogout(request: Request, env: Env): Promise<Response> {
  await destroySession(request, env);
  return json({ ok: true }, 200, { "Set-Cookie": clearCookieHeader() });
}

async function handleMe(request: Request, env: Env): Promise<Response> {
  const user = await getSessionUser(request, env);
  if (!user) return json({ ok: false }, 200);
  return json({ ok: true, email: user.email, personId: user.personId, role: user.role });
}

async function handleSignupRequest(request: Request, env: Env): Promise<Response> {
  const body = (await safeJson(request)) as { name?: string; email?: string; message?: string } | null;
  const name = body?.name?.trim();
  const email = body?.email?.trim().toLowerCase();
  const message = body?.message?.trim() ?? "";
  if (!name || !email) return json({ error: "Name and email are required." }, 400);

  const existingUser = await getUser(env, email);
  if (existingUser) return json({ error: "There's already an account for that email." }, 409);

  const pending = await listSignupRequests(env);
  if (pending.some((r) => r.status === "pending" && r.email.toLowerCase() === email)) {
    return json({ error: "There's already a pending request for that email." }, 409);
  }

  await createSignupRequest(env, { name, email, message });
  return json({ ok: true });
}

async function handleListSignupRequests(request: Request, env: Env): Promise<Response> {
  const admin = await requireAdmin(request, env);
  if (admin instanceof Response) return admin;
  const requests = await listSignupRequests(env);
  return json({ requests });
}

async function handleApprove(id: string, request: Request, env: Env): Promise<Response> {
  const admin = await requireAdmin(request, env);
  if (admin instanceof Response) return admin;

  const body = (await safeJson(request)) as
    | { personId?: string; password?: string; role?: "admin" | "employee" }
    | null;
  const personId = body?.personId?.trim();
  const password = body?.password ?? "";
  const role = body?.role === "admin" ? "admin" : "employee";
  if (!personId || password.length < 8) {
    return json({ error: "A personId and a password (min. 8 characters) are required." }, 400);
  }

  const reqRecord = await getSignupRequest(env, id);
  if (!reqRecord) return json({ error: "Signup request not found." }, 404);
  if (reqRecord.status !== "pending") return json({ error: "That request was already handled." }, 409);

  const existingUser = await getUser(env, reqRecord.email);
  if (existingUser) return json({ error: "There's already an account for that email." }, 409);

  const { hash, salt, iterations } = await hashPassword(password);
  await putUser(env, { email: reqRecord.email, personId, role, passwordHash: hash, salt, iterations });
  await putSignupRequest(env, { ...reqRecord, status: "approved" });

  return json({ ok: true, email: reqRecord.email });
}

async function handleReject(id: string, request: Request, env: Env): Promise<Response> {
  const admin = await requireAdmin(request, env);
  if (admin instanceof Response) return admin;

  const reqRecord = await getSignupRequest(env, id);
  if (!reqRecord) return json({ error: "Signup request not found." }, 404);
  await putSignupRequest(env, { ...reqRecord, status: "rejected" });
  return json({ ok: true });
}

async function handleChangePassword(request: Request, env: Env): Promise<Response> {
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: "Not signed in." }, 401);

  const body = (await safeJson(request)) as { currentPassword?: string; newPassword?: string } | null;
  const currentPassword = body?.currentPassword ?? "";
  const newPassword = body?.newPassword ?? "";
  if (!(await verifyPassword(currentPassword, user))) {
    return json({ error: "Current password is incorrect." }, 401);
  }
  if (newPassword.length < 8) return json({ error: "New password must be at least 8 characters." }, 400);

  const { hash, salt, iterations } = await hashPassword(newPassword);
  await putUser(env, { ...user, passwordHash: hash, salt, iterations });
  return json({ ok: true });
}

async function handleAdminResetPassword(request: Request, env: Env): Promise<Response> {
  const admin = await requireAdmin(request, env);
  if (admin instanceof Response) return admin;

  const body = (await safeJson(request)) as { email?: string; newPassword?: string } | null;
  const email = body?.email?.trim().toLowerCase();
  const newPassword = body?.newPassword ?? "";
  if (!email || newPassword.length < 8) {
    return json({ error: "Email and a new password (min. 8 characters) are required." }, 400);
  }

  const user = await getUser(env, email);
  if (!user) return json({ error: "No account for that email." }, 404);

  const { hash, salt, iterations } = await hashPassword(newPassword);
  await putUser(env, { ...user, passwordHash: hash, salt, iterations });
  return json({ ok: true });
}

async function requireAdmin(request: Request, env: Env) {
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: "Not signed in." }, 401);
  if (user.role !== "admin") return json({ error: "Admins only." }, 403);
  return user;
}

async function safeJson(request: Request): Promise<unknown> {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

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
  catalog?: { id: string; title: string; chapterId: string | null; summary: string }[];
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

// ── helpers ──────────────────────────────────────────────────────────────────
function json(data: unknown, status = 200, extraHeaders?: Record<string, string>): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json", ...extraHeaders },
  });
}

// UTF-8 safe base64 for the Workers runtime (no `unescape`).
function toBase64(str: string): string {
  const bytes = new TextEncoder().encode(str);
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}
