import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useStore } from "../lib/store";
import { InfoPanel } from "../components/InfoPanel";
import { agenda } from "../content/agenda";
import { modulesById } from "../content/modules";
import { profilesById } from "../content/profiles";
import { completionStats, moduleStatus } from "../lib/progress";
import { groupByDay, formatDay, formatLoad } from "../lib/schedule";
import type { Person } from "../content/types";

export function Employee() {
  const { currentUser } = useStore();
  const hasSchedule =
    !!currentUser && Object.keys(currentUser.schedule ?? {}).length > 0;
  const [view, setView] = useState<"phase" | "date">(
    hasSchedule ? "date" : "phase",
  );
  if (!currentUser) return null;
  const stats = completionStats(currentUser);

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <div className="space-y-6">
        <Header person={currentUser} pct={stats.pct} stats={stats} />

        <div className="inline-flex items-center gap-1 rounded-xl bg-white p-1 shadow-card ring-1 ring-slate-100">
          <ViewTab active={view === "phase"} onClick={() => setView("phase")}>
            By phase
          </ViewTab>
          <ViewTab active={view === "date"} onClick={() => setView("date")}>
            📅 By date
          </ViewTab>
        </div>

        {view === "date" ? (
          <ScheduleView person={currentUser} />
        ) : (
          <PhaseView person={currentUser} />
        )}
      </div>

      <InfoPanel />
    </div>
  );
}

function ViewTab({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition ${
        active
          ? "bg-biomar-navy text-white"
          : "text-slate-500 hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
  );
}

// Row shared by both views.
function ModuleRow({
  person,
  moduleId,
}: {
  person: Person;
  moduleId: string;
}) {
  const m = modulesById[moduleId];
  const status = moduleStatus(person, moduleId);
  const score = person.progress[moduleId]?.quizScore;
  return (
    <Link
      to={`/module/${moduleId}`}
      className="flex items-center gap-3 rounded-xl border border-slate-100 px-3 py-2.5 transition hover:border-biomar-swoosh hover:bg-biomar-ice/40"
    >
      <StatusDot done={status === "done"} />
      <span className="flex-1">
        <span className="block text-sm font-semibold text-biomar-navy">
          {m.title}
        </span>
        <span className="block text-xs text-slate-400">{m.summary}</span>
      </span>
      <span className="text-right text-xs text-slate-400">
        <span className="block">{m.estMinutes} min</span>
        {status === "done" && score != null && (
          <span className="font-semibold text-biomar-green">quiz {score}%</span>
        )}
      </span>
    </Link>
  );
}

// ── By phase ─────────────────────────────────────────────────────────────────
function PhaseView({ person }: { person: Person }) {
  return (
    <>
      {agenda.map((phase) => {
        const assigned = phase.moduleIds.filter((id) =>
          person.assignedModuleIds.includes(id),
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
              {assigned.map((id) => (
                <ModuleRow key={id} person={person} moduleId={id} />
              ))}
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
    </>
  );
}

// ── By date (calendar) ───────────────────────────────────────────────────────
function ScheduleView({ person }: { person: Person }) {
  const { days, unscheduled } = groupByDay(person);

  if (days.length === 0) {
    return (
      <section className="card p-6 text-center">
        <p className="text-sm text-slate-500">
          No calendar dates set yet. Your onboarding lead will schedule your
          modules — meanwhile, switch to{" "}
          <span className="font-semibold text-biomar-navy">By phase</span> to
          start.
        </p>
      </section>
    );
  }

  return (
    <>
      {days.map((day) => {
        const done = day.moduleIds.filter(
          (id) => person.progress[id]?.completed,
        ).length;
        return (
          <section key={day.date} className="card overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 bg-biomar-ice/40 px-5 py-3">
              <h2 className="text-sm font-bold text-biomar-navy">
                {formatDay(day.date)}
              </h2>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">
                  {done}/{day.moduleIds.length} done
                </span>
                <span className="chip bg-biomar-navy text-white">
                  {formatLoad(day.totalMin)}
                </span>
              </div>
            </div>
            <div className="space-y-2 p-4">
              {day.moduleIds.map((id) => (
                <ModuleRow key={id} person={person} moduleId={id} />
              ))}
            </div>
          </section>
        );
      })}

      {unscheduled.length > 0 && (
        <section className="card p-5">
          <h2 className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
            Not scheduled yet
          </h2>
          <div className="space-y-2">
            {unscheduled.map((id) => (
              <ModuleRow key={id} person={person} moduleId={id} />
            ))}
          </div>
        </section>
      )}
    </>
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
