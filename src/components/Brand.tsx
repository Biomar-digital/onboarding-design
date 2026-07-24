// Lightweight in-brand wordmark + swoosh. Not the official BioMar logo asset —
// a stand-in mark so the app reads as BioMar until the real asset is dropped in.
export function Swoosh({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 32" className={className} aria-hidden="true">
      <path
        d="M2 22c8-10 20-14 32-8-9-1-17 2-22 9 8-4 16-4 24 1-11 3-22 2-34-2z"
        fill="currentColor"
      />
    </svg>
  );
}

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`grid h-9 w-9 place-items-center rounded-lg ${
          light ? "bg-white/15" : "bg-biomar-navy"
        }`}
      >
        <Swoosh className={`h-5 w-5 ${light ? "text-white" : "text-biomar-swoosh"}`} />
      </span>
      <div className="leading-tight">
        <div
          className={`text-sm font-bold tracking-tight ${
            light ? "text-white" : "text-biomar-navy"
          }`}
        >
          BioMar<span className="text-biomar-swoosh"> Design Hub</span>
        </div>
        <div
          className={`text-[10px] font-medium uppercase tracking-widest ${
            light ? "text-white/70" : "text-slate-400"
          }`}
        >
          Designer Onboarding
        </div>
      </div>
    </div>
  );
}

export const TAGLINE = "Powered by Partnership. Driven by Innovation.";
