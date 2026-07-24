// Cloudflare Pages Function — POST /api/publish
//
// This is the "GitHub as backend" write path. The admin edits people and
// assignments in the browser; publishing commits the updated dataset back to
// the repository as src/content/people.generated.json, so the repo stays the
// single source of truth and every change is versioned.
//
// Required environment variables (Cloudflare Pages → Settings → Env vars):
//   GITHUB_TOKEN  — a fine-grained PAT with "Contents: Read and write" on the repo
//   GITHUB_REPO   — e.g. "biomar-digital/onboarding-design"
//   GITHUB_BRANCH — e.g. "main" (the branch the site deploys from)
//
// Until these are set, the endpoint returns 501 and the app keeps changes in
// the browser (localStorage) — nothing is lost.

interface Env {
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string;
  GITHUB_BRANCH?: string;
}

const FILE_PATH = "src/content/people.generated.json";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { env, request } = context;

  if (!env.GITHUB_TOKEN || !env.GITHUB_REPO) {
    return json(
      {
        error:
          "Publishing not configured. Set GITHUB_TOKEN and GITHUB_REPO env vars in Cloudflare Pages.",
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

  // Look up the current file SHA (needed to update an existing file).
  let sha: string | undefined;
  const getRes = await fetch(`${api}?ref=${branch}`, { headers });
  if (getRes.ok) {
    const cur = (await getRes.json()) as { sha?: string };
    sha = cur.sha;
  }

  const content = btoa(
    unescape(encodeURIComponent(JSON.stringify(body.people, null, 2) + "\n")),
  );

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
    const text = await putRes.text();
    return json({ error: `GitHub API error: ${text}` }, putRes.status);
  }

  const data = (await putRes.json()) as { commit?: { sha?: string } };
  return json({ ok: true, commit: data.commit?.sha ?? null });
};

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}
