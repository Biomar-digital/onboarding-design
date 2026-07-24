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

## 2. Authentication — Cloudflare Access (Zero Trust)

The built-in login screen is a **demo** (pick-a-user, no password). For real
use, gate the whole site with **Cloudflare Access** so only BioMar identities
get in:

1. Zero Trust dashboard → **Access** → **Applications** → **Add a
   self-hosted application**, pointed at your Pages domain.
2. Add a policy: allow emails ending in `@biomar.com` (or your Entra/Google
   IdP group).
3. Access injects the signed-in user's email in the `Cf-Access-Authenticated-User-Email`
   header. Map that to a person record (extend the Worker with a
   `/api/me` route that returns the matching person) to drop the demo
   picker entirely.

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
- Put the publish/admin routes behind an Access policy that only allows the
  admin identity, so employees can't reach the write endpoints.
