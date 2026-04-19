import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { useI18n } from "../i18n";

type MenuItem = { to: string; label: string; end?: boolean };
type MenuGroup = { label: string; items: MenuItem[] };

function buildGroups(
  t: (k: string) => string,
  isAdmin: boolean,
  isPremium: boolean,
): MenuGroup[] {
  const account: MenuItem[] = [
    { to: "/referrals", label: t("nav.referrals") },
  ];
  if (!isPremium) account.push({ to: "/upgrade", label: t("nav.upgrade") });
  if (isAdmin) account.push({ to: "/admin", label: t("nav.admin") });

  return [
    {
      label: t("menu.charts"),
      items: [
        { to: "/", label: t("nav.dashboard"), end: true },
        { to: "/profiles", label: t("nav.profiles") },
        { to: "/businesses", label: t("nav.business") },
      ],
    },
    {
      label: t("menu.readings"),
      items: [
        { to: "/numerology", label: t("nav.numbers") },
        { to: "/name", label: t("nav.name") },
        { to: "/fengshui", label: t("nav.fengshui") },
        { to: "/face", label: t("nav.face") },
        { to: "/palm", label: t("nav.palm") },
        { to: "/compatibility", label: t("nav.compatibility") },
      ],
    },
    {
      label: t("menu.tools"),
      items: [
        { to: "/chat", label: t("nav.chat") },
      ],
    },
    {
      label: t("menu.account"),
      items: account,
    },
  ];
}

export function Shell() {
  const { user, logout } = useAuth();
  const { lang, setLang, t } = useI18n();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement | null>(null);

  const groups = buildGroups(t, user?.is_admin ?? false, user?.is_premium ?? false);

  // Close when the user navigates.
  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  // Close on outside click + Escape.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Prevent background scroll when the sheet is open on mobile.
  useEffect(() => {
    if (open) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = prev; };
    }
  }, [open]);

  const credits = user?.feature_credits ?? 0;
  const slots = user?.extra_profile_slots ?? 0;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 border-b border-ink/10 bg-white/85 backdrop-blur supports-[backdrop-filter]:bg-white/70">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-3">
          <NavLink to="/" end className="flex items-center gap-2 shrink-0">
            <img src="/favicon.svg" alt="八字" className="w-8 h-8 rounded-lg" />
            <span className="font-display text-base text-ink hidden sm:inline">
              Metaphysical Suite
            </span>
          </NavLink>

          <div className="flex-1" />

          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as "en" | "zh" | "ms")}
            className="text-xs rounded-lg border border-ink/15 bg-white px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-earth/40"
            title={t("common.language")}
            aria-label={t("common.language")}
          >
            <option value="en">EN</option>
            <option value="zh">中文</option>
            <option value="ms">BM</option>
          </select>

          <div ref={wrapperRef} className="relative">
            <button
              onClick={() => setOpen((o) => !o)}
              aria-expanded={open}
              aria-haspopup="menu"
              className="flex items-center gap-2 min-h-[40px] rounded-lg border border-ink/15 bg-white px-3 py-1.5 text-sm hover:bg-ink/5 active:bg-ink/10 transition focus:outline-none focus:ring-2 focus:ring-earth/40"
            >
              <HamburgerIcon open={open} />
              <span className="hidden sm:inline">{t("menu.menu")}</span>
            </button>

            {open && (
              <>
                {/* Mobile backdrop */}
                <div
                  aria-hidden
                  className="md:hidden fixed inset-0 top-[61px] z-30 bg-ink/30 backdrop-blur-[2px]"
                />
                {/* Dropdown panel */}
                <div
                  role="menu"
                  aria-label={t("menu.menu")}
                  className="fixed md:absolute z-40 right-0 md:right-0 left-0 md:left-auto top-[61px] md:top-full md:mt-2 w-auto md:w-80 max-h-[calc(100vh-61px)] md:max-h-[80vh] overflow-y-auto rounded-none md:rounded-2xl border-t md:border border-ink/10 bg-white shadow-2xl"
                >
                  {user?.email && (
                    <div className="px-4 pt-4 pb-3 border-b border-ink/10">
                      <div className="text-xs text-muted truncate">{user.email}</div>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        {user.is_premium ? (
                          <span className="chip bg-earth text-white">
                            {t("common.premium")}
                          </span>
                        ) : (
                          <NavLink
                            to="/upgrade"
                            className="chip element-metal hover:bg-ink/10"
                          >
                            {t("common.free")}
                          </NavLink>
                        )}
                        {credits > 0 && (
                          <span className="chip element-earth text-[11px]">
                            {credits} {t("billing.credits_chip")}
                          </span>
                        )}
                        {slots > 0 && (
                          <span className="chip element-wood text-[11px]">
                            +{slots} {t("billing.slots_chip")}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="py-1">
                    {groups.map((group) => (
                      <section key={group.label} className="py-1">
                        <div className="px-4 pt-3 pb-1 text-[10px] uppercase tracking-[0.12em] text-muted font-semibold">
                          {group.label}
                        </div>
                        {group.items.map((item) => (
                          <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.end}
                            className={({ isActive }) =>
                              `flex items-center min-h-[44px] px-4 text-sm transition ${
                                isActive
                                  ? "bg-ink text-parchment"
                                  : "text-ink hover:bg-ink/5 active:bg-ink/10"
                              }`
                            }
                          >
                            <span className="flex-1 truncate">{item.label}</span>
                            <ChevronRightIcon />
                          </NavLink>
                        ))}
                      </section>
                    ))}
                  </div>

                  <div className="sticky bottom-0 border-t border-ink/10 bg-white p-2">
                    <button
                      onClick={logout}
                      className="w-full flex items-center justify-between min-h-[44px] px-3 rounded-lg text-sm text-fire hover:bg-fire-soft/50 active:bg-fire-soft transition"
                    >
                      <span>{t("common.signout")}</span>
                      <SignOutIcon />
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
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

function HamburgerIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      className="transition-transform"
    >
      {open ? (
        <>
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </>
      ) : (
        <>
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </>
      )}
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      className="opacity-40"
    >
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

function SignOutIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}
