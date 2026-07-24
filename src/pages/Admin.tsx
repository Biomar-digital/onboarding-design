import { useState } from "react";
import { Link } from "react-router-dom";
import { useStore } from "../lib/store";
import { completionStats } from "../lib/progress";
import { profilesById } from "../content/profiles";
import { modules } from "../content/modules";
import type { Person } from "../content/types";

export function Admin() {
  const { people, dirty, publish, resetDemo } = useStore();
  const employees = people.filter((p) => p.role === "employee");
  const [msg, setMsg] = useState<string | null>(null);
  const [publishing, setPublishing] = useState(false);

  const doPublish = async () => {
    setPublishing(true);
    setMsg(null);
    const r = await publish();
    setMsg(r.message);
    setPublishing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-biomar-navy">
            Onboarding admin
          </h1>
          <p className="text-sm text-slate-500">
            Assign material per designer. The AI suggests a route from their
            profile; you review and approve.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/admin/new" className="btn-ghost">
            + Add designer
          </Link>
          <button
            className="btn-primary"
            onClick={doPublish}
            disabled={publishing}
          >
            {publishing
              ? "Publishing…"
              : dirty
                ? "Publish to GitHub"
                : "Published ✓"}
          </button>
        </div>
      </div>

      {msg && (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          {msg}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Designers onboarding" value={employees.length} />
        <MetricCard
          label="Avg completion"
          value={`${avg(employees.map((e) => completionStats(e).pct))}%`}
        />
        <MetricCard label="Modules in catalog" value={modules.length} />
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-4 py-3">Designer</th>
              <th className="px-4 py-3">Profile</th>
              <th className="px-4 py-3">Assigned</th>
              <th className="px-4 py-3">Progress</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {employees.map((p) => (
              <Row key={p.id} person={p} />
            ))}
            {employees.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                  No designers yet. Add one to start.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="text-right">
        <button
          className="text-xs text-slate-400 hover:text-red-500"
          onClick={() => {
            if (confirm("Reset all demo data to the seeded state?")) resetDemo();
          }}
        >
          Reset demo data
        </button>
      </div>
    </div>
  );
}

function Row({ person }: { person: Person }) {
  const stats = completionStats(person);
  const profile = person.profile ? profilesById[person.profile] : null;
  return (
    <tr className="hover:bg-slate-50/60">
      <td className="px-4 py-3">
        <div className="font-semibold text-biomar-navy">{person.name}</div>
        <div className="text-xs text-slate-400">{person.email}</div>
      </td>
      <td className="px-4 py-3 text-slate-600">
        {profile ? profile.label : "—"}
      </td>
      <td className="px-4 py-3 text-slate-600">
        {person.assignedModuleIds.length} modules
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full bg-biomar-swoosh"
              style={{ width: `${stats.pct}%` }}
            />
          </div>
          <span className="text-xs text-slate-500">{stats.pct}%</span>
        </div>
      </td>
      <td className="px-4 py-3 text-right">
        <Link
          to={`/admin/person/${person.id}`}
          className="text-sm font-semibold text-biomar-swoosh hover:underline"
        >
          Manage →
        </Link>
      </td>
    </tr>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-5">
      <div className="text-3xl font-bold text-biomar-navy">{value}</div>
      <div className="text-xs uppercase tracking-wide text-slate-400">
        {label}
      </div>
    </div>
  );
}

const avg = (xs: number[]) =>
  xs.length === 0 ? 0 : Math.round(xs.reduce((a, b) => a + b, 0) / xs.length);
