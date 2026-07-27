import { moduleVideos } from "../content/materials";

// Plays a module's confidential videos, streamed same-origin from the private
// R2 bucket through the Worker (/media/video/<key>). Nothing is public: access
// is gated by Cloudflare Access on the site.
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
          <figure key={v.key}>
            <div className="overflow-hidden rounded-xl bg-black">
              <video
                controls
                preload="metadata"
                poster={v.poster}
                className="h-auto w-full"
                src={`/media/video/${encodeURIComponent(v.key)}`}
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
