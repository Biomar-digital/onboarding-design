import { useEffect } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { modulesById } from "../content/modules";
import { chaptersById } from "../content/chapters";
import { journey } from "../content/journey";
import { orderedAssigned } from "../lib/schedule";
import { GlossaryText } from "../components/GlossaryText";
import { useStore } from "../lib/store";
import { InfoPanel } from "../components/InfoPanel";
import { ViewingBanner } from "./Employee";
import { DeckViewer } from "../components/DeckViewer";
import { VideoPlayer } from "../components/VideoPlayer";
import { ToolsMap } from "../components/ToolsMap";
import { FolderStructureExplorer } from "../components/FolderStructureExplorer";
import type { LessonSection } from "../content/types";

export function ModuleView() {
  const { moduleId, personId } = useParams();
  const { currentUser, people, markModuleComplete } = useStore();
  const navigate = useNavigate();
  const module = moduleId ? modulesById[moduleId] : undefined;
  // Admins can preview any designer's module via /admin/view/:personId/module/:moduleId (read only).
  const viewingAs =
    personId && currentUser?.role === "admin"
      ? people.find((p) => p.id === personId) ?? null
      : null;
  const subject = personId ? viewingAs : currentUser;
  const base = viewingAs ? `/admin/view/${viewingAs.id}` : "";
  const { hash } = useLocation();

  // Jump to a section when arriving with #section-N (from the index or search).
  useEffect(() => {
    if (!hash) {
      window.scrollTo({ top: 0 });
      return;
    }
    const t = setTimeout(
      () => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: "smooth", block: "start" }),
      50,
    );
    return () => clearTimeout(t);
  }, [hash, moduleId]);

  if (!module || !subject) {
    return (
      <div className="card p-8 text-center text-slate-500">
        Module not found.{" "}
        <Link to={base || "/"} className="text-biomar-swoosh">
          Back
        </Link>
      </div>
    );
  }

  const alreadyDone = subject.progress[module.id]?.completed;
  const chapter = module.chapterId ? chaptersById[module.chapterId] : null;
  const section = journey.find((j) => j.moduleIds.includes(module.id));
  const order = orderedAssigned(subject.assignedModuleIds);
  const at = order.indexOf(module.id);
  const prev = at > 0 ? modulesById[order[at - 1]] : null;
  const next = at >= 0 && at < order.length - 1 ? modulesById[order[at + 1]] : null;
  // Each glossary term is underlined only the first time it appears on the page.
  const seen = new Set<string>();
  const hasIndex =
    module.id !== "tools-map" &&
    module.id !== "folder-structure" &&
    module.sections.some((x) => x.heading);

  return (
    <div>
    {viewingAs && <ViewingBanner person={viewingAs} />}
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <article className="space-y-6">
        <div>
          <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-sm text-slate-400">
            <Link to={base || "/"} className="hover:text-biomar-swoosh">
              {viewingAs ? `${viewingAs.name}'s onboarding` : "My onboarding"}
            </Link>
            {section && section.key !== "welcome" && (
              <>
                <span aria-hidden>›</span>
                <span>
                  {section.icon} {section.title}
                </span>
              </>
            )}
            <span aria-hidden>›</span>
            <span className="text-slate-500">{module.title}</span>
          </nav>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="chip bg-biomar-ice text-biomar-blue uppercase">
              {chapter ? chapter.icon + " " + chapter.title : "Reference"}
            </span>
            <span className="text-xs text-slate-400">
              {module.estMinutes} min
              {chapter ? ` · Source: ${chapter.source}` : ""}
            </span>
          </div>
          <h1 className="mt-2 text-2xl font-bold text-biomar-navy">
            {module.title}
          </h1>
          <p className="mt-1 text-slate-500">{module.summary}</p>
        </div>

        <DeckViewer material={module.material} resources={module.resources} />
        {module.extraMaterial?.map((m) => (
          <DeckViewer key={m.file} material={m} />
        ))}
        <VideoPlayer moduleId={module.id} />

        {module.id === "tools-map" ? (
          <ToolsMap />
        ) : module.id === "folder-structure" ? (
          <FolderStructureExplorer />
        ) : (
          <section className="card space-y-5 p-6">
            {module.material && (
              <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
                Key points
              </h2>
            )}
            {module.sections.map((s, i) => (
              <Section key={i} id={`section-${i}`} section={s} seen={seen} />
            ))}
          </section>
        )}

        {viewingAs ? (
          <section className="card p-6 text-sm text-slate-500">
            {alreadyDone
              ? `${viewingAs.name} completed this module.`
              : `${viewingAs.name} hasn't completed this module yet.`}
          </section>
        ) : alreadyDone ? (
          <section className="card flex items-center justify-between p-6">
            <p className="text-sm text-biomar-green">✓ You completed this module.</p>
            <button className="btn-ghost" onClick={() => navigate("/")}>
              Back to my onboarding
            </button>
          </section>
        ) : (
          <section className="card flex items-center justify-between p-6">
            <p className="text-sm text-slate-500">
              Done with this module? Mark it complete to continue.
            </p>
            <button
              className="btn-accent"
              onClick={() => {
                markModuleComplete(subject.id, module.id);
                navigate("/");
              }}
            >
              Mark complete & continue
            </button>
          </section>
        )}

        {(prev || next) && (
          <nav aria-label="Module navigation" className="grid gap-3 sm:grid-cols-2">
            {prev ? (
              <Link
                to={`${base}/module/${prev.id}`}
                className="card block p-4 transition hover:border-biomar-swoosh hover:bg-biomar-ice/40"
              >
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">← Previous</span>
                <span className="mt-1 block text-sm font-semibold text-biomar-navy">{prev.title}</span>
              </Link>
            ) : (
              <span />
            )}
            {next && (
              <Link
                to={`${base}/module/${next.id}`}
                className="card block p-4 text-right transition hover:border-biomar-swoosh hover:bg-biomar-ice/40"
              >
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Next →</span>
                <span className="mt-1 block text-sm font-semibold text-biomar-navy">{next.title}</span>
              </Link>
            )}
          </nav>
        )}
      </article>

      <div className="space-y-4 lg:sticky lg:top-20 lg:self-start lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto">
        {hasIndex && (
          <aside className="card p-4">
            <h2 className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
              On this page
            </h2>
            <ul className="space-y-1">
              {module.sections.map((x, i) =>
                x.heading ? (
                  <li key={i}>
                    <a
                      href={`#section-${i}`}
                      onClick={(e) => {
                        e.preventDefault();
                        document
                          .getElementById(`section-${i}`)
                          ?.scrollIntoView({ behavior: "smooth", block: "start" });
                      }}
                      className="block rounded-md px-2 py-1 text-sm text-slate-600 hover:bg-biomar-ice/60 hover:text-biomar-navy"
                    >
                      {x.heading}
                    </a>
                  </li>
                ) : null,
              )}
            </ul>
          </aside>
        )}
        <InfoPanel />
      </div>
    </div>
    </div>
  );
}

