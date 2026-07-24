// Official BioMar logo (served from /public) + product lockup.
const logoUrl = "/biomar-logo.png";

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <img
        src={logoUrl}
        alt="BioMar"
        className="h-10 w-10 rounded-lg object-contain"
      />
      <div className="leading-tight">
        <div
          className={`text-sm font-bold tracking-tight ${
            light ? "text-white" : "text-biomar-navy"
          }`}
        >
          Design Hub
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
