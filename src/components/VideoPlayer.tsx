import { moduleVideos } from "../content/materials";

// Builds the Vimeo player embed URL. Supports a bare id ("123456789") and the
// unlisted "id/hash" form ("123456789/abcdef1234"), which becomes
// player.vimeo.com/video/123456789?h=abcdef1234.
function vimeoEmbed(ref: string): string {
  const [id, hash] = ref.split("/");
  const params = new URLSearchParams({ dnt: "1", title: "0", byline: "0" });
  if (hash) params.set("h", hash);
  return `https://player.vimeo.com/video/${id}?${params.toString()}`;
}

// Plays a module's videos via the Vimeo player. Keep the videos unlisted (and,
// on a Vimeo Pro/Plus plan, domain-restricted to the site) so they stay private.
export function VideoPlayer({ moduleId }: { moduleId: string }) {
  const videos = moduleVideos[moduleId] ?? [];
  if (videos.length === 0) return null;

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-slate-100 px-4 py-3">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          🎬 Video
        </h2>
      </div>
      <div className="space-y-4 p-4">
        {videos.map((v) => (
          <figure key={v.vimeo}>
            <div
              className="relative w-full overflow-hidden rounded-xl bg-black"
              style={{ aspectRatio: "16 / 9" }}
            >
              <iframe
                src={vimeoEmbed(v.vimeo)}
                title={v.title ?? "Video"}
                className="absolute inset-0 h-full w-full"
                frameBorder={0}
                allow="autoplay; fullscreen; picture-in-picture"
                allowFullScreen
              />
            </div>
            {v.title && (
              <figcaption className="mt-2 text-sm text-slate-500">
                {v.title}
              </figcaption>
            )}
          </figure>
        ))}
      </div>
    </section>
  );
}
