// Owner: Member D (WBS 5.1.1)
//
// Locale files are AUTO-DISCOVERED: any web/src/i18n/<lang>.json is loaded, so Member A adds ar.json
// without editing this file. Arabic switches <html dir="rtl">; web/src/styles/rtl.css (Member A) is loaded
// if it exists.
import en from "./en.json";

export type Lang = string;
type Dict = Record<string, string>;

const files = import.meta.glob<{ default: Dict }>("./*.json", { eager: true });
const dicts: Record<Lang, Dict> = {};
for (const [path, mod] of Object.entries(files)) {
  const lang = path.replace("./", "").replace(".json", "");
  dicts[lang] = mod.default;
}

// Optional RTL stylesheet owned by Member A. Loading it via glob means "no file" is not a build error.
import.meta.glob("../styles/*.css", { eager: true });

const RTL_LANGS = new Set(["ar"]);
const STORAGE_KEY = "ori-lang";

let current: Lang = readStoredLang();

function readStoredLang(): Lang {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && dicts[stored]) return stored;
  } catch {
    /* storage unavailable */
  }
  return "en";
}

export function availableLangs(): Lang[] {
  return Object.keys(dicts).sort();
}

export function getLang(): Lang {
  return current;
}

export function setLang(lang: Lang): void {
  if (!dicts[lang]) return;
  current = lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = RTL_LANGS.has(lang) ? "rtl" : "ltr";
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* ignore */
  }
}

/** Translate a key; falls back to English, then to the key itself. */
export function t(key: string, vars: Record<string, string | number> = {}): string {
  const raw = dicts[current]?.[key] || (en as Dict)[key] || key;
  return raw.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? `{${k}}`));
}

setLang(current);
