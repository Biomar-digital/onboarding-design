# Deployment — Cloudflare Pages + GitHub

This app is built to run on **Cloudflare Pages** with the **GitHub repository as
its backend**. The static frontend and the serverless Pages Functions deploy
together; the repo stores the content and the published people/assignment data.

```
┌─────────────┐   reads bundled content   ┌──────────────────────┐
│  Browser    │ ────────────────────────► │  Cloudflare Pages     │
│  (designer) │                           │  static site (dist/)  │
└─────┬───────┘                           └──────────┬───────────┘
      │ admin: "Publish" / "Suggest"                 │ functions/api/*
      ▼                                               ▼
┌──────────────────────┐   commit    ┌──────────────────────────────┐
│ /api/publish (Worker)│ ──────────► │  GitHub repo (source of truth)│
│ /api/suggest (Worker)│ ──► Claude  │  src/content/*                │
└──────────────────────┘             └──────────────────────────────┘
```

## 1. Connect the repo to Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**.
2. Pick this repository and the branch to deploy (e.g. `main`).
3. Build settings:
   - **Framework preset:** Vite
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
4. Deploy. Cloudflare automatically picks up the functions in `functions/` and
   serves them at `/api/*`. The `public/_redirects` file keeps client-side
   routing working (all paths fall back to `index.html`).

## 2. Login — per-person accounts + admin-approved signup

Each person signs in with their own email and password, checked server-side
by the Worker (`/api/auth/*` routes in [`worker/auth.ts`](worker/auth.ts) and
[`worker/index.ts`](worker/index.ts)). New accounts are never created
directly — someone without one uses **Request access** on the login screen,
and an admin approves the request (choosing/creating their designer record
and setting a password) from **Admin → Signup requests**.

Credentials are the one piece of data that can't live in the GitHub-backed
content model (they must never round-trip through a public repo), so they're
kept in a small Cloudflare KV store instead.

### 2.1 Create the KV namespace

1. Cloudflare dashboard → **Workers & Pages** → **KV** → **Create a
   namespace** → name it e.g. `onboarding-auth`.
2. Copy its id and paste it into `wrangler.jsonc` → `kv_namespaces[0].id`
   (replacing `REPLACE_WITH_YOUR_KV_NAMESPACE_ID`), **or** bind it from the
   dashboard: your Worker's **Settings → Bindings → Add → KV Namespace**,
   with variable name `AUTH_KV`.

### 2.2 Bootstrap the first admin account

There's no account yet to approve the first one, so the first admin is
provisioned from two Worker secrets instead of the UI:

1. **Settings → Variables and Secrets** on the Worker → add
   `ADMIN_BOOTSTRAP_EMAIL` (e.g. `you@biomar.com`) and
   `ADMIN_BOOTSTRAP_PASSWORD` (a real password — encrypt this one as a
   **secret**, not a plaintext variable).
2. Sign in once with that email/password. The account is created
   automatically on that first login and works exactly like any other admin
   account from then on (you can change the password afterwards from the
   app). The bootstrap secrets only matter until that first sign-in.
3. Every other account — admin or employee — is created by an admin
   approving a signup request, never by editing secrets again.

### 2.3 How day-to-day accounts get created

1. A new hire opens the app → **Request access** → submits name + email.
2. An admin opens **Admin → Signup requests**, reviews it, picks (or leaves
   as "create a new designer record") who it maps to, sets an initial
   password (or generates one), and approves.
3. The admin shares that password with the new hire directly (Slack, in
   person, etc.) — there's no email-sending step. They can change it after
   signing in.

Until `AUTH_KV` is bound, `/api/auth/*` returns a clear "not configured"
error and the frontend falls back to the old pick-a-user demo sign-in so the
site stays explorable.

## Presentation materials & the embedded viewer

