import { FormEvent, useEffect, useRef, useState } from "react";
import { api, ChatMessage, ChatSession, Profile } from "../api";

export function ChatPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

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
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const resp = await api.chatSend(
        question.trim(),
        sessionId ?? undefined,
        profileId === "" ? undefined : Number(profileId),
      );
      if (!sessionId) {
        setSessionId(resp.session.id);
        setSessions([resp.session, ...sessions]);
      }
      setMessages((prev) => [...prev, resp.user_message, resp.assistant_message]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  async function deleteSession(id: number) {
    if (!confirm("Delete this chat?")) return;
    await api.chatDeleteSession(id);
    setSessions(sessions.filter((s) => s.id !== id));
    if (sessionId === id) {
      setSessionId(null);
      setMessages([]);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="font-display text-2xl">Ask the Reader</h1>
          <p className="text-sm text-muted">
            A personal Ba Zi / feng shui consultant. It reads your saved chart and answers
            questions as a warm, direct advisor. Powered by Ollama + Gemma (self-hosted).
          </p>
        </div>
        <label className="block">
          <span className="text-xs text-muted">Chart context</span>
          <select
            className="input mt-1"
            value={profileId}
            onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">No profile (general)</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
      </div>

      <div className="grid md:grid-cols-[220px_1fr] gap-4">
        <aside className="space-y-2">
          <button
            className="btn-ghost w-full text-sm"
            onClick={() => { setSessionId(null); setMessages([]); }}
          >
            + New chat
          </button>
          <div className="text-xs uppercase tracking-wider text-muted mt-3">Recent</div>
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
            {messages.length === 0 && (
              <div className="h-full flex items-center justify-center text-center text-sm text-muted">
                <div>
                  <div className="font-display text-3xl mb-2">八字</div>
                  <p>Ask a question — career, love, money, timing, feng shui of a room.</p>
                  <p className="mt-2 text-xs">The reader will answer in under 250 words, grounded in your chart.</p>
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
            {busy && (
              <div className="flex justify-start">
                <div className="rounded-2xl px-4 py-2 bg-parchment border border-ink/10 text-sm text-muted">
                  The reader is consulting the chart…
                </div>
              </div>
            )}
          </div>
          {error && <div className="text-fire text-sm px-4 py-2 border-t border-fire/30 bg-fire-soft">{error}</div>}
          <form onSubmit={onSubmit} className="flex gap-2 border-t border-ink/10 p-3">
            <input
              className="input flex-1"
              placeholder="How is my career luck in 2026? What should I do about my bedroom layout?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={busy}
              required
            />
            <button type="submit" disabled={busy || !question.trim()} className="btn-primary">
              Ask
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
