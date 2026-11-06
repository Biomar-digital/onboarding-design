// Glossary terms shown as hover/focus tooltips in module text and in search.
// Definitions only restate what the onboarding material itself says.
// `match` lists the exact strings (case-sensitive) that trigger the tooltip.

export interface GlossaryEntry {
  term: string;
  match: string[];
  definition: string;
}

export const glossary: GlossaryEntry[] = [
  {
    term: "DRAFT",
    match: ["DRAFT"],
    definition:
      "Version naming: a concept or idea has been started. It isn't ready to be shown to the counterpart.",
  },
  {
    term: "PROOF",
    match: ["PROOF", "PROOF2", "PROOF3"],
    definition:
      "Version naming: the version ready for review, sent to the counterpart. With more rounds it goes PROOF, PROOF2, PROOF3…",
  },
  {
    term: "FINAL",
    match: ["FINAL"],
    definition:
      "The file has been approved and can be used. In practice the file name ends in PRINT or DIGITAL instead of 'final'.",
  },
  {
    term: "PRINT",
    match: ["PRINT"],
    definition:
      "Print-ready final: has the production specifications such as crop marks and bleed.",
  },
  {
    term: "DIGITAL",
    match: ["DIGITAL"],
    definition:
      "Final for digital use (computer, phone), usually exported as an interactive PDF.",
  },
  {
    term: "Brief",
    match: ["Brief", "brief", "Briefs", "briefs"],
    definition:
      "The foundation of every project: objective, target audience, deliverables, timeline, text copy, format specifications and any relevant assets or references.",
  },
  {
    term: "Task",
    match: ["Task", "Tasks"],
    definition:
      "A small, short request that doesn't need many reviews or much information — e.g. ads, handouts, brochures.",
  },
  {
    term: "Project",
    match: ["Project", "Projects"],
    definition:
      "A group of tasks that together accomplish a bigger goal — e.g. logos, new product branding, global campaigns.",
  },
  {
    term: "Design Hub",
    match: ["Design Hub"],
    definition:
      "BioMar's centralised design and advertising agency, providing shared services across the BioMar world.",
  },
  {
    term: "Global Marketing",
    match: ["Global Marketing"],
    definition:
      "Manages the BioMar brand, creates the positioning for all product concepts and services, and runs the centralised Design and Digital Shared Services agency.",
  },
  {
    term: "The Pond",
    match: ["The Pond", "Kontainer"],
    definition:
      "BioMar's brand asset library (Kontainer): guidelines, logos and photos.",
  },
  {
    term: "DAM",
    match: ["DAM"],
    definition: "Digital Asset Management — the library where brand assets are stored and shared.",
  },
  {
    term: "Swoosh",
    match: ["Swoosh", "swoosh"],
    definition:
      "Derived directly from the BioMar logo, it is our primary graphic element and symbolises movement, progress and continuity.",
  },
  {
    term: "Watermark",
    match: ["Watermark", "watermark", "Watermarks", "watermarks"],
    definition:
      "A BioMar background graphic meant to bleed off the page and sit behind all other design elements and type.",
  },
  {
    term: "Wordmark",
    match: ["wordmark", "word mark"],
    definition: "The 'BioMar' lettering that is part of the logo.",
  },
  {
    term: "Element logo",
    match: ["Element logo", "logo element"],
    definition:
      "The BioMar logo made only from its elements, without the wordmark — used when a symbol is more appropriate or the law prohibits the wordmark.",
  },
  {
    term: "Brand House",
    match: ["Brand House"],
    definition:
      "BioMar's four values: Collaboration, Innovation, Sustainability and Performance.",
  },
  {
    term: "Tagline",
    match: ["tagline", "Tagline"],
    definition: "“Powered by Partnership. Driven by Innovation.”",
  },
  {
    term: "CMYK",
    match: ["CMYK"],
    definition:
      "Colour format for print (cyan, magenta, yellow, black). Don't convert between RGB and CMYK — colours become inaccurate.",
  },
  {
    term: "RGB",
    match: ["RGB"],
    definition:
      "Colour format for screens and web (red, green, blue). Don't convert between RGB and CMYK — colours become inaccurate.",
  },
  {
    term: "Pantone",
    match: ["Pantone", "PANTONE"],
    definition: "A standard colour-matching system used to reproduce brand colours in print.",
  },
  {
    term: "Bleed",
    match: ["bleed", "Bleed"],
    definition:
      "Extra printed area beyond the trim edge so colour or images reach the very edge of the page. Ask the supplier what they need.",
  },
  {
    term: "Crop marks",
    match: ["crop marks", "crop-marks", "Cropmarks"],
    definition: "Small lines in the corners of a print file that show where the page will be trimmed.",
  },
];

// One regex for all matchable strings, longest first so "Element logo" wins over "logo".
const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const allMatches = glossary.flatMap((g) => g.match.map((m) => ({ m, g })));
allMatches.sort((a, b) => b.m.length - a.m.length);
export const glossaryLookup = new Map(allMatches.map(({ m, g }) => [m, g]));
export const glossaryRegex = new RegExp(
  `(?<![\\w-])(${allMatches.map(({ m }) => escape(m)).join("|")})(?![\\w-])`,
  "g",
);
