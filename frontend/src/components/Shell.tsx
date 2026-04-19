import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";
import { useI18n } from "../i18n";

function buildLinks(t: (k: string) => string, isAdmin: boolean) {
  const base = [
    { to: "/", label: t("nav.dashboard"), end: true },
    { to: "/profiles", label: t("nav.profiles") },
    { to: "/numerology", label: t("nav.numbers") },
    { to: "/name", label: t("nav.name") },
    { to: "/fengshui", label: t("nav.fengshui") },
    { to: "/compatibility", label: t("nav.compatibility") },
    { to: "/chat", label: t("nav.chat") },
    { to: "/referrals", label: t("nav.referrals") },
  ];
  if (isAdmin) base.push({ to: "/admin", label: t("nav.admin") });
  return base;
}

export function Shell() {
  const { user, logout } = useAuth();
  const { lang, setLang, t } = useI18n();
  const links = buildLinks(t, user?.is_admin ?? false);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink/10 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-2">
          <NavLink to="/" className="flex items-center gap-2 shrink-0">
            <img src="/favicon.svg" alt="八字" className="w-8 h-8 rounded-lg" />
            <span className="font-display text-base text-muted hidden sm:inline">Metaphysical Suite</span>
          </NavLink>
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
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value as any)}
              className="text-xs rounded-lg border border-ink/15 bg-white px-2 py-1 focus:outline-none"
              title={t("common.language")}
            >
              <option value="en">EN</option>
              <option value="zh">中文</option>
              <option value="ms">BM</option>
            </select>
            <span className="hidden sm:inline text-xs text-muted">
              {user?.email}
              {user?.is_premium ? (
                <span className="ml-2 chip bg-earth text-white">{t("common.premium")}</span>
              ) : (
                <span className="ml-2 chip element-metal">{t("common.free")}</span>
              )}
            </span>
            <button onClick={logout} className="btn-ghost text-xs">{t("common.signout")}</button>
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
        {t("common.footer")}
      </footer>
    </div>
  );
}
