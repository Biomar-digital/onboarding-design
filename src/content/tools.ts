// Structured tool inventory for the visual Tools Map (see components/ToolsMap).
// No credentials — access is requested via Loop Link and the tool owner.

export interface Tool {
  name: string;
  purpose: string;
  icon: string;
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
