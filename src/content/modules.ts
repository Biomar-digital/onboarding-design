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
      "What Global Marketing is, its three working areas, the org structure and the team.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--01-team-organisation.pptx`,
      type: "pptx",
      range: "Slides 1–6",
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
          "BioMar Marketing (brand, positioning, shared services)",
          "Product Marketing Management (manages a segment, develops the product range)",
          "Local Marketing (launches the range and runs local initiatives)",
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
        note: "See the Marketing Organisation chart in the slides above.",
      },
      {
        heading: "The Global Marketing team",
        bullets: [
          "Isidora Silva Chiros — Graphic Designer",
          "Nerea Palacios — Content Creator",
          "Matt Evans — Digital Marketing Platforms Specialist",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which are the three working areas of Marketing? (select all)",
        options: ["BioMar Marketing", "Product Marketing Management", "Local Marketing", "Fleet Operations"],
        correct: [0, 1, 2],
        explanation:
          "The three areas are BioMar Marketing, Product Marketing Management and Local Marketing.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Which markets belong to the Salmon division?",
        options: ["Vietnam & China", "Baltics & WestMed", "Australia, UK, Norway, Chile", "Costa Rica & Ecuador"],
        correct: [2],
        explanation:
          "Salmon covers Australia, UK, Norway and Chile.",
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
    title: "Larval Research Facilities",
    summary:
      "The ATC Hirtshals larval research facilities — and the signage work the Design Hub supports there.",
    estMinutes: 15,
    material: {
      file: `${SLICE}/dh2026--06-larval-research-facilities.pptx`,
      type: "pptx",
      range: "Slides 30–33",
    },
    sections: [
      {
        heading: "ATC Hirtshals",
        body: [
          "BioMar has invested in advanced larval research facilities at ATC Hirtshals, capable of performing trials in semi-industrial conditions. The trial facilities serve as a hub for research and development, product consolidation and validation.",
        ],
      },
      {
        heading: "Trial facilities layout",
        bullets: [
          "Signage: 60×40cm",
          "Wall space for design/canvas at the end of the hallway",
          "Wall dimensions approx. 1.2m × 2.5m",
        ],
        note: "This is real design work the Hub supports — wayfinding and signage for the facility.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What is ATC Hirtshals?",
        options: [
          "A marketing office",
          "BioMar's advanced larval research facility",
          "A print supplier",
          "A stock photography agency",
        ],
        correct: [1],
        explanation:
          "ATC Hirtshals is BioMar's advanced larval research facility for semi-industrial trials.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What size is the facility signage?",
        options: ["30×20cm", "60×40cm", "100×100cm", "A4"],
        correct: [1],
        explanation: "The signage spec is 60×40cm.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Signage concept",
        prompt:
          "Sketch a signage concept for the hallway wall space (approx. 1.2m × 2.5m) at the end of the hallway, following brand guidelines.",
        successCriteria: ["Concept fits the stated dimensions", "On-brand (logo, colour, typography)"],
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
          "Go through this map and, via Loop Link, request access to the tools your role needs. Note the owner for any that require approval.",
        successCriteria: ["Access requested for the tools your role uses", "Owner noted for anything pending"],
      },
    ],
  },
];

export const modulesById = Object.fromEntries(modules.map((m) => [m.id, m]));
