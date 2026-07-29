import type { Person } from "./types";
import { profilesById } from "./profiles";
import { autoSchedule } from "../lib/schedule";

// Seed people. In production these live in the repo as data and are edited by
// the admin (published back to GitHub). Progress accrues on the employee side.
//
// This is the initial dataset the app boots with; local changes are layered on
// top in the browser until "published".
export const seedPeople: Person[] = [
  {
    id: "admin",
    name: "Andres Bernadou",
    email: "andresbernadou@gmail.com",
    role: "admin",
    profile: null,
    startDate: "2024-01-15",
    assignedModuleIds: [],
    progress: {},
  },
  {
    id: "emp-lucia",
    name: "Lucía Fernández",
    email: "lucia.demo@biomar.com",
    role: "employee",
    profile: "graphic-junior",
    startDate: "2026-07-20",
    assignedModuleIds: profilesById["graphic-junior"].recommendedModuleIds,
    // Demo calendar auto-built from her start date at ~2h/day (admin-editable).
    schedule: autoSchedule(profilesById["graphic-junior"].recommendedModuleIds, {
      startISO: "2026-07-20",
      dailyBudgetMin: 120,
      includeWeekends: false,
    }),
    progress: {
      "strategic-01": { completed: true, quizScore: 100 },
      "strategic-02": { completed: true, quizScore: 50 },
      "strategic-03": { completed: false, quizScore: null },
    },
  },
  {
    id: "emp-marco",
    name: "Marco Rossi",
    email: "marco.demo@biomar.com",
    role: "employee",
    profile: "motion",
    startDate: "2026-07-22",
    assignedModuleIds: profilesById["motion"].recommendedModuleIds,
    progress: {
      "strategic-01": { completed: true, quizScore: 100 },
    },
  },
];
