import type { Person } from "../content/types";

export function moduleStatus(person: Person, moduleId: string) {
  const p = person.progress[moduleId];
  if (!person.assignedModuleIds.includes(moduleId)) return "unassigned" as const;
  if (p?.completed) return "done" as const;
  return "todo" as const;
}

export function completionStats(person: Person) {
  const total = person.assignedModuleIds.length;
  const done = person.assignedModuleIds.filter(
    (id) => person.progress[id]?.completed,
  ).length;
  const pct = total === 0 ? 0 : Math.round((done / total) * 100);
  return { total, done, pct };
}
