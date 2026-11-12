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
      file: `${SLICE}/strategic--01-who-we-are-v2.pptx`,
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
          "Andres Bernadou — Multimedia Designer. 2 years at BioMar. Video & digital design (external and internal). Supporting storytelling and concept creation across markets. Works with campaigns & corporate communication.",
          "New designer — joining the Design Hub.",
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
  },
  {
    id: "strategic-03",
    chapterId: "strategic",
    title: "Process, History & Brand Governance",
    summary:
      "How the Hub approaches work, its timeline through the years, and a first look at brand governance.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/strategic--03-process-history-governance-v2.pptx`,
      type: "pptx",
      range: "Slides 9–13",
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
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Global & Group Marketing (18 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "global-01",
    chapterId: "global",
    title: "Team & Organisation",
    summary:
      "What Global Marketing is, its three working areas, the Global Marketing team and the regional marketing organisation.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/global--01-team-organisation-v2.pptx`,
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
        facts: [
          {
            label: "Global Marketing",
            value:
              "Brand & strategy ownership. Owns the global brand identity and architecture, marketing strategy and frameworks, global campaigns and concept launches, and tone of voice and messaging standards.",
          },
          {
            label: "Group Marketing",
            value:
              "BioMar Group as a market. Owns the BioMar Group LinkedIn page, Instagram @biomargroup, YouTube channel, the Group website and content for Sustainability, R&D and Sourcing.",
          },
          {
            label: "Marketing Agency",
            value:
              "Support services — an internal agency serving markets and divisions. Creative production and design & visual assets (DesignHUB); digital marketing and content marketing support (DigitalHUB).",
          },
        ],
        note: "The Design Hub is part of the Marketing Agency.",
      },
      {
        heading: "The Global Marketing team",
        facts: [
          { label: "Global Marketing Director", value: "Helle Vansgaard" },
          { label: "Design Hub — Multimedia Designer", value: "Andres Bernadou" },
          { label: "Digital Marketing Platforms Specialist", value: "Matt Evans" },
          { label: "Content Creator", value: "Nerea Palacios" },
        ],
      },
      {
        heading: "Marketing organisation — three levels",
        bullets: [
          "Global Marketing manages the BioMar brand, creates the positioning for all product concepts and services and runs the centralised Design and Digital Shared Services agency",
          "Product Marketing Management manages its segment and develops the product range in its product portfolio",
          "Local Marketing launches its product range and runs marketing initiatives to support its businesses",
        ],
      },
      {
        heading: "Regional marketing teams",
        facts: [
          {
            label: "EMEA",
            value:
              "Kseniya Akkaya (Manager, Turkey) · Cathrine Weirbach (Manager, Denmark) · Iris Hernandez (Manager, Spain) · Christina Kravariti (Assistant, Greece)",
          },
          {
            label: "LATAM",
            value:
              "Daniela Vera · Valeria Triviño Alvarez (Marketing Manager, Ecuador) · Steven Leon Ulloa (Marketing Responsible, Costa Rica)",
          },
          {
            label: "Asia",
            value:
              "Xinru Wang · Thu Minh Dang (Marketing Assistant, Vietnam) · Ma Teng (Marketing Manager, China)",
          },
          {
            label: "Salmon",
            value:
              "Joana Silva · Thomas Hansen (Manager, Norway) · Andrew Richardson (Responsible, UK) · Claudio Muñoz (Manager, Chile) · Victoria Valdenegro (Manager, Australia)",
          },
        ],
        note: "On the org chart, Daniela Vera, Xinru Wang and Joana Silva sit on the inner ring with their segment; the others are the local marketing contacts per country.",
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
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Design Hub 2026 (33 slides)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "dh2026",
    chapterId: "dh2026",
    title: "Design Hub 2026",
    summary:
      "The full Design Hub 2026 presentation: the challenges, how and when to reach out, deadlines and priority, the start-to-finish process, feedback, files, turnaround times, communication, responsibility and the Brief Template with a worked example.",
    estMinutes: 90,
    material: {
      file: `${SLICE}/dh2026--design-hub-2026.pptx`,
      type: "pptx",
      range: "Full presentation (28 slides)",
    },
    resources: [BRIEF_TEMPLATE],
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
        heading: "Start to finish — the Design Hub process",
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
        heading: "What the Design Hub does",
        bullets: [
          "Review the brief, enter it in the Design Hub task manager, tag the contact person and inform them via email — request any missing information",
          "Submit drafts via email, following the same thread: paths for files, links for videos",
          "Adjust based on feedback and submit the final files",
          "Close the task and move the card to the Completed tab",
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
      {
        heading: "File storage — you'll always find",
        bullets: [
          "Editable file (for the Design Hub)",
          "File for review (for the Draft Date — ends in PROOF)",
          "Final file (for the Final Date — ends in PRINT or DIGITAL)",
        ],
      },
      {
        heading: "Turnaround times",
        bullets: [
          "Day-to-day reference (Strategic presentation, the most recent): a task takes about 2–6 days with 1–3 review rounds; a project 2–24 weeks with several review rounds.",
          "The table in the slides gives indicative times by type of piece — use it for the bigger items (logo creation, new product, new concept). Where it differs for small tasks, the figures above apply.",
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
      {
        heading: "A worked example — reading a real brief",
        body: [
          "Right after the Brief Template comes a real brief the Design Hub received: a request for signage at BioMar's larval research facility at ATC Hirtshals. It's included here as a worked example — notice how concrete it is compared to a vague request.",
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
        note: "Compare this against the four minimum-info items: purpose, timeline, specifications, copy/assets. This example nails the specifications — exact sizes, not \"medium-ish\" or \"the usual size\".",
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
  },
  {
    id: "playbook-02",
    chapterId: "playbook",
    title: "Email Tags & the Task Manager",
    summary:
      "How the inbox stays tagged, and the task manager board — columns, cards, tags, to-dos and notes.",
    estMinutes: 35,
    material: {
      file: `${SLICE}/playbook--02-email-tags-task-manager-v2.pptx`,
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
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: BioMar Brand Guidelines 2026, v5 (48 pages)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "brand-guidelines-01",
    chapterId: "brand-guidelines",
    title: "Corporate Logo",
    summary:
      "Our purpose and tagline, and our most valuable brand asset: elements, file formats, placement, incorrect uses, the promotional-only version and the element logo.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/brand-guidelines-2026--01-corporate-logo.pdf`,
      type: "pdf",
      range: "Pages 1–8",
    },
    sections: [
      {
        heading: "Our purpose and tagline",
        facts: [
          { label: "Purpose", value: "We are innovators dedicated to an efficient and sustainable global aquaculture." },
          { label: "Purpose statement", value: "We are dedicated to innovating aquaculture." },
          { label: "Shortened purpose statement", value: "Powered by Partnership. Driven by Innovation. We are innovators in high performance aqua feeds dedicated to doing our part in sustainable global aquaculture." },
          { label: "Tagline", value: "Powered by Partnership. Driven by Innovation." },
        ],
        note: "Founded in 1962 by fish farmers, BioMar is in it for the long haul: open, long-term partnerships and a true dedication to innovation across the globe.",
      },
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
        heading: "Logo over BioMar Blue",
        body: [
          "It is permitted to use the BioMar primary logo over a BioMar Blue background. It is also permitted to use a dark outer glow to define the edges of the box element.",
        ],
      },
      {
        heading: "Incorrect uses",
        bullets: [
          "The dimensions of the logo are fixed and must not be altered",
          "Don't use the logo out of the box with black text",
          "Don't use the logo in a square box",
          "Don't alter the dimensions",
          "Don't change the colours",
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
        heading: "Size & clear space",
        facts: [
          { label: "Recommended size", value: "1/7th of the page width — on a standard A4 that is 30 mm wide" },
          { label: "Minimum size", value: "15 mm wide (a recommendation — it must stay legible and appropriate for each application)" },
          { label: "Clear space", value: "Nothing should intrude into the minimum clear space, calculated using the top 'wave' of the logo" },
        ],
        note: "The box icon is not a perfect square — keep the ratio accurate when scaling.",
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
      {
        heading: "Element logo (without wordmark)",
        body: [
          "Made up of the elements of the BioMar Blue logo, excluding the wordmark. Use it when a symbol format is more appropriate, and when the law prohibits using the BioMar wordmark.",
        ],
        facts: [
          { label: "Colour versions", value: "2 — White and BioMar Blue" },
          { label: "Pattern", value: "A pattern format of the element logo exists for cases where a pattern is required" },
        ],
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
      file: `${SLICE}/brand-guidelines-2026--02-typography.pdf`,
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
  },
  {
    id: "brand-guidelines-03",
    chapterId: "brand-guidelines",
    title: "Colour & Brand Shapes",
    summary:
      "Colour settings, the full BioMar palette and greys, logo colours, the BioMar shapes and the watermark sets — with the colours ready to download as Adobe swatches.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/brand-guidelines-2026--03-colour-brand-shapes.pdf`,
      type: "pdf",
      range: "Pages 15–20",
    },
    resources: [
      { title: "Adobe swatches — RGB (.ase)", file: "/downloads/BioMar-Colours-2026-RGB.ase" },
      { title: "Adobe swatches — CMYK (.ase)", file: "/downloads/BioMar-Colours-2026-CMYK.ase" },
      { title: "All colour values (.csv)", file: "/downloads/BioMar-Colours-2026.csv" },
      { title: "Swatch preview (.png)", file: "/downloads/BioMar-Colours-2026-preview.png" },
    ],
    sections: [
      {
        heading: "Colour settings",
        body: [
          "Before any BioMar design work in Adobe apps (InDesign, Photoshop, Illustrator), set Edit → Colour Settings → Settings → Europe General Purpose 3 — otherwise colours display differently.",
        ],
        facts: [
          { label: "RGB working space", value: "sRGB IEC61966-2.1" },
          { label: "CMYK working space", value: "Coated FOGRA39 (ISO 12647-2:2004)" },
        ],
        note: "Web uses RGB, print uses CMYK. Choose the right format for your output when you start the document — converting between them gives inaccurate colours. Always consult your printing supplier for the most accurate reproduction.",
      },
      {
        heading: "BioMar colour palette",
        facts: [
          { label: "BioMar Blue", value: "RGB 31/62/119 · CMYK 100/84/26/12 · Pantone 654 C · #1f3e77" },
          { label: "Sky Blue", value: "RGB 146/206/232 · CMYK 50/0/6/0 · Pantone 297 C · #92cee8" },
          { label: "Leafy Green", value: "RGB 151/209/48 · CMYK 56/0/92/0 · Pantone 368 C · #97d130" },
          { label: "Shrimp Orange", value: "RGB 221/105/40 · CMYK 8/68/91/1 · Pantone 166 C · #dd6928" },
          { label: "Ocean Blue", value: "RGB 4/113/173 · CMYK 87/50/8/0 · Pantone 285 C · #0471ad" },
          { label: "Crisp Blue", value: "RGB 195/228/239 · CMYK 25/0/3/0 · Pantone 277 C · #c3e4ef" },
          { label: "Wheat Yellow", value: "RGB 234/179/24 · CMYK 10/28/91/1 · Pantone 115 U · #eab318" },
        ],
      },
      {
        heading: "Greys and the use of black",
        body: [
          "All BioMar greys are made from percentages of black, for a neutral-toned palette. Always proof grey tones so they aren't too cool or too warm.",
          "BioMar is blue: dark text should be BioMar Blue. Where BioMar Blue can't be used, use Black 80% (RGB 87/87/86 · #575756) or Black.",
        ],
      },
      {
        heading: "Logo colours",
        body: [
          "The primary logo comes in 1-colour versions: BioMar Blue, White, Sky Blue and Leafy Green.",
        ],
      },
      {
        heading: "BioMar shapes & origins — graphic elements",
        body: [
          "Two complementary categories make up the BioMar graphic elements: the BioMar Swoosh and the Aquaculture Graphics.",
        ],
        facts: [
          { label: "The BioMar Swoosh", value: "Derived directly from the logo — our primary graphic element. Symbolises movement, progress and continuity." },
          { label: "Aquaculture Graphics", value: "Abstract graphics inspired by aquaculture — fish, shrimp/krill and feed/pellets — adding texture, depth and visual interest." },
        ],
        note: "The graphic elements should never be modified, distorted or used in a way that compromises the integrity of the BioMar brand.",
      },
      {
        heading: "Watermark sets",
        bullets: [
          "Swoosh watermarks — a set of 6 (01–06) in the 5 colour variations",
          "Organic watermarks — 12 different layouts drawn from the raw materials, for textured backgrounds",
          "Icon watermarks — fish, shrimp/krill and feed pellets, 2 layouts each; as a general rule landscape layouts only",
          "They can be used in any orientation, are meant to bleed off the page and sit behind all other elements and type",
          "Files fit A3 (297 × 420 mm) and scale proportionally to other formats",
        ],
        note: "Never try to re-create or edit the watermarks. If none of the variations fits your project's needs, contact Global Marketing.",
      },
      {
        heading: "Watermark colours",
        facts: [
          { label: "01 Light Grey / 02 Dark Grey", value: "Behind body text, or where more interest is needed than a plain white background" },
          { label: "03 Sky Blue / 04 Ocean Blue", value: "Page breaks and section breaks — Ocean Blue for a section break, Sky Blue for a sub-section" },
          { label: "05 BioMar Blue", value: "In place of a plain dark blue background, back pages and the corporate sign off" },
        ],
        note: "These 5 colour variations are predefined and must never be altered. Files are named by series, shape number, colour setting and colour number so you can find the right one.",
      },
      {
        heading: "Watermark usage",
        bullets: [
          "Light grey watermarks work best behind large bodies of text; coloured watermarks must never sit behind large bodies of text",
          "Corporate sign off: use a BioMar Blue watermark behind the logo, tagline and footer — pick one that cuts through where the logo sits so it stands out",
          "Business card: a dark organic watermark plus the icon layouts",
          "Cover pages: a BioMar Blue watermark or an approved water photograph",
        ],
      },
      {
        heading: "Adobe swatches — download",
        body: [
          "The whole palette is ready to load into Adobe so you never type colour values by hand: 30 swatches in three groups — the core palette, the greys and the product sub-brand colours. Use the RGB file for screen and web, and the CMYK file for print.",
        ],
        bullets: [
          "Illustrator or InDesign: Swatches panel → menu → Open Swatch Library → Other Library… and choose the .ase file. In Photoshop: Swatches panel menu → Import Swatches",
          "To keep them in your Creative Cloud Library: select the swatches and use Add to CC Library, or Libraries panel → + → Color",
          "Do it once with the RGB file and once with the CMYK file, each in its own library — Adobe doesn't mix colour modes inside one swatch",
        ],
        note: "Pantone references aren't stored inside the .ase files — they're in the .csv. The product sub-brand colours come from the Product Brand Guidelines; use them only for the product they belong to.",
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
      file: `${SLICE}/brand-guidelines-2026--04-photo-style-guide.pdf`,
      type: "pdf",
      range: "Pages 21–30",
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
      {
        heading: "Photographers and file management",
        bullets: [
          "Give any photographer the photo style guide before the shoot, to keep a uniform look across BioMar",
          "Plan a detailed shot list and a mood board with a wide range of shot positions and angles — it avoids re-shoots and saves cost",
          "Share all 'hero' shots from every shoot globally, in the Global Marketing Photo Library",
          "Put the photo information in the file name: location, species, production type, personnel and date. All submitted photos must be GDPR compliant",
          "Send a link instead of very large photo files by email — the aim is to eliminate external transfer tools like Dropbox and WeTransfer",
        ],
      },
    ],
  },
  {
    id: "brand-guidelines-06",
    chapterId: "brand-guidelines",
    title: "Layout Design",
    summary:
      "Bringing it all together: templates, grid, social media, email, stationery, promotional items, uniforms, signage, packaging, vehicles, special cases and print.",
    estMinutes: 45,
    material: {
      file: `${SLICE}/brand-guidelines-2026--05-layout-design.pdf`,
      type: "pdf",
      range: "Pages 31–47",
    },
    sections: [
      {
        heading: "Templates — ease of use",
        body: [
          "Templates have been created to bring the guidelines together. Adobe templates have instructions inside the file and are ready to go; instructions in each template give a consistent look across all media.",
        ],
        bullets: [
          "Adobe InDesign: business card, presentation folder, envelopes, certificate, greeting card, 'with compliments' card",
          "Microsoft Word: letterhead, press release, corporate memo",
          "Adobe Illustrator: feed bags, roll up banners, flags (each supplier has different templates — contact Global Marketing)",
        ],
        note: "Some templates are exceptions to the general rules — each template overrides them for its application. If the rules don't apply or don't display well, contact Global Marketing.",
      },
      {
        heading: "Grid system",
        facts: [
          { label: "Margins (example)", value: "Top 12 mm · Bottom 12 mm · Inside 25 mm · Outside 12 mm" },
          { label: "Grid", value: "Two grids: 3 columns × 5 rows, and 15 columns × 25 rows — each large square holds 25 smaller squares" },
          { label: "Square (200×200)", value: "Margins 12 mm · small grid 7×7 · large grid 21×21" },
          { label: "A4 (210×297)", value: "Margins 12 mm · small grid 9×6 · large grid 27×18" },
        ],
        note: "All grids sit within the margins and have no gutter.",
      },
      {
        heading: "Social media — tone and emojis",
        bullets: [
          "Create a cohesive look and feel across all platforms; use the BioMar introduction statement (with or without hashtags)",
          "Take a professional tone: say what we support/like, share simple facts and accurate figures, always be respectful",
          "Avoid being overly friendly or familiar, debate-style or negative messaging, and 'don't support/like' wording; no opinions on discussions unless approved by Global Marketing or Corporate Communications",
          "No emojis with facial expressions, and no more than 3 per post. Allowed: shrimp, fish, planet (sustainability), light bulb (innovation), two hands up, thumbs up",
        ],
      },
      {
        heading: "Social media — banners, icons and profile pictures",
        bullets: [
          "Use the same logo and cover image on every platform; to highlight a launch or campaign, pin a post instead of changing the cover. A cover video is provided",
          "Use the BioMar social media icon set (rounded square like the logo): BioMar Blue for light backgrounds, Grey or White for dark ones — don't use other colours or shapes",
          "Profile pictures: show the primary logo in a square with rounded corners wherever possible; only use a circle when the channel gives no square option, with clear space so the elements aren't touching or cropped",
        ],
      },
      {
        heading: "Email",
        facts: [
          { label: "Body text", value: "Arial, 10 pt, BioMar Blue" },
          { label: "Signature — name", value: "Arial Bold, 11 pt, BioMar Blue" },
          { label: "Signature — job title", value: "Arial, 9 pt, Ocean Blue" },
          { label: "Signature — contact details & address", value: "Arial, 9 pt, BioMar Blue" },
          { label: "Signature — BioMar title & website", value: "Arial Bold, 9 pt, BioMar Blue" },
          { label: "Signature — legal info", value: "Arial, 9 pt, Light Grey" },
          { label: "Logo", value: "125 px wide (file provided)" },
        ],
        note: "All BioMar employees worldwide use the same signature, which reinforces brand recognition. Social icons (20% black) are optional — only the ones relevant to your market. Advertising and tagline banners are optional templates; local languages are allowed, but text and image display must stay the same.",
      },
      {
        heading: "Business cards",
        bullets: [
          "Front: choose from 3 options, each with the BioMar logo and tagline",
          "Back: 3 watermarks — Pellets, Shrimp or Fish",
          "Use the InDesign template so everyone has the same card",
          "Optional personalised dynamic QR code with your contact details (a vCard) — it can be edited later without changing the code",
          "Finish: satin paper with a matte finish recommended; spot gloss on the front is an optional extra",
        ],
      },
      {
        heading: "Envelopes, cards, folders and certificates",
        facts: [
          { label: "Envelopes", value: "3 variations (logo + office info; logo + tagline; logo only). Sizes C4, C5, M5, M65. For bulk buying across markets, print without the address and add it with a sticker or stamp" },
          { label: "Greeting card", value: "A6 tent fold (flat 148×210 mm, folded 148×105 mm), blank inside; 260 gsm card, matte or silk finish; optional silver foil" },
          { label: "'With Compliments' card", value: "A7 (105 × 74 mm), double-sided, no fold, for gifts; print-ready PDF in the template" },
          { label: "Presentation folder", value: "Dark blue watermark or a neutral water image; full colour BioMar Blue inside recommended (blank interior permitted); matte finish; consider slits for business cards. Use your printer's own template" },
          { label: "Certificate", value: "Watermark on the reverse; recipient's name by hand or in the typeface Signpainter; 160 gsm or higher silk coated paper" },
        ],
      },
      {
        heading: "Letterhead, press release, invoice and presentations",
        bullets: [
          "Letterhead, press release and corporate memo are Microsoft Word templates; the invoice follows the BioMar invoice layout",
          "The PowerPoint template is installed on all BioMar computers — use the Widescreen format for all new presentations (apply the theme to a blank document if you need 4:3)",
        ],
      },
      {
        heading: "Promotional material and clothing",
        bullets: [
          "Promotional product colours should be blue; black only when blue isn't available; white only in certain countries for environmental and weather reasons",
          "Dark blue, navy or black items: corporate logo without box, or solid white logo. Light items: solid blue logo. Clear items: corporate logo with box, solid blue or solid white. High-vis items: the silver logo, only on high-vis coloured items",
          "The logo without the box is only for promotional items — never on light backgrounds, never with a black 'BioMar' text, never in print or digital media",
          "T-shirt: logo over the heart and on the opposite sleeve (both recommended), 55 mm wide and the same size; the tagline only on the back, centred across the shoulder blades (140 mm down from the neckline, 70 mm in from the sleeve seams)",
          "Never re-create the tagline; use the 'rt' ligature version so the r and t meet smoothly. Two versions: BioMar Blue for light fabric, White for medium to dark",
        ],
      },
      {
        heading: "Uniforms, corporate clothing and headwear",
        bullets: [
          "Navy or black items: logo without box. White/light items: solid BioMar Blue logo",
          "Standard logo 55 mm wide (65 mm on thicker embroidered fabrics like puffa jackets and fleece); front left chest, upper arm or pants side pocket 55–65 mm; large back logo 180 mm wide, centred on the upper back; high-vis logo front left chest, silver when possible",
          "Corporate clothing that isn't a uniform: logo embroidered in the same colour as the shirt — centred near the collar at the back (35–45 mm) or front left chest (35–55 mm)",
          "Beanies and caps in high-quality navy blue (beanie logo 35–45 mm, cap 55–65 mm); hard hats get die-cut stickers with the full corporate logo, 45–55 mm wide",
        ],
      },
      {
        heading: "Signage",
        facts: [
          { label: "Background", value: "BioMar Blue" },
          { label: "Text", value: "White, in the corporate typeface Avenir Next" },
        ],
        note: "All exterior signage follows this to carry BioMar's visual identity through our workspaces.",
      },
      {
        heading: "Packaging — feed bags",
        bullets: [
          "Standard 20–25 kg bags are printed in BioMar Blue and show the BioMar logo, except in regions where the law restricts the use of the BioMar word mark on product packaging — there the logo element is used",
          "Big bags: use the logo element when the solid blue BioMar logo can't be used for legal reasons",
          "Black & white sticker labels for feed bags: use the Corporate Logo variation",
          "Patterns (with logo, or element only) are provided. Each supplier has different templates — send them to Global Marketing to be updated with the new branding",
        ],
      },
      {
        heading: "Vehicles, containers and boats",
        bullets: [
          "Logo always centred vertically and horizontally; on trucks and trailers use the logo or the logo with tagline (tagline only once on the side and once on the back). Trucks fully painted BioMar Blue",
          "Cars: aim for BioMar Blue (white is next best) — primary logo without the box on blue vehicles, solid blue logo on white. 3 logos in total: one on each front door and one on the rear, on the driver's side unless car branding gets in the way",
          "Shipping containers: BioMar Blue (full colour corporate logo) or white (solid blue logo)",
          "Boats: BioMar Blue with the logo (the word mark is also permitted); where surfaces can't be painted blue, always use the logo with the box",
        ],
      },
      {
        heading: "Special cases — engraving and QR codes",
        bullets: [
          "Metal: silver products; Wood: light-coloured wood. In both, use the corporate logo variation and engrave text in Avenir Next where possible",
          "QR codes for business cards are generated on qr-code-generator.com (login from your Marketing Manager): vCard Plus → BioMar QR Template → customise with the BioMar preset → download as JPG with high error correction. The codes are dynamic, so contact details can be changed later",
        ],
        note: "These are general rules; special cases that need a different solution should go to Global Marketing.",
      },
      {
        heading: "Paper and printing",
        bullets: [
          "Digital printing is best for small runs; offset is only cost-effective for large runs. Neither is best — it depends on cost, quantity and colour output, and the two can give slightly different colours",
          "Whenever possible choose environmentally friendly/eco paper and printing suppliers, and look for eco-labels in your country (for example the Nordic Swan)",
          "Settings listed in the guidelines (ring binder, divider tabs, internal pages) are just what was used locally — consult your own printer for your finish",
        ],
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
        note: "The Brand Voice Guidelines (July 2026) set sentence case for subheadings, captions, table headers and chart labels, and Title Case for article, press release, report and slide titles — follow them where they differ from the tips above.",
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
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CHAPTER: Voice, Product & Photo Guidelines
  // Brand Voice (Jul 2026) · Product Brand Guidelines (2025) · Photoshoot and
  // Global Portrait Photo Guidelines (2024)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "voice-guidelines",
    chapterId: "more-guidelines",
    title: "Brand Voice Guidelines",
    summary:
      "How BioMar writes: identity in words, principles, British English, casing, the BioMar name, vocabulary, channels and Global Spanish.",
    estMinutes: 20,
    material: {
      file: `${SLICE}/voice-guidelines-2026-07.pdf`,
      type: "pdf",
      range: "11 pages · v1, July 2026",
    },
    sections: [
      {
        heading: "Our identity in words",
        body: [
          "What distinguishes BioMar is that we work alongside the people who use our feed, and we say only what the science supports. We explain rather than assert: we give the reader the evidence and let it do the persuading, and we are willing to say what we don't yet know.",
          "We write as a knowledgeable colleague, not as a supplier addressing a buyer: confident, calm and specific, never distant. A farm manager, a scientist and a journalist reading the same paragraph should each find it accurate, and none should find it patronising.",
        ],
        note: "These guidelines apply to all written communication: corporate materials, scientific articles, press releases, social media and customer-facing content.",
      },
      {
        heading: "Core principles",
        facts: [
          { label: "Clear and informed", value: "Complex topics in straightforward, structured language, supported by data where relevant." },
          { label: "Professional and approachable", value: "Balanced — not overly formal, not casual. Open, factual and respectful." },
          { label: "Accurate and responsible", value: "Evidence-based claims; no hype, exaggeration or ambiguous promises." },
          { label: "Consistent across markets", value: "One global company: the depth of detail may vary by audience, the tone stays constant." },
        ],
        note: "When principles conflict, accuracy wins. If a claim can't be simplified without losing precision, keep the precise version and add a sentence of explanation.",
      },
      {
        heading: "Language style",
        bullets: [
          "Straightforward and structured: clean sentences; technical terms only when they add value",
          "Short, readable paragraphs",
          "Neutral and objective: facts lead; avoid unnecessary adjectives and dramatic language",
          "British English for all English content — spelling, vocabulary and grammar",
        ],
      },
      {
        heading: "Casing",
        facts: [
          { label: "Title Case", value: "Article titles, press release headlines, report titles and presentation slide titles. Capitalise the first and last word and all nouns, pronouns, verbs, adjectives and adverbs; keep articles, coordinating conjunctions and prepositions of four letters or fewer in lower case." },
          { label: "Sentence case", value: "Subheadings, captions, table headers and chart labels." },
          { label: "Full capitals", value: "Not used — they read as raised volume. Exceptions: established acronyms (ASC, SBTi, FCR, EPA, DHA, R&D), brand names formally set in capitals (such as LARVIVA) and legal or safety text." },
          { label: "Not permitted", value: "Capitals for emphasis, and in calls to action, buttons, navigation labels, social posts or email subject lines." },
        ],
        note: "Yes: “BioMar is expanding its French facility.” / “Download the report”. No: “BioMar is proud to announce a MAJOR expansion.” / “DOWNLOAD THE REPORT”. Where this differs from the Complementary Guidelines (chart titles and labels), follow Brand Voice — it is the reference those guidelines point to.",
      },
      {
        heading: "The name BioMar, titles and “we”",
        bullets: [
          "Always BioMar — capital B and capital M, no space. Never Biomar, BIOMAR, biomar, Bio Mar or BioMAR, in any casing context",
          "Capitalise a job title before a name or as part of a formal title (Chief Executive Officer Carlos Diaz); lower case for a team or role in general (the Global Marketing team)",
          "“We” in BioMar-authored content such as website articles, corporate explanations or storytelling",
          "Third person in joint press releases, partnership announcements or wherever neutrality is required. Naming BioMar directly is allowed and often preferred; “the company” only when third person is required (official reports, regulatory contexts)",
        ],
      },
      {
        heading: "Writing in practice — before and after",
        facts: [
          { label: "Press release opening", value: "Before: “BioMar is thrilled to unveil a revolutionary new chapter…”  After: “BioMar has expanded its Aquaculture Technology Centre in Hirtshals, adding four recirculation systems for trial work with sea bass and sea bream.”" },
          { label: "LinkedIn post", value: "Before: “HUGE news from the BioMar team!!”  After: “Our team in Costa Rica has been trialling a new shrimp feed formulation with three partner farms. Early results on survival rates are encouraging…”" },
          { label: "Describing research", value: "Before: “Our groundbreaking research proves that targeted nutrition eliminates gill health issues…”  After: “In a 12-week trial, salmon fed the test diet showed reduced gill score severity compared with the control group.”" },
        ],
      },
      {
        heading: "What to avoid",
        bullets: [
          "Exaggerated or dramatic language: revolutionary, game-changing, breakthrough, unveil, thrilled",
          "Overpromising or implying guarantees; sustainability claims without supporting data",
          "Marketing clichés and abstract corporate jargon; slang or overly casual expressions",
          "US spelling or tone; emotional language in place of evidence",
          "Debate-style engagement on social media; full capitals for emphasis",
        ],
      },
      {
        heading: "Preferred vocabulary",
        facts: [
          { label: "aquafeed", value: "Use instead of “feed” (feed is permitted to avoid repetition)" },
          { label: "production facility / production site", value: "Use instead of “feed mill” or “factory”" },
          { label: "design / formulate feed", value: "Use instead of “make feed”" },
          { label: "reliance on…", value: "Use instead of “dependence on…”" },
          { label: "targeted nutrition", value: "Use instead of “precision nutrition”" },
          { label: "Also preferred", value: "alternative ingredients / alternative raw materials · blue foods · feed solutions · novel ingredients / novel raw materials · raw materials · resilient (industry or species level) · strong (leave where possible for LARVIVA materials)" },
        ],
      },
      {
        heading: "“Responsible” and “low-impact”",
        body: [
          "We prefer responsible to sustainable, and low-impact to sustainability, where the sentence allows. This is not a stylistic preference: environmental claims are increasingly regulated, and terms such as sustainable and green carry legal exposure when used without substantiation. Responsible and low-impact describe an approach; sustainable asserts an outcome.",
        ],
        note: "Replacing the word does not license a vaguer claim. If there is no figure, no methodology and no verification behind the sentence, neither word makes it publishable.",
      },
      {
        heading: "Key themes and channels",
        facts: [
          { label: "Innovation", value: "Explain purpose, relevance and outcomes without dramatisation." },
          { label: "Environmental performance", value: "Metrics, methodologies and recognised terminology; no vague or undefined claims." },
          { label: "Partnerships and people", value: "Warm yet professional; highlight collaboration, shared progress and expertise." },
          { label: "Corporate website", value: "Structured, explanatory and accessible; titles in title case." },
          { label: "External press releases", value: "Concise, factual and direct; key message in the opening paragraph, natural-sounding quotes." },
          { label: "LinkedIn and social media", value: "Professional tone, short paragraphs, accurate information; emojis sparingly (see the Social Media Guidelines)." },
          { label: "Sustainability and R&D", value: "Precise and evidence-driven; research translated into accessible, factual language." },
        ],
      },
      {
        heading: "Non-translatable elements",
        bullets: [
          "Taglines stay in English: Better Feed. Better Fish. Better Food. · Start Strong. Stay Strong. · Powered by Partnership. Driven by Innovation. · You Care. We Care. · Optimise your Performance",
          "Strategy names (Above & Beyond) and concept and product names (Blue Impact, SmartCare, Control Gill, BioFarm…)",
          "The full company name BioMar Group stays in English; “the Group” may be used to avoid repetition and can be translated (el grupo)",
        ],
      },
      {
        heading: "BioMar Global Spanish",
        body: [
          "Spanish is the second global language. For global communications, internal and external, we use BioMar Global Spanish: one version that works across all Spanish-speaking markets. Local marketing teams are free to use their own regional terminology whenever possible.",
        ],
        bullets: [
          "One Spanish for all markets: no regionalisms, slang or country-specific expressions unless truly necessary",
          "Terminology: follow a market's own term when it relates uniquely to its species or production (camarón, because Ecuador is the only Spanish-speaking market farming shrimp); prefer the widely understood one otherwise (alimento / alimento acuícola for feed)",
          "Informal tú for individuals and ustedes for groups; neutral sentence structure",
          "No title case in Spanish — sentence case for titles and headlines; the ban on full capitals applies equally",
        ],
        note: "The BioMar voice: a knowledgeable, trustworthy and close partner in global aquaculture. Owner: Global Marketing. Approver: Executive Committee.",
      },
    ],
  },
  {
    id: "product-guidelines-01",
    chapterId: "more-guidelines",
    title: "Product Brand Guidelines — Swoosh, naming & LARVIVA",
    summary:
      "The BioMar Swoosh that unites every product logo, how product and sub-brand names are capitalised, and the LARVIVA hatchery range.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/product-guidelines-2025--01-swoosh-larviva.pdf`,
      type: "pdf",
      range: "Pages 1–36 · Product Brand Guidelines v1, 2025",
    },
    sections: [
      {
        heading: "The BioMar Swoosh — one family of product logos",
        body: [
          "Product logos have been redesigned to form one visual family, reflecting BioMar's position as a global brand where consistency and recognition are key. At the core is the swoosh: the recurring element across all product logos and the link that ties them back to BioMar.",
          "The swoosh symbolises movement, continuity and the shared purpose of our feeds, and unites the full product range under a single identity — every product logo is instantly recognisable as BioMar.",
        ],
      },
      {
        heading: "Capitalisation of product names",
        facts: [
          { label: "On logos", value: "Concept name and sub-brand are always in uppercase." },
          { label: "In body text — standard", value: "Concept name in uppercase; sub-brand with first letter uppercase and the rest lowercase. E.g. “EFICO Alpha”." },
          { label: "Internal capitalisation", value: "Keep the sub-brand's defined form. E.g. “LARVIVA ProStart”." },
          { label: "Two or more words", value: "Each word starts uppercase unless otherwise specified. E.g. “EXIA Maxio Boost”." },
          { label: "Additional letters", value: "The word follows the standard form and the extra letters stay uppercase. E.g. “Plus MT”." },
          { label: "SmartCare", value: "Always written SmartCare, in logos and body text. Sub-brands in body text: one word → first letter uppercase (Calm); several words → each starts uppercase (Assist Skin); standalone letters stay uppercase (Control Gill Q)." },
        ],
        note: "The Brand Voice Guidelines refer to this document for how product names are set — don't extend capitals to product names that aren't set that way.",
      },
      {
        heading: "LARVIVA — hatchery feeds",
        body: [
          "LARVIVA offers a complete range of hatchery feeds for fish and shrimp, developed to maximise the success of hatchery operations: give larvae a strong start and ensure robust, high-quality fry and post-larvae, well prepared for grow-out.",
        ],
        facts: [
          { label: "Tagline", value: "Start Strong. Stay Strong. — shown by itself or under the LARVIVA logo, always in a single colour, in its fixed position." },
          { label: "Logo colour", value: "Always a single colour: BioMar Blue or White." },
          { label: "Never", value: "Alter the dimensions, change the colour, flip or move the icon, change the spacing, or type the logo. The logo should never be re-created." },
        ],
      },
      {
        heading: "LARVIVA sub-branding",
        bullets: [
          "First line: the main LARVIVA logo. Second line: the sub-brand name, left-aligned beneath it. Names should not exceed 8–10 characters per line; a third line is allowed for longer names — maximum three lines",
          "Fixed spacing: one-tenth of the BioMar logo height between the LARVIVA logo and the sub-brand name, and one-fifth between the sub-brand and the BioMar logo",
          "Sub-brand colours come from the approved BioMar palette; a new colour must be pre-approved by Global Marketing",
          "Typography: the main LARVIVA logo is custom made in Avenir Next Regular; sub-brand names use Avenir Next Medium",
        ],
        note: "The rest of the section (pages 15–36) shows the sub-brand overview for fish and for shrimp and each sub-product's logo.",
      },
    ],
  },
  {
    id: "product-guidelines-02",
    chapterId: "more-guidelines",
    title: "Product Brand Guidelines — INICIO, INTRO & EXIA",
    summary:
      "The starter-feed range INICIO (fish and shrimp), the INTRO transfer-period strategy and EXIA for shrimp.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/product-guidelines-2025--02-inicio-intro-exia.pdf`,
      type: "pdf",
      range: "Pages 37–92 · Product Brand Guidelines v1, 2025",
    },
    sections: [
      {
        heading: "INICIO — starter feed",
        body: [
          "INICIO is BioMar's range of high-quality extruded starter feeds, designed to give fry the very best start in life. The guidelines cover INICIO for fish (pages 37–50) and for shrimp (pages 51–64).",
        ],
        facts: [
          { label: "Logo colour", value: "Always a single colour. Approved colours: Celeste, BioMar Blue and White." },
        ],
        note: "The concept description pages are still marked “Coming soon” in this version.",
      },
      {
        heading: "INTRO — the transfer period",
        body: [
          "INTRO is a holistic nutritional strategy that prepares and supports fish through the challenging transfer period, delivering robustness and high performance.",
        ],
      },
      {
        heading: "EXIA — shrimp",
        body: [
          "EXIA delivers high-performance feeds and smart nutrition solutions that help shrimp farmers achieve optimal results, adapted to their farming conditions and production goals.",
        ],
      },
      {
        heading: "How each section is organised",
        bullets: [
          "The concept and its logo, with the approved colours and the single-colour rules",
          "Incorrect uses of the logo",
          "The sub-brand structure and an overview of each sub-product's logo",
        ],
      },
    ],
  },
  {
    id: "product-guidelines-03",
    chapterId: "more-guidelines",
    title: "Product Brand Guidelines — EFICO, MAXIO & POWER",
    summary:
      "The performance ranges EFICO, MAXIO and POWER, which share the tagline “Optimise your Performance”.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/product-guidelines-2025--03-efico-maxio-power.pdf`,
      type: "pdf",
      range: "Pages 93–140 · Product Brand Guidelines v1, 2025",
    },
    sections: [
      {
        heading: "One tagline for three ranges",
        body: [
          "EFICO, MAXIO and POWER each use the tagline Optimise your Performance, which stays in English in every market.",
        ],
        facts: [
          { label: "EFICO", value: "Logo always in a single colour. Pages 93–116." },
          { label: "MAXIO", value: "Logo in a single colour — Ocean Blue — and, secondarily, BioMar Blue or White. Pages 117–124." },
          { label: "POWER", value: "Logo always in a single colour. Pages 125–140." },
        ],
        note: "The concept description pages are still marked “Coming soon” in this version. EFICO bags have their own packaging exceptions — see Complementary Guidelines → Packaging.",
      },
      {
        heading: "In body text",
        body: [
          "Concept names are written in uppercase and sub-brands follow their defined form — for example “EFICO Alpha”. See the naming rules in the first Product Brand Guidelines module.",
        ],
      },
    ],
  },
  {
    id: "product-guidelines-04",
    chapterId: "more-guidelines",
    title: "Product Brand Guidelines — SmartCare",
    summary:
      "SmartCare, BioMar's preventative healthcare programme, its logo system and sub-brands.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/product-guidelines-2025--04-smartcare.pdf`,
      type: "pdf",
      range: "Pages 141–196 · Product Brand Guidelines v1, 2025",
    },
    sections: [
      {
        heading: "What SmartCare is",
        body: [
          "SmartCare is a preventative healthcare programme that helps tackle the daily challenges faced in aquaculture operations. By adjusting nutritional and functional ingredients, you can reduce the risk of health challenges while supporting growth.",
        ],
      },
      {
        heading: "Writing SmartCare names",
        bullets: [
          "The concept is always SmartCare — capital S and C — in logos and body text",
          "Sub-brands are uppercase on logos; in body text a single word has only its first letter uppercase (Calm), several words each start uppercase (Assist Skin), and standalone letters stay uppercase (Control Gill Q)",
        ],
      },
      {
        heading: "Using this section",
        body: [
          "This is the longest section of the product guidelines (56 pages): it sets the SmartCare logo and then each sub-brand's logo, colours and layout. Use it as a reference when you work on a SmartCare piece.",
        ],
      },
    ],
  },
  {
    id: "product-guidelines-05",
    chapterId: "more-guidelines",
    title: "Product Brand Guidelines — Blue Impact, Orbit, Symbio, DAN-EX & Tri-X",
    summary:
      "The Blue Impact range and its dual-colour logo system, plus the Orbit, Symbio, DAN-EX and Tri-X ranges.",
    estMinutes: 30,
    material: {
      file: `${SLICE}/product-guidelines-2025--05-blue-impact-orbit-symbio-danex-trix.pdf`,
      type: "pdf",
      range: "Pages 197–240 · Product Brand Guidelines v1, 2025",
    },
    extraMaterial: [
      {
        file: `${SLICE}/product-guidelines-2025--blue-impact-standalone.pdf`,
        type: "pdf",
        range: "Blue Impact guidelines — standalone version (17 pages)",
      },
    ],
    sections: [
      {
        heading: "Blue Impact",
        body: [
          "The Blue Impact feed range acts as a catalyst for driving change: applied, science-based sustainability is used to select ingredients with a lower impact on our planet. New nutrient-dense ingredients that don't compete with food for human consumption come to market first in Blue Impact diets.",
        ],
        facts: [
          { label: "Tagline", value: "Progressively transforming aquaculture" },
          { label: "Logo colours", value: "Dual colour: BioMar Blue, Blue IMPACT Green (#baf190 · Pantone 365 C) and White. The top of the icon is always Blue IMPACT Green; the bottom of the icon and the wordmark are always BioMar Blue or White." },
          { label: "Single colour", value: "Only where there are barriers, such as limited-colour print — otherwise always dual colour." },
          { label: "Never", value: "Use a solid colour, reverse the assigned colours, alter dimensions, change colours, flip or change the spacing of the icon, or type the logo." },
          { label: "Sub-brands", value: "Blue IMPACT AQUA and Blue IMPACT QUINNAT, each with its own approved dual-colour combinations. The sub-brand name sits on the third line, in BioMar Blue." },
        ],
        note: "For the standard bag design, refer to the BioMar Brand Guidelines (Layout Design → Packaging).",
      },
      {
        heading: "Orbit",
        body: [
          "Orbit is designed for land-based production systems, with a focus on high fish and system performance — the choice for intensive farming environments, to enhance faecal stability and water quality and minimise waste.",
        ],
      },
      {
        heading: "Symbio",
        body: [
          "Cleaner fish are highly valued partners of fish farmers, gently and continually de-lousing salmon. The Symbio range prioritises the nutritional balance and wellbeing of this fish.",
        ],
        note: "The Symbio logo should be shown in two colours whenever possible, using the accepted combinations; single colour only where there are barriers such as one-colour print.",
      },
      {
        heading: "DAN-EX",
        body: [
          "With the widest range of sizes for all eel stages, DAN-EX aims for the lowest feed quotient, the highest growth rate and the maximum production per m³, to minimise the total cost per kg of eel produced.",
        ],
      },
      {
        heading: "Tri-X",
        body: [
          "Tri-X is formulated for the rapid growth and unique needs of triploid salmon, from freshwater to harvest. It delivers the precise nutrition — particularly vital minerals — needed for strong skeletal development, helping to minimise the deformities and cataracts often associated with triploid farming.",
        ],
      },
    ],
  },
  {
    id: "photoshoot-guidelines",
    chapterId: "more-guidelines",
    title: "Photoshoot Guidelines",
    summary:
      "Briefing a photographer: photo use, people, colour palette, wardrobe and props, annotated examples and animal welfare.",
    estMinutes: 25,
    material: {
      file: `${SLICE}/photoshoot-guidelines-2024.pdf`,
      type: "pdf",
      range: "22 slides · 2024",
    },
    sections: [
      {
        heading: "Photo use",
        body: [
          "Photos are used on the website, social media, campaigns, press releases, handouts, banners and brochures, so a variety of landscape and portrait images — and video footage where possible — is needed.",
        ],
        bullets: [
          "Leave visual space around the key focus so photos can be cropped; a mix of landscape and portrait is required",
          "Include the outside scenery so the location is recognisable (Norway, Chile, UK…); a slightly blurred background is preferred",
          "Warn locations beforehand so they can clean up",
        ],
      },
      {
        heading: "People",
        bullets: [
          "Where it makes sense, two people collaborating; avoid photos with too many people. People in the background are fine if they don't distract",
          "Natural, not overly posed — everyday workers doing regular tasks, with a diversity mix and a mix of identifiable and non-identifiable people, facing and not facing the camera",
          "BioMar logo only on BioMar people or props; customers should not wear BioMar clothing, and their own company logo is welcome on their own people",
          "Where possible, use the SmartCare brand colours subtly in the environment, water or clothing",
          "Everyone on site signs a GDPR consent before the shoot",
        ],
      },
      {
        heading: "Colour palette",
        body: [
          "Follow the mood boards: soft blue tones and imagery that shows caring and nurturing, in the background, clothing, water and props.",
        ],
        note: "Avoid red, orange and yellow — except for life jackets.",
      },
      {
        heading: "Wardrobe",
        bullets: [
          "Simple, conservative, classic clothing that matches the location; solid tones — blue, black, grey, white and natural notes, with shades of blue preferred",
          "Avoid red, yellow, pink and orange (orange or yellow is permitted in a life jacket), prints, stripes, busy patterns, neon colours and visible branding — except BioMar-branded items or the customer's brand. Wearing BioMar clothing is recommended, with the logo visible (for example on the sleeve over a life jacket)",
          "Grooming: minimal, simple jewellery; no shimmering make-up; neutral nails (no red, yellow, pink or orange); hair not over-styled",
        ],
      },
      {
        heading: "Props",
        body: [
          "Bring your own clean, branded props, so the quality of the shots is consistent.",
        ],
        bullets: [
          "Buckets: branded feed buckets, or large neutral buckets for water — white or black",
          "Jackets: BioMar branded, logo on the right sleeve and left chest. T-shirts branded per the BioMar Brand Guidelines. Caps: BioMar branded",
          "Beakers; feed scoops — BioMar branded, or white, black or blue, never red or yellow",
        ],
      },
      {
        heading: "Learning from the annotated examples",
        bullets: [
          "Depth: several layers at different focus levels (location, people, hands and fish) show the eye where to look",
          "Natural poses and expressions — less direct eye contact, more focus on the task; a slight angle works better than straight on",
          "Subtle, tactful BioMar logo; framing that gives context; clear backgrounds with some blur",
          "Underwater: watch the water quality (too many particles looks dirty — choose the time of year), use artificial lights if needed, aim for sharp, clear images since they are often zoomed in and cropped; including the feed shows the product in action",
          "Replace damaged or dirty props, and clear distracting colours from the background — a strong red steals attention",
        ],
      },
      {
        heading: "Animal welfare",
        body: [
          "Be mindful and respectful in how fish and shrimp are handled. Photos that show them cared for are preferred over showing them cut up, damaged or broken: careful, delicate, gentle handling. Avoid hunting or trophy-style poses.",
        ],
        note: "It's hard for fish and shrimp to look alive and well in photos — water movement, such as ripples or droplets, helps.",
      },
    ],
  },
  {
    id: "portrait-guidelines",
    chapterId: "more-guidelines",
    title: "Global Portrait Photo Guidelines",
    summary:
      "How portraits of BioMar people should look: use, framing, wardrobe and props, and dos and don'ts.",
    estMinutes: 15,
    material: {
      file: `${SLICE}/portrait-photo-guidelines-2024.pdf`,
      type: "pdf",
      range: "11 slides · v1, 2024",
    },
    sections: [
      {
        heading: "Photo use",
        body: [
          "Portraits are used on the website, social media and press releases, so a variety of natural, friendly poses is needed — with the person comfortable and well represented — and a balance of casual and professional photos.",
        ],
        bullets: [
          "Backgrounds can reflect the person's position, but must be blurred and cool-toned; many portraits go on the website, so they must be consistent",
          "Profile pictures are often shown in circles and at small scale: leave enough space around the person and keep the background light",
        ],
      },
      {
        heading: "Framing",
        bullets: [
          "Wide shots from the waist up, ideally in landscape format with visual space, so they can be cropped to other formats",
          "A blurred, dynamic background adds depth; props where appropriate; a consistent colour palette unifies a group photo",
          "Wear BioMar colours and branded items to keep the look and feel alive",
        ],
      },
      {
        heading: "Wardrobe and props",
        bullets: [
          "“Smart office” in the right colour tones — simple, conservative and classic, matching the person's position; if casual, a BioMar branded collared polo",
          "Blue, black, grey, white and natural tones, shades of blue preferred; avoid red, yellow, pink and orange",
          "Avoid prints, stripes and busy patterns, shimmering make-up and neon colours; natural make-up and minimal jewellery. A BioMar pin on a classic suit is a nice branded touch",
        ],
      },
      {
        heading: "Do's and don'ts",
        facts: [
          { label: "Do", value: "Shoot from the waist up with space for cropping and a blurred background · pose facing slightly right against a light, cool-toned background · take multiple poses with different, natural expressions · wear BioMar colours with natural make-up" },
          { label: "Don't", value: "Use black and white, poor resolution or tight crops · face the camera straight on against a warm-toned flat background · wear warm colours — above all red" },
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
  },
  {
    id: "folder-structure",
    chapterId: null,
    title: "Folder Structure — The Shared Drive, Mapped",
    summary:
      "How the Design Hub's shared drive is organised: the logic in one page, the full tree, and a wizard for where a new file belongs.",
    estMinutes: 15,
    sections: [
      {
        note: "This is a live map of the real structure — not a simplified example. Start with How it works, then use the tree to look around, the wizard when you're not sure where something goes, and the search when you already know what you're looking for.",
      },
    ],
  },
  // ═══════════════════════════════════════════════════════════════════════════
  // EXTRA INFO — additional material, always last.
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: "extra-info",
    chapterId: null,
    title: "Extra info",
    summary:
      "Additional material worth knowing: the recent logo rebranding.",
    estMinutes: 5,
    material: {
      file: `${SLICE}/extra-info--recent-logo-rebranding.pptx`,
      type: "pptx",
      range: "Recent logo rebranding (1 slide)",
    },
    sections: [
      {
        heading: "Recent logo rebranding",
        facts: [
          { label: "Before", value: "All brands treated independently, no alignment — seemed to be from different parents." },
          { label: "Now", value: "All brands follow the same framework and carry the swoosh — seem to be from the same parent." },
        ],
      },
    ],
  },
];

export const modulesById = Object.fromEntries(modules.map((m) => [m.id, m]));
