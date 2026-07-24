import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { modulesById } from "../content/modules";
import { useStore } from "../lib/store";
import { InfoPanel } from "../components/InfoPanel";
import type { LessonSection, QuizQuestion } from "../content/types";

export function ModuleView() {
  const { moduleId } = useParams();
  const { currentUser, markModuleComplete } = useStore();
  const navigate = useNavigate();
  const module = moduleId ? modulesById[moduleId] : undefined;

  if (!module || !currentUser) {
    return (
      <div className="card p-8 text-center text-slate-500">
        Module not found.{" "}
        <Link to="/" className="text-biomar-swoosh">
          Back
        </Link>
      </div>
    );
  }

  const alreadyDone = currentUser.progress[module.id]?.completed;

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <article className="space-y-6">
        <div>
          <Link
            to="/"
            className="text-sm text-slate-400 hover:text-biomar-swoosh"
          >
            ← Back to my onboarding
          </Link>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="chip bg-biomar-ice text-biomar-blue uppercase">
              {module.category}
            </span>
            <span className="text-xs text-slate-400">
              {module.estMinutes} min · Source: {module.source}
            </span>
          </div>
          <h1 className="mt-2 text-2xl font-bold text-biomar-navy">
            {module.title}
          </h1>
          <p className="mt-1 text-slate-500">{module.summary}</p>
        </div>

        <section className="card space-y-5 p-6">
          {module.sections.map((s, i) => (
            <Section key={i} section={s} />
          ))}
        </section>

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

        <Quiz
          questions={module.quiz}
          alreadyDone={!!alreadyDone}
          onPass={(score) => {
            markModuleComplete(currentUser.id, module.id, score);
            navigate("/");
          }}
        />
      </article>

      <InfoPanel />
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

function Quiz({
  questions,
  alreadyDone,
  onPass,
}: {
  questions: QuizQuestion[];
  alreadyDone: boolean;
  onPass: (score: number) => void;
}) {
  const [answers, setAnswers] = useState<Record<string, number[]>>({});
  const [submitted, setSubmitted] = useState(false);

  const score = useMemo(() => {
    let correct = 0;
    for (const q of questions) {
      const a = (answers[q.id] ?? []).slice().sort();
      const c = q.correct.slice().sort();
      if (a.length === c.length && a.every((v, i) => v === c[i])) correct++;
    }
    return Math.round((correct / questions.length) * 100);
  }, [answers, questions]);

  const allAnswered = questions.every((q) => (answers[q.id]?.length ?? 0) > 0);

  const toggle = (q: QuizQuestion, idx: number) => {
    if (submitted) return;
    setAnswers((prev) => {
      const cur = prev[q.id] ?? [];
      if (q.type === "multi") {
        return {
          ...prev,
          [q.id]: cur.includes(idx)
            ? cur.filter((i) => i !== idx)
            : [...cur, idx],
        };
      }
      return { ...prev, [q.id]: [idx] };
    });
  };

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
          Knowledge check
        </h2>
        {alreadyDone && !submitted && (
          <span className="chip bg-biomar-green/10 text-biomar-green">
            Already completed — retake anytime
          </span>
        )}
      </div>

      <div className="mt-4 space-y-6">
        {questions.map((q, qi) => {
          const chosen = answers[q.id] ?? [];
          return (
            <div key={q.id}>
              <p className="font-semibold text-biomar-navy">
                {qi + 1}. {q.prompt}
                {q.type === "multi" && (
                  <span className="ml-2 text-xs font-normal text-slate-400">
                    (select all that apply)
                  </span>
                )}
              </p>
              <div className="mt-2 space-y-1.5">
                {q.options.map((opt, oi) => {
                  const isChosen = chosen.includes(oi);
                  const isCorrect = q.correct.includes(oi);
                  let cls =
                    "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm cursor-pointer transition ";
                  if (submitted) {
                    if (isCorrect)
                      cls += "border-biomar-green bg-biomar-green/10 text-biomar-navy";
                    else if (isChosen)
                      cls += "border-red-300 bg-red-50 text-red-700";
                    else cls += "border-slate-100 text-slate-500";
                  } else {
                    cls += isChosen
                      ? "border-biomar-swoosh bg-biomar-ice text-biomar-navy"
                      : "border-slate-200 hover:border-biomar-swoosh/60";
                  }
                  return (
                    <label key={oi} className={cls}>
                      <input
                        type={q.type === "multi" ? "checkbox" : "radio"}
                        name={q.id}
                        checked={isChosen}
                        onChange={() => toggle(q, oi)}
                        className="accent-biomar-swoosh"
                      />
                      {opt}
                      {submitted && isCorrect && (
                        <span className="ml-auto text-xs font-semibold text-biomar-green">
                          correct
                        </span>
                      )}
                    </label>
                  );
                })}
              </div>
              {submitted && (
                <p className="mt-2 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600">
                  {q.explanation}
                </p>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
        {!submitted ? (
          <>
            <p className="text-sm text-slate-400">
              {allAnswered
                ? "All answered — submit to check."
                : "Answer every question to submit."}
            </p>
            <button
              className="btn-primary"
              disabled={!allAnswered}
              onClick={() => setSubmitted(true)}
            >
              Submit answers
            </button>
          </>
        ) : (
          <>
            <p className="text-sm">
              You scored{" "}
              <span
                className={`font-bold ${
                  score >= 70 ? "text-biomar-green" : "text-amber-600"
                }`}
              >
                {score}%
              </span>
              {score < 70 && " — review and retake to reinforce the concepts."}
            </p>
            <div className="flex gap-2">
              <button
                className="btn-ghost"
                onClick={() => {
                  setSubmitted(false);
                  setAnswers({});
                }}
              >
                Retake
              </button>
              <button className="btn-accent" onClick={() => onPass(score)}>
                Mark complete & continue
              </button>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
