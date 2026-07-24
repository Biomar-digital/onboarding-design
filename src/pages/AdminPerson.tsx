import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useStore } from "../lib/store";
import { modules } from "../content/modules";
import { profiles, profilesById } from "../content/profiles";
import { suggestWithAI, recommendByProfile, type Suggestion } from "../lib/ai";
import { completionStats } from "../lib/progress";
import type { Person, ProfileId } from "../content/types";

const CATEGORY_LABEL: Record<string, string> = {
  foundations: "Foundations",
  process: "The Process",
  brand: "Brand & Guidelines",
  tools: "Tools & Ways of Working",
  people: "People & Integration",
};

// Handles both editing an existing person (/admin/person/:id) and creating a
// new one (/admin/new).
export function AdminPerson({ mode }: { mode: "edit" | "new" }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const { people, upsertPerson, removePerson } = useStore();

  const existing = mode === "edit" ? people.find((p) => p.id === id) : undefined;

  const [name, setName] = useState(existing?.name ?? "");
  const [email, setEmail] = useState(existing?.email ?? "");
  const [profile, setProfile] = useState<ProfileId | "">(
    existing?.profile ?? "",
  );
  const [notes, setNotes] = useState("");
  const [assigned, setAssigned] = useState<string[]>(
    existing?.assignedModuleIds ?? [],
  );
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [loadingAI, setLoadingAI] = useState(false);

  if (mode === "edit" && !existing) {
    return (
      <div className="card p-8 text-center text-slate-500">
        Person not found.{" "}
        <Link to="/admin" className="text-biomar-swoosh">
          Back
        </Link>
      </div>
    );
  }

  const toggle = (moduleId: string) =>
    setAssigned((a) =>
      a.includes(moduleId)
        ? a.filter((x) => x !== moduleId)
        : [...a, moduleId],
    );

  const runSuggest = async () => {
    setLoadingAI(true);
    const s = await suggestWithAI(profile || null, notes);
    setSuggestion(s);
    setLoadingAI(false);
  };

  const applySuggestion = () => {
    if (suggestion) setAssigned(suggestion.moduleIds);
  };

  // Instant rules preview whenever the profile changes, before hitting AI.
  const preview = useMemo(
    () => (profile ? recommendByProfile(profile, notes) : null),
    [profile, notes],
  );

  const save = () => {
    if (!name.trim() || !email.trim()) {
      alert("Name and email are required.");
      return;
    }
    const person: Person = existing
      ? {
          ...existing,
          name,
          email,
          profile: profile || null,
          assignedModuleIds: assigned,
        }
      : {
          id: `emp-${Date.now().toString(36)}`,
          name,
          email,
          role: "employee",
          profile: profile || null,
          startDate: new Date().toISOString().slice(0, 10),
          assignedModuleIds: assigned,
          progress: {},
        };
    upsertPerson(person);
    navigate("/admin");
  };

  const byCategory = modules.reduce<Record<string, typeof modules>>(
    (acc, m) => {
      (acc[m.category] ??= []).push(m);
      return acc;
    },
    {},
  );

  return (
    <div className="space-y-6">
      <Link to="/admin" className="text-sm text-slate-400 hover:text-biomar-swoosh">
        ← Back to admin
      </Link>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        {/* Left: identity + AI */}
        <div className="space-y-4">
          <div className="card p-5">
            <h1 className="text-lg font-bold text-biomar-navy">
              {mode === "new" ? "Add designer" : existing!.name}
            </h1>
            <div className="mt-4 space-y-3">
              <Field label="Name">
                <input
                  className="input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Full name"
                />
              </Field>
              <Field label="Email">
                <input
                  className="input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@biomar.com"
                />
              </Field>
              <Field label="Profile / level">
                <select
                  className="input"
                  value={profile}
                  onChange={(e) => setProfile(e.target.value as ProfileId | "")}
                >
                  <option value="">— Select a profile —</option>
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </Field>
              {profile && (
                <p className="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
                  {profilesById[profile].description}
                </p>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="flex items-center gap-2 text-sm font-bold text-biomar-navy">
              <span>✨</span> AI-suggested route
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              The AI proposes modules from the profile and your notes. You
              review and apply — nothing is assigned without your approval.
            </p>
            <Field label="Context / notes (optional)">
              <textarea
                className="input h-20 resize-none"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Senior, strong in motion, joining for the salmon campaigns…"
              />
            </Field>
            <button
              className="btn-accent mt-3 w-full"
              onClick={runSuggest}
              disabled={loadingAI}
            >
              {loadingAI ? "Thinking…" : "Suggest modules"}
            </button>

            {preview && !suggestion && (
              <p className="mt-3 text-xs text-slate-400">
                Rules preview: {preview.moduleIds.length} modules from “
                {profilesById[profile as ProfileId].label}”.
              </p>
            )}

            {suggestion && (
              <div className="mt-3 rounded-xl border border-biomar-swoosh/30 bg-biomar-ice/40 p-3">
                <div className="flex items-center justify-between">
                  <span className="chip bg-biomar-navy text-white">
                    {suggestion.source === "ai" ? "AI" : "Rules"} ·{" "}
                    {suggestion.moduleIds.length} modules
                  </span>
                  <button
                    className="text-xs font-semibold text-biomar-swoosh hover:underline"
                    onClick={applySuggestion}
                  >
                    Apply →
                  </button>
                </div>
                <p className="mt-2 text-xs text-slate-600">
                  {suggestion.rationale}
                </p>
              </div>
            )}
          </div>

          {existing && (
            <div className="card p-5">
              <h2 className="text-sm font-bold text-biomar-navy">Progress</h2>
              <ProgressSummary person={existing} />
              <button
                className="mt-4 text-xs text-slate-400 hover:text-red-500"
                onClick={() => {
                  if (confirm(`Remove ${existing.name}?`)) {
                    removePerson(existing.id);
                    navigate("/admin");
                  }
                }}
              >
                Remove designer
              </button>
            </div>
          )}
        </div>

        {/* Right: module assignment */}
        <div className="card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-bold text-biomar-navy">
              Assigned modules
            </h2>
            <span className="chip bg-biomar-ice text-biomar-blue">
              {assigned.length} selected
            </span>
          </div>

          <div className="space-y-5">
            {Object.entries(byCategory).map(([cat, mods]) => (
              <div key={cat}>
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">
                    {CATEGORY_LABEL[cat] ?? cat}
                  </h3>
                  <button
                    className="text-[11px] text-biomar-swoosh hover:underline"
                    onClick={() => {
                      const ids = mods.map((m) => m.id);
                      const allOn = ids.every((i) => assigned.includes(i));
                      setAssigned((a) =>
                        allOn
                          ? a.filter((i) => !ids.includes(i))
                          : [...new Set([...a, ...ids])],
                      );
                    }}
                  >
                    toggle all
                  </button>
                </div>
                <div className="space-y-1.5">
                  {mods.map((m) => {
                    const on = assigned.includes(m.id);
                    const suggested = suggestion?.moduleIds.includes(m.id);
                    return (
                      <label
                        key={m.id}
                        className={`flex cursor-pointer items-start gap-3 rounded-xl border px-3 py-2.5 transition ${
                          on
                            ? "border-biomar-swoosh bg-biomar-ice/40"
                            : "border-slate-200 hover:border-slate-300"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={on}
                          onChange={() => toggle(m.id)}
                          className="mt-0.5 accent-biomar-swoosh"
                        />
                        <span className="flex-1">
                          <span className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-biomar-navy">
                              {m.title}
                            </span>
                            {suggested && (
                              <span className="chip bg-biomar-swoosh/15 text-biomar-swoosh">
                                ✨ suggested
                              </span>
                            )}
                          </span>
                          <span className="block text-xs text-slate-400">
                            {m.summary}
                          </span>
                        </span>
                        <span className="text-xs text-slate-400">
                          {m.estMinutes}m
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
            <span className="text-xs text-slate-400">
              Total time ≈{" "}
              {modules
                .filter((m) => assigned.includes(m.id))
                .reduce((s, m) => s + m.estMinutes, 0)}{" "}
              min
            </span>
            <div className="flex gap-2">
              <Link to="/admin" className="btn-ghost">
                Cancel
              </Link>
              <button className="btn-primary" onClick={save}>
                {mode === "new" ? "Create & assign" : "Save assignment"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </span>
      {children}
    </label>
  );
}

function ProgressSummary({ person }: { person: Person }) {
  const stats = completionStats(person);
  return (
    <div className="mt-2 space-y-2">
      <div className="flex items-center gap-2">
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full bg-biomar-swoosh"
            style={{ width: `${stats.pct}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-slate-500">
          {stats.pct}%
        </span>
      </div>
      <p className="text-xs text-slate-400">
        {stats.done}/{stats.total} modules ·{" "}
        {stats.avgScore == null ? "no quizzes yet" : `avg quiz ${stats.avgScore}%`}
      </p>
    </div>
  );
}
