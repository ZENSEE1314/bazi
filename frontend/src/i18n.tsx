import { createContext, ReactNode, useContext, useEffect, useState } from "react";

export type Lang = "en" | "zh" | "ms";

const STORE_KEY = "bazi.lang";

const translations: Record<Lang, Record<string, string>> = {
  en: {
    "nav.dashboard": "Dashboard",
    "nav.profiles": "Profiles",
    "nav.numbers": "Numbers",
    "nav.name": "Name",
    "nav.fengshui": "Feng Shui",
    "nav.compatibility": "Compatibility",
    "nav.chat": "Ask Reader",
    "common.signout": "Sign out",
    "common.free": "FREE",
    "common.premium": "PREMIUM",
    "common.today": "Today",
    "common.loading": "Loading…",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.language": "Language",

    "numerology.title": "Number Check",
    "numerology.subtitle":
      "Score any number — phone, bank, car plate, ID, credit card. Profile-linked for personalized guidance.",
    "numerology.link_profile": "Link to profile (personalized)",
    "numerology.select_profile": "General (no profile)",
    "numerology.type_phone": "Phone",
    "numerology.type_bank": "Bank Account",
    "numerology.type_car": "Car Plate",
    "numerology.type_id": "ID / IC",
    "numerology.type_credit": "Credit Card",
    "numerology.score": "Score",
    "numerology.scoring": "Scoring…",
    "numerology.wealth": "Wealth",
    "numerology.safety": "Safety",
    "numerology.health": "Health",
    "numerology.overall": "Overall",
    "numerology.life_path": "Life Path",
    "numerology.element_profile": "Element Profile",
    "numerology.dominant": "Dominant",
    "numerology.pair_analysis": "Pair-by-Pair Analysis",
    "numerology.auspicious": "auspicious",
    "numerology.inauspicious": "inauspicious",
    "numerology.why": "Why",
    "numerology.suggestions": "Better Alternatives",
    "numerology.issues": "Issues Detected",
    "numerology.personalized": "Personalized for you",
    "numerology.preferred_digits": "Favored digits (Useful God)",
    "numerology.avoid_digits": "Digits to avoid",

    "chart.prevention": "What to Prevent",
    "chart.enhancement": "What Makes It Better",
    "chart.colors_favor": "Colors to Wear",
    "chart.colors_avoid": "Colors to Minimize",
    "chart.foods_favor": "Foods to Favor",
    "chart.foods_avoid": "Foods to Avoid",
    "chart.gemstones": "Supportive Gemstones",
    "chart.lucky_numbers": "Lucky Numbers",
    "chart.best_direction": "Best Direction",
    "chart.best_careers": "Career Fit",

    "chat.title": "Ask the Reader",
    "chat.subtitle":
      "A personal Ba Zi / feng shui consultant. Reads your chart and answers in your language.",
    "chat.chart_context": "Chart context",
    "chat.no_profile": "No profile (general)",
    "chat.new_chat": "+ New chat",
    "chat.recent": "Recent",
    "chat.consulting": "The reader is consulting the chart…",
    "chat.ask_placeholder":
      "How is my career luck in 2026? What should I change in my bedroom?",
    "chat.ask": "Ask",
    "chat.empty": "Ask a question — career, love, money, timing, feng shui.",
  },
  zh: {
    "nav.dashboard": "首页",
    "nav.profiles": "命盘",
    "nav.numbers": "号码",
    "nav.name": "姓名",
    "nav.fengshui": "风水",
    "nav.compatibility": "合婚",
    "nav.chat": "问师",
    "common.signout": "退出",
    "common.free": "免费",
    "common.premium": "尊享",
    "common.today": "今天",
    "common.loading": "加载中…",
    "common.save": "保存",
    "common.cancel": "取消",
    "common.language": "语言",

    "numerology.title": "号码检测",
    "numerology.subtitle":
      "为电话、银行账户、车牌、身份证、信用卡打分。绑定命盘获得专属建议。",
    "numerology.link_profile": "绑定命盘（个性化）",
    "numerology.select_profile": "通用（无命盘）",
    "numerology.type_phone": "电话",
    "numerology.type_bank": "银行账户",
    "numerology.type_car": "车牌",
    "numerology.type_id": "身份证",
    "numerology.type_credit": "信用卡",
    "numerology.score": "评分",
    "numerology.scoring": "正在评分…",
    "numerology.wealth": "财运",
    "numerology.safety": "平安",
    "numerology.health": "健康",
    "numerology.overall": "综合",
    "numerology.life_path": "生命数",
    "numerology.element_profile": "五行分布",
    "numerology.dominant": "主导",
    "numerology.pair_analysis": "数字组合解读",
    "numerology.auspicious": "吉",
    "numerology.inauspicious": "凶",
    "numerology.why": "原因",
    "numerology.suggestions": "更佳替代",
    "numerology.issues": "问题诊断",
    "numerology.personalized": "为您定制",
    "numerology.preferred_digits": "有利数字（用神）",
    "numerology.avoid_digits": "忌讳数字",

    "chart.prevention": "需要避忌",
    "chart.enhancement": "如何增益",
    "chart.colors_favor": "宜穿颜色",
    "chart.colors_avoid": "少用颜色",
    "chart.foods_favor": "宜食",
    "chart.foods_avoid": "忌食",
    "chart.gemstones": "助运宝石",
    "chart.lucky_numbers": "吉数",
    "chart.best_direction": "吉方",
    "chart.best_careers": "事业方向",

    "chat.title": "问师",
    "chat.subtitle":
      "随身八字/风水顾问。读懂您的命盘，用您的语言回答。",
    "chat.chart_context": "命盘依据",
    "chat.no_profile": "不绑定命盘（通用）",
    "chat.new_chat": "+ 新对话",
    "chat.recent": "最近",
    "chat.consulting": "正在翻盘推算……",
    "chat.ask_placeholder":
      "2026年我的事业运如何？卧室该怎么调整？",
    "chat.ask": "问",
    "chat.empty": "请提问——事业、爱情、财运、择日、风水。",
  },
  ms: {
    "nav.dashboard": "Papan Pemuka",
    "nav.profiles": "Profil",
    "nav.numbers": "Nombor",
    "nav.name": "Nama",
    "nav.fengshui": "Feng Shui",
    "nav.compatibility": "Keserasian",
    "nav.chat": "Tanya Sifu",
    "common.signout": "Log keluar",
    "common.free": "PERCUMA",
    "common.premium": "PREMIUM",
    "common.today": "Hari Ini",
    "common.loading": "Memuatkan…",
    "common.save": "Simpan",
    "common.cancel": "Batal",
    "common.language": "Bahasa",

    "numerology.title": "Pemeriksa Nombor",
    "numerology.subtitle":
      "Skor sebarang nombor — telefon, akaun bank, plat kereta, IC, kad kredit. Ikatkan profil untuk panduan peribadi.",
    "numerology.link_profile": "Ikat profil (peribadi)",
    "numerology.select_profile": "Umum (tiada profil)",
    "numerology.type_phone": "Telefon",
    "numerology.type_bank": "Akaun Bank",
    "numerology.type_car": "Plat Kereta",
    "numerology.type_id": "IC",
    "numerology.type_credit": "Kad Kredit",
    "numerology.score": "Skor",
    "numerology.scoring": "Mengira…",
    "numerology.wealth": "Kekayaan",
    "numerology.safety": "Keselamatan",
    "numerology.health": "Kesihatan",
    "numerology.overall": "Keseluruhan",
    "numerology.life_path": "Laluan Hidup",
    "numerology.element_profile": "Profil Unsur",
    "numerology.dominant": "Dominan",
    "numerology.pair_analysis": "Analisis Pasangan Digit",
    "numerology.auspicious": "baik",
    "numerology.inauspicious": "buruk",
    "numerology.why": "Sebab",
    "numerology.suggestions": "Alternatif Lebih Baik",
    "numerology.issues": "Masalah",
    "numerology.personalized": "Khas untuk anda",
    "numerology.preferred_digits": "Digit pilihan (Dewa Berguna)",
    "numerology.avoid_digits": "Digit yang perlu dielakkan",

    "chart.prevention": "Perkara Untuk Dielakkan",
    "chart.enhancement": "Cara Tambah Baik",
    "chart.colors_favor": "Warna Galakan",
    "chart.colors_avoid": "Warna Kurangkan",
    "chart.foods_favor": "Makanan Disyorkan",
    "chart.foods_avoid": "Makanan Dielakkan",
    "chart.gemstones": "Batu Permata Penyokong",
    "chart.lucky_numbers": "Nombor Tuah",
    "chart.best_direction": "Arah Terbaik",
    "chart.best_careers": "Bidang Kerjaya",

    "chat.title": "Tanya Sifu",
    "chat.subtitle":
      "Penasihat Ba Zi / feng shui peribadi. Membaca carta anda dan menjawab dalam bahasa pilihan anda.",
    "chat.chart_context": "Konteks carta",
    "chat.no_profile": "Tiada profil (umum)",
    "chat.new_chat": "+ Chat baru",
    "chat.recent": "Terkini",
    "chat.consulting": "Sifu sedang menyemak carta…",
    "chat.ask_placeholder":
      "Bagaimana nasib kerjaya saya 2026? Apa perlu diubah dalam bilik tidur?",
    "chat.ask": "Tanya",
    "chat.empty": "Tanya soalan — kerjaya, cinta, kewangan, masa, feng shui.",
  },
};

type Ctx = {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string) => string;
};

const I18nContext = createContext<Ctx | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const stored = localStorage.getItem(STORE_KEY) as Lang | null;
    if (stored === "en" || stored === "zh" || stored === "ms") return stored;
    return "en";
  });

  useEffect(() => {
    localStorage.setItem(STORE_KEY, lang);
    document.documentElement.setAttribute("lang", lang === "zh" ? "zh-CN" : lang);
  }, [lang]);

  const t = (key: string): string => translations[lang][key] ?? translations.en[key] ?? key;
  const setLang = (l: Lang) => setLangState(l);

  return <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside I18nProvider");
  return ctx;
}
