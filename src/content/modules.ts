import type { Module } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// The onboarding curriculum.
//
// Each chapter (see chapters.ts) is exactly one source document. The modules
// below are that document's own content, cut into items that follow its
// original slide/page order end to end — nothing skipped, nothing reordered
// across topics. A handful of modules aren't sourced from one document (e.g.
// the tools map) and carry chapterId: null — they render as standalone
// reference material instead of inside a chapter.
// ─────────────────────────────────────────────────────────────────────────────

const SLICE = "/materials/slices";
const BRIEF_TEMPLATE = {
  title: "Brief Template",
  file: "/materials/design-hub-brief-template.potx",
};

export const modules: Module[] = [
  // ═══════════════════════════════════════════════════════════════════════════
  // WELCOME — not sourced from a document; always the very first thing.
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "welcome",
    chapterId: null,
    title: "Welcome to BioMar",
    summary: "A welcome message from our CEO, Carlos Díaz, to BioMar.",
    estMinutes: 10,
    sections: [
      {
        heading: "A welcome from our CEO",
        body: [
          "Before diving into how the Design Hub works, take a moment to hear from Carlos Díaz, CEO of BioMar, welcoming you to the company.",
        ],
      },
      {
        note: "Powered by Partnership. Driven by Innovation.",
      },
    ],
    quiz: [],
    exercises: [],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Design Hub — Strategic Presentation (17 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "strategic-01",
    chapterId: "strategic",
    title: "Who We Are",
    summary:
      "The cover, what the Design Hub is, and the team behind it.",
    estMinutes: 15,
    material: {
      file: `${SLICE}/strategic--01-who-we-are.pptx`,
      type: "pptx",
      range: "Slides 1–3",
    },
    sections: [
      {
        heading: "A centralized creative & brand support function",
        bullets: [
          "Supports both global and local communication needs",
          "Ensures brand consistency across markets and channels",
          "Provides strategic and operational design support",
          "Cross-functional collaboration with marketing, sustainability, corporate, product and technical teams, plus external partners",
          "Combines creative execution, brand governance and technical, technology-based knowledge",
        ],
      },
      {
        heading: "By the numbers",
        note: "The Design Hub completes 1000+ tasks annually — 489 in 2025, +71% vs the previous year — from a few hours to several months of work, 14 hours every weekday.",
      },
      {
        heading: "Who we are",
        bullets: [
          "Isidora Silva Ch. — Graphic Designer. 3 years at BioMar. Graphic & print design (external and internal). Supporting brand consistency across markets. Works with campaigns & corporate communication.",
          "Andres Bernadou — Multimedia Designer. 2 years at BioMar. Video & digital design (external and internal). Supporting storytelling and concept creation across markets. Works with campaigns & corporate communication.",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "What does the Design Hub combine? (select all)",
        options: [
          "Creative execution",
          "Brand governance",
          "Technical, technology-based knowledge",
          "Sales forecasting",
        ],
        correct: [0, 1, 2],
        explanation:
          "The Design Hub combines creative execution, brand governance and technical/technology-based knowledge — not sales forecasting.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "The Design Hub completes more than 1000 tasks annually.",
        options: ["True", "False"],
        correct: [0],
        explanation:
          "True — the Hub does more than 1000 tasks a year, ranging from a few hours to several months of work.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Team & function recap",
        prompt:
          "In one or two sentences, write what the Design Hub is and who's currently on it.",
        successCriteria: [
          "Mentions the centralized creative & brand support function",
          "Names the current team",
        ],
      },
    ],
  },
  {
    id: "strategic-02",
    chapterId: "strategic",
    title: "Strategy, Role & Responsibilities",
    summary:
      "Where the Design Hub sits in the 2028 strategy house, its five pillars, and everything it's responsible for.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/strategic--02-strategy-role-responsibilities.pptx`,
      type: "pptx",
      range: "Slides 4–8",
    },
    sections: [
      {
        heading: "Marketing 2028 refined strategy house",
        body: [
          "The Design Hub is one of Marketing's functional services/operations: our centralised design and advertising agency, providing shared services across the BioMar world and offering services to markets 14 hours every weekday.",
        ],
        bullets: [
          "Management and execution of brand and product guidelines",
          "Visual design creation",
        ],
      },
      {
        heading: "Strategic role — five pillars",
        facts: [
          { label: "Consistency", value: "A unified visual identity globally, adapted to local needs" },
          { label: "Efficiency", value: "Centralized expertise, less duplicated work, smart prioritization" },
          { label: "Quality", value: "Professional, strategic, creative — every output earns its place" },
          { label: "Scalability", value: "Many markets, formats and campaigns; adaptations to specific needs" },
          { label: "Brand & Product Protection", value: "Correct logo, typography, imagery — applied consistently" },
        ],
      },
      {
        heading: "Areas of responsibility — external communication",
        bullets: [
          "Campaigns, advertisements, social media assets",
          "Videos & motion graphics, brochures & flyers",
          "Event material, trade show assets",
          "Product communication, presentations",
          "Website assets, publications & reports",
        ],
      },
      {
        heading: "Areas of responsibility — internal communication",
        bullets: [
          "Internal campaigns, office branding, stationery",
          "Corporate templates & presentations",
          "HR / internal material, employer branding, signage",
          "Onboarding assets, legal documents, merch, packaging, learning material",
        ],
      },
      {
        heading: "Ownership — one team, multiple support",
        bullets: [
          "Graphic Design — campaigns, layouts, digital & print, packaging",
          "Motion & Video — animation, video editing, motion graphics, storytelling",
          "Brand & Creative Direction — visual consistency, art direction, strategic guidance",
          "Production & Coordination — workflow, printer/publisher coordination, file & asset organization",
        ],
      },
      {
        heading: "Beyond daily design support",
        facts: [
          { label: "Brand Management", value: "Brand consistency / evolution / visual governance" },
          { label: "Creative Development", value: "Concepts and campaigns / art direction / visual storytelling" },
          { label: "Production & Adaptation", value: "Market adaptation / resizing and roll-outs / print & digital production" },
          { label: "Strategic Support", value: "Cross-market coordination / creative recommendations / design consultation" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which are pillars of the Design Hub? (select all)",
        options: ["Consistency", "Efficiency", "Discounting", "Brand & Product Protection"],
        correct: [0, 1, 3],
        explanation:
          "The five pillars are Consistency, Efficiency, Quality, Scalability and Brand & Product Protection.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Which ownership area covers art direction and strategic guidance?",
        options: ["Graphic Design", "Motion & Video", "Brand & Creative Direction", "Production & Coordination"],
        correct: [2],
        explanation:
          "Brand & Creative Direction owns visual consistency, art direction and strategic guidance.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Pillars in practice",
        prompt:
          "Pick one recent Design Hub deliverable and explain which of the five pillars it served and how.",
        successCriteria: [
          "A real deliverable chosen",
          "At least two pillars connected to concrete decisions",
        ],
      },
    ],
  },
  {
    id: "strategic-03",
    chapterId: "strategic",
    title: "Process, History & Brand Governance",
    summary:
      "How the Hub approaches work, its timeline through the years, and a first look at brand governance.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/strategic--03-process-history-governance.pptx`,
      type: "pptx",
      range: "Slides 9–14",
    },
    sections: [
      {
        heading: "Design Hub Process",
        body: [
          "The Design Hub takes a collaborative rather than transactional approach: continuous communication with local stakeholders, support for local adaptation while maintaining brand consistency, and prioritization based on timelines and business impact.",
        ],
      },
      {
        heading: "Different workflows depending on scope",
        note: "Tasks vs Projects sets the workflow — covered in full detail in the Design Hub 2026 chapter.",
      },
      {
        heading: "Design Hub through the years",
        facts: [
          { label: "2010", value: "Fragmented design and communication in the markets" },
          { label: "2019", value: "BioMar rebranding. New Brand Guidelines." },
          { label: "2020", value: "Incorporation of full-time in-house designer for Global Marketing needs" },
          { label: "2021", value: "Design Hub starts working with local markets for brand consistency" },
          { label: "2023", value: "Incorporation of a second in-house graphic designer" },
          { label: "2024", value: "Multimedia designer added; 286 tasks completed" },
          { label: "2025", value: "489 tasks completed (+71%). Product Logos Rebrand, Product Brand Guidelines v1" },
          { label: "2026", value: "New swoosh watermarks, first major Brand Guidelines update, IPO launch support" },
        ],
      },
      {
        heading: "Visual Branding & Design Governance",
        bullets: [
          "Logo usage · Typography · Color palette · Layout principles",
          "Imagery style · Tone and consistency · Digital vs print applications",
        ],
        note: "Guidelines support consistency while allowing flexibility. The full guidelines are their own chapter — see BioMar Brand Guidelines.",
      },
      {
        heading: "Recent logo rebranding",
        facts: [
          { label: "Before", value: "All brands treated independently, no alignment — seemed to be from different parents." },
          { label: "Now", value: "All brands follow the same framework and carry the swoosh — seem to be from the same parent." },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "boolean",
        prompt: "The Design Hub describes its approach as transactional rather than collaborative.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — it is explicitly collaborative rather than transactional.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What visual element unifies the brand family after the rebrand?",
        options: ["A drop shadow", "The swoosh", "A gradient", "A serif wordmark"],
        correct: [1],
        explanation: "The swoosh unifies the family so the brands read as sharing one parent.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Timeline recap",
        prompt:
          "Pick two milestones from the Design Hub timeline and explain why each mattered for how the Hub works today.",
        successCriteria: ["Two milestones chosen", "Each connected to a concrete change"],
      },
    ],
  },
  {
    id: "strategic-04",
    chapterId: "strategic",
    title: "Ways of Working & What's Next",
    summary:
      "The weekly/daily/always-on rhythm, and where the Hub is headed (Hub 2.0 → 3.0).",
    estMinutes: 20,
    material: {
      file: `${SLICE}/strategic--04-ways-of-working.pptx`,
      type: "pptx",
      range: "Slides 15–17",
    },
    sections: [
      {
        heading: "Ways of working",
        facts: [
          { label: "Weekly", value: "Meetings, project alignment, prioritization, capacity, cross-functional coordination" },
          { label: "Daily", value: "Collaboration, feedback loops, stakeholder communication, iterative review" },
          { label: "Always-on", value: "File & asset management, shared systems, version control, accessibility" },
        ],
      },
      {
        heading: "Current challenges & opportunities — today (Hub 2.0)",
        bullets: [
          "Volume of requests is increasing",
          "Global consistency vs local flexibility",
          "Scaling processes efficiently",
          "Quality across channels, local scaling",
        ],
      },
      {
        heading: "Opportunities — looking ahead (Hub 3.0)",
        bullets: [
          "Swift on necessities + campaigns, storytelling and events",
          "Enhance collaboration, scale the hub resources",
          "High-value vs low-value tasks; commercial vs internal balance",
          "Automation, improved workflows and transparency",
        ],
        note: "Looking ahead: product ownership.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "File & asset management and version control fall under which rhythm?",
        options: ["Weekly", "Daily", "Always-on", "Monthly"],
        correct: [2],
        explanation: "Always-on — shared systems, version control and accessibility run continuously.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What is one current (Hub 2.0) challenge mentioned?",
        options: [
          "Too few requests",
          "Global consistency vs local flexibility",
          "No markets to serve",
          "Excess designers",
        ],
        correct: [1],
        explanation: "Balancing global consistency with local flexibility is a named current challenge.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Channel choice drill",
        prompt:
          "For five scenarios (new task, quick status check, unclear brief, feedback, deep review), decide whether it belongs in a weekly, daily or always-on rhythm — and why.",
        successCriteria: ["Rhythm assigned for each scenario", "One-line justification each"],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Global & Group Marketing (18 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "global-01",
    chapterId: "global",
    title: "Team & Organisation",
    summary:
      "What Global Marketing is, how Global / Divisional / Local marketing split responsibilities, the org chart, and how the team collaborates.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--01-team-organisation-2025.pdf`,
      type: "pdf",
      range: "One BioMar Marketing, org chart & collaboration (5 pages)",
    },
    sections: [
      {
        heading: "What is Global Marketing and Branding",
        body: [
          "Global Marketing manages the BioMar brand, creates the positioning for all product concepts and services, and runs a centralised Design and Digital Shared Services agency.",
        ],
      },
      {
        heading: "Our three working areas",
        bullets: [
          "Global Marketing (brand, positioning, shared services — this is the Design Hub's home)",
          "Divisional Marketing (develops the product range for its product portfolio and manages its businesses)",
          "Local Marketing (launches the product range and runs local initiatives)",
        ],
      },
      {
        heading: "One BioMar Marketing",
        body: [
          "Global Marketing sits above four global product/service lines (Global Product Concepts, Trademarks, Marketing Agency, Digital Marketing), which in turn cover five product segments (Salmon, FW, MS, Hatchery, Shrimp) delivered locally by 12 business units — Chile, Norway, Greece, Turkey, Costa Rica, Ecuador, UK, Australia, Baltics, West MED, China, Vietnam.",
        ],
      },
      {
        heading: "The Global Marketing team",
        bullets: [
          "Katherine Bryar — Global Marketing Director",
          "Olivia Andrews — Graphic Designer",
          "Elizabeth Jørgensen — Graphic Designer",
          "Steffan Kyhe — Digital Marketing Lead",
          "Nerea Palacios — Student Assistant",
        ],
        note: "Creative Direction is provided externally by Bitsch & Bitsch. Videographers, photographers and additional creative designers are brought in as needed.",
      },
      {
        heading: "Marketing Forum & collaboration cadence",
        body: [
          "Global Marketing is guided by the Marketing Forum (Salmon · FW & MS · Shrimp & Hatchery · Product Strategist), which sets positioning for product concepts and services and runs the shared Design and Digital agency.",
          "Below the Forum, a regular Global Marketing Meeting brings together the local marketing managers across every business unit to stay aligned.",
        ],
      },
      {
        heading: "Marketing organisation & divisions",
        facts: [
          { label: "EMEA", value: "Baltics & WestMed" },
          { label: "Asia", value: "Vietnam & China" },
          { label: "LATAM", value: "Costa Rica & Ecuador" },
          { label: "Salmon", value: "Australia, UK, Norway, Chile" },
          { label: "Hatchery", value: "LARVIVA" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which are the three working areas of Marketing? (select all)",
        options: ["Global Marketing", "Divisional Marketing", "Local Marketing", "Fleet Operations"],
        correct: [0, 1, 2],
        explanation:
          "The three areas are Global Marketing, Divisional Marketing and Local Marketing.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Who leads Global Marketing, the Design Hub's home team?",
        options: ["Carlos Díaz", "Katherine Bryar", "Bitsch & Bitsch", "Marcel Huijsmans"],
        correct: [1],
        explanation:
          "Katherine Bryar is the Global Marketing Director. Bitsch & Bitsch provides external Creative Direction; Marcel Huijsmans directs Salmon Marketing.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Who's who",
        prompt:
          "List the current Global Marketing team and note one thing each person is responsible for.",
        successCriteria: ["All team members listed", "One responsibility captured per person"],
      },
    ],
  },
  {
    id: "global-02",
    chapterId: "global",
    title: "Stakeholders & Meetings",
    summary:
      "The stakeholders around Global Marketing, and the regular and special meetings that keep everyone aligned.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--02-stakeholders-meetings.pptx`,
      type: "pptx",
      range: "Slides 7–12",
    },
    sections: [
      {
        heading: "Marketing stakeholders",
        body: [
          "Global Marketing works across group function stakeholders and key stakeholders in markets around the world — the same people you'll coordinate with as tasks and projects come in.",
        ],
        note: "The full named contact list (who to ask about datasheets, R&D, LARVIVA, technical questions...) is in the Playbook chapter → Stakeholder Map.",
      },
      {
        heading: "Marketing meetings",
        facts: [
          { label: "Regular meetings", value: "Recurring cadence for alignment, prioritization and capacity" },
          { label: "Special meetings", value: "Ad hoc sessions — planning, reviews, specific initiatives" },
        ],
      },
      {
        heading: "Meeting the marketing managers",
        body: [
          "Meet the marketing managers bit by bit. The order can follow how much the Design Hub works with each market — this isn't only about meeting them as people, but learning what they do and how they work with the Hub.",
        ],
        bullets: [
          "Baltics · WestMed · Norway · Chile",
          "Asia · Hatchery · UK · Australia · LATAM",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What principle orders the marketing manager introductions?",
        options: [
          "Alphabetical by country",
          "How much the Design Hub works with each market",
          "By time zone only",
          "Randomly",
        ],
        correct: [1],
        explanation:
          "Meet them based on how much the Hub works with each market — the closest collaborators first.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What is the difference between regular and special meetings?",
        options: [
          "Regular meetings never happen",
          "Regular = recurring cadence; Special = ad hoc sessions",
          "Special meetings are for social events only",
          "There is no difference",
        ],
        correct: [1],
        explanation:
          "Regular meetings are a recurring alignment cadence; special meetings are ad hoc (planning, reviews, initiatives).",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Intro notes template",
        prompt:
          "Prepare a short intro-meeting template (focus, typical requests, local specifics) and fill it in after your first marketing manager meeting.",
        successCriteria: ["Reusable template created", "First meeting captured against it"],
      },
    ],
  },
  {
    id: "global-03",
    chapterId: "global",
    title: "Communication, 2026 Plan & Budgets",
    summary:
      "How Global Marketing communicates, the shape of the 2026 plan, and budget awareness.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--03-communication-plan-budgets.pptx`,
      type: "pptx",
      range: "Slides 13–18",
    },
    sections: [
      {
        heading: "How we communicate",
        facts: [
          { label: "Email", value: "New task/project · feedback" },
          { label: "Teams chat", value: "Follow-ups" },
          { label: "Meeting", value: "Define/clarify · deep review" },
        ],
      },
      {
        heading: "2026 Global Marketing Plan",
        body: [
          "The plan is organized at two levels — Group and Global — reflecting decisions and initiatives that apply across the whole organisation versus those specific to Global Marketing.",
        ],
      },
      {
        heading: "Budgets",
        note: "Budget processes and figures are managed by Marketing leadership. As a designer, the practical impact is on prioritisation and turnaround — see the Design Hub 2026 chapter for how priority and turnaround work day to day.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "You need to submit a brand-new task. Which channel?",
        options: ["Teams chat", "Email", "A hallway chat", "SMS"],
        correct: [1],
        explanation:
          "New tasks/projects and formal feedback go by email; Teams is for follow-ups; meetings are for defining/reviewing.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "The 2026 Global Marketing Plan is organized at which two levels?",
        options: ["Group and Global", "Weekly and Monthly", "Print and Digital", "EMEA and Asia"],
        correct: [0],
        explanation: "Group and Global — organisation-wide vs Global Marketing-specific.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Plan awareness",
        prompt:
          "Take one past project and note whether it was a Group-level or Global-level initiative, and why.",
        successCriteria: ["Project classified", "Reasoning given"],
      },
    ],
  },
  {
    id: "global-04",
    chapterId: "global",
    title: "Product & Brand Glossary",
    summary:
      "What LARVIVA, ORBIT, SmartCare, EXIA and the rest of BioMar's product brands actually are — the names you'll see on every brief.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--04-product-brand-glossary.pdf`,
      type: "pdf",
      range: "Product Offering section (18 pages)",
    },
    sections: [
      {
        heading: "Why this matters",
        note: "Every product name below is also a real folder branch on the shared drive (see the Folder Structure module) and shows up constantly in briefs. Knowing what each one is for makes both far easier to navigate.",
      },
      {
        heading: "BioMar's brand archetype",
        body: [
          "BioMar's brand archetype is the Enabler: in collaboration with industry partners, the BioMar brand acts as a catalyst for change, developing practical solutions that keep transforming aquaculture. \"The collaborative way we do business is our competitive difference.\"",
        ],
      },
      {
        heading: "Global brands (cut across products)",
        facts: [
          { label: "Blue Impact", value: "Sustainability-focused feed range — lower-impact, circular & restorative ingredients" },
          { label: "ORBIT", value: "Feed for advanced farming tech (RAS) — maximises fish and biofilter performance" },
          { label: "SmartCare", value: "\"You care. We care.\" — preventative health feed programme, biofunctional ingredients" },
          { label: "VetCare", value: "Veterinary / medicated feed line" },
        ],
      },
      {
        heading: "Product segments & their brands",
        facts: [
          { label: "Salmon", value: "POWER · Symbio (cleaner fish) · intro" },
          { label: "FW (Fresh Water)", value: "Efico · Inicio · Salvea" },
          { label: "MS (Marine/Sea Water)", value: "Efico · Maxio" },
          { label: "Hatchery", value: "LARVIVA — \"Start Strong. Stay Strong.\" Complete hatchery feed range for fish and shrimp." },
          { label: "Shrimp", value: "EXIA — performance-driven feed from larval stage to harvest" },
        ],
      },
      {
        heading: "A few name combinations worth knowing",
        bullets: [
          "LARVIVA ORBIT — the ORBIT concept applied to marine nurseries running on RAS",
          "Symbio — nutrition specifically for cleaner fish (the fish that de-louse salmon)",
        ],
      },
      {
        heading: "Quality & growth concepts",
        facts: [
          { label: "P 3.0 Concept", value: "Feeds optimised for different fish products and market situations, whatever fish prices or costs do" },
          { label: "BioRhythmic Nutrition", value: "Feed matched to the fish's needs at each growth stage — pellet size and nutrients adjusted as fish grow" },
          { label: "Best Total Economic Performance", value: "The outcome all of the above is aimed at: the best result for the farmer's conditions and objectives" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "A brief mentions a RAS (recirculating aquaculture system) hatchery project. Which brand is it most likely for?",
        options: ["SmartCare", "ORBIT / LARVIVA ORBIT", "VetCare", "Blue Impact"],
        correct: [1],
        explanation:
          "ORBIT is BioMar's feed range for advanced farming tech like RAS; LARVIVA ORBIT applies that specifically to marine nurseries.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What is BioMar's brand archetype?",
        options: ["The Ruler", "The Innocent", "The Enabler", "The Jester"],
        correct: [2],
        explanation:
          "BioMar is positioned as the Enabler — a catalyst for change through collaboration with industry partners.",
      },
      {
        id: "q3",
        type: "single",
        prompt: "Which brand is BioMar's preventative health feed programme?",
        options: ["SmartCare", "LARVIVA", "EXIA", "P 3.0"],
        correct: [0],
        explanation: "SmartCare — \"You care. We care.\" — is the preventative health feed range.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Match the brand",
        prompt:
          "Pick three product folders from the Folder Structure explorer you don't recognise and, using this glossary, write one line on what each brand actually is.",
        successCriteria: ["Three folders picked", "Correct brand explained for each"],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Design Hub 2026 (33 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "dh2026-01",
    chapterId: "dh2026",
    title: "Challenges & How to Reach Out",
    summary:
      "The problems this new way of working solves, and the first decision every requester makes: Task or Project?",
    estMinutes: 20,
    material: {
      file: `${SLICE}/dh2026--01-challenges-how-to-reach-out.pptx`,
      type: "pptx",
      range: "Slides 1–6",
    },
    sections: [
      {
        heading: "Challenges this way of working addresses",
        bullets: [
          "Disruption",
          "Disorganisation / no clear brief",
          "Versions — 5+ rounds",
          "Editing text + content back and forth",
          "Inefficient / unnecessary meetings",
          "Confusion due to disorganisation",
          "No clear process",
          "Priority decided by who screams loudest",
        ],
      },
      {
        heading: "Before you reach out: what do you need?",
        body: [
          "A simple decision guide: do you need one quick deliverable, or a bigger goal made of multiple pieces? That answer tells you whether you're asking for a Task or a Project.",
        ],
      },
      {
        heading: "Tasks vs Projects",
        facts: [
          { label: "Task", value: "Small, short — not many reviews or much info needed. E.g. ads, handouts, brochures." },
          { label: "Project", value: "A group of tasks toward a bigger goal. E.g. logos, new product branding, global campaigns." },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "A single event flyer with one round of review is a…",
        options: ["Project", "Task", "Campaign", "Program"],
        correct: [1],
        explanation: "A small, short, self-contained deliverable is a Task.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Launching a new product brand (logo, guidelines, campaign) is a…",
        options: ["Task", "Project"],
        correct: [1],
        explanation: "Multiple interdependent deliverables toward one bigger goal = a Project.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Task or Project?",
        prompt: "Take five recent requests and label each Task or Project, with a one-line reason.",
        successCriteria: ["All five labelled", "Reasoning references reviews / scope / info needed"],
      },
    ],
  },
  {
    id: "dh2026-02",
    chapterId: "dh2026",
    title: "Deadlines, Priority & the InCopy Course",
    summary:
      "Real dates instead of 'ASAP', how priority is set by business value, and the InCopy/InDesign training.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/dh2026--02-deadlines-priority-incopy.pptx`,
      type: "pptx",
      range: "Slides 7–14",
    },
    sections: [
      {
        heading: "ASAP is not a deadline",
        facts: [
          { label: "First Draft Date", value: "When the first version (PROOF) is expected." },
          { label: "Final Due Date", value: "When the approved final is needed." },
        ],
      },
      {
        heading: "How we set priority — business value",
        bullets: ["Low priority → lower business value", "High priority → higher business value / impact"],
      },
      {
        heading: "What is Adobe InCopy?",
        body: [
          "InCopy lets people create, edit and format content and helps teams work collaboratively. It integrates with InDesign so designers and writers work on the same layout without clashing — avoiding unnecessary back-and-forth.",
        ],
      },
      {
        heading: "The course — 4 modules",
        bullets: [
          "Module 1: Introduction to InCopy",
          "Module 2: Editing Text",
          "Module 3: Reviewing Copy",
          "Module 4: Saving and Export",
        ],
      },
      {
        heading: "Available courses",
        facts: [
          { label: "EN — 5 hours", value: "Beginner–Intermediate" },
          { label: "EN — 3 hours", value: "Infrequent users" },
          { label: "ES — 5 hours", value: "Beginner–Intermediate" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What are the two dates every request must have?",
        options: ["Start date and end date", "First Draft Date and Final Due Date", "ASAP and EOD", "Draft and review"],
        correct: [1],
        explanation: "First Draft Date and Final Due Date — 'ASAP' is not a deadline.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "Priority is set by whoever asks the loudest.",
        options: ["True", "False"],
        correct: [1],
        explanation: "False — priority is set by business value and impact.",
      },
      {
        id: "q3",
        type: "single",
        prompt: "What problem does the InCopy + InDesign workflow solve?",
        options: [
          "Rendering 3D",
          "Letting writers and designers work on the same layout without clashing",
          "Video editing",
          "Color management",
        ],
        correct: [1],
        explanation: "InCopy integrates with InDesign so writers and designers work in unison, avoiding back-and-forth.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Real dates + InCopy flow",
        prompt:
          "Turn an 'ASAP' request into a First Draft Date + Final Due Date. Then open a sample InDesign layout with an InCopy story, make a tracked text edit, and export.",
        successCriteria: [
          "Both dates defined, review rounds accounted for",
          "Edited via InCopy with track changes, exported correctly",
        ],
      },
    ],
  },
  {
    id: "dh2026-03",
    chapterId: "dh2026",
    title: "Start to Finish Process & Feedback",
    summary:
      "The end-to-end process from Marketing's side and the Hub's side, and how feedback is submitted per media type.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/dh2026--03-start-to-finish-feedback.pptx`,
      type: "pptx",
      range: "Slides 15–19",
    },
    sections: [
      {
        heading: "Design Hub Process",
        body: [
          "Collaborative rather than transactional: continuous communication with local stakeholders, support for local adaptation while maintaining brand consistency, and prioritization based on timelines and business impact.",
        ],
      },
      {
        heading: "What Marketing does",
        bullets: [
          "Fill out the Brief form and send it via email to design@biomar.com",
          "Submit feedback relevant to the media type; inform the Design Hub via email that feedback has been given",
          "Approve final files and inform the Design Hub that the task/project is complete",
        ],
      },
      {
        heading: "Submitting feedback — different methods for different media",
        facts: [
          { label: "PDF", value: "Sent as a link to the folder" },
          { label: "JPG / PNG", value: "Sent as a link to the folder" },
          { label: "Video", value: "Sent as a link to SharePoint" },
        ],
        note: "For video feedback, comments must reference a timestamp written as HH:MM:SS.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Where does Marketing send the Brief form?",
        options: ["design@biomar.com", "Any team member's personal email", "Slack", "It's submitted verbally only"],
        correct: [0],
        explanation: "The Brief form is filled out and sent via email to design@biomar.com.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "How must video feedback be referenced?",
        options: ["By frame number", "By a timestamp written as HH:MM:SS", "By color", "It can't be — video isn't reviewed"],
        correct: [1],
        explanation: "Video feedback must include a timestamp in HH:MM:SS.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Run a review round",
        prompt:
          "Export a PROOF, send it as a folder link (not an attachment), and collect mock feedback in the correct format for a PDF, an image and a video.",
        successCriteria: ["Sent as folder link", "Feedback format matches the media type (incl. timestamp for video)"],
      },
    ],
  },
  {
    id: "dh2026-04",
    chapterId: "dh2026",
    title: "File Storage, Turnaround & Calendar",
    summary:
      "The three files you'll always find, how turnaround times work, and the yearly recurring calendar.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/dh2026--04-file-storage-turnaround-calendar.pptx`,
      type: "pptx",
      range: "Slides 20–23",
    },
    sections: [
      {
        heading: "You'll always find",
        bullets: [
          "Editable file (for the Design Hub)",
          "File for review (for the Draft Date — ends in PROOF)",
          "Final file (for the Final Date — ends in PRINT or DIGITAL)",
        ],
      },
      {
        heading: "Turnaround times",
        bullets: [
          "The sooner you submit, the sooner it goes on the calendar and gets an accurate timeframe.",
          "First come, first served — although prioritisation by business value still applies.",
          "Build the rounds of review into the timeline.",
        ],
      },
      {
        heading: "Yearly calendar",
        bullets: ["Sustainability Booklet", "Christmas Artwork", "Easter", "Summer"],
        note: "Plan around the yearly calendar so recurring work is booked ahead.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What ending marks a file for the Draft Date?",
        options: ["FINAL", "PROOF", "PRINT", "DIGITAL"],
        correct: [1],
        explanation: "The file for review, tied to the Draft Date, ends in PROOF.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "Submitting earlier gets you a more accurate timeframe on the calendar.",
        options: ["True", "False"],
        correct: [0],
        explanation: "True — the sooner you submit, the sooner it's on the calendar with an accurate timeframe.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Plan around the calendar",
        prompt:
          "Pick a recurring yearly item (e.g. Christmas artwork) and, using the turnaround guidance, note when it should be kicked off.",
        successCriteria: ["Recurring item chosen", "Kickoff date reasoned from turnaround + review rounds"],
      },
    ],
  },
  {
    id: "dh2026-05",
    chapterId: "dh2026",
    title: "Communication, Personal Responsibility & the Brief Template",
    summary:
      "When to use email, Teams or a meeting; what stays each person's responsibility; and the Brief Template itself.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/dh2026--05-communication-responsibility-brief.pptx`,
      type: "pptx",
      range: "Slides 24–29",
    },
    resources: [BRIEF_TEMPLATE],
    sections: [
      {
        heading: "Ways of communicating",
        facts: [
          { label: "Email", value: "Submitting new task/project · submitting feedback" },
          { label: "Teams chat", value: "Follow up on tasks/projects" },
          { label: "Verbal / meetings", value: "Clarify/define projects · in-depth artwork review" },
        ],
      },
      {
        heading: "Personal responsibility",
        bullets: [
          "Task/Project status",
          "Finding files / links",
          "Submitting feedback",
          "Translations",
          "New tasks — Marketing Managers must inform their relevant Forum member of current tasks/projects",
        ],
      },
      {
        heading: "Brief Template",
        note: "Download the Brief Template below and use it to submit new requests with all the required information.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "An in-depth review of the artwork is best done…",
        options: ["By email only", "In a verbal meeting", "Via Flaticon", "Never"],
        correct: [1],
        explanation: "In-depth artwork review and clarifying/defining projects are handled verbally.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Who must inform the relevant Forum member about current tasks/projects?",
        options: ["The Design Hub", "Marketing Managers", "IT", "External partners"],
        correct: [1],
        explanation: "Marketing Managers must inform their relevant Forum member of current tasks/projects.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Use the template",
        prompt: "Fill out the attached Brief Template for a mock request.",
        successCriteria: ["Template downloaded and filled out", "All required fields completed"],
      },
    ],
  },
  {
    id: "dh2026-06",
    chapterId: "dh2026",
    title: "Brief Template — A Worked Example",
    summary:
      "A real, filled-out brief the Hub received right after the template — see what good specificity looks like.",
    estMinutes: 15,
    material: {
      file: `${SLICE}/dh2026--06-larval-research-facilities.pptx`,
      type: "pptx",
      range: "Slides 30–33",
    },
    sections: [
      {
        heading: "Reading a real example",
        body: [
          "Right after the Brief Template comes a real brief the Design Hub received: a request for signage at BioMar's larval research facility at ATC Hirtshals. It's included here as a worked example — notice how concrete it is compared to a vague request.",
        ],
      },
      {
        heading: "What the requester wrote",
        body: [
          "\"BioMar has invested in advanced larval research facilities at ATC Hirtshals, capable of performing trials in semi-industrial conditions. The trial facilities serve as a hub for research and development, product consolidation and validation.\" — this is the purpose/context, stated clearly.",
        ],
      },
      {
        heading: "The specs included",
        bullets: [
          "Signage: 60×40cm",
          "Wall space for design/canvas at the end of the hallway",
          "Wall dimensions approx. 1.2m × 2.5m",
        ],
        note: "Compare this against the four minimum-info items from earlier: purpose, timeline, specifications, copy/assets. This example nails the specifications — exact sizes, not \"medium-ish\" or \"the usual size\".",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What makes this example brief strong?",
        options: [
          "It's very short",
          "It gives exact, concrete specifications (sizes, location)",
          "It has no deadline",
          "It was submitted verbally",
        ],
        correct: [1],
        explanation:
          "Exact specs (60×40cm signage, ~1.2×2.5m wall) are exactly the kind of concrete detail a good brief includes.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "This example is meant to be memorised as general BioMar facility information, not as a brief-writing example.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — it's a worked example attached to the Brief Template, illustrating good specificity, not standalone facility trivia.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Spot the good brief habits",
        prompt:
          "Go back to this example and mark which of the four minimum-info items (purpose, timeline, specifications, copy/assets) it covers well — and which, if any, are missing.",
        successCriteria: [
          "All four minimum-info items checked against the example",
          "Any gap identified",
        ],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Design Hub Playbook (27 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "playbook-01",
    chapterId: "playbook",
    title: "Overview & The Brief",
    summary:
      "The overall process at a glance, and the brief — the foundation of every project.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/playbook--01-overview-the-brief.pptx`,
      type: "pptx",
      range: "Slides 1–5",
    },
    resources: [BRIEF_TEMPLATE],
    sections: [
      {
        heading: "From brief to final version",
        bullets: [
          "1 · Email & briefing — the request arrives and is reviewed",
          "2 · Work on version — DRAFT concept develops",
          "3 · Send for review — a PROOF goes to the requester",
          "4 · Receive feedback — comments come back",
          "5 · Iterate — PROOF2, PROOF3 as needed",
          "6 · Final version — approved, exported for PRINT or DIGITAL",
          "7 · Close task — moved to Completed and filed by market",
        ],
      },
      {
        heading: "The brief is the foundation of every project",
        body: [
          "It provides the essential information needed to understand the request: objective, target audience, deliverables, timeline, copy, format specifications, and any relevant assets or references. A clear brief minimizes revisions later.",
        ],
      },
      {
        heading: "Minimum information required",
        facts: [
          { label: "Purpose", value: "What is the project for?" },
          { label: "Timeline", value: "Draft and final delivery dates" },
          { label: "Specifications", value: "Format, dimensions, production requirements" },
          { label: "Copy & assets", value: "Text copy and any provided images / references" },
        ],
        note: "If the minimum information is missing, move the request to Waiting and ask for what's missing before starting.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which of these are part of the minimum information a brief must include?",
        options: ["Purpose (what it's for)", "Draft and final dates", "Format & specifications", "The designer's mood"],
        correct: [0, 1, 2],
        explanation: "Purpose, timeline and specifications are required, along with copy/assets.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "A brief is missing the final delivery date and specs. What do you do?",
        options: ["Start anyway and guess", "Move it to Waiting and request the missing info", "Close the task", "Escalate to the CEO"],
        correct: [1],
        explanation: "Move it to Waiting and ask for the missing information before starting.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Brief triage",
        prompt:
          "Take three recent request emails and score each against the four minimum-info items. Draft the follow-up question for any gaps.",
        successCriteria: ["Each brief scored on all four items", "A clear follow-up drafted for every gap"],
      },
    ],
  },
  {
    id: "playbook-02",
    chapterId: "playbook",
    title: "Email Tags & the Task Manager",
    summary:
      "How the inbox stays tagged, and the task manager board — columns, cards, tags, to-dos and notes.",
    estMinutes: 35,
    material: {
      file: `${SLICE}/playbook--02-email-tags-task-manager.pptx`,
      type: "pptx",
      range: "Slides 6–12",
    },
    sections: [
      {
        heading: "Email tags",
        bullets: [
          "'Teams' tag → the request has been registered in the task manager",
          "No tag → assume it has NOT been added yet and needs reviewing",
        ],
      },
      {
        heading: "Task manager — columns",
        bullets: [
          "Tasks / Projects — new requests enter here; active but not yet assigned to a designer",
          "Designer columns — once you start a task, move it to your personal column",
          "Sent for Review — PROOF shared, waiting for feedback/approval",
          "In Progress — larger, longer-term work",
          "Waiting — on hold for missing info",
          "Completed [Year] — done, then categorized by market",
        ],
      },
      {
        heading: "Task card structure",
        bullets: [
          "Market tags — identify which market the project belongs to",
          "People — add the requester as a member; they get notified and can follow updates",
          "To-do — list multiple deliverables/formats to track individually",
          "Notes — always include: draft deadline, final deadline, email subject",
        ],
        note: "Adding the email subject to Notes is especially important — it's how you jump back to the original thread.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "An email has no 'Teams' tag. What should you assume?",
        options: [
          "It's already in the task manager",
          "It has not been added to the task manager yet",
          "It's spam",
          "It's already completed",
        ],
        correct: [1],
        explanation: "No tag means assume it has not yet been added and needs to be reviewed.",
      },
      {
        id: "q2",
        type: "multi",
        prompt: "What must the Notes section of a card always include?",
        options: ["Draft deadline", "Final deadline", "Email subject", "The client's phone number"],
        correct: [0, 1, 2],
        explanation: "Always include the draft deadline, final deadline and email subject.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Build a card",
        prompt:
          "Create a practice task card with a market tag, the requester added as a member, a two-item to-do list, and complete Notes.",
        successCriteria: [
          "Market tag applied",
          "Requester added as member",
          "Notes include both deadlines + email subject",
        ],
      },
    ],
  },
  {
    id: "playbook-03",
    chapterId: "playbook",
    title: "Task Process, Files & Naming",
    summary:
      "Walking a task end to end, plus where files live and how to name them.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/playbook--03-task-process-files-naming.pptx`,
      type: "pptx",
      range: "Slides 13–17",
    },
    sections: [
      {
        heading: "For every project you'll always find",
        bullets: [
          "Editable file (for the Design Hub)",
          "File for review (for the Draft date — ends in PROOF)",
          "Final file (for the Final date — ends in PRINT or DIGITAL)",
        ],
      },
      {
        heading: "Naming — design files",
        facts: [
          { label: "Pattern", value: "Year-Month Language_Market Brand/Product-FileType" },
          { label: "Example", value: "2022-03 ES_Orbit_Brochure" },
          { label: "Draft example", value: "DRAFT_2021-03 EN_EMEA SmartCare FOCUS (Marine) DM" },
        ],
      },
      {
        heading: "Naming — images",
        bullets: [
          "What it is: species, life-stage, location, action, etc.",
          "License / Shutterstock number / picture default name",
          "Example: Trout_Smolt_Denmark",
        ],
      },
      {
        heading: "Per-project folders you can create",
        bullets: [
          "Files Provided — everything the requester sent",
          "Assets — things you'll use in the project",
          "Previous Versions — once feedback is received, prior PROOFs move here",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Which follows the design-file naming pattern?",
        options: ["brochure_final_v2.pdf", "2022-03 ES_Orbit_Brochure", "orbit thing.ai", "FINAL FINAL real.pdf"],
        correct: [1],
        explanation: "The pattern is Year-Month Language_Market Brand/Product-FileType.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Where do superseded PROOF versions go once feedback arrives?",
        options: ["Trash", "Files Provided", "Previous Versions", "The requester's inbox"],
        correct: [2],
        explanation: "Move them into the Previous Versions folder.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Name it right",
        prompt:
          "Rename five sample files (three designs, two images) to follow the conventions. Set up the three per-project folders for one.",
        successCriteria: [
          "Design files follow Year-Month Language_Market pattern",
          "Image names describe content + license",
          "Files Provided / Assets / Previous Versions folders created",
        ],
      },
    ],
  },
  {
    id: "playbook-04",
    chapterId: "playbook",
    title: "Versioning, Review & Closing",
    summary:
      "DRAFT → PROOF → FINAL, how feedback comes back, exporting finals, and the two-step closeout.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/playbook--04-versioning-review-closing.pptx`,
      type: "pptx",
      range: "Slides 18–24",
    },
    sections: [
      {
        heading: "Versioning",
        facts: [
          { label: "DRAFT", value: "A concept/idea in progress — not ready to show the counterpart" },
          { label: "PROOF", value: "Ready for review, sent to the counterpart (PROOF, PROOF2, PROOF3…)" },
          { label: "FINAL", value: "Approved — can move to production (PRINT or DIGITAL)" },
        ],
      },
      {
        heading: "Sending & receiving feedback",
        note: "Instead of attaching the file, send the link to the folder. PDF and images: link to folder. Video: link to SharePoint, with timestamps written as HH:MM:SS.",
      },
      {
        heading: "Exporting FINAL versions",
        facts: [
          { label: "PRINT", value: "Usually needs bleed and/or crop-marks — confirm with the supplier" },
          { label: "DIGITAL", value: "Usually Interactive PDF — confirm pages/orientation with the requester" },
        ],
      },
      {
        heading: "Closing a task — two places",
        bullets: [
          "Task manager — move the card to 'Completed [Year]' and categorize it by market",
          "Email inbox — mark the thread 'done' and move it to the requesting market's folder",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Which version stage is ready to be shown to the counterpart for review?",
        options: ["DRAFT", "PROOF", "FINAL", "None — never show them anything"],
        correct: [1],
        explanation: "PROOF is the review stage sent to the counterpart.",
      },
      {
        id: "q2",
        type: "multi",
        prompt: "Closing a task happens in which two places?",
        options: ["The task manager", "The email inbox", "LinkedIn", "The printer's portal"],
        correct: [0, 1],
        explanation: "Close in both the task manager and the email inbox.",
      },
      {
        id: "q3",
        type: "single",
        prompt: "What do PRINT final files usually need?",
        options: ["Bleed and/or crop-marks", "A transparent background", "Embedded video", "Nothing special"],
        correct: [0],
        explanation: "Print material usually needs bleed and/or crop-marks.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Full cycle: PROOF to closed",
        prompt:
          "Take a practice task through DRAFT → PROOF (sent as a folder link) → feedback → FINAL export (correct spec) → closing in both the task manager and the inbox.",
        successCriteria: [
          "PROOF sent as folder link, feedback captured correctly",
          "FINAL exported to the right spec",
          "Card in Completed + market category, email filed",
        ],
      },
    ],
  },
  {
    id: "playbook-05",
    chapterId: "playbook",
    title: "Stakeholder Map & Communication",
    summary:
      "Who's in charge of what, and when to use email vs Teams vs a meeting.",
    estMinutes: 15,
    material: {
      file: `${SLICE}/playbook--05-stakeholder-map-communication.pptx`,
      type: "pptx",
      range: "Slides 25–27",
    },
    sections: [
      {
        heading: "Have a question about…? Write to…",
        facts: [
          { label: "Datasheets", value: "Kat — katmi@biomar.com" },
          { label: "R&D", value: "Elisabeth — eliaa@biomar.com" },
          { label: "LARVIVA", value: "Daniela — vdv@biomar.com" },
          { label: "SmartCare (salmon)", value: "Torunn" },
          { label: "Technical questions", value: "Iannis, Andreina, Bruno or Ewan" },
        ],
      },
      {
        heading: "Ways of communicating",
        facts: [
          { label: "Email", value: "Submitting new task/project · submitting feedback" },
          { label: "Teams chat", value: "Follow up on tasks/projects" },
          { label: "Verbal / meetings", value: "Clarify/define · in-depth review" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "You have a datasheet question. Who do you write to?",
        options: ["Daniela", "Kat", "Torunn", "Ewan"],
        correct: [1],
        explanation: "Datasheets → Kat (katmi@biomar.com).",
      },
      {
        id: "q2",
        type: "single",
        prompt: "A LARVIVA (hatchery) question should go to…",
        options: ["Elisabeth", "Kat", "Daniela", "Bruno"],
        correct: [2],
        explanation: "LARVIVA questions go to Daniela (vdv@biomar.com).",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Route it",
        prompt:
          "Given five incoming questions (a datasheet spec, an R&D claim, a hatchery product, a salmon SmartCare asset, a technical detail), name the right contact for each.",
        successCriteria: ["Correct contact for all five"],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: BioMar Brand Guidelines 2020 (30 pages)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "brand-guidelines-01",
    chapterId: "brand-guidelines",
    title: "Corporate Logo",
    summary:
      "Our most valuable brand asset: elements, file formats, placement, incorrect uses and the promotional-only version.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/brand-guidelines--01-corporate-logo.pdf`,
      type: "pdf",
      range: "Pages 1–8",
    },
    sections: [
      {
        heading: "The corporate logo",
        body: [
          "The BioMar Corporate logo is our most valuable brand asset. It is very important we use it as the primary logo around the globe.",
        ],
      },
      {
        heading: "Logo elements",
        body: [
          "The BioMar Logo elements create a sense of movement and connectivity. The box icon has rounded corners to speak to the friendly aspects of our brand personality. The colours reflect our planet's water, sky and land.",
        ],
      },
      {
        heading: "File formats",
        facts: [
          { label: "EPS", value: "For print" },
          { label: "JPG / PNG", value: "For digital use" },
        ],
      },
      {
        heading: "Displaying the logo",
        bullets: [
          "The logo should appear on all BioMar material",
          "Can be placed on most coloured and photographic backgrounds — always place it prominently and clearly",
          "Place in one of the four corners; the distance from both edges must be equal",
          "As a general rule, the BioMar logo must be placed in the top or bottom right hand corner",
        ],
      },
      {
        heading: "Logo & tagline",
        body: [
          "The logo and tagline exist in exactly 4 versions: vertical + BioMar Blue text, vertical + white text, horizontal + BioMar Blue text, horizontal + white text. No other versions of the logo/tagline combination are allowed.",
        ],
      },
      {
        heading: "Logo for promotional materials",
        note: "The Primary Logo without the box element is ONLY for promotional-material applications where the primary logo can't work. It can never be used against any colour other than dark blue, navy or black — and it can NEVER be used in print or digital media applications.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "As a general rule, where should the BioMar logo be placed?",
        options: ["Dead center", "Top or bottom right corner", "Bottom left only", "Anywhere, no rule"],
        correct: [1],
        explanation: "As a general rule, the logo must be placed in the top or bottom right hand corner.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "The promotional-only logo (without the box) can be used in print or digital media.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — it can NEVER be used in print or digital media, only for specific promotional-material applications.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Logo audit",
        prompt:
          "Review three recent layouts and check: correct logo placement, correct tagline version (one of the 4 allowed), and that the promotional-only logo wasn't used in print/digital.",
        successCriteria: ["All three layouts checked", "Any violation flagged with the correct fix"],
      },
    ],
  },
  {
    id: "brand-guidelines-02",
    chapterId: "brand-guidelines",
    title: "Typography",
    summary:
      "Avenir Next as primary typeface, Arial Bold headlines as secondary, and the line detail style.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/brand-guidelines--02-typography.pdf`,
      type: "pdf",
      range: "Pages 9–14",
    },
    sections: [
      {
        heading: "Primary typeface — Avenir Next",
        body: [
          "Avenir Next is our corporate typeface and should be used whenever possible, following the text arrangements specified in the guidelines to keep brand consistency across markets.",
        ],
        facts: [
          { label: "Primary weights", value: "Regular and Bold" },
          { label: "Printed media", value: "Avenir Next should always be used" },
          { label: "Digital media", value: "When Avenir Next can't be used, fall back to the secondary typeface" },
        ],
      },
      {
        heading: "Secondary typeface — headlines",
        bullets: [
          "Headlines are always written in Arial Bold, left aligned or centered",
          "Sub-headers are Arial Bold at the same point size as the body text",
        ],
      },
      {
        heading: "Line detail",
        body: [
          "The line detail separates text or adds a small visual element to a page.",
        ],
        facts: [
          { label: "How", value: "InDesign / Adobe stroke panel → 'Straight Hash'" },
          { label: "Weight", value: "3pt recommended for most applications" },
          { label: "Colours", value: "Crisp Blue · Sky Blue · Ocean Blue · BioMar Blue" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What is BioMar's primary corporate typeface?",
        options: ["Arial", "Avenir Next", "Times New Roman", "Helvetica"],
        correct: [1],
        explanation: "Avenir Next is the primary corporate typeface, used whenever possible.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "When Avenir Next can't be used in digital media, what do you use?",
        options: ["Any font available", "The secondary typeface (Arial)", "A hand-drawn font", "No text at all"],
        correct: [1],
        explanation: "Digital media falls back to the secondary typeface (Arial) when Avenir Next isn't available.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Type check",
        prompt:
          "Review a document: confirm headlines are Arial Bold, body text is Avenir Next, and any line details use the Straight Hash stroke at 3pt.",
        successCriteria: ["Headline typeface checked", "Body typeface checked", "Line detail style checked"],
      },
    ],
  },
  {
    id: "brand-guidelines-03",
    chapterId: "brand-guidelines",
    title: "Colour & Brand Shapes",
    summary:
      "Correct colour settings, the BioMar colour palette, and the brand shapes & watermarks drawn from our raw materials.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/brand-guidelines--03-colour-brand-shapes.pdf`,
      type: "pdf",
      range: "Pages 15–19",
    },
    sections: [
      {
        heading: "Colour settings",
        note: "Before any BioMar design work in Adobe apps (InDesign, Photoshop, Illustrator), set the colour settings to 'Europe General Purpose 3' via Edit → Colour Settings — otherwise colours will display differently.",
      },
      {
        heading: "BioMar colour palette",
        facts: [
          { label: "BioMar Blue", value: "CMYK 100/84/26/12 · Pantone 654C" },
          { label: "White", value: "RGB 255/255/255" },
          { label: "Sky Blue", value: "Pantone 297C" },
          { label: "Leafy Green", value: "Pantone 368C" },
        ],
      },
      {
        heading: "BioMar shapes & origins",
        body: [
          "The BioMar shapes are a friendly, abstract representation of the raw materials in our feed: Fish, Shrimp/Krill, Macro Algae, Wheat, Corn, Leafy Greens, Palm.",
        ],
        note: "The BioMar shapes should NEVER be used on their own without explicit purpose.",
      },
      {
        heading: "Organic watermark set",
        body: [
          "The shapes have been developed into a set of watermarks that add texture and movement across applications — 12 shape variants, in 5 predefined colour variations that should never be altered.",
        ],
        facts: [
          { label: "Grey tones", value: "Behind body text, or where more interest is needed than plain white" },
          { label: "Ocean / Sky Blue", value: "Used as page breaks or similar" },
          { label: "BioMar Blue", value: "In place of a plain dark blue background" },
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Before doing BioMar design work in Adobe apps, what colour setting must you use?",
        options: ["sRGB Web", "Europe General Purpose 3", "US Web Coated", "Default"],
        correct: [1],
        explanation: "Set colour settings to 'Europe General Purpose 3' so colours display consistently.",
      },
      {
        id: "q2",
        type: "multi",
        prompt: "Which are BioMar Shapes (raw materials)? Select all that apply.",
        options: ["Fish", "Shrimp / Krill", "Salmon feed pellet", "Wheat"],
        correct: [0, 1, 3],
        explanation:
          "The 7 shapes are Fish, Shrimp/Krill, Macro Algae, Wheat, Corn, Leafy Greens and Palm — 'Salmon feed pellet' isn't one of them.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Palette & watermark check",
        prompt:
          "Confirm a layout uses the correct Pantone colours, and if a watermark is used, that it's one of the 5 approved colour variations.",
        successCriteria: ["Colours checked against the palette", "Watermark variation confirmed as approved"],
      },
    ],
  },
  {
    id: "brand-guidelines-04",
    chapterId: "brand-guidelines",
    title: "Photo Style Guide",
    summary:
      "Our values as a Brand House, the focus for water/sustainability/people/product photography, and dos & don'ts.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/brand-guidelines--04-photo-style-guide.pdf`,
      type: "pdf",
      range: "Pages 20–30",
    },
    sections: [
      {
        heading: "Our values — the Brand House",
        bullets: ["Collaboration", "Innovation", "Sustainability", "Performance"],
      },
      {
        heading: "Water",
        body: [
          "Water connects every aspect of the BioMar brand, regardless of species. Images should show calm, clear, location-neutral water — under and above the surface. Avoid crashing waves and stormy seas.",
        ],
      },
      {
        heading: "Sustainability & performance",
        body: [
          "Look for images of fresh, clean produce in its natural environment, local communities, farmers and workers. Performance imagery must show the high quality nature of what we do.",
        ],
      },
      {
        heading: "Other focus areas",
        facts: [
          { label: "Animal Welfare", value: "Focus on genuine, respectful representation" },
          { label: "End Product", value: "Seafood as the outcome of the value chain" },
          { label: "Responsible Sourcing", value: "Where and how raw materials are sourced" },
          { label: "People", value: "Real people, in context, treated with respect" },
          { label: "Product Photography", value: "Clean, accurate representation of the product" },
        ],
      },
      {
        heading: "Photo tips — dos and don'ts",
        bullets: [
          "Good contrast and balance of light and dark reads better than a flat, low-contrast image",
          "Avoid over-exposure — you should still see tone in the sky",
          "Desaturation can improve harmony (skin tone, materials) versus an overly vibrant image",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "What are the 4 values that form BioMar's 'Brand House'?",
        options: ["Collaboration", "Innovation", "Sustainability", "Discounting"],
        correct: [0, 1, 2],
        explanation: "Collaboration, Innovation, Sustainability and Performance form the Brand House.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "Crashing waves and stormy seas are the preferred style for water imagery.",
        options: ["True", "False"],
        correct: [1],
        explanation: "False — water imagery should be calm, clear and location-neutral.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Photo pick",
        prompt:
          "Choose 3 candidate stock photos for a campaign and evaluate each against the Photo Style Guide (values, water style if relevant, contrast/exposure).",
        successCriteria: ["3 photos evaluated", "Each judged against at least two guide criteria"],
      },
    ],
  },
  {
    id: "brand-guidelines-05",
    chapterId: "brand-guidelines",
    title: "Complementary Guidelines",
    summary:
      "Practical tips and best practices from real projects — colours & gradients, packaging (website vs real bags, custom bags), icons, fonts, Our Blue Journey and social media. A complement to the Brand Book, not a replacement.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/brand-guidelines--05-complementary-guidelines.pdf`,
      type: "pdf",
      range: "All 17 pages",
    },
    sections: [
      {
        heading: "What this document is",
        note: "These are additional recommendations, tips and best practices developed over time working with the BioMar brand — not official guidelines. Use them alongside the Brand Book and existing templates, and use your own judgment: every project is different.",
      },
      {
        heading: "Alternative colours",
        bullets: [
          "All approved colours are in the BioMar Product Brand Guidelines — always the primary reference",
          "A few extra colours were approved for specific projects: ones used in GSRs / Our Blue Journey, ones used in packaging, and ones used in other material",
          "They're not part of the core palette — use them when they complement the brand colours and stay consistent with the BioMar identity",
        ],
      },
      {
        heading: "Capitalization",
        bullets: [
          "Title Case for titles, headings and short elements: graph titles, chart labels, infographic headings",
          "Sentence case for longer copy, body text, captions and paragraphs — unless there's a reason to follow another style (official product names, trademarks)",
          "In doubt, check the Brand Voice Guidelines",
        ],
      },
      {
        heading: "Avoid gradients",
        bullets: [
          "Brand consistency: BioMar's identity is clean, simple and Scandinavian-inspired — solid colours reinforce it, gradients look decorative",
          "Print production: gradients are hard to reproduce, especially on packaging — they need specialised equipment or suppliers, add cost and risk inconsistent results",
          "Use solid colours, colour blocks or overlays for depth and hierarchy instead",
        ],
        note: "Exception: a black-to-transparent gradient with a Multiply effect can improve text legibility over images or busy backgrounds — as a supporting tool only, never the main design element or a style on its own.",
      },
      {
        heading: "The BioMar Wave",
        bullets: [
          "A visual element that adds movement, depth and visual interest across materials",
          "Especially in communication materials, it reinforces a friendlier, more organic and approachable look and connects the brand to the natural environment",
          "Keep it simple and balanced — it supports the content, it isn't the main focus",
        ],
      },
      {
        heading: "Packaging — website bags vs. real bags",
        bullets: [
          "Website bags are digital-only and follow a specific structure for consistency across the website. They are not a direct representation of physical packaging",
          "Each website bag has two elements: colour coding (the product category / segmentation) and the life stage wheel (target species stage, easier navigation of the portfolio)",
          "When creating or updating website bags, follow the established digital structure — don't adapt physical bag designs directly",
          "Real bags are the physical packaging used in the market: BioMar standard bags (global packaging structure and visual identity) and custom-made bags (for specific markets or customer requests)",
          "Custom designs can have adaptations but must stay aligned with the BioMar identity and existing packaging principles",
          "When creating or reviewing physical packaging, always consider previous bag developments",
        ],
      },
      {
        heading: "Packaging — consistency (BioMar Blue top)",
        bullets: [
          "In recent developments the top area of the bag is BioMar Blue with the secondary white BioMar logo, so the brand is the first thing people recognise",
          "Exceptions exist depending on market requirements, product positioning or project needs — the goal stays consistency across the portfolio and stronger brand recognition",
          "Known exceptions: BioMar Blue requested on the bottom; a bag that must be differentiated from EXIA packaging; a different visual from the general EFICO bag because it is Functional Feed",
          "Before creating a new design, review existing bags and packaging examples to understand the current direction",
        ],
      },
      {
        heading: "Packaging — custom bag considerations",
        bullets: [
          "Stay aligned with existing packaging: follow the current BioMar direction and review existing bags before starting a concept",
          "Use approved colours whenever possible. If none suit, any new colour must be approved by Global Marketing and the Product Manager before implementation",
          "Keep BioMar Blue as the dominant colour on the bag",
          "Avoid red: it's strongly associated with a main competitor. Only exception: medical feed, where some markets require it by local regulation or industry standard",
          "Keep the design clean and timeless: Scandinavian-inspired, no unnecessary decoration, prioritise clarity, simplicity and longevity over trends",
        ],
      },
      {
        heading: "Icon style",
        note: "Not yet formally defined in the Brand Guidelines. To stay consistent: simple and clean, one-coloured filled icons preferred; avoid stroke icons, which feel lighter and less consistent with the brand expression.",
      },
      {
        heading: "Our Blue Journey booklet",
        bullets: [
          "Showcases BioMar's milestones and progress towards the Our Promise sustainability goals. It has allowed more creative exploration than other corporate material — each edition can develop its own visual direction while staying connected to the brand",
          "Root the design in the corporate colour palette, with room for complementary colours when relevant",
          "Previous directions are in the folder Sustainability > 1. Sustainability Report",
          "Start a new edition by identifying a guiding theme from that year's key topics, achievements or focus areas — it becomes the foundation of the visual concept and story",
        ],
        facts: [
          { label: "2025 — Partnership", value: "“The Impact Line”: a continuous line as a metaphor for collaboration, connecting actions, people and initiatives across the value chain" },
          { label: "2024 — Better Nutrition", value: "“The Bigger the Better”: large-scale numbers, impactful data visualisation and prominent graphs to make achievements easy to grasp" },
        ],
        note: "Each edition should feel unique and relevant to its year while keeping a clear connection to BioMar's visual identity and sustainability story.",
      },
      {
        heading: "Fonts for non-Latin languages",
        facts: [
          { label: "Chinese", value: "Noto Sans CJK SC" },
          { label: "Vietnamese", value: "Arial" },
          { label: "Greek", value: "Arial" },
          { label: "Turkish", value: "Avenir Next" },
          { label: "Russian", value: "Arial" },
        ],
        note: "Always make sure the chosen font supports all required characters and keeps a clean, professional look across applications and formats.",
      },
      {
        heading: "Other fonts we've used",
        bullets: [
          "Alternative fonts are allowed with a clear design justification (e.g. a festive typeface for seasonal material, complementary fonts for the Sustainability Report or Our Blue Journey)",
          "Any alternative font must be selected intentionally and approved by Global Marketing",
          "Coastline is one of the few still in use — first introduced in a campaign, now in selected campaigns and social posts for a warmer, more human touch. Use it sparingly, for short headlines or accent text; it complements the primary typography, never replaces it",
          "Website: due to licensing, titles use Montserrat — see the Website Font Guidelines",
        ],
      },
      {
        heading: "Product bags in social media",
        bullets: [
          "Don't rely too heavily on bag mockups. They're useful when introducing a new product, but shouldn't be the default visual",
          "Communicate the benefits, value and story behind the product — use imagery, illustrations or concepts that explain its purpose, application or impact",
          "Product bags should support the message, not be the message",
        ],
        note: "Tip — ask yourself: “Could this post work without showing the bag?” If yes, lead with the concept and use the bag only when it adds value.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "boolean",
        prompt: "Gradients are the preferred way to add depth to BioMar design concepts.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — avoid gradients (they hurt brand consistency and print reproduction). Use solid colours, colour blocks or overlays instead.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What colour is generally avoided on BioMar packaging, except for medical feed?",
        options: ["Blue", "Green", "Red", "White"],
        correct: [2],
        explanation:
          "Red is a prohibited colour — it's strongly associated with a main competitor. Medical feed is the only exception, where local regulations may require it.",
      },
      {
        id: "q3",
        type: "single",
        prompt: "A custom bag needs a colour that isn't in the approved palette. What do you do?",
        options: [
          "Pick the closest shade yourself",
          "Get it approved by Global Marketing and the Product Manager before implementing",
          "Copy the colour from a competitor's bag",
          "Use a gradient to blend two approved colours",
        ],
        correct: [1],
        explanation:
          "Any new colour must be approved by Global Marketing and the Product Manager before implementation. Competitor colours and gradients are both to be avoided.",
      },
      {
        id: "q4",
        type: "single",
        prompt: "What are the two main elements of a website bag?",
        options: [
          "Wave and icon set",
          "Colour coding and life stage wheel",
          "Blue top and white logo",
          "Gradient and mockup",
        ],
        correct: [1],
        explanation:
          "Website bags are digital-only: colour coding shows the product category, the life stage wheel shows the target species stage. They're not a direct copy of the physical bag.",
      },
      {
        id: "q5",
        type: "single",
        prompt: "How should the top area of a recent BioMar bag look?",
        options: [
          "BioMar Blue with the secondary white BioMar logo",
          "White with a gradient",
          "Red for medical feed, blue for everything else",
          "Whatever the market prefers, no reference needed",
        ],
        correct: [0],
        explanation:
          "Recent bags keep the top in BioMar Blue with the secondary white logo so the brand is recognised first. Exceptions exist, but always review existing bags first.",
      },
      {
        id: "q6",
        type: "single",
        prompt: "Which casing do you use for chart titles and short headings?",
        options: ["Title Case", "Sentence case", "ALL CAPS", "lowercase"],
        correct: [0],
        explanation:
          "Title Case for titles, headings and short elements; sentence case for longer copy, body text and captions.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Spot the fix",
        prompt:
          "Find an existing piece of BioMar marketing material (real or a mockup) that breaks one of these guidelines and note what you'd change.",
        successCriteria: ["A concrete example found", "The specific guideline it breaks identified"],
      },
      {
        id: "e2",
        title: "Packaging review",
        prompt:
          "Open three existing BioMar bags from different ranges. For each, note whether it follows the BioMar Blue top, whether it avoids red, and any approved exception that applies.",
        successCriteria: [
          "Three bags reviewed",
          "Blue top / red check done for each",
          "Any exception identified and explained",
        ],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // STANDALONE REFERENCE (not sourced from a single document)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "tools-map",
    chapterId: null,
    title: "Tools & Platforms Map — What We Use & What For",
    summary:
      "The full toolkit the Design Hub works with, grouped by purpose. (Access & logins live in Loop Link — never here.)",
    estMinutes: 15,
    sections: [
      {
        note: "Logins and passwords are never stored here — request access through Loop Link and the tool owner. This map is only about what each tool is and when to reach for it.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "You need an AI voice-over for a video. Which tool?",
        options: ["Grammarly", "ElevenLabs", "Lasertryk", "Miro"],
        correct: [1],
        explanation:
          "ElevenLabs generates AI voice-overs. Higgsfield.ai is for AI video/image; Grammarly is copy; Lasertryk is print.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Where do the actual logins / passwords for these tools live?",
        options: ["In this Tools Map", "In Loop Link (request access from the owner)", "In the task manager", "In Grammarly"],
        correct: [1],
        explanation:
          "Access and credentials are managed via Loop Link and the tool owner — never stored in the onboarding material.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Get your access",
        prompt:
          "Open the Platforms & Accesses page in Loop Link (linked at the top of this map and in the Always-on info panel), then request access to the tools your role needs. Note the owner for any that require approval.",
        successCriteria: ["Access requested for the tools your role uses", "Owner noted for anything pending"],
      },
    ],
  },
  {
    id: "folder-structure",
    chapterId: null,
    title: "Folder Structure — The Shared Drive, Mapped",
    summary:
      "The real folder tree of the Design Hub's shared drive, explorable and searchable, plus an interactive wizard for where a new file belongs.",
    estMinutes: 15,
    sections: [
      {
        note: "This is a live map of the real structure — not a simplified example. Use the wizard when you're not sure where something goes, and the search when you already know what you're looking for.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "You need to save a roll-up banner for a specific LARVIVA sub-product campaign. What's the first question to ask yourself?",
        options: [
          "Is it an asset?",
          "Is it a product?",
          "Is it for a specific market?",
          "Does that category have a folder?",
        ],
        correct: [1],
        explanation:
          "The wizard always starts by asking whether the file is for a product — that's what routes you into the Product folders (LARVIVA, INICIO, SmartCare, etc.) in the first place.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "A brand logo or template isn't tied to any one product or market. Where does it belong?",
        options: ["Design Assets", "Global", "Corporate", "Create a new top-level folder"],
        correct: [0],
        explanation:
          "Anything that isn't a product and isn't market/org-specific but is an asset (logo, template, guideline) goes into Design Assets.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Find it yourself",
        prompt:
          "Using the search, find where BioMar's brand guidelines live, and separately, where you'd save a new roll-up banner for a SmartCare campaign. Write down both paths.",
        successCriteria: [
          "Correct path found for the brand guidelines",
          "Correct path found (or created, per the wizard) for the SmartCare roll-up banner",
        ],
      },
    ],
  },
  {
    id: "global-strategy-2025",
    chapterId: null,
    title: "Global Marketing Strategy — Q2 2025 Update",
    summary:
      "How Global Marketing segments products and customers, and where that thinking is heading. Optional deep-dive, not required day-to-day.",
    estMinutes: 25,
    material: {
      file: "/materials/global-marketing-strategy-house-q2-2025.pdf",
      type: "pdf",
      range: "Full deck (32 pages)",
    },
    sections: [
      {
        heading: "Why this is here",
        note: "This is internal Global Marketing strategy work, not something you need to do your day-to-day design tasks. It's here for context, for anyone who wants to understand how Marketing thinks about products and customers.",
      },
      {
        heading: "Product segmentation",
        body: [
          "Products are segmented by life stage (Hatchery → Starter/Fresh Water → Grower/Sea Water) and by performance tier (Standard, High, Top), with optional attributes like Medicated or Premium. This segmentation now feeds a gross profit report, reconciled monthly with finance data.",
        ],
      },
      {
        heading: "Needs-based customer segmentation",
        body: [
          "Based on 23 in-depth interviews, four customer clusters were identified along two axes — Innovation & Risk Appetite (Conservative ↔ Progressive) and Business Mindset (Market Differentiation ↔ Operational Efficiency): Future Shapers, Scalable Performers, Solid Executors and Cautious Builders.",
        ],
        facts: [
          { label: "Future Shapers", value: "Ambitious innovators — differentiation as their edge" },
          { label: "Scalable Performers", value: "Operational minds — push for volume & efficiency" },
          { label: "Solid Executors", value: "Reliable — stability, consistency, doing what works" },
          { label: "Cautious Builders", value: "Risk-averse — differentiation through safe, proven steps" },
        ],
      },
      {
        heading: "Where this is heading",
        body: [
          "Next steps layer a BCG-style matrix (market growth vs. market share) onto the customer clusters, using 2022–2024 data on products/services used or needed, to define clear value propositions, a change-management matrix and KPIs per cluster.",
        ],
      },
    ],
    quiz: [],
    exercises: [],
  },
];

export const modulesById = Object.fromEntries(modules.map((m) => [m.id, m]));
