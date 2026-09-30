import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Person } from "../content/types";
import { seedPeople } from "../content/people";
import { modulesById } from "../content/modules";
import * as authApi from "./authApi";

// ─────────────────────────────────────────────────────────────────────────────
// App state.
//
// Reads: content is bundled from the repo (GitHub as source of truth).
// Writes: the admin's changes to people/assignments/progress are kept in the
// browser (localStorage) and can be "published" — in production that publish
// call commits the updated people dataset back to GitHub via a Cloudflare
// Pages Function (see functions/api/publish.ts). Until published, everyone in
// the same browser sees the working copy.
// ─────────────────────────────────────────────────────────────────────────────

// Bump this whenever the module/chapter structure changes in a way that
// invalidates ids a browser may have cached (a content restructure, not a
// content edit). Old cached state under a previous key is simply ignored —
// the app reloads from the current seed instead of showing stale/broken data.
const STORAGE_KEY = "biomar-onboarding-state-v3";
// Only used as a fallback when there's no live Worker behind this URL (e.g. a
// static preview) — real deployments authenticate via the server session
// cookie instead. See `login` vs. `demoLogin` below.
const DEMO_SESSION_KEY = "biomar-onboarding-demo-session";

interface StoredState {
  people: Person[];
  dirty: boolean;
}

// Defends against a subtler version of the same problem: content edits that
// remove or rename individual module ids without a full restructure. Strips
// any assignment/progress/schedule entries that no longer resolve to a real
// module, so a stale id degrades gracefully instead of rendering nothing.
function reconcilePerson(person: Person): Person {
  const assignedModuleIds = person.assignedModuleIds.filter(
    (id) => modulesById[id],
  );
  const progress = Object.fromEntries(
    Object.entries(person.progress).filter(([id]) => modulesById[id]),
  );
  const schedule = person.schedule
    ? Object.fromEntries(
        Object.entries(person.schedule).filter(([id]) => modulesById[id]),
      )
    : person.schedule;
  return { ...person, assignedModuleIds, progress, schedule };
}

interface StoreValue {
  people: Person[];
  currentUserId: string | null;
  currentUser: Person | null;
  dirty: boolean;
  /** True until the initial session check (`/api/auth/me`) has resolved. */
  authLoading: boolean;
  /** null while unknown, then whether a real Worker/AUTH_KV backend answered. */
  backendAvailable: boolean | null;
  /** Real sign-in against the Worker's session-cookie auth. */
  login: (email: string, password: string) => Promise<{ ok: boolean; message?: string }>;
  /** Fallback used only when `backendAvailable` is false (no live Worker) — picks
   * a seeded person with no password, purely so a static preview stays clickable. */
  demoLogin: (id: string) => void;
  logout: () => void;
  upsertPerson: (person: Person) => void;
  removePerson: (id: string) => void;
  setAssignments: (personId: string, moduleIds: string[]) => void;
  setSchedule: (personId: string, schedule: Record<string, string>) => void;
  markModuleComplete: (
    personId: string,
    moduleId: string,
    quizScore: number,
  ) => void;
  publish: () => Promise<{ ok: boolean; message: string }>;
  resetDemo: () => void;
}

const StoreContext = createContext<StoreValue | null>(null);

function load(): StoredState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as StoredState;
      return { ...parsed, people: parsed.people.map(reconcilePerson) };
    }
  } catch {
    /* ignore */
  }
  return { people: seedPeople.map(reconcilePerson), dirty: false };
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<StoredState>(load);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [backendAvailable, setBackendAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  // On load, ask the Worker who (if anyone) the session cookie belongs to. If
  // there's no Worker at this URL at all (a static preview), fall back to the
  // old browser-local demo session so the preview stays explorable.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const session = await authApi.fetchMe();
        if (cancelled) return;
        setBackendAvailable(true);
        if (session.ok && session.personId) setCurrentUserId(session.personId);
      } catch (err) {
        if (cancelled) return;
        if (authApi.isBackendUnavailable(err)) {
          setBackendAvailable(false);
          const demoId = localStorage.getItem(DEMO_SESSION_KEY);
          if (demoId) setCurrentUserId(demoId);
        } else {
          setBackendAvailable(true);
        }
      } finally {
        if (!cancelled) setAuthLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo<StoreValue>(() => {
    const setPeople = (
      updater: (people: Person[]) => Person[],
      markDirty = true,
    ) =>
      setState((s) => ({
        people: updater(s.people),
        dirty: markDirty ? true : s.dirty,
      }));

    return {
      people: state.people,
      dirty: state.dirty,
      currentUserId,
      currentUser:
        state.people.find((p) => p.id === currentUserId) ?? null,
      authLoading,
      backendAvailable,
      login: async (email, password) => {
        const result = await authApi.login(email, password);
        if (!result.ok) return { ok: false, message: result.error };
        setCurrentUserId(result.personId);
        return { ok: true };
      },
      demoLogin: (id) => {
        localStorage.setItem(DEMO_SESSION_KEY, id);
        setCurrentUserId(id);
      },
      logout: () => {
        localStorage.removeItem(DEMO_SESSION_KEY);
        setCurrentUserId(null);
        if (backendAvailable) authApi.logout().catch(() => {});
      },
      upsertPerson: (person) =>
        setPeople((people) => {
          const idx = people.findIndex((p) => p.id === person.id);
          if (idx === -1) return [...people, person];
          const next = [...people];
          next[idx] = person;
          return next;
        }),
      removePerson: (id) =>
        setPeople((people) => people.filter((p) => p.id !== id)),
      setAssignments: (personId, moduleIds) =>
        setPeople((people) =>
          people.map((p) =>
            p.id === personId ? { ...p, assignedModuleIds: moduleIds } : p,
          ),
        ),
      setSchedule: (personId, schedule) =>
        setPeople((people) =>
          people.map((p) => (p.id === personId ? { ...p, schedule } : p)),
        ),
      markModuleComplete: (personId, moduleId, quizScore) =>
        setPeople((people) =>
          people.map((p) =>
            p.id === personId
              ? {
                  ...p,
                  progress: {
                    ...p.progress,
                    [moduleId]: { completed: true, quizScore },
                  },
                }
              : p,
          ),
        ),
      publish: async () => {
        try {
          const res = await fetch("/api/publish", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ people: state.people }),
          });
          if (!res.ok) {
            const text = await res.text();
            return {
              ok: false,
              message:
                res.status === 404
                  ? "Publish endpoint not configured yet. Changes are saved locally in this browser. Configure functions/api/publish.ts + a GitHub token to commit to the repo."
                  : `Publish failed (${res.status}): ${text}`,
            };
          }
          setState((s) => ({ ...s, dirty: false }));
          const data = (await res.json().catch(() => ({}))) as {
            commit?: string;
          };
          return {
            ok: true,
            message: data.commit
              ? `Published to GitHub (commit ${data.commit.slice(0, 7)}).`
              : "Published to GitHub.",
          };
        } catch (err) {
          return {
            ok: false,
            message: `Could not reach publish endpoint. Changes remain saved locally. (${
              (err as Error).message
            })`,
          };
        }
      },
      resetDemo: () => {
        setState({ people: seedPeople, dirty: false });
        setCurrentUserId(null);
      },
    };
  }, [state, currentUserId, authLoading, backendAvailable]);

  return (
    <StoreContext.Provider value={value}>{children}</StoreContext.Provider>
  );
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore must be used within StoreProvider");
  return ctx;
}
