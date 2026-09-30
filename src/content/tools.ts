// Structured tool inventory for the visual Tools Map (see components/ToolsMap).
// No credentials — access is requested via Loop Link and the tool owner.

// "Platforms & Accesses" Loop page (BioMar SharePoint): where to request access
// and find each tool's owner. Sign-in with your BioMar account is required.
export const PLATFORMS_ACCESSES_URL =
  "https://biomar.sharepoint.com/:fl:/r/contentstorage/CSP_efbc6581-c67a-4cf1-8d4b-d3e20c8ca86d/Dokumentbibliotek/LoopAppData/Platforms%20%26%20Accesses.loop?d=w7e1166452ade4b6380045136758cbc50&csf=1&web=1&e=NZ6uKB&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF9lZmJjNjU4MS1jNjdhLTRjZjEtOGQ0Yi1kM2UyMGM4Y2E4NmQmZD1iJTIxZ1dXODczckc4VXlOUzlQaURJeW9iUVNyZVZhNEZZRkp1Y3JFSlJaam9OOThMRUltcTlqYVRvaDFKanF3ZVpFMiZmPTAxSjZPRFVNMkZNWUlYNVhSS01ORllBQkNSR1oyWVpQQ1EmYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lcg%3D%3D";

export interface Tool {
  name: string;
  purpose: string;
  icon: string;
  /** Optional link, opened in a new tab. */
  url?: string;
}

export interface ToolGroup {
  title: string;
  /** Tailwind text/bg accent keyed off the BioMar palette. */
  accent: string; // e.g. "biomar-swoosh"
  icon: string;
  tools: Tool[];
}

export const toolGroups: ToolGroup[] = [
  {
    title: "Internal systems",
    accent: "biomar-navy",
    icon: "🔑",
    tools: [
      { name: "Loop Link", purpose: "Start here: request access & find owners", icon: "🔗", url: PLATFORMS_ACCESSES_URL },
      { name: "The Pond (Kontainer)", purpose: "Brand asset DAM: guidelines, logos, photos", icon: "🌊" },
      { name: "Umbraco Content Library", purpose: "Website content management", icon: "🧱" },
      { name: "Internal Design Library", purpose: "Internal templates (Global Marketing only)", icon: "🗃️" },
      { name: "QR Code Generator", purpose: "Generate QR codes for campaigns", icon: "🔳" },
    ],
  },
  {
    title: "Design & creative",
    accent: "biomar-swoosh",
    icon: "🎨",
    tools: [
      { name: "Figma", purpose: "UI/UX, prototyping & design systems", icon: "🖌️" },
      { name: "Canva", purpose: "Quick, templated & self-serve design", icon: "✨" },
      { name: "Miro", purpose: "Whiteboard: brainstorm, map, workshop", icon: "🧩" },
    ],
  },
  {
    title: "Stock & assets",
    accent: "biomar-blue",
    icon: "🖼️",
    tools: [
      { name: "Shutterstock", purpose: "Stock photos, illustrations & video", icon: "📷" },
      { name: "Adobe Stock · Flaticon", purpose: "More stock imagery & icons", icon: "🔎" },
    ],
  },
  {
    title: "AI generation",
    accent: "biomar-orange",
    icon: "🤖",
    tools: [
      { name: "ElevenLabs", purpose: "AI voice-over for videos", icon: "🎙️" },
      { name: "Higgsfield.ai", purpose: "AI video / image generation", icon: "🎞️" },
    ],
  },
  {
    title: "Copywriting",
    accent: "biomar-green",
    icon: "✍️",
    tools: [
      { name: "Grammarly", purpose: "Grammar, spelling & tone for copy", icon: "📝" },
    ],
  },
  {
    title: "Print & production",
    accent: "biomar-navy",
    icon: "🖨️",
    tools: [
      { name: "Lasertryk", purpose: "Online print supplier for printed material", icon: "📄" },
    ],
  },
  {
    title: "Business cards",
    accent: "biomar-blue",
    icon: "📇",
    tools: [
      { name: "Add to Wallet", purpose: "Digital business cards (wallet passes)", icon: "📲" },
      { name: "Cards admin panel", purpose: "Create & manage the digital cards", icon: "🗂️" },
    ],
  },
  {
    title: "Product & market data",
    accent: "biomar-sand",
    icon: "📊",
    tools: [
      { name: "The Box", purpose: "Baltics product datasheets repository", icon: "📦" },
      { name: "FeedingTool", purpose: "BioMar feeding recommendation tool", icon: "🐟" },
    ],
  },
  {
    title: "Web & compliance",
    accent: "biomar-gray",
    icon: "🛡️",
    tools: [
      { name: "Cookie Information", purpose: "Cookie consent & GDPR for the sites", icon: "🍪" },
    ],
  },
  {
    title: "Governance & platform",
    accent: "biomar-navy",
    icon: "🏛️",
    tools: [
      { name: "Global Policies Library", purpose: "Repository of BioMar global policies", icon: "📚" },
      { name: "GitHub", purpose: "Version control & hosting (this platform)", icon: "🐙" },
    ],
  },
];
