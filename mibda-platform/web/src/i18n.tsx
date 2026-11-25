import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { api, Bi, Lang } from "./api";

type Dict = Record<string, string>;
interface Ctx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  b: (v: Bi | undefined) => string;
}
const I18n = createContext<Ctx>(null as unknown as Ctx);

export function fmtTime(s: number): string {
  const n = Math.round(Math.max(0, s));
  const h = Math.floor(n / 3600), m = Math.floor((n % 3600) / 60), sec = n % 60;
  const p = (x: number) => String(x).padStart(2, "0");
  return h ? `${h}:${p(m)}:${p(sec)}` : `${p(m)}:${p(sec)}`;
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [strings, setStrings] = useState<Record<string, Dict> | null>(null);
  const [lang, setLangState] = useState<Lang>((localStorage.getItem("lang") as Lang) || "en");
  useEffect(() => { api.get<Record<string, Dict>>("/api/i18n").then(setStrings); }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);
  const value = useMemo<Ctx>(() => ({
    lang,
    setLang: (l) => { localStorage.setItem("lang", l); setLangState(l); },
    t: (key, vars) => {
      let s = strings?.[lang]?.[key] ?? strings?.en?.[key] ?? key;
      if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
      return s;
    },
    b: (v) => (v ? v[lang] || v.en : ""),
  }), [strings, lang]);
  if (!strings) return null;
  return <I18n.Provider value={value}>{children}</I18n.Provider>;
}

export const useI18n = () => useContext(I18n);
