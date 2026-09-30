# BioMar Design Hub — Designer Onboarding Platform

An internal onboarding platform for designers joining BioMar's Global Marketing
**Design Hub**. It gives every new designer a personalized learning route —
material to study, knowledge-check quizzes, hands-on exercises, an ordered
agenda, and an always-on reference panel — while giving the admin (you, with AI
help) control over exactly what each person is assigned.

> _Powered by Partnership. Driven by Innovation._

## Two sides

| | What it does |
|---|---|
| **Employee** | Sees only their assigned modules, laid out as an onboarding journey (Foundations → Process → Brand → Tools → People → First Tasks). Reads the material, does the exercises, takes the quiz to mark a module complete. A persistent **Always-on info** panel (who to ask, file naming, versioning, channels, brand rules, platforms) is always one click away. |
| **Admin** | Sees every designer and their progress. Opens a person, picks a **profile/level**, and gets an **AI-suggested route** — reviews it, adjusts the module selection, and approves. Publishing commits the updated assignments back to GitHub. |

The AI **suggests, you approve** — nothing is ever assigned automatically.

## Content = data in the repo ("GitHub as backend")

All learning content and people data live as typed data under
[`src/content/`](src/content/) and are the single source of truth:

- `modules.ts` — the full curriculum (sections, quizzes, exercises), sourced
  from the Onboarding Plan, Playbook, Strategic Presentation and Global
  Marketing deck.
- `agenda.ts` — the phased onboarding journey.
- `profiles.ts` — role/level profiles that seed the AI recommendation.
- `infoPanel.ts` — the persistent reference panel.
- `people.ts` — the seed people dataset.
- `types.ts` — the content model.

To edit material, edit these files and commit. Admin changes made in the UI are
published back to the repo via a Cloudflare Pages Function (see below).

## Tech

- **React + Vite + TypeScript + Tailwind** frontend → deploys to **Cloudflare Pages**.
- **Cloudflare Worker** ([`worker/index.ts`](worker/index.ts)) for the write
  path (commit to GitHub), optional AI suggestions (Anthropic), and login.
- The repo is the backend for all learning content and people data — no
  database to run. The one exception is login credentials (password hashes,
  sessions, pending signup requests), which live in a small Cloudflare KV
  store (`AUTH_KV`) since they can't round-trip through a public repo. See
  [DEPLOYMENT.md](DEPLOYMENT.md) § Login.

## Local development

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # typecheck + production build to dist/
npm run preview  # serve the production build
```

### Sign-in

Each person has their own account: email + password, checked server-side by
the Worker. There's no shared password and no admin-created accounts —
someone without one uses **Request access** on the login screen, and an admin
approves the request (sets the password) from **Admin → Signup requests**.
See [DEPLOYMENT.md](DEPLOYMENT.md) § Login for how to provision the first
(bootstrap) admin account and the `AUTH_KV` store this needs.

Running `npm run dev` or a static preview with no Worker behind it (no
`/api/*` routes answering) falls back to a **demo sign-in** — pick any seeded
user, no password — purely so the UI stays explorable without a backend. A
real deployment never shows this fallback once `AUTH_KV` is configured.

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the full Cloudflare Pages + GitHub
setup, environment variables, auth, and how the AI/publish endpoints turn on.
