import type { WizardFlow } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// "Where does this go?" — the file-placement decision wizard from the Design
// Hub Folder Map (Figma). A straight transcription of that flowchart, in its
// original English: answer each question and the wizard narrows down to
// where a new file belongs.
// ─────────────────────────────────────────────────────────────────────────────
export const folderWizard: WizardFlow = {
  start: "is-product",
  nodes: {
    "is-product": {
      type: "question",
      prompt: "Is it a product?",
      yes: "enter-product-folder",
      no: "is-market",
    },
    "enter-product-folder": {
      type: "action",
      prompt: "Enter one of the Product folders (LARVIVA, INICIO, SmartCare, etc.)",
      next: "is-subproduct",
    },
    "is-subproduct": {
      type: "question",
      prompt: "Is it a sub-product?",
      yes: "subproduct-folder-exists",
      no: "category-question",
    },
    "subproduct-folder-exists": {
      type: "question",
      prompt: "Does the folder for the specific sub-product exist?",
      yes: "enter-subproduct-folder",
      no: "create-subfolder",
    },
    "enter-subproduct-folder": {
      type: "action",
      prompt: "Enter the sub-product folder",
      next: "category-question",
    },
    "create-subfolder": {
      type: "action",
      prompt: "Create sub-folder",
      next: "category-question",
    },
    "category-question": {
      type: "question",
      prompt:
        "Is it an advert, brochure, handout/leaflet, roll-up banner, digital banner, SoMe or presentation?",
      yes: "category-has-folder",
      no: "create-project-folder",
    },
    "category-has-folder": {
      type: "question",
      prompt: "Does that category have a folder?",
      yes: "enter-category-folder",
      no: "create-category-folder",
    },
    "enter-category-folder": {
      type: "action",
      prompt: "Enter folder",
      final: true,
    },
    "create-category-folder": {
      type: "action",
      prompt: "Create folder for that category (Eg. Ads)",
      final: true,
    },
    "create-project-folder": {
      type: "action",
      prompt:
        "Create folder for specific project following name convention (eg. 2026-07 EN_INICIO Plus Ad-A4)",
      final: true,
    },
    "is-market": {
      type: "question",
      prompt: "Is it for a specific market, for Digital Hub, for Corporate or for Global?",
      yes: "choose-specific-folder",
      no: "is-asset",
    },
    "choose-specific-folder": {
      type: "action",
      prompt: "Choose a specific folder among the main categories",
      options: [
        "SALMON",
        "EMEA",
        "ASIA",
        "LATAM",
        "GLOBAL",
        "DIGITAL HUB",
        "CORPORATE",
        "BioFarm",
        "Sustainability",
        "R&D",
      ],
      final: true,
    },
    "is-asset": {
      type: "question",
      prompt: "Is it an asset (logo, photo, template, guideline)?",
      yes: "enter-design-assets",
      no: "start-again",
    },
    "enter-design-assets": {
      type: "action",
      prompt: "Enter Design Assets",
      final: true,
    },
    "start-again": {
      type: "action",
      prompt: "Start again — it must belong to a category",
      restart: true,
    },
  },
};
