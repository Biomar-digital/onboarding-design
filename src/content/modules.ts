import type { Module } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// The onboarding curriculum, sourced from:
//  • OnBoarding Plan 2026 – Designer – Global Marketing
//  • Design Hub Playbook
//  • Design Hub 2026 Strategic Presentation
//  • Global and Group Marketing deck
// ─────────────────────────────────────────────────────────────────────────────

export const modules: Module[] = [
  // ── FOUNDATIONS ────────────────────────────────────────────────────────────
  {
    id: "what-is-biomar",
    category: "foundations",
    title: "What is BioMar",
    summary:
      "The company you just joined: innovators dedicated to efficient and sustainable aquaculture.",
    estMinutes: 20,
    source: "Corporate Slidedeck · OnBoarding Plan 2026",
    sections: [
      {
        body: [
          "BioMar is one of the world's leading suppliers of high-performance feed for fish and shrimp, operating across more than 80 countries. We describe ourselves as innovators dedicated to an efficient and sustainable aquaculture.",
          "Understanding the company is the foundation of design work here: everything the Design Hub produces protects and expresses the BioMar brand, so you need to know what the brand stands for before you shape how it looks.",
        ],
      },
      {
        heading: "Our promise",
        note: "Powered by Partnership. Driven by Innovation. — you will see this line close almost every deck.",
      },
      {
        heading: "The BioMar brand family",
        body: [
          "BioMar is the parent brand, but the group includes historically independent brands — EWOS, Aller Aqua-adjacent markets, LARVIVA (hatchery) and others. As of the 2025 rebrand these brands now share one framework and carry the swoosh, so they read as coming from the same parent.",
        ],
        bullets: [
          "BioMar — the master brand (Change / Magician-Rebel archetype)",
          "EWOS — salmon heritage brand",
          "LARVIVA — hatchery / larval feed",
          "Product brands now aligned under one visual system with swoosh watermarks",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "How does BioMar describe itself?",
        options: [
          "A logistics company for frozen seafood",
          "Innovators dedicated to efficient and sustainable aquaculture",
          "A retail pet-food brand",
          "A fishing fleet operator",
        ],
        correct: [1],
        explanation:
          "BioMar positions itself as innovators dedicated to efficient and sustainable aquaculture — feed for fish and shrimp, not fishing or retail.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt:
          "After the 2025 rebrand, group brands like EWOS and LARVIVA now share one visual framework and carry the swoosh.",
        options: ["True", "False"],
        correct: [0],
        explanation:
          "Correct — the rebrand aligned the brands so they look like they share the same parent, unified by the swoosh.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Brand family map",
        prompt:
          "Open the corporate slidedeck and sketch a one-page map of the BioMar brand family: parent, group brands and where the swoosh appears.",
        successCriteria: [
          "BioMar identified as the master brand",
          "At least 3 group/product brands placed",
          "You can explain what 'one parent' visual alignment means",
        ],
      },
    ],
  },
  {
    id: "global-marketing",
    category: "foundations",
    title: "Global Marketing & Structure",
    summary:
      "Where the Design Hub sits: the team, the three working areas, divisions and markets.",
    estMinutes: 25,
    source: "Global and Group Marketing deck · OnBoarding Plan 2026",
    sections: [
      {
        heading: "The three working areas",
        body: [
          "Global Marketing manages the BioMar brand, creates the positioning for all product concepts and services, and runs a centralised Design and Digital Shared Services agency.",
        ],
        bullets: [
          "BioMar Marketing (brand, positioning, shared services)",
          "Product Marketing Management (manages a segment, develops the product range)",
          "Local Marketing (launches the range and runs local initiatives)",
        ],
      },
      {
        heading: "Divisions & Markets",
        body: [
          "You will support many markets. Knowing which division a request belongs to helps you tag it correctly and understand priorities.",
        ],
        facts: [
          { label: "EMEA", value: "Baltics & WestMed" },
          { label: "Asia", value: "Vietnam & China" },
          { label: "LATAM", value: "Costa Rica & Ecuador" },
          { label: "Salmon", value: "Australia, UK, Norway, Chile" },
          { label: "Hatchery", value: "LARVIVA" },
        ],
      },
      {
        heading: "The people around you",
        bullets: [
          "Isidora Silva Chiros — Graphic Designer",
          "Andres Bernadou — Multimedia Designer",
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
        options: [
          "BioMar Marketing",
          "Product Marketing Management",
          "Local Marketing",
          "Fleet Operations",
        ],
        correct: [0, 1, 2],
        explanation:
          "The three areas are BioMar Marketing, Product Marketing Management and Local Marketing. Fleet Operations is not a marketing area.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Which markets belong to the Salmon division?",
        options: [
          "Vietnam & China",
          "Baltics & WestMed",
          "Australia, UK, Norway, Chile",
          "Costa Rica & Ecuador",
        ],
        correct: [2],
        explanation:
          "Salmon covers Australia, UK, Norway and Chile. Asia = Vietnam & China; EMEA = Baltics & WestMed; LATAM = Costa Rica & Ecuador.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Who's who",
        prompt:
          "In the task manager, list the current Global Marketing team and note one thing each person is responsible for.",
        successCriteria: [
          "All current team members listed",
          "One responsibility captured per person",
        ],
      },
    ],
  },
  {
    id: "what-is-design-hub",
    category: "foundations",
    title: "What is the Design Hub",
    summary:
      "A centralized creative & brand support function — its strategic role, five pillars and ownership.",
    estMinutes: 30,
    source: "Design Hub 2026 Strategic Presentation",
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
        heading: "The five pillars",
        facts: [
          { label: "Consistency", value: "A unified visual identity globally, adapted to local needs" },
          { label: "Efficiency", value: "Centralized expertise, less duplicated work, smart prioritization" },
          { label: "Quality", value: "Professional, strategic, creative — every output earns its place" },
          { label: "Scalability", value: "Many markets, formats and campaigns; adaptations to specific needs" },
          { label: "Brand & Product Protection", value: "Correct logo, typography, imagery — applied consistently" },
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
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which are pillars of the Design Hub? (select all)",
        options: ["Consistency", "Efficiency", "Discounting", "Brand & Product Protection"],
        correct: [0, 1, 3],
        explanation:
          "The five pillars are Consistency, Efficiency, Quality, Scalability and Brand & Product Protection. 'Discounting' is not one of them.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Roughly how many tasks does the Design Hub complete annually?",
        options: ["Around 50", "Around 200", "More than 1000", "Exactly 489 forever"],
        correct: [2],
        explanation:
          "The Hub does more than 1000 tasks annually. 489 was the 2025 count (a +71% jump), but the annual capacity is 1000+.",
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

  // ── PROCESS ─────────────────────────────────────────────────────────────────
  {
    id: "process-overview",
    category: "process",
    title: "The Design Hub Process (Overview)",
    summary:
      "From brief to final version: the seven stages every task moves through.",
    estMinutes: 20,
    source: "Design Hub Playbook",
    sections: [
      {
        body: [
          "The Design Hub takes a collaborative rather than transactional approach: continuous communication with local stakeholders, support for local adaptation while maintaining brand consistency, and prioritization based on timelines and business impact.",
          "Everything starts with an email. Every request flows through the same backbone so nothing gets lost.",
        ],
      },
      {
        heading: "From Brief to Final Version",
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
        heading: "Tasks vs Projects",
        note: "Workflow depends on scope. Small, self-contained requests are Tasks; large, multi-deliverable, longer-term efforts are Projects and use the 'In Progress' status.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What does every Design Hub request start with?",
        options: ["A Teams call", "An email", "A Figma comment", "A verbal request in the hallway"],
        correct: [1],
        explanation:
          "Everything starts with an email. Teams and meetings are used for follow-ups and clarification, but the request itself begins as an email.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "The Design Hub describes its approach as transactional rather than collaborative.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — it is explicitly collaborative rather than transactional, with continuous communication with local stakeholders.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Trace a task",
        prompt:
          "Take a completed task from the task manager and map it against the seven stages. Note where it looped (PROOF2, PROOF3).",
        successCriteria: ["All seven stages identified", "Review loops counted"],
      },
    ],
  },
  {
    id: "tasks-vs-projects",
    category: "process",
    title: "Tasks vs Projects",
    summary:
      "When a request is a quick Task and when it's a multi-part Project — and how that changes the workflow.",
    estMinutes: 15,
    source: "Design Hub 2026",
    sections: [
      {
        heading: "Before you reach out: what do you need?",
        body: [
          "A simple decision guide: do you need one quick deliverable, or a bigger goal made of multiple pieces? That answer tells you whether you're asking for a Task or a Project — and it sets the right expectations for reviews, timeline and the information the Design Hub needs.",
        ],
      },
      {
        heading: "The distinction",
        facts: [
          {
            label: "Task",
            value:
              "Small, short — not many reviews or much info needed. E.g. ads, handouts, brochures.",
          },
          {
            label: "Project",
            value:
              "A group of tasks toward a bigger goal. E.g. logos, new product branding, global campaigns.",
          },
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
        explanation:
          "A small, short, self-contained deliverable is a Task. Projects are groups of tasks toward a bigger goal.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Launching a new product brand (logo, guidelines, campaign) is a…",
        options: ["Task", "Project"],
        correct: [1],
        explanation:
          "Multiple interdependent deliverables toward one bigger goal = a Project.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Task or Project?",
        prompt:
          "Take five recent requests and label each Task or Project, with a one-line reason.",
        successCriteria: [
          "All five labelled",
          "Reasoning references reviews / scope / info needed",
        ],
      },
    ],
  },
  {
    id: "deadlines-priorities",
    category: "process",
    title: "Deadlines, Priorities & Turnaround",
    summary:
      "'ASAP is not a deadline' — real dates, how priority is set by business value, and how turnaround works.",
    estMinutes: 20,
    source: "Design Hub 2026",
    sections: [
      {
        heading: "ASAP is not a deadline",
        body: ["Every request needs two real dates:"],
        facts: [
          { label: "First Draft Date", value: "When the first version (PROOF) is expected." },
          { label: "Final Due Date", value: "When the approved final is needed." },
        ],
      },
      {
        heading: "How we set priority — business value",
        body: [
          "Work is prioritized by business value and impact, not by who asks loudest.",
        ],
        bullets: [
          "Low priority → lower business value",
          "High priority → higher business value / impact",
        ],
      },
      {
        heading: "Turnaround times",
        bullets: [
          "The sooner you submit, the sooner it goes on the calendar and gets an accurate timeframe.",
          "First come, first served — although prioritisation by business value still applies.",
          "Build the rounds of review into the timeline.",
        ],
        note: "Plan around the yearly calendar (sustainability booklet, Christmas / Easter / Summer artwork) so recurring work is booked ahead.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What are the two dates every request must have?",
        options: [
          "Start date and end date",
          "First Draft Date and Final Due Date",
          "ASAP and EOD",
          "Draft and review",
        ],
        correct: [1],
        explanation:
          "First Draft Date and Final Due Date — 'ASAP' is not a deadline.",
      },
      {
        id: "q2",
        type: "boolean",
        prompt: "Priority is set by whoever asks the loudest.",
        options: ["True", "False"],
        correct: [1],
        explanation: "False — priority is set by business value and impact.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Set real dates",
        prompt:
          "Take an 'ASAP' request and turn it into a First Draft Date + Final Due Date, factoring in the rounds of review.",
        successCriteria: ["Both dates defined", "Review rounds accounted for"],
      },
    ],
  },
  {
    id: "the-brief",
    category: "process",
    title: "The Brief",
    summary:
      "The foundation of every project: reviewing it and enforcing the minimum information required.",
    estMinutes: 20,
    source: "Design Hub Playbook",
    sections: [
      {
        body: [
          "The brief is the foundation of every project. It provides the essential information needed to understand the request: objective, target audience, deliverables, timeline, copy, format specifications, and any relevant assets or references.",
          "A clear brief gets the project moving in the right direction and minimizes revisions later. Before starting anything, make sure the brief includes the minimum information required — this avoids unnecessary back-and-forth.",
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
      },
      {
        note: "If the minimum information is missing, the request goes to 'Waiting' and you ask for what's missing before starting. Don't guess.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "multi",
        prompt: "Which of these are part of the minimum information a brief must include?",
        options: [
          "Purpose (what it's for)",
          "Draft and final dates",
          "Format & specifications",
          "The designer's mood",
        ],
        correct: [0, 1, 2],
        explanation:
          "Purpose, timeline (draft + final dates) and specifications are all required, along with copy/assets. The designer's mood is not.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "A brief is missing the final delivery date and specs. What do you do?",
        options: [
          "Start anyway and guess",
          "Move it to Waiting and request the missing info",
          "Close the task",
          "Escalate to the CEO",
        ],
        correct: [1],
        explanation:
          "Move it to Waiting and ask for the missing information before starting — this prevents rework.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Brief triage",
        prompt:
          "Take three recent request emails and score each against the four minimum-info items. Draft the follow-up question for any gaps.",
        successCriteria: [
          "Each brief scored on all four items",
          "A clear follow-up drafted for every gap",
        ],
      },
    ],
  },
  {
    id: "email-tags-folders",
    category: "process",
    title: "Email Tags & Folder Structure",
    summary:
      "How the inbox stays under control: the Teams tag, status tags and market folders.",
    estMinutes: 15,
    source: "Design Hub Playbook · OnBoarding Plan 2026",
    sections: [
      {
        heading: "Teams tag — is it in the task manager?",
        bullets: [
          "'Teams' tag → the request has been registered in the task manager",
          "No tag → assume it has NOT been added yet and needs reviewing",
        ],
      },
      {
        heading: "Status tags — where is it?",
        bullets: [
          "Waiting — on hold for missing information or clarification",
          "Done — the task is completed",
        ],
      },
      {
        heading: "Folders",
        note: "Once a task is completed, its email is marked 'done' and moved to the folder of the market that requested it.",
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
        explanation:
          "No tag means assume it has not yet been added and needs to be reviewed and registered.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Inbox zero pass",
        prompt:
          "Do one pass of the shared inbox: verify each open thread has the correct Teams/status tag and is in the right market folder.",
        successCriteria: ["Every open thread tagged", "Completed threads filed by market"],
      },
    ],
  },
  {
    id: "task-manager",
    category: "process",
    title: "The Task Manager",
    summary:
      "Columns, cards, market tags and to-dos — the board where every project lives.",
    estMinutes: 30,
    source: "Design Hub Playbook",
    sections: [
      {
        heading: "Columns",
        bullets: [
          "Tasks / Projects — new requests enter here; active but not yet assigned to a designer",
          "Designer columns — once you start a task, move it to your personal column so ownership is clear",
          "Sent for Review — PROOF shared, waiting for feedback/approval",
          "In Progress — larger, longer-term work actively being worked on",
          "Waiting — temporarily on hold for missing info",
          "Completed [Year] — done, then categorized by market",
        ],
      },
      {
        heading: "Task card structure",
        body: [
          "Each card holds everything needed to manage a project start to finish.",
        ],
        bullets: [
          "Market tags — identify which market the project belongs to (filtering & workload)",
          "People — add the requester as a member; they get notified and can follow updates",
          "To-do — list multiple deliverables/formats to track them individually",
          "Notes — always include: Draft deadline, Final deadline, Email subject",
        ],
      },
      {
        note: "Adding the email subject to the Notes is especially important — it's how you jump back to the original thread.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "When you start working on a task, what should you do on the board?",
        options: [
          "Leave it in Tasks/Projects",
          "Move it to your personal designer column",
          "Move it straight to Completed",
          "Delete it",
        ],
        correct: [1],
        explanation:
          "Move it to your personal column so ownership is clear and the team can see who's responsible.",
      },
      {
        id: "q2",
        type: "multi",
        prompt: "What must the Notes section of a card always include?",
        options: ["Draft deadline", "Final deadline", "Email subject", "The client's phone number"],
        correct: [0, 1, 2],
        explanation:
          "Always include the draft deadline, final deadline and email subject. The email subject makes it easy to find the original thread.",
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
    id: "files-naming",
    category: "process",
    title: "File Storage & Naming Conventions",
    summary:
      "Where files live and how to name them so anyone can find the right version.",
    estMinutes: 25,
    source: "Design Hub Playbook",
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
        note: "File Type = Brochure, Ad, Datasheet, Video, etc.",
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
          "Files Provided — everything the requester sent (Excel, Word, images, video)",
          "Assets — things you'll use in the project (images, logos, datasheets, graphics)",
          "Previous Versions — once feedback is received, prior PROOFs move here",
        ],
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Which follows the design-file naming pattern?",
        options: [
          "brochure_final_v2.pdf",
          "2022-03 ES_Orbit_Brochure",
          "orbit thing.ai",
          "FINAL FINAL real.pdf",
        ],
        correct: [1],
        explanation:
          "The pattern is Year-Month Language_Market Brand/Product-FileType — '2022-03 ES_Orbit_Brochure' matches it.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "Where do superseded PROOF versions go once feedback arrives?",
        options: ["Trash", "Files Provided", "Previous Versions", "The requester's inbox"],
        correct: [2],
        explanation:
          "Move them into the Previous Versions folder in case they want to revert or review how things evolved.",
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
    id: "versioning-review",
    category: "process",
    title: "Versioning, Review & Feedback",
    summary:
      "DRAFT → PROOF → FINAL, how to send for review, and how feedback comes back per format.",
    estMinutes: 25,
    source: "Design Hub Playbook",
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
        heading: "Sending a file to review",
        note: "Instead of attaching the PDF, send the link to the folder.",
      },
      {
        heading: "Receiving feedback — by format",
        facts: [
          { label: "PDF", value: "Sent as a link to the folder" },
          { label: "JPG / PNG", value: "Sent as a link to the folder" },
          { label: "Video", value: "Sent as a link to SharePoint" },
        ],
        note: "For video feedback, comments must reference a timestamp written as HH:MM:SS.",
      },
      {
        heading: "Previous Version folder",
        body: [
          "After feedback, move the PROOF (and sometimes the editable file) into Previous Versions — keeping older directions in case they revert, and to show how the work evolved.",
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
        explanation:
          "PROOF is the review stage sent to the counterpart. DRAFT is internal; FINAL is post-approval.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "How must video feedback be referenced?",
        options: [
          "By frame number",
          "By a timestamp written as HH:MM:SS",
          "By color",
          "It can't be — video isn't reviewed",
        ],
        correct: [1],
        explanation:
          "Video feedback must include a timestamp in HH:MM:SS so the note maps to an exact moment.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Run a review round",
        prompt:
          "Export a PROOF, send it as a folder link (not an attachment), collect mock feedback, then archive the PROOF to Previous Versions.",
        successCriteria: [
          "Sent as folder link",
          "Feedback captured (timestamped if video)",
          "PROOF archived correctly",
        ],
      },
    ],
  },
  {
    id: "export-close",
    category: "process",
    title: "Exporting Finals & Closing Tasks",
    summary:
      "Print vs digital export requirements, and the two-step closeout in the board and inbox.",
    estMinutes: 20,
    source: "Design Hub Playbook",
    sections: [
      {
        heading: "Exporting FINAL versions",
        facts: [
          { label: "PRINT", value: "Usually needs bleed and/or crop-marks — ask the supplier what they need" },
          { label: "DIGITAL", value: "Usually Interactive PDF — ask where it'll be displayed to pick 1 or 2 pages, vertical or horizontal" },
        ],
      },
      {
        heading: "Closing a task — two places",
        bullets: [
          "Task manager — move the card to 'Completed [Year]' and categorize it by the market it was made for",
          "Email inbox — mark the thread 'done' and move it to the requesting market's folder",
        ],
      },
      {
        note: "Example: a Vietnam job moves to 'Completed 2026' → categorized under 'Vietnam', and its email moves to the Vietnam folder.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What do PRINT final files usually need?",
        options: [
          "Bleed and/or crop-marks",
          "A transparent background",
          "Embedded video",
          "Nothing special",
        ],
        correct: [0],
        explanation:
          "Print material usually needs bleed and/or crop-marks — always confirm exactly what the supplier requires.",
      },
      {
        id: "q2",
        type: "multi",
        prompt: "Closing a task happens in which two places?",
        options: ["The task manager", "The email inbox", "LinkedIn", "The printer's portal"],
        correct: [0, 1],
        explanation:
          "You close in both the task manager (move to Completed, categorize by market) and the email inbox (mark done, file by market).",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Close it out",
        prompt:
          "Take one finished practice task through full closeout: export a correct FINAL, move the card to Completed + market, and file the email.",
        successCriteria: [
          "FINAL exported to the right spec (print or digital)",
          "Card in Completed + market category",
          "Email marked done + filed",
        ],
      },
    ],
  },

  // ── BRAND ───────────────────────────────────────────────────────────────────
  {
    id: "brand-guidelines",
    category: "brand",
    title: "Brand Guidelines & Design Governance",
    summary:
      "The visual system you protect: logo, typography, color, layout, imagery, print vs digital.",
    estMinutes: 35,
    source: "Design Hub 2026 Strategic Presentation",
    sections: [
      {
        body: [
          "Guidelines are tools to support consistency while allowing flexibility for communication needs. Brand & Product Protection is one of the five pillars — correct logo, typography and imagery, applied consistently everywhere.",
        ],
      },
      {
        heading: "Key elements",
        bullets: [
          "Logo usage",
          "Typography",
          "Color palette",
          "Layout principles",
          "Imagery style",
          "Tone and consistency",
          "Digital vs print applications",
        ],
      },
      {
        heading: "The 2025 logo rebrand",
        body: [
          "Before: every brand was treated independently — no alignment, they looked like they came from different parents.",
          "Now: all brands follow the same framework, look like they share the same parent, and carry the swoosh. New swoosh watermarks were derived from the product-logo rebrand.",
        ],
      },
      {
        heading: "Where to find them",
        note: "Brand Guidelines, product communication standards and art-direction references all live on The Pond.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "boolean",
        prompt: "Guidelines exist to lock everything down with zero flexibility.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — guidelines support consistency while allowing flexibility for real communication needs.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "What visual element unifies the brand family after the rebrand?",
        options: ["A drop shadow", "The swoosh", "A gradient", "A serif wordmark"],
        correct: [1],
        explanation:
          "The swoosh (and swoosh watermarks) unifies the family so the brands read as sharing one parent.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Guideline hunt",
        prompt:
          "On The Pond, locate the Brand Guidelines and note the rules for logo clear-space, primary typography and the core color values.",
        successCriteria: [
          "Guidelines located on The Pond",
          "Logo clear-space, type and color values captured",
        ],
      },
    ],
  },
  {
    id: "material-guide",
    category: "brand",
    title: "Material Guide & Practical Do's and Don'ts",
    summary:
      "The hard-won production rules: alternative colors, opacity traps, gradients, packaging, alt-language fonts.",
    estMinutes: 25,
    source: "OnBoarding Plan 2026 · Additional Guidelines",
    sections: [
      {
        heading: "Color & production do's and don'ts",
        bullets: [
          "Use BioMar alternative colours where the palette allows",
          "Capitalized text where the style calls for it",
          "No BioMar Blue (BB) opacity — it looks purple",
          "Use black opacity instead",
          "Avoid gradients — they print poorly",
          "Packaging: the top is always BioMar Blue",
          "Objects/OBJ: choose a theme / connecting thread (hilo conductor)",
        ],
      },
      {
        heading: "Alternative fonts for other languages",
        facts: [
          { label: "CN (Chinese)", value: "Noto Sans (CN)" },
          { label: "VN (Vietnamese)", value: "Alternative font set" },
          { label: "GR (Greek)", value: "Alternative font set" },
          { label: "RU (Russian)", value: "Alternative font set" },
        ],
        note: "Coastline is another font in rotation. Confirm the exact per-language font in the guidelines before setting non-Latin copy.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Why should you avoid putting opacity on BioMar Blue?",
        options: [
          "It disappears entirely",
          "It looks purple",
          "It's against the law",
          "It turns green",
        ],
        correct: [1],
        explanation:
          "BioMar Blue with opacity looks purple. Use black opacity instead when you need a see-through effect.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "On packaging, what colour is always at the top?",
        options: ["Green", "BioMar Blue", "White", "It varies by market"],
        correct: [1],
        explanation:
          "The top of packaging is always BioMar Blue — a fixed rule for shelf consistency.",
      },
      {
        id: "q3",
        type: "boolean",
        prompt: "Gradients are encouraged because they print beautifully.",
        options: ["True", "False"],
        correct: [1],
        explanation:
          "False — gradients print poorly and should be avoided.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Spot the violations",
        prompt:
          "Review three past layouts and flag any BB-opacity, gradients, or missing packaging-top rules. Note the correct fix for each.",
        successCriteria: [
          "Each layout checked against the do's/don'ts",
          "A concrete fix noted for every violation",
        ],
      },
    ],
  },

  // ── TOOLS ───────────────────────────────────────────────────────────────────
  {
    id: "incopy-indesign",
    category: "tools",
    title: "InCopy & InDesign Workflow",
    summary:
      "How InCopy lets writers and designers work on the same layout without clashing — plus the training course.",
    estMinutes: 30,
    source: "Design Hub 2026",
    sections: [
      {
        heading: "What is Adobe InCopy?",
        body: [
          "Adobe InCopy lets people create, edit and format content and helps teams work collaboratively. It integrates with InDesign so designers and writers work in unison on the same layout without clashing — avoiding unnecessary back-and-forth between design and editing.",
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
        prompt: "What problem does the InCopy + InDesign workflow solve?",
        options: [
          "Rendering 3D",
          "Letting writers and designers work on the same layout without clashing",
          "Video editing",
          "Color management",
        ],
        correct: [1],
        explanation:
          "InCopy integrates with InDesign so writers and designers work on the same layout in unison, avoiding back-and-forth.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "How many modules is the InCopy course split into?",
        options: ["2", "3", "4", "6"],
        correct: [2],
        explanation:
          "Four: Introduction, Editing Text, Reviewing Copy, and Saving & Export.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Try the InCopy flow",
        prompt:
          "Open a sample InDesign layout with an InCopy story, make a text edit with track changes, and export.",
        successCriteria: [
          "Edited via InCopy, not directly in InDesign",
          "Track changes used",
          "Exported correctly",
        ],
      },
    ],
  },
  {
    id: "platforms",
    category: "tools",
    title: "Platforms We Use",
    summary:
      "The Pond, Loop Link, Umbraco, Canva and the asset libraries — plus who owns each.",
    estMinutes: 25,
    source: "OnBoarding Plan 2026",
    sections: [
      {
        heading: "Core platforms",
        bullets: [
          "Loop Link — for accesses and lists (start here to get access to everything)",
          "The Pond (Kontainer) — brand assets, guidelines and the DAM",
          "Umbraco Content Library — website content",
          "Internal Design Library — only available for Global Marketing",
          "QR Code Generator · Business Cards · Canva Templates",
          "Stock photography and videos libraries",
        ],
      },
      {
        heading: "Asset sources",
        bullets: ["Adobe Stock", "Shutterstock", "Flaticon"],
      },
      {
        heading: "Complementary",
        bullets: ["Canva — for templated / self-serve material"],
      },
      {
        note: "Each platform has an owner. Use Loop Link to request access and to find the current list of who owns what.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "Where do you go first to get accesses and find the platform list?",
        options: ["The Pond", "Loop Link", "Flaticon", "Umbraco"],
        correct: [1],
        explanation:
          "Loop Link is the starting point for accesses and lists. The Pond is the brand-asset DAM.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "The Internal Design Library is available to…",
        options: ["Everyone at BioMar", "Only Global Marketing", "Only external partners", "Only Chile"],
        correct: [1],
        explanation:
          "The Internal Design Library is restricted to Global Marketing.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Access checklist",
        prompt:
          "Using Loop Link, confirm you have access to The Pond, the task manager, the shared inbox and at least one stock source. Note who to ask for anything missing.",
        successCriteria: [
          "Access verified for the core platforms",
          "Owner/contact noted for any gaps",
        ],
      },
    ],
  },
  {
    id: "tools-map",
    category: "tools",
    title: "Tools Map — What We Use & What For",
    summary:
      "The full toolkit the Design Hub works with, grouped by purpose. (Access & logins live in Loop Link — never in here.)",
    estMinutes: 15,
    source: "Design Hub tool list",
    sections: [
      {
        note: "Logins and passwords are never stored here — request access through Loop Link and the tool owner. This map is only about what each tool is and when to reach for it.",
      },
      {
        heading: "Design & creative",
        facts: [
          { label: "Figma", value: "UI/UX design, prototyping, collaborative design & design systems." },
          { label: "Canva", value: "Quick, templated design and self-serve materials." },
          { label: "Miro", value: "Online whiteboard for brainstorming, mapping and workshops." },
        ],
      },
      {
        heading: "Stock & visual assets",
        facts: [
          { label: "Shutterstock", value: "Stock photos, illustrations and video." },
          { label: "Adobe Stock · Flaticon", value: "Additional stock imagery and icons (see Platforms)." },
        ],
      },
      {
        heading: "AI generation",
        facts: [
          { label: "ElevenLabs", value: "AI voice-over generation for videos." },
          { label: "Higgsfield.ai", value: "AI video / image generation for creative content." },
        ],
      },
      {
        heading: "Copywriting",
        facts: [
          { label: "Grammarly", value: "Grammar, spelling and tone checking for copy." },
        ],
      },
      {
        heading: "Print & production",
        facts: [
          { label: "Lasertryk", value: "Online print supplier for producing printed materials." },
        ],
      },
      {
        heading: "Business cards",
        facts: [
          { label: "Add to Wallet", value: "Digital business cards (Apple / Google Wallet passes)." },
          { label: "Digital business cards admin panel", value: "Back-office to create and manage the digital cards." },
        ],
      },
      {
        heading: "Product & market data",
        facts: [
          { label: "The Box", value: "Baltics product datasheets repository." },
          { label: "FeedingTool", value: "BioMar feeding recommendation / calculation tool." },
        ],
      },
      {
        heading: "Web & compliance",
        facts: [
          { label: "Cookie Information", value: "Cookie consent & GDPR compliance for the websites." },
        ],
      },
      {
        heading: "Governance & platform",
        facts: [
          { label: "Global Policies Library", value: "Repository of BioMar global policies." },
          { label: "GitHub", value: "Version control & hosting (this onboarding platform lives here)." },
        ],
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
        options: [
          "In this Tools Map",
          "In Loop Link (request access from the owner)",
          "In the task manager",
          "In Grammarly",
        ],
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
        successCriteria: [
          "Access requested for the tools your role uses",
          "Owner noted for anything pending",
        ],
      },
    ],
  },
  {
    id: "communication",
    category: "tools",
    title: "Ways of Working & Communicating",
    summary:
      "Weekly/daily/always-on rhythms, and when to use email vs Teams vs a meeting.",
    estMinutes: 15,
    source: "Design Hub Playbook · Strategic Presentation",
    sections: [
      {
        heading: "Rhythm",
        facts: [
          { label: "Weekly", value: "Meetings, project alignment, prioritization, capacity, cross-functional coordination" },
          { label: "Daily", value: "Collaboration, feedback loops, stakeholder communication, iterative review" },
          { label: "Always-on", value: "File & asset management, shared systems, version control, accessibility" },
        ],
      },
      {
        heading: "When to use what",
        facts: [
          { label: "Email", value: "Submitting a new task/project · submitting feedback" },
          { label: "Teams chat", value: "Following up on tasks/projects" },
          { label: "Verbal / meetings", value: "Clarifying or defining projects · in-depth artwork review" },
        ],
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
          "New tasks/projects and formal feedback go by email. Teams is for follow-ups; meetings are for defining/reviewing.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "An in-depth review of the artwork is best done…",
        options: ["By email only", "In a verbal meeting", "Via Flaticon", "Never"],
        correct: [1],
        explanation:
          "In-depth artwork review and clarifying/defining projects are best handled verbally in a meeting.",
      },
    ],
    exercises: [
      {
        id: "e1",
        title: "Channel choice drill",
        prompt:
          "For five scenarios (new task, quick status check, unclear brief, feedback, deep review), pick the right channel and justify it.",
        successCriteria: ["Correct channel for each", "One-line justification each"],
      },
    ],
  },

  // ── PEOPLE ──────────────────────────────────────────────────────────────────
  {
    id: "stakeholder-map",
    category: "people",
    title: "Stakeholder Map — Who's in Charge of What",
    summary:
      "The go-to people for datasheets, R&D, LARVIVA, SmartCare and technical questions.",
    estMinutes: 15,
    source: "Design Hub Playbook · OnBoarding Plan 2026",
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
        note: "Knowing who owns what saves hours — route the question to the right person instead of guessing.",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "You have a datasheet question. Who do you write to?",
        options: ["Daniela", "Kat", "Torunn", "Ewan"],
        correct: [1],
        explanation:
          "Datasheets → Kat (katmi@biomar.com). Daniela = LARVIVA, Torunn = SmartCare, technical = Iannis/Andreina/Bruno/Ewan.",
      },
      {
        id: "q2",
        type: "single",
        prompt: "A LARVIVA (hatchery) question should go to…",
        options: ["Elisabeth", "Kat", "Daniela", "Bruno"],
        correct: [2],
        explanation:
          "LARVIVA questions go to Daniela (vdv@biomar.com). Elisabeth handles R&D.",
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
  {
    id: "meet-managers",
    category: "people",
    title: "Meeting the Marketing Managers",
    summary:
      "The plan to meet each market's marketing manager — who they are and how you work together.",
    estMinutes: 20,
    source: "OnBoarding Plan 2026",
    sections: [
      {
        body: [
          "Meet the marketing managers bit by bit. The order can follow how much the Design Hub works with each market. The goal isn't only to meet them as people, but to learn what they do and how they work with the Hub.",
        ],
      },
      {
        heading: "Suggested order (by how much we work together)",
        bullets: [
          "Baltics",
          "WestMed",
          "Norway",
          "Chile",
          "Asia",
          "Hatchery",
          "UK",
          "Australia",
          "LATAM",
        ],
      },
      {
        note: "For each intro, capture: what the market focuses on, the kinds of requests they send, and any local specifics (language, formats, recurring campaigns).",
      },
    ],
    quiz: [
      {
        id: "q1",
        type: "single",
        prompt: "What principle orders the manager introductions?",
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
    ],
    exercises: [
      {
        id: "e1",
        title: "Intro notes template",
        prompt:
          "Prepare a short intro-meeting template (focus, typical requests, local specifics) and fill it in after your first manager meeting.",
        successCriteria: [
          "Reusable template created",
          "First meeting captured against it",
        ],
      },
    ],
  },
];

export const modulesById = Object.fromEntries(modules.map((m) => [m.id, m]));
