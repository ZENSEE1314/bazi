import { useEffect, useState } from "react";
import { api, HistoryItem } from "../api";
import { useI18n } from "../i18n";

type Props = {
  kind: "numerology" | "name" | "face" | "palm";
  refreshKey?: number;                        // bump to force reload
  onOpen: (id: number) => void;
  currentId?: number | null;
};

export function HistorySidebar({ kind, refreshKey, onOpen, currentId }: Props) {
  const { t } = useI18n();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(query?: string) {
    setLoading(true);
    try {
      setItems(await api.listHistory(kind, query));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [kind, refreshKey]);

  async function onDelete(id: number) {
    try {
      await api.deleteHistory(id);
      load(q);
    } catch {/* ignore */}
  }

  return (
    <aside className="rounded-2xl border border-ink/10 bg-white p-3 h-full">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs uppercase tracking-wider text-muted">
          {t("history.title")}
        </div>
        {items.length > 0 && (
          <span className="text-[10px] text-muted">{items.length}</span>
        )}
      </div>
      <input
        type="search"
        className="input text-xs mb-2"
        placeholder={t("history.search")}
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") load(q);
        }}
      />
      {loading ? (
        <div className="text-xs text-muted">{t("common.loading")}</div>
      ) : items.length === 0 ? (
        <div className="text-xs text-muted">{t("history.empty")}</div>
      ) : (
        <div className="space-y-1 max-h-[480px] overflow-y-auto">
          {items.map((it) => (
            <div
              key={it.id}
              className={`group flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-sm cursor-pointer ${
                currentId === it.id ? "bg-ink text-parchment" : "hover:bg-ink/5"
              }`}
              onClick={() => onOpen(it.id)}
              title={new Date(it.created_at).toLocaleString()}
            >
              <div className="min-w-0 flex-1">
                <div className="truncate font-mono text-xs">{it.label}</div>
                {it.subtype && (
                  <div className="text-[10px] opacity-70">{it.subtype}</div>
                )}
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(it.id); }}
                className="opacity-0 group-hover:opacity-100 text-xs hover:text-fire shrink-0"
                aria-label={t("history.delete")}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}
