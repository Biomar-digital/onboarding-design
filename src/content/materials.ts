// ─────────────────────────────────────────────────────────────────────────────
// Videos (Vimeo).
//
// Slide/page material now lives directly on each Module (see modules.ts,
// `material` field) since it's a 1:1 cut of that module's own document range.
// Videos are separate — a module can carry zero or more.
// ─────────────────────────────────────────────────────────────────────────────

export interface ModuleVideo {
  /** Vimeo video id, or an id/hash pair for unlisted videos ("123456789/abcdef1234"). */
  vimeo: string;
  /** Caption shown under the player. */
  title?: string;
}

export const moduleVideos: Record<string, ModuleVideo[]> = {
  welcome: [
    { vimeo: "1213275191/e9194f1235", title: "Welcome to BioMar — Carlos Díaz, CEO" },
  ],
};
