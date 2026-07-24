import { Link, useLocation, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { Logo, TAGLINE } from "./Brand";
import { useStore } from "../lib/store";

export function Layout({ children }: { children: ReactNode }) {
  const { currentUser, logout, dirty } = useStore();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isAdmin = currentUser?.role === "admin";

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
                      Unpublished changes
                    </span>
                  )}
                </>
              ) : (
                <NavLink to="/" active={pathname === "/"}>
                  My onboarding
                </NavLink>
              )}
              <div className="ml-3 flex items-center gap-2 border-l border-slate-200 pl-3">
                <div className="text-right leading-tight">
                  <div className="text-xs font-semibold text-biomar-navy">
                    {currentUser.name}
                  </div>
                  <div className="text-[10px] uppercase tracking-wide text-slate-400">
                    {currentUser.role}
                  </div>
                </div>
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
