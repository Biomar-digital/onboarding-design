import type { FolderNode } from "./types";
import { folderTree } from "./folderStructure";

// Shared helpers for the folder-structure visualisations (guide, tree, wizard).
// Everything is derived from folderTree, so the views never drift from the data.

export type BranchKind = "digital" | "assets" | "product" | "market" | "other";

// Literal class names so Tailwind can see them.
export const KIND_STYLE: Record<
  BranchKind,
  { dot: string; soft: string; text: string; ring: string; bar: string }
> = {
  digital: { dot: "bg-biomar-swoosh", soft: "bg-biomar-swoosh/10", text: "text-biomar-swoosh", ring: "ring-biomar-swoosh/40", bar: "border-biomar-swoosh" },
  assets: { dot: "bg-biomar-green", soft: "bg-biomar-green/10", text: "text-biomar-green", ring: "ring-biomar-green/40", bar: "border-biomar-green" },
  product: { dot: "bg-biomar-navy", soft: "bg-biomar-navy/10", text: "text-biomar-navy", ring: "ring-biomar-navy/40", bar: "border-biomar-navy" },
  market: { dot: "bg-biomar-orange", soft: "bg-biomar-orange/10", text: "text-biomar-orange", ring: "ring-biomar-orange/40", bar: "border-biomar-orange" },
  other: { dot: "bg-slate-400", soft: "bg-slate-100", text: "text-slate-500", ring: "ring-slate-300", bar: "border-slate-300" },
};

/** What kind of branch a top-level folder is. */
export function branchKind(name: string): BranchKind {
  if (/^00\.\s*Digital Hub/i.test(name)) return "digital";
  if (/^0\.\s*Design Assets/i.test(name)) return "assets";
  if (/^[1-9]\.\s/.test(name)) return "product";
  if (["ASIA", "EMEA", "LATAM", "SALMON", "GLOBAL", "CORPORATE"].includes(name)) return "market";
  return "other";
}

// ── flat index ──────────────────────────────────────────────────────────────
export interface FlatEntry {
  node: FolderNode;
  /** Names from the root to this node, inclusive. */
  names: string[];
  /** Child indexes from the root to this node, inclusive (unique even for same-named siblings). */
  idxPath: number[];
}

function flatten(nodes: FolderNode[], names: string[] = [], idx: number[] = []): FlatEntry[] {
  const out: FlatEntry[] = [];
  nodes.forEach((n, i) => {
    const nn = [...names, n.name];
    const ii = [...idx, i];
    out.push({ node: n, names: nn, idxPath: ii });
    if (n.children?.length) out.push(...flatten(n.children, nn, ii));
  });
  return out;
}

export const flatTree: FlatEntry[] = flatten(folderTree);

export const keyOf = (idxPath: number[]) => idxPath.join(".");

export function nodeAtPath(idxPath: number[]): FolderNode {
  let level = folderTree;
  let node: FolderNode = folderTree[0];
  for (const i of idxPath) {
    node = level[i];
    level = node.children ?? [];
  }
  return node;
}

/** Resolve a path of folder names (starting at the root) to child indexes. */
export function resolveNames(names: string[]): number[] | null {
  let level = folderTree;
  const idx: number[] = [];
  for (const name of names) {
    const i = level.findIndex((n) => n.name === name);
    if (i < 0) return null;
    idx.push(i);
    level = level[i].children ?? [];
  }
  return idx;
}

export function countDescendants(n: FolderNode): number {
  return (n.children ?? []).reduce((sum, c) => sum + 1 + countDescendants(c), 0);
}

// ── top-level branches that follow the "where" pattern ──────────────────────
export interface BranchRow {
  idxPath: number[];
  name: string;
  kind: BranchKind;
}

export const branchRows: BranchRow[] = (folderTree[0].children ?? [])
  .map((n, i) => ({ idxPath: [0, i], name: n.name, kind: branchKind(n.name) }))
  .filter((r) => r.kind === "product" || r.kind === "market" || r.kind === "digital");

// ── real example paths used to teach the logic ──────────────────────────────
export interface ExamplePath {
  title: string;
  kind: BranchKind;
  /** Folder names from the root, and what each segment means. */
  segments: { name: string; role: string }[];
}

export const examplePaths: ExamplePath[] = [
  {
    title: "A LARVIVA fish advert",
    kind: "product",
    segments: [
      { name: "Design Hub 2.0", role: "The drive" },
      { name: "2. LARVIVA", role: "Product" },
      { name: "0. FISH", role: "Sub-product" },
      { name: "Adverts", role: "Category" },
    ],
  },
  {
    title: "A brochure for China",
    kind: "market",
    segments: [
      { name: "Design Hub 2.0", role: "The drive" },
      { name: "ASIA", role: "Market region" },
      { name: "China", role: "Country" },
      { name: "□ Brochures", role: "Category" },
    ],
  },
  {
    title: "Website images",
    kind: "digital",
    segments: [
      { name: "Design Hub 2.0", role: "The drive" },
      { name: "00. Digital Hub (SoMe)", role: "Digital Hub" },
      { name: "Digital Project", role: "Project type" },
      { name: "¤ Website Assets", role: "Category" },
    ],
  },
  {
    title: "A BioMar logo file",
    kind: "assets",
    segments: [
      { name: "Design Hub 2.0", role: "The drive" },
      { name: "0. Design Assets", role: "Shared assets" },
      { name: "¤ BioMar Logos", role: "Asset library" },
    ],
  },
];