function Section({
  section,
  id,
  seen,
}: {
  section: LessonSection;
  id: string;
  seen: Set<string>;
}) {
  const g = (t: string) => <GlossaryText text={t} seen={seen} />;
  return (
    <div id={id} className="scroll-mt-24">
      {section.heading && (
        <h2 className="mb-2 text-base font-bold text-biomar-navy">
          {section.heading}
        </h2>
      )}
      {section.body?.map((p, i) => (
        <p key={i} className="mb-2 text-[15px] leading-relaxed text-slate-700">
          {g(p)}
        </p>
      ))}
      {section.bullets && (
        <ul className="mb-2 space-y-1.5">
          {section.bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-2 text-[15px] text-slate-700">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-biomar-swoosh" />
              <span>{g(b)}</span>
            </li>
          ))}
        </ul>
      )}
      {section.facts && (
        <dl className="mb-2 divide-y divide-slate-100 rounded-xl border border-slate-100">
          {section.facts.map((f, i) => (
            <div key={i} className="grid grid-cols-[140px_1fr] gap-3 px-3 py-2">
              <dt className="text-sm font-semibold text-biomar-navy">
                {f.label}
              </dt>
              <dd className="text-sm text-slate-600">{g(f.value)}</dd>
            </div>
          ))}
        </dl>
      )}
      {section.note && (
        <p className="rounded-lg border-l-4 border-biomar-swoosh bg-biomar-ice/50 px-3 py-2 text-sm text-biomar-navy">
          💡 {g(section.note)}
        </p>
      )}
    </div>
  );
}
