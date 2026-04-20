import { FormEvent, useEffect, useRef, useState } from "react";
import { api, ChatMessage, ChatSession, Profile } from "../api";
import { useI18n } from "../i18n";

type PendingMessage = {
  id: string;            // client-generated id (negative/string to avoid int collision)
  role: "user";
  content: string;
  created_at: string;
};

export function ChatPage() {
  const { t, lang } = useI18n();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState<PendingMessage | null>(null);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    api.listProfiles().then((list) => {
      setProfiles(list);
      const main = list.find((p) => p.is_main) ?? list[0];
      if (main) setProfileId(main.id);
    });
    api.chatSessions().then(setSessions);
  }, []);

  useEffect(() => {
    if (sessionId) api.chatMessages(sessionId).then(setMessages);
    else setMessages([]);
    setPending(null);
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending, busy]);

  useEffect(() => {
    if (busy) {
      setElapsed(0);
      timerRef.current = window.setInterval(() => setElapsed((e) => e + 1), 1000);
      return () => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };
    }
  }, [busy]);

  async function sendQuestion(q: string) {
    // Optimistic UI: show the user's message immediately.
    const optimistic: PendingMessage = {
      id: `pending-${Date.now()}`,
      role: "user",
      content: q,
      created_at: new Date().toISOString(),
    };
    setPending(optimistic);
    setQuestion("");
    setBusy(true);
    setError(null);

    try {
      const resp = await api.chatSend(
        q,
        sessionId ?? undefined,
        profileId === "" ? undefined : Number(profileId),
        lang,
      );
      if (!sessionId) {
        setSessionId(resp.session.id);
        setSessions((prev) => [resp.session, ...prev]);
      }
      setMessages((prev) => [...prev, resp.user_message, resp.assistant_message]);
      setPending(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
      setPending(null);
      setQuestion(q); // restore the input so they can retry
    } finally {
      setBusy(false);
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (q) void sendQuestion(q);
  }

  // Quick-start prompts shown on the empty chat state. These intentionally
  // open the conversation with simple, plain-language questions so the
  // reader's "explain like I'm new to this" prompt kicks in naturally.
  const quickPrompts: string[] = [
    t("chat.qp_explain"),
    t("chat.qp_career"),
    t("chat.qp_love"),
    t("chat.qp_year"),
    t("chat.qp_colors"),
    t("chat.qp_home"),
  ];

  async function deleteSession(id: number) {
    if (!confirm(t("chat.delete_confirm"))) return;
    await api.chatDeleteSession(id);
    setSessions(sessions.filter((s) => s.id !== id));
    if (sessionId === id) {
      setSessionId(null);
      setMessages([]);
    }
  }

  const hasAnyContent = messages.length > 0 || pending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="font-display text-2xl">{t("chat.title")}</h1>
          <p className="text-sm text-muted">{t("chat.subtitle")}</p>
        </div>
        <label className="block">
          <span className="text-xs text-muted">{t("chat.chart_context")}</span>
          <select
            className="input mt-1"
            value={profileId}
            onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">{t("chat.no_profile")}</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
      </div>

      <div className="grid md:grid-cols-[220px_1fr] gap-4">
        <aside className="space-y-2">
          <button
            className="btn-ghost w-full text-sm"
            onClick={() => { setSessionId(null); setMessages([]); setPending(null); }}
          >
            {t("chat.new_chat")}
          </button>
          <div className="text-xs uppercase tracking-wider text-muted mt-3">{t("chat.recent")}</div>
          <div className="space-y-1 max-h-[420px] overflow-y-auto">
            {sessions.length === 0 && <div className="text-xs text-muted">No chats yet</div>}
            {sessions.map((s) => (
              <div
                key={s.id}
                className={`group flex items-center justify-between rounded-lg px-2 py-1.5 text-sm cursor-pointer ${
                  sessionId === s.id ? "bg-ink text-parchment" : "hover:bg-ink/5"
                }`}
                onClick={() => setSessionId(s.id)}
              >
                <div className="truncate">{s.title}</div>
                <button
                  className="opacity-0 group-hover:opacity-100 text-xs ml-1"
                  onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}
                  title="Delete"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </aside>

        <section className="rounded-2xl border border-ink/10 bg-white flex flex-col min-h-[500px]">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
            {!hasAnyContent && !busy && (
              <div className="h-full flex flex-col items-center justify-center text-center text-sm text-muted py-6">
                <div className="font-display text-4xl mb-2">八字</div>
                <p className="mb-5 max-w-md">{t("chat.empty")}</p>
                <div className="w-full max-w-xl">
                  <div className="text-[11px] uppercase tracking-[0.15em] text-muted/80 mb-2">
                    {t("chat.quick_starters")}
                  </div>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {quickPrompts.map((q, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => sendQuestion(q)}
                        disabled={busy}
                        className="text-left rounded-xl border border-ink/10 bg-parchment/60 hover:bg-parchment hover:border-earth/40 hover:-translate-y-0.5 active:translate-y-0 transition px-3 py-2.5 text-sm text-ink"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`rounded-2xl px-4 py-2 max-w-[80%] text-sm whitespace-pre-wrap ${
                  m.role === "user" ? "bg-ink text-parchment" : "bg-parchment border border-ink/10"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}

            {pending && (
              <div className="flex justify-end">
                <div className="rounded-2xl px-4 py-2 max-w-[80%] text-sm whitespace-pre-wrap bg-ink text-parchment opacity-80">
                  {pending.content}
                </div>
              </div>
            )}

            {busy && (
              <div className="flex justify-start">
                <div className="rounded-2xl px-4 py-3 bg-parchment border border-ink/10 text-sm text-muted max-w-[80%] space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex gap-1" aria-hidden>
                      <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </span>
                    <span>{t("chat.consulting")}</span>
                    <span className="text-[11px] text-ink/50">· {t("chat.elapsed")} {elapsed}s</span>
                  </div>
                  {elapsed >= 10 && (
                    <div className="text-[11px] text-ink/50">{t("chat.consulting_cold")}</div>
                  )}
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="text-fire text-sm px-4 py-2 border-t border-fire/30 bg-fire-soft">
              {error}
            </div>
          )}

          <form onSubmit={onSubmit} className="flex gap-2 border-t border-ink/10 p-3">
            <input
              className="input flex-1"
              placeholder={t("chat.ask_placeholder")}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={busy}
              required
            />
            <button type="submit" disabled={busy || !question.trim()} className="btn-primary">
              {t("chat.ask")}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
