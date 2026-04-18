import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/profiles", label: "Profiles" },
  { to: "/numerology", label: "Numbers" },
  { to: "/name", label: "Name" },
  { to: "/fengshui", label: "Feng Shui" },
  { to: "/compatibility", label: "Compatibility" },
  { to: "/chat", label: "Ask Reader" },
];

export function Shell() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink/10 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-display text-xl tracking-tight">八字</span>
            <span className="font-display text-base text-muted">Metaphysical Suite</span>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-lg text-sm transition ${
                    isActive ? "bg-ink text-parchment" : "text-ink hover:bg-ink/5"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline text-xs text-muted">
              {user?.email}
              {user?.is_premium ? (
                <span className="ml-2 chip bg-earth text-white">PREMIUM</span>
              ) : (
                <span className="ml-2 chip element-metal">FREE</span>
              )}
            </span>
            <button onClick={logout} className="btn-ghost text-xs">Sign out</button>
          </div>
        </div>
        <nav className="md:hidden border-t border-ink/10 overflow-x-auto">
          <div className="flex gap-1 px-3 py-2">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  `whitespace-nowrap px-3 py-1.5 rounded-lg text-sm transition ${
                    isActive ? "bg-ink text-parchment" : "text-ink hover:bg-ink/5"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </div>
        </nav>
      </header>
      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-6">
          <Outlet />
        </div>
      </main>
      <footer className="border-t border-ink/10 py-4 text-center text-xs text-muted">
        Ba Zi • Numerology • Compatibility — not medical, financial, or legal advice.
      </footer>
    </div>
  );
}
