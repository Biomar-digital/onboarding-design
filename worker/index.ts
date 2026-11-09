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
//   POST /api/admin/invite               → admin: create a one-time "set your password" link (emails it if a mail provider is configured)
//   GET  /api/auth/invite?token=…        → public: validate an invite link
//   POST /api/auth/accept-invite         → public: the invited person chooses a password and is signed in
//   GET  /api/people             → admin: every person record; employee: only their own
//   PUT  /api/people             → admin: save the people list (employee progress is kept)
//   POST /api/progress           → the signed-in person records a completed module
//   POST /api/feedback           → the signed-in person sends feedback / a question about a chapter
//   GET  /api/feedback           → admin: all feedback, newest first
//   POST /api/feedback/:id/resolve → admin: mark a message resolved (or reopen it)
//   *                            → static assets (dist/) + SPA fallback
//
// Credentials live in Cloudflare KV (binding: AUTH_KV) — see worker/auth.ts and
// DEPLOYMENT.md for how to provision it. Everything else stays "GitHub as
// backend" as before.
// ─────────────────────────────────────────────────────────────────────────────

import type { AuthEnv } from "./auth";
import type { Person } from "../src/content/types";
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
  /** Optional: with both set, invites are emailed via Resend; otherwise the admin gets the link. */
  RESEND_API_KEY?: string;
  MAIL_FROM?: string;
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
    if (path === "/api/people" || path === "/api/progress") {
      return handlePeopleRoute(path, request, env);
    }
    if (path === "/api/feedback" || path.startsWith("/api/feedback/")) {
      return handleFeedbackRoute(path, request, env);
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
  if (path === "/api/admin/invite" && request.method === "POST") return handleInvite(request, env);
  if (path === "/api/auth/invite" && request.method === "GET") return handleGetInvite(request, env);
  if (path === "/api/auth/accept-invite" && request.method === "POST")
    return handleAcceptInvite(request, env);

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

// ── people records (server-side, so a new hire's record exists for them too) ──
// KV layout:  person:<id> → Person   ·   people:meta → { updatedAt }
// Per-person keys so two employees saving progress at once never overwrite
// each other. The admin owns everything except `progress`, which belongs to
// the employee: admin saves never reset it.
async function handlePeopleRoute(path: string, request: Request, env: Env): Promise<Response> {
  if (!env.AUTH_KV) return json({ error: "Login isn't configured yet." }, 501);
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: "Not signed in." }, 401);

  if (path === "/api/people" && request.method === "GET") {
    if (user.role === "admin") {
      const initialised = await env.AUTH_KV.get("people:meta");
      if (!initialised) return json({ people: null });
      return json({ people: await listPeople(env) });
    }
    const own = await env.AUTH_KV.get(`person:${user.personId}`);
    return json({ people: own ? [JSON.parse(own) as Person] : [] });
  }

  if (path === "/api/people" && request.method === "PUT") {
    if (user.role !== "admin") return json({ error: "Admins only." }, 403);
    const body = (await safeJson(request)) as { people?: Person[] } | null;
    if (!Array.isArray(body?.people)) return json({ error: "Body must include a `people` array." }, 400);
    const incoming = body!.people.filter((p) => p && typeof p.id === "string" && p.id);

    const existing = await listPeople(env);
    const existingById = new Map(existing.map((p) => [p.id, p]));
    const merged = incoming.map((p) => {
      const current = existingById.get(p.id);
      return current ? { ...p, progress: current.progress } : p;
    });
    const keep = new Set(merged.map((p) => p.id));

    await Promise.all([
      ...merged.map((p) => env.AUTH_KV.put(`person:${p.id}`, JSON.stringify(p))),
      ...existing.filter((p) => !keep.has(p.id)).map((p) => env.AUTH_KV.delete(`person:${p.id}`)),
      env.AUTH_KV.put("people:meta", JSON.stringify({ updatedAt: new Date().toISOString() })),
    ]);
    return json({ ok: true, people: merged });
  }

  if (path === "/api/progress" && request.method === "POST") {
    const body = (await safeJson(request)) as { moduleId?: string; quizScore?: number | null } | null;
    const moduleId = body?.moduleId;
    if (typeof moduleId !== "string" || !moduleId) return json({ error: "moduleId is required." }, 400);
    const score = typeof body?.quizScore === "number" ? body.quizScore : null;

    const raw = await env.AUTH_KV.get(`person:${user.personId}`);
    if (!raw) return json({ error: "No record for this account yet — ask an admin." }, 404);
    const person = JSON.parse(raw) as Person;
    person.progress = { ...person.progress, [moduleId]: { completed: true, quizScore: score } };
    await env.AUTH_KV.put(`person:${person.id}`, JSON.stringify(person));
    return json({ ok: true });
  }

  return json({ error: "Not found." }, 404);
}

