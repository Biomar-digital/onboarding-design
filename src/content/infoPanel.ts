import type { InfoPanelGroup } from "./types";

// The persistent reference panel — always available on the employee side so a
// new designer never has to dig for the essentials mid-task.
export const infoPanel: InfoPanelGroup[] = [
  {
    id: "contacts",
    title: "Who to ask",
    icon: "👥",
    rows: [
      { label: "Datasheets", value: "Kat", hint: "katmi@biomar.com" },
      { label: "R&D", value: "Elisabeth", hint: "eliaa@biomar.com" },
      { label: "LARVIVA", value: "Daniela", hint: "vdv@biomar.com" },
      { label: "SmartCare (salmon)", value: "Torunn" },
      { label: "Technical", value: "Iannis · Andreina · Bruno · Ewan" },
    ],
  },
  {
    id: "naming",
    title: "File naming",
    icon: "🗂️",
    rows: [
      { label: "Design files", value: "Year-Month Language_Market Brand/Product-FileType" },
      { label: "Example", value: "2022-03 ES_Orbit_Brochure" },
      { label: "Images", value: "What it is + license/number", hint: "Trout_Smolt_Denmark" },
    ],
  },
  {
    id: "versioning",
    title: "Versioning",
    icon: "🔖",
    rows: [
      { label: "DRAFT", value: "Concept — don't show the counterpart" },
      { label: "PROOF", value: "Review version sent out (PROOF2, PROOF3…)" },
      { label: "FINAL", value: "Approved → PRINT or DIGITAL" },
    ],
  },
  {
    id: "channels",
    title: "Which channel?",
    icon: "💬",
    rows: [
      { label: "Email", value: "New task/project · feedback" },
      { label: "Teams", value: "Follow-ups" },
      { label: "Meeting", value: "Define/clarify · deep review" },
    ],
  },
  {
    id: "brand",
    title: "Brand quick rules",
    icon: "🎨",
    rows: [
      { label: "BB opacity", value: "Never — looks purple. Use black opacity" },
      { label: "Gradients", value: "Avoid — print poorly" },
      { label: "Packaging top", value: "Always BioMar Blue" },
      { label: "Guidelines live on", value: "The Pond" },
    ],
  },
  {
    id: "platforms",
    title: "Platforms",
    icon: "🧰",
    rows: [
      { label: "Accesses & lists", value: "Loop Link" },
      { label: "Brand assets (DAM)", value: "The Pond (Kontainer)" },
      { label: "Website content", value: "Umbraco" },
      { label: "Stock", value: "Adobe Stock · Shutterstock · Flaticon" },
    ],
  },
];
