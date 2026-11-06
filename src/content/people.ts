import type { Person } from "./types";
import { journeyOrder } from "./journey";

// Seed people. In production these live in the repo as data and are edited by
// the admin (published back to GitHub). Progress accrues on the employee side.
//
// This is the initial dataset the app boots with; local changes are layered on
// top in the browser until "published".
export const seedPeople: Person[] = [
  {
    id: "admin",
    name: "BioMar Marketing",
    email: "marketing@biomar.com",
    role: "admin",
    profile: null,
    startDate: "2024-01-15",
    assignedModuleIds: [],
    progress: {},
  },
  {
    id: "emp-helene",
    name: "Helene",
    email: "",
    role: "employee",
    profile: null,
    startDate: "2026-11-06",
    // Every module available, in learning order.
    assignedModuleIds: journeyOrder,
    progress: {},
  },
];
