import type { Person } from "../content/types";
import { modules, modulesById } from "../content/modules";
import { agenda } from "../content/agenda";

// Canonical learning order: agenda phase order, then module order within each
// phase, with any leftover assigned modules appended in catalog order.
export function orderedAssigned(assignedIds: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const phase of agenda) {
    for (const id of phase.moduleIds) {
      if (assignedIds.includes(id) && !seen.has(id)) {
        seen.add(id);
        out.push(id);
      }
    }
  }
  for (const m of modules) {
    if (assignedIds.includes(m.id) && !seen.has(m.id)) {
      seen.add(m.id);
      out.push(m.id);
    }
  }
  return out;
}

// ── date helpers ────────────────────────────────────────────────────────────
export function toISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}
export function parseISO(s: string): Date {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}
function isWeekend(d: Date): boolean {
  const day = d.getDay();
  return day === 0 || day === 6;
}
export function addDays(d: Date, n: number): Date {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}
export function formatDay(iso: string): string {
  return parseISO(iso).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "2-digit",
    month: "short",
  });
}

export interface AutoOptions {
  startISO: string;
  dailyBudgetMin: number;
  includeWeekends: boolean;
}

// Distribute the assigned modules across days, filling each day up to the
// minutes budget before moving on. A module longer than the budget still gets
// its own day.
export function autoSchedule(
  assignedIds: string[],
  opts: AutoOptions,
): Record<string, string> {
  const order = orderedAssigned(assignedIds);
  const map: Record<string, string> = {};
  let day = parseISO(opts.startISO);
  const advance = () => {
    do {
      day = addDays(day, 1);
    } while (!opts.includeWeekends && isWeekend(day));
  };
  // ensure the very first day is valid
  while (!opts.includeWeekends && isWeekend(day)) day = addDays(day, 1);

  let load = 0;
  for (const id of order) {
    const min = modulesById[id]?.estMinutes ?? 30;
    if (load > 0 && load + min > opts.dailyBudgetMin) {
      advance();
      load = 0;
    }
    map[id] = toISO(day);
    load += min;
  }
  return map;
}

export interface DayGroup {
  date: string;
  moduleIds: string[];
  totalMin: number;
}

// Group a person's scheduled modules by day (chronological) + the unscheduled.
export function groupByDay(person: Person): {
  days: DayGroup[];
  unscheduled: string[];
} {
  const schedule = person.schedule ?? {};
  const byDate: Record<string, string[]> = {};
  const unscheduled: string[] = [];
  for (const id of person.assignedModuleIds) {
    const date = schedule[id];
    if (date) (byDate[date] ??= []).push(id);
    else unscheduled.push(id);
  }
  const days: DayGroup[] = Object.entries(byDate)
    .map(([date, ids]) => ({
      date,
      moduleIds: ids.sort(
        (a, b) =>
          orderedAssigned(person.assignedModuleIds).indexOf(a) -
          orderedAssigned(person.assignedModuleIds).indexOf(b),
      ),
      totalMin: ids.reduce((s, id) => s + (modulesById[id]?.estMinutes ?? 0), 0),
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
  return { days, unscheduled };
}

export function formatLoad(min: number): string {
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}