// ── feedback / questions per chapter ─────────────────────────────────────────
// KV layout:  feedback:<id> → FeedbackItem   ·   fbrate:<email>:<day> → count (TTL)
interface FeedbackItem {
  id: string;
  createdAt: string;
  personId: string;
  name: string;
  email: string;
  sectionKey: string;
  sectionTitle: string;
  message: string;
  resolved: boolean;
}

async function handleFeedbackRoute(path: string, request: Request, env: Env): Promise<Response> {
  if (!env.AUTH_KV) return json({ error: "Login isn't configured yet." }, 501);
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: "Not signed in." }, 401);

  if (path === "/api/feedback" && request.method === "POST") {
    const body = (await safeJson(request)) as
      | { sectionKey?: string; sectionTitle?: string; message?: string }
      | null;
    const message = body?.message?.trim() ?? "";
    if (message.length < 3) return json({ error: "Please write a message." }, 400);
    if (message.length > 2000) return json({ error: "Please keep it under 2000 characters." }, 400);

    // Light abuse guard: at most 20 messages per person per day.
    const day = new Date().toISOString().slice(0, 10);
    const rateKey = `fbrate:${user.email}:${day}`;
    const count = Number((await env.AUTH_KV.get(rateKey)) ?? 0);
    if (count >= 20) return json({ error: "Daily feedback limit reached — try again tomorrow." }, 429);
    await env.AUTH_KV.put(rateKey, String(count + 1), { expirationTtl: 172800 });

    const personRaw = await env.AUTH_KV.get(`person:${user.personId}`);
    const name = personRaw ? (JSON.parse(personRaw) as Person).name : user.email;
    const createdAt = new Date().toISOString();
    const id = `${Date.now()}-${crypto.randomUUID().slice(0, 8)}`;
    const item: FeedbackItem = {
      id,
      createdAt,
      personId: user.personId,
      name,
      email: user.email,
      sectionKey: (body?.sectionKey ?? "").slice(0, 60),
      sectionTitle: (body?.sectionTitle ?? "").slice(0, 120),
      message,
      resolved: false,
    };
    await env.AUTH_KV.put(`feedback:${id}`, JSON.stringify(item));
    return json({ ok: true });
  }

  if (path === "/api/feedback" && request.method === "GET") {
    if (user.role !== "admin") return json({ error: "Admins only." }, 403);
    const list = await env.AUTH_KV.list({ prefix: "feedback:" });
    const items = await Promise.all(
      list.keys.map(async (k) => {
        const raw = await env.AUTH_KV.get(k.name);
        return raw ? (JSON.parse(raw) as FeedbackItem) : null;
      }),
    );
    return json({
      items: items
        .filter((i): i is FeedbackItem => !!i)
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt)),
    });
  }

  const resolve = path.match(/^\/api\/feedback\/([^/]+)\/resolve$/);
  if (resolve && request.method === "POST") {
    if (user.role !== "admin") return json({ error: "Admins only." }, 403);
    const id = decodeURIComponent(resolve[1]);
    const raw = await env.AUTH_KV.get(`feedback:${id}`);
    if (!raw) return json({ error: "Not found." }, 404);
    const body = (await safeJson(request)) as { resolved?: boolean } | null;
    const item = JSON.parse(raw) as FeedbackItem;
    item.resolved = body?.resolved !== false;
    await env.AUTH_KV.put(`feedback:${id}`, JSON.stringify(item));
    return json({ ok: true });
  }

  return json({ error: "Not found." }, 404);
}

async function listPeople(env: Env): Promise<Person[]> {
  const list = await env.AUTH_KV.list({ prefix: "person:" });
  const people = await Promise.all(
    list.keys.map(async (k) => {
      const raw = await env.AUTH_KV.get(k.name);
      return raw ? (JSON.parse(raw) as Person) : null;
    }),
  );
  return people.filter((p): p is Person => !!p);
}

// ── invitations: "set your password" links ────────────────────────────────────
// KV layout:  invite:<token> → Invite (TTL 7 days, single use)
//             invite-email:<email> → token   (a new invite replaces the previous one)
interface Invite {
  email: string;
  personId: string;
  role: "admin" | "employee";
  createdAt: string;
  createdBy: string;
}
const INVITE_TTL_SECONDS = 7 * 24 * 60 * 60;

