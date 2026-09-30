// ─────────────────────────────────────────────────────────────────────────────
// Thin client for the Worker's /api/auth/* and /api/admin/* routes.
//
// These only work once the app is deployed for real to Cloudflare, with the
// AUTH_KV namespace bound (see DEPLOYMENT.md). A static-only preview (no
// Worker behind it) has nothing at these paths, so calls here fail — callers
// use `isBackendAvailable` to tell "no server" apart from "wrong password".
// ─────────────────────────────────────────────────────────────────────────────

export interface SessionInfo {
  ok: boolean;
  email?: string;
  personId?: string;
  role?: "admin" | "employee";
}

export interface SignupRequestRow {
  id: string;
  name: string;
  email: string;
  message: string;
  requestedAt: string;
  status: "pending" | "approved" | "rejected";
}

class BackendUnavailableError extends Error {}

async function call(path: string, init?: RequestInit): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(path, { credentials: "include", ...init });
  } catch (err) {
    throw new BackendUnavailableError((err as Error).message);
  }
  // No Worker behind this host (e.g. a static preview) → the SPA fallback
  // serves index.html for any unknown path, so we get HTML back, not JSON.
  const contentType = res.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new BackendUnavailableError("No API backend at this URL.");
  }
  return res;
}

export function isBackendUnavailable(err: unknown): boolean {
  return err instanceof BackendUnavailableError;
}

export async function fetchMe(): Promise<SessionInfo> {
  const res = await call("/api/auth/me");
  return res.json();
}

export async function login(
  email: string,
  password: string,
): Promise<{ ok: true; email: string; personId: string; role: "admin" | "employee" } | { ok: false; error: string }> {
  const res = await call("/api/auth/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Login failed (${res.status}).` };
  return data;
}

export async function logout(): Promise<void> {
  await call("/api/auth/logout", { method: "POST" });
}

export async function requestSignup(
  name: string,
  email: string,
  message: string,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const res = await call("/api/auth/signup-request", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name, email, message }),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Request failed (${res.status}).` };
  return { ok: true };
}

export async function listSignupRequests(): Promise<SignupRequestRow[]> {
  const res = await call("/api/auth/signup-requests");
  if (!res.ok) throw new Error((await res.json()).error ?? "Could not load signup requests.");
  const data = await res.json();
  return data.requests;
}

export async function approveSignup(
  id: string,
  personId: string,
  password: string,
  role: "admin" | "employee",
): Promise<{ ok: true } | { ok: false; error: string }> {
  const res = await call(`/api/auth/signup-requests/${id}/approve`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ personId, password, role }),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Approval failed (${res.status}).` };
  return { ok: true };
}

export async function rejectSignup(id: string): Promise<{ ok: true } | { ok: false; error: string }> {
  const res = await call(`/api/auth/signup-requests/${id}/reject`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Failed (${res.status}).` };
  return { ok: true };
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const res = await call("/api/auth/change-password", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ currentPassword, newPassword }),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Failed (${res.status}).` };
  return { ok: true };
}

export async function adminResetPassword(
  email: string,
  newPassword: string,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const res = await call("/api/admin/reset-password", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, newPassword }),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, error: data.error ?? `Failed (${res.status}).` };
  return { ok: true };
}
