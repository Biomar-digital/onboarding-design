import { Link, useNavigate, useParams } from "react-router-dom";
import { modulesById } from "../content/modules";
import { chaptersById } from "../content/chapters";
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

  return (
    <div>
    {viewingAs && <ViewingBanner person={viewingAs} />}
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <article className="space-y-6">
        <div>
          <Link
            to={base || "/"}
            className="text-sm text-slate-400 hover:text-biomar-swoosh"
          >
            ← {viewingAs ? `Back to ${viewingAs.name}'s onboarding` : "Back to my onboarding"}
          </Link>
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
              <Section key={i} section={s} />
            ))}
          </section>
        )}

        {module.exercises.length > 0 && (
          <section className="card p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
              Practice
            </h2>
            <div className="mt-3 space-y-4">
              {module.exercises.map((ex) => (
                <div
                  key={ex.id}
                  className="rounded-xl border border-dashed border-biomar-swoosh/40 bg-biomar-ice/40 p-4"
                >
                  <h3 className="font-semibold text-biomar-navy">
                    🛠️ {ex.title}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">{ex.prompt}</p>
                  <ul className="mt-2 space-y-1">
                    {ex.successCriteria.map((c, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-xs text-slate-500"
                      >
                        <span className="text-biomar-green">✓</span> {c}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
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
      </article>

      <InfoPanel />
    </div>
    </div>
  );
}

function Section({ section }: { section: LessonSection }) {
  return (
    <div>
      {section.heading && (
        <h2 className="mb-2 text-base font-bold text-biomar-navy">
          {section.heading}
        </h2>
      )}
      {section.body?.map((p, i) => (
        <p key={i} className="mb-2 text-[15px] leading-relaxed text-slate-700">
          {p}
        </p>
      ))}
      {section.bullets && (
        <ul className="mb-2 space-y-1.5">
          {section.bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-2 text-[15px] text-slate-700">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-biomar-swoosh" />
              {b}
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
              <dd className="text-sm text-slate-600">{f.value}</dd>
            </div>
          ))}
        </dl>
      )}
      {section.note && (
        <p className="rounded-lg border-l-4 border-biomar-swoosh bg-biomar-ice/50 px-3 py-2 text-sm text-biomar-navy">
          💡 {section.note}
        </p>
      )}
    </div>
  );
}