function newToken(): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(32)))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function handleInvite(request: Request, env: Env): Promise<Response> {
  const admin = await requireAdmin(request, env);
  if (admin instanceof Response) return admin;

  const body = (await safeJson(request)) as
    | { email?: string; personId?: string; role?: "admin" | "employee" }
    | null;
  const email = body?.email?.trim().toLowerCase();
  const personId = body?.personId?.trim();
  if (!email || !email.includes("@") || !personId) {
    return json({ error: "A valid email and a personId are required." }, 400);
  }
  if (await getUser(env, email)) {
    return json({ error: "That person already has an account — use Reset password instead." }, 409);
  }

  // Replace any earlier pending invite for this email.
  const previous = await env.AUTH_KV.get(`invite-email:${email}`);
  if (previous) await env.AUTH_KV.delete(`invite:${previous}`);

  const token = newToken();
  const invite: Invite = {
    email,
    personId,
    role: body?.role === "admin" ? "admin" : "employee",
    createdAt: new Date().toISOString(),
    createdBy: admin.email,
  };
  await env.AUTH_KV.put(`invite:${token}`, JSON.stringify(invite), { expirationTtl: INVITE_TTL_SECONDS });
  await env.AUTH_KV.put(`invite-email:${email}`, token, { expirationTtl: INVITE_TTL_SECONDS });

  const link = `${new URL(request.url).origin}/set-password?token=${token}`;
  const personRaw = await env.AUTH_KV.get(`person:${personId}`);
  const name = personRaw ? (JSON.parse(personRaw) as Person).name : email;
  const mail = await sendInviteEmail(env, email, name, link);
  return json({
    ok: true,
    link,
    expiresInDays: 7,
    emailSent: mail.sent,
    emailError: mail.error ?? null,
  });
}

async function sendInviteEmail(
  env: Env,
  to: string,
  name: string,
  link: string,
): Promise<{ sent: boolean; error?: string }> {
  if (!env.RESEND_API_KEY || !env.MAIL_FROM) return { sent: false };
  const first = name.split(" ")[0];
  const safeFirst = first.replace(/[&<>"]/g, "");
  const text =
    `Hi ${first},\n\n` +
    `You've been added to the BioMar Design Hub onboarding. Use this link to choose your password and sign in:\n\n` +
    `${link}\n\n` +
    `The link works once and expires in 7 days. If it expires, ask the Design Hub team for a new one.\n\n` +
    `Powered by Partnership. Driven by Innovation.`;
  const html =
    `<p>Hi ${safeFirst},</p>` +
    `<p>You've been added to the <strong>BioMar Design Hub onboarding</strong>. Use the button below to choose your password and sign in.</p>` +
    `<p><a href="${link}" style="display:inline-block;background:#1F3E77;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600">Set my password</a></p>` +
    `<p style="color:#64748b;font-size:13px">The link works once and expires in 7 days. If it expires, ask the Design Hub team for a new one.</p>` +
    `<p style="color:#64748b;font-size:13px">Powered by Partnership. Driven by Innovation.</p>`;
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
      body: JSON.stringify({
        from: env.MAIL_FROM,
        to: [to],
        subject: "Set your password — BioMar Design Hub onboarding",
        text,
        html,
      }),
    });
    if (!res.ok) return { sent: false, error: `The email service answered ${res.status}.` };
    return { sent: true };
  } catch (err) {
    return { sent: false, error: (err as Error).message };
  }
}

async function readInvite(env: Env, token: string | null | undefined): Promise<Invite | null> {
  if (!token || !/^[0-9a-f]{64}$/.test(token)) return null;
  const raw = await env.AUTH_KV.get(`invite:${token}`);
  return raw ? (JSON.parse(raw) as Invite) : null;
}

async function handleGetInvite(request: Request, env: Env): Promise<Response> {
  const invite = await readInvite(env, new URL(request.url).searchParams.get("token"));
  if (!invite) return json({ error: "This link is invalid or has expired. Ask the Design Hub team for a new one." }, 404);
  const personRaw = await env.AUTH_KV.get(`person:${invite.personId}`);
  const name = personRaw ? (JSON.parse(personRaw) as Person).name : invite.email;
  return json({ ok: true, email: invite.email, name });
}

async function handleAcceptInvite(request: Request, env: Env): Promise<Response> {
  const body = (await safeJson(request)) as { token?: string; password?: string } | null;
  const invite = await readInvite(env, body?.token);
  if (!invite) return json({ error: "This link is invalid or has expired. Ask the Design Hub team for a new one." }, 404);
  const password = body?.password ?? "";
  if (password.length < 8) return json({ error: "Password must be at least 8 characters." }, 400);
  if (await getUser(env, invite.email)) {
    return json({ error: "This account already exists — sign in instead." }, 409);
  }

  const { hash, salt, iterations } = await hashPassword(password);
  await putUser(env, {
    email: invite.email,
    personId: invite.personId,
    role: invite.role,
    passwordHash: hash,
    salt,
    iterations,
  });
  // Single use: burn the link, then sign the person in.
  await env.AUTH_KV.delete(`invite:${body!.token}`);
  await env.AUTH_KV.delete(`invite-email:${invite.email}`);
  const session = await createSession(env, invite.email);
  return json({ ok: true, personId: invite.personId, role: invite.role }, 200, {
    "Set-Cookie": sessionCookieHeader(session),
  });
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
