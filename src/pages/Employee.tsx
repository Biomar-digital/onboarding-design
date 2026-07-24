import { Link } from "react-router-dom";
import { useStore } from "../lib/store";
import { InfoPanel } from "../components/InfoPanel";
import { agenda } from "../content/agenda";
import { modulesById } from "../content/modules";
import { profilesById } from "../content/profiles";
import { completionStats, moduleStatus } from "../lib/progress";
import type { Person } from "../content/types";

export function Employee() {
  const { currentUser } = useStore();
  if (!currentUser) return null;
  const stats = completionStats(currentUser);

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <div className="space-y-6">
        <Header person={currentUser} pct={stats.pct} stats={stats} />
        {agenda.map((phase) => {
          const assigned = phase.moduleIds.filter((id) =>
            currentUser.assignedModuleIds.includes(id),
          );
          if (assigned.length === 0 && (phase.milestones?.length ?? 0) === 0)
            return null;
          return (
            <section key={phase.id} className="card p-5">
              <div className="mb-3 flex items-baseline justify-between">
                <div>
                  <h2 className="text-base font-bold text-biomar-navy">
                    {phase.title}
                  </h2>
                  <p className="text-sm text-slate-500">{phase.description}</p>
                </div>
                <span className="chip bg-biomar-ice text-biomar-blue">
                  {phase.timeframe}
                </span>
              </div>

              <div className="space-y-2">
                {assigned.map((id) => {
                  const m = modulesById[id];
                  const status = moduleStatus(currentUser, id);
                  const score = currentUser.progress[id]?.quizScore;
                  return (
                    <Link
                      key={id}
                      to={`/module/${id}`}
                      className="flex items-center gap-3 rounded-xl border border-slate-100 px-3 py-2.5 transition hover:border-biomar-swoosh hover:bg-biomar-ice/40"
                    >
                      <StatusDot done={status === "done"} />
                      <span className="flex-1">
                        <span className="block text-sm font-semibold text-biomar-navy">
                          {m.title}
                        </span>
                        <span className="block text-xs text-slate-400">
                          {m.summary}
                        </span>
                      </span>
                      <span className="text-right text-xs text-slate-400">
                        <span className="block">{m.estMinutes} min</span>
                        {status === "done" && score != null && (
                          <span className="font-semibold text-biomar-green">
                            quiz {score}%
                          </span>
                        )}
                      </span>
                    </Link>
                  );
                })}
              </div>

              {phase.milestones && phase.milestones.length > 0 && (
                <ul className="mt-3 space-y-1 border-t border-slate-100 pt-3">
                  {phase.milestones.map((ms, i) => (
                    <li
                      key={i}
                      className="flex items-center gap-2 text-sm text-slate-500"
                    >
                      <span className="text-biomar-swoosh">◦</span> {ms}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          );
        })}
      </div>

      <InfoPanel />
    </div>
  );
}

function Header({
  person,
  pct,
  stats,
}: {
  person: Person;
  pct: number;
  stats: ReturnType<typeof completionStats>;
}) {
  const profile = person.profile ? profilesById[person.profile] : null;
  return (
    <section className="card overflow-hidden">
      <div className="bg-gradient-to-r from-biomar-navy to-biomar-blue p-6 text-white">
        <p className="text-xs uppercase tracking-widest text-white/60">
          Your onboarding
        </p>
        <h1 className="mt-1 text-2xl font-bold">Hi, {person.name.split(" ")[0]}</h1>
        {profile && (
          <p className="mt-1 text-sm text-white/80">
            Track: <span className="font-semibold">{profile.label}</span>
          </p>
        )}
      </div>
      <div className="grid grid-cols-3 divide-x divide-slate-100">
        <Stat label="Modules" value={`${stats.done}/${stats.total}`} />
        <Stat label="Complete" value={`${pct}%`} />
        <Stat
          label="Avg quiz"
          value={stats.avgScore == null ? "—" : `${stats.avgScore}%`}
        />
      </div>
      <div className="h-2 w-full bg-slate-100">
        <div
          className="h-full bg-biomar-swoosh transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-4 py-3 text-center">
      <div className="text-xl font-bold text-biomar-navy">{value}</div>
      <div className="text-[11px] uppercase tracking-wide text-slate-400">
        {label}
      </div>
    </div>
  );
}

function StatusDot({ done }: { done: boolean }) {
  return (
    <span
      className={`grid h-6 w-6 shrink-0 place-items-center rounded-full text-xs ${
        done
          ? "bg-biomar-green text-white"
          : "border border-slate-300 text-transparent"
      }`}
    >
      ✓
    </span>
  );
}
