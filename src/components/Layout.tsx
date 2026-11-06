import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, type ReactNode } from "react";
import { SearchPalette } from "./SearchPalette";
import { Logo, TAGLINE } from "./Brand";
import { useStore } from "../lib/store";

export function Layout({ children }: { children: ReactNode }) {
  const { currentUser, logout, dirty, backendAvailable } = useStore();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isAdmin = currentUser?.role === "admin";
  const [searchOpen, setSearchOpen] = useState(false);
  const canSearch = !!currentUser && !isAdmin;

  // Ctrl/Cmd+K opens the search for designers.
  useEffect(() => {
    if (!canSearch) return;
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [canSearch]);

  return (
    <div className="flex min-h-full flex-col">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
          <Link to="/">
            <Logo />
          </Link>
          {currentUser && (
            <nav className="flex items-center gap-1 text-sm">
              {isAdmin ? (
                <>
                  <NavLink to="/admin" active={pathname.startsWith("/admin")}>
                    Admin
                  </NavLink>
                  {dirty && (
                    <span className="chip bg-amber-100 text-amber-700">
                      {backendAvailable ? "Saving…" : "Unpublished changes"}
                    </span>
                  )}
                </>
              ) : (
                <>
                  <NavLink to="/" active={pathname === "/"}>
                    My onboarding
                  </NavLink>
                  <button
                    onClick={() => setSearchOpen(true)}
                    className="ml-1 flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-slate-500 transition hover:border-biomar-swoosh hover:text-biomar-navy"
                    aria-label="Search"
                  >
                    <span aria-hidden>🔍</span>
                    <span className="hidden sm:inline">Search</span>
                    <kbd className="hidden rounded border border-slate-200 px-1.5 py-0.5 text-[10px] text-slate-400 sm:inline">
                      Ctrl K
                    </kbd>
                  </button>
                </>
              )}
              <div className="ml-3 flex items-center gap-2 border-l border-slate-200 pl-3">
                <Link to="/account" className="text-right leading-tight hover:opacity-70">
                  <div className="text-xs font-semibold text-biomar-navy">
                    {currentUser.name}
                  </div>
                  <div className="text-[10px] uppercase tracking-wide text-slate-400">
                    {currentUser.role}
                  </div>
                </Link>
                <button
                  className="btn-ghost px-3 py-1.5 text-xs"
                  onClick={() => {
                    logout();
                    navigate("/");
                  }}
                >
                  Switch user
                </button>
              </div>
            </nav>
          )}
        </div>
      </header>

      {canSearch && currentUser && (
        <SearchPalette
          assignedIds={currentUser.assignedModuleIds}
          open={searchOpen}
          onClose={() => setSearchOpen(false)}
        />
      )}

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8">{children}</main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 text-center text-xs text-slate-400">
          {TAGLINE}
        </div>
      </footer>
    </div>
  );
}

function NavLink({
  to,
  active,
  children,
}: {
  to: string;
  active: boolean;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      className={`rounded-lg px-3 py-1.5 font-medium transition ${
        active
          ? "bg-biomar-ice text-biomar-navy"
          : "text-slate-500 hover:bg-slate-50 hover:text-biomar-navy"
      }`}
    >
      {children}
    </Link>
  );
}
