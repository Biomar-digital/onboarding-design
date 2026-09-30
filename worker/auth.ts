// ─────────────────────────────────────────────────────────────────────────────
// Auth helpers: password hashing, sessions and cookies for the Worker.
//
// Credentials live in Cloudflare KV (binding: AUTH_KV) — the one piece of this
// app's data that can't live in the GitHub-backed content model, since it must
// stay server-side and never round-trip through a public repo. Everything else
// (people, assignments, progress) is still "GitHub as backend" as before.
//
// KV layout:
//   user:<email>            → { email, personId, role, passwordHash, salt, iterations }
//   session:<token>         → { email, expires } (TTL'd)
//   signup:<id>             → { id, name, email, message, requestedAt, status }
// ─────────────────────────────────────────────────────────────────────────────

import type { Role } from "../src/content/types";

export interface AuthEnv {
  AUTH_KV: KVNamespace;
  ADMIN_BOOTSTRAP_EMAIL?: string;
  ADMIN_BOOTSTRAP_PASSWORD?: string;
}

export interface UserRecord {
  email: string;
  personId: string;
  role: Role;
  passwordHash: string;
  salt: string;
  iterations: number;
}

export interface SignupRequest {
  id: string;
  name: string;
  email: string;
  message: string;
  requestedAt: string;
  status: "pending" | "approved" | "rejected";
}

const PBKDF2_ITERATIONS = 100_000;
const SESSION_TTL_SECONDS = 30 * 24 * 60 * 60; // 30 days
const SESSION_COOKIE = "session";

// ── password hashing (Web Crypto PBKDF2-SHA256) ────────────────────────────
export async function hashPassword(
  password: string,
  salt?: string,
): Promise<{ hash: string; salt: string; iterations: number }> {
  const saltBytes = salt ? hexToBytes(salt) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: saltBytes, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    key,
    256,
  );
  return {
    hash: bytesToHex(new Uint8Array(bits)),
    salt: bytesToHex(saltBytes),
    iterations: PBKDF2_ITERATIONS,
  };
}

export async function verifyPassword(password: string, user: UserRecord): Promise<boolean> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: hexToBytes(user.salt), iterations: user.iterations, hash: "SHA-256" },
    key,
    256,
  );
  return timingSafeEqual(bytesToHex(new Uint8Array(bits)), user.passwordHash);
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function hexToBytes(hex: string): Uint8Array {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}

// ── users ────────────────────────────────────────────────────────────────
export async function getUser(env: AuthEnv, email: string): Promise<UserRecord | null> {
  const raw = await env.AUTH_KV.get(`user:${email.toLowerCase()}`);
  return raw ? (JSON.parse(raw) as UserRecord) : null;
}

export async function putUser(env: AuthEnv, user: UserRecord): Promise<void> {
  await env.AUTH_KV.put(`user:${user.email.toLowerCase()}`, JSON.stringify(user));
}

/** First login of the bootstrap admin auto-provisions their account from Worker
 * secrets (set only in the Cloudflare dashboard, never committed) — otherwise
 * there'd be no way to create the very first account. */
export async function ensureBootstrapAdmin(env: AuthEnv, email: string): Promise<void> {
  if (
    !env.ADMIN_BOOTSTRAP_EMAIL ||
    !env.ADMIN_BOOTSTRAP_PASSWORD ||
    email.toLowerCase() !== env.ADMIN_BOOTSTRAP_EMAIL.toLowerCase()
  ) {
    return;
  }
  const existing = await getUser(env, email);
  if (existing) return;
  const { hash, salt, iterations } = await hashPassword(env.ADMIN_BOOTSTRAP_PASSWORD);
  await putUser(env, {
    email: env.ADMIN_BOOTSTRAP_EMAIL,
    personId: "admin",
    role: "admin",
    passwordHash: hash,
    salt,
    iterations,
  });
}

// ── sessions ─────────────────────────────────────────────────────────────
export async function createSession(env: AuthEnv, email: string): Promise<string> {
  const token = bytesToHex(crypto.getRandomValues(new Uint8Array(32)));
  await env.AUTH_KV.put(
    `session:${token}`,
    JSON.stringify({ email, expires: Date.now() + SESSION_TTL_SECONDS * 1000 }),
    { expirationTtl: SESSION_TTL_SECONDS },
  );
  return token;
}

export async function getSessionUser(request: Request, env: AuthEnv): Promise<UserRecord | null> {
  const token = readCookie(request, SESSION_COOKIE);
  if (!token) return null;
  const raw = await env.AUTH_KV.get(`session:${token}`);
  if (!raw) return null;
  const session = JSON.parse(raw) as { email: string; expires: number };
  if (session.expires < Date.now()) return null;
  return getUser(env, session.email);
}

export async function destroySession(request: Request, env: AuthEnv): Promise<void> {
  const token = readCookie(request, SESSION_COOKIE);
  if (token) await env.AUTH_KV.delete(`session:${token}`);
}

export function sessionCookieHeader(token: string): string {
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${SESSION_TTL_SECONDS}`;
}

export function clearCookieHeader(): string {
  return `${SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

function readCookie(request: Request, name: string): string | null {
  const header = request.headers.get("Cookie");
  if (!header) return null;
  for (const part of header.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

// ── signup requests ──────────────────────────────────────────────────────
export async function createSignupRequest(
  env: AuthEnv,
  input: { name: string; email: string; message: string },
): Promise<SignupRequest> {
  const req: SignupRequest = {
    id: crypto.randomUUID(),
    name: input.name,
    email: input.email,
    message: input.message,
    requestedAt: new Date().toISOString(),
    status: "pending",
  };
  await env.AUTH_KV.put(`signup:${req.id}`, JSON.stringify(req));
  return req;
}

export async function listSignupRequests(env: AuthEnv): Promise<SignupRequest[]> {
  const list = await env.AUTH_KV.list({ prefix: "signup:" });
  const requests = await Promise.all(
    list.keys.map(async (k) => {
      const raw = await env.AUTH_KV.get(k.name);
      return raw ? (JSON.parse(raw) as SignupRequest) : null;
    }),
  );
  return requests
    .filter((r): r is SignupRequest => !!r)
    .sort((a, b) => b.requestedAt.localeCompare(a.requestedAt));
}

export async function getSignupRequest(env: AuthEnv, id: string): Promise<SignupRequest | null> {
  const raw = await env.AUTH_KV.get(`signup:${id}`);
  return raw ? (JSON.parse(raw) as SignupRequest) : null;
}

export async function putSignupRequest(env: AuthEnv, req: SignupRequest): Promise<void> {
  await env.AUTH_KV.put(`signup:${req.id}`, JSON.stringify(req));
}