The original decks live in `/public/materials` and deploy as static assets, so
each has a public URL (e.g. `https://<site>/materials/design-hub-playbook.pptx`).
Each module embeds its deck **exactly as the original PowerPoint** using
Microsoft's Office Online viewer (`view.officeapps.live.com/op/embed.aspx`).

> ⚠️ **Important tradeoff:** the Office viewer works by having Microsoft's
> servers fetch the `.pptx` from that public URL. This means:
> - The decks must be **publicly reachable** for the viewer to render them.
> - If you put the whole site behind **Cloudflare Access**, Microsoft can no
>   longer fetch the files and the embedded viewer breaks (the "Open /
>   download" link still works for signed-in users).
>
> If the decks are confidential and must stay private, the alternative is to
> **export each deck to PDF** (PowerPoint → File → Export → PDF), drop the PDFs
> in `/public/materials`, and swap the viewer for a self-hosted PDF.js viewer —
> that renders exactly, stays private, and works behind Access. Ping me to make
> that switch.

## 3. Environment variables

Set these in **Pages → Settings → Environment variables** (Production).

| Variable | Needed for | Notes |
|---|---|---|
| `GITHUB_TOKEN` | `/api/publish` | Fine-grained PAT with **Contents: Read and write** on this repo only. |
| `GITHUB_REPO` | `/api/publish` | `biomar-digital/onboarding-design` |
| `GITHUB_BRANCH` | `/api/publish` | The deploy branch, e.g. `main`. |
| `ANTHROPIC_API_KEY` | `/api/suggest` | Enables the AI route suggestion. Without it, the admin still gets the deterministic rules-based suggestion. |
| `AUTH_KV` (binding, not a var) | `/api/auth/*` | KV namespace for login credentials, sessions and signup requests. See § Login above. |
| `ADMIN_BOOTSTRAP_EMAIL` / `ADMIN_BOOTSTRAP_PASSWORD` | `/api/auth/login` | One-time bootstrap for the very first admin account. Set as **secrets**. Safe to remove once that account exists. |

Until `GITHUB_TOKEN`/`GITHUB_REPO` are set, **Publish** returns a clear message
and admin changes stay saved in the browser (localStorage) — nothing is lost,
they just aren't committed yet.

## 4. How publishing works

- Admin edits people/assignments in the UI → stored in the browser.
- **Publish to GitHub** → `POST /api/publish` → the Worker commits the people
  dataset to `src/content/people.generated.json` on the deploy branch.
- That commit triggers a fresh Cloudflare Pages build, so the published data
  becomes the new baseline for everyone.

> **Wiring the published file as the read source (optional next step):** once
> you publish for the first time, `src/content/people.generated.json` exists in
> the repo. To have the app boot from it instead of the seed list, import it in
> `src/content/people.ts` and use it as `seedPeople`. It's intentionally left
> unwired so the first build has no missing-file dependency.

## 5. The AI suggestion endpoint

`POST /api/suggest` sends the profile, the admin's notes and the module catalog
to Claude and returns `{ moduleIds, rationale }`. The frontend validates the
ids against the catalog and always has a rules-based fallback, so the feature
degrades gracefully if the key is missing or the call fails.

## Security notes

- The `GITHUB_TOKEN` lives only in Cloudflare's encrypted env — it is never
  shipped to the browser. All GitHub writes happen server-side in the Worker.
- Scope the PAT to **this repository only** with the minimum
  **Contents: Read and write** permission.
- Passwords are never stored in plaintext: the Worker hashes them
  (PBKDF2-SHA256, 100k iterations, random salt per account) before writing to
  `AUTH_KV`. Sessions are an opaque random token in an `HttpOnly`, `Secure`
  cookie — the token itself is the KV lookup key, so there's nothing to forge.
- `/api/auth/signup-requests*`, the approve/reject routes, and
  `/api/admin/reset-password` all check the session's role is `admin`
  server-side — a non-admin session gets a 403 even if it guesses the URL.
