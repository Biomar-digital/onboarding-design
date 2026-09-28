import type { WizardFlow } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// "¿Dónde guardo esto?" — the file-placement decision wizard from the Design
// Hub Folder Map (Figma). A straight transcription of that flowchart: answer
// each question and the wizard narrows down to where a new file belongs.
// ─────────────────────────────────────────────────────────────────────────────
export const folderWizard: WizardFlow = {
  start: "is-product",
  nodes: {
    "is-product": {
      type: "question",
      prompt: "¿Es un producto?",
      yes: "enter-product-folder",
      no: "is-market",
    },
    "enter-product-folder": {
      type: "action",
      prompt: "Entrá a una de las carpetas de Producto (LARVIVA, INICIO, SmartCare, etc.)",
      next: "is-subproduct",
    },
    "is-subproduct": {
      type: "question",
      prompt: "¿Es un sub-producto?",
      yes: "subproduct-folder-exists",
      no: "category-question",
    },
    "subproduct-folder-exists": {
      type: "question",
      prompt: "¿Existe la carpeta para ese sub-producto específico?",
      yes: "enter-subproduct-folder",
      no: "create-subfolder",
    },
    "enter-subproduct-folder": {
      type: "action",
      prompt: "Entrá a la carpeta del sub-producto",
      next: "category-question",
    },
    "create-subfolder": {
      type: "action",
      prompt: "Creá la sub-carpeta",
      next: "category-question",
    },
    "category-question": {
      type: "question",
      prompt:
        "¿Es un advert, brochure, handout/leaflet, roll-up banner, digital banner, SoMe o presentation?",
      yes: "category-has-folder",
      no: "create-project-folder",
    },
    "category-has-folder": {
      type: "question",
      prompt: "¿Esa categoría ya tiene carpeta?",
      yes: "enter-category-folder",
      no: "create-category-folder",
    },
    "enter-category-folder": {
      type: "action",
      prompt: "Entrá a la carpeta",
      final: true,
    },
    "create-category-folder": {
      type: "action",
      prompt: "Creá la carpeta para esa categoría (ej. Ads)",
      final: true,
    },
    "create-project-folder": {
      type: "action",
      prompt:
        "Creá la carpeta para el proyecto específico siguiendo la convención de nombres (ej. 2026-07 EN_INICIO Plus Ad-A4)",
      final: true,
    },
    "is-market": {
      type: "question",
      prompt: "¿Es para un mercado específico, para Digital Hub, para Corporate o para Global?",
      yes: "choose-specific-folder",
      no: "is-asset",
    },
    "choose-specific-folder": {
      type: "action",
      prompt: "Elegí la carpeta específica entre las categorías principales",
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
      prompt: "¿Es un asset (logo, foto, plantilla, guideline)?",
      yes: "enter-design-assets",
      no: "start-again",
    },
    "enter-design-assets": {
      type: "action",
      prompt: "Entrá a Design Assets",
      final: true,
    },
    "start-again": {
      type: "action",
      prompt: "Empezá de nuevo: tiene que pertenecer a alguna categoría",
      restart: true,
    },
  },
};
