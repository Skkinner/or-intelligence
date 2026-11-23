// Owner: Member D (WBS 5.1.1)
//
// Pages are AUTO-DISCOVERED: every web/src/pages/<Name>/index.tsx that exports `route` and a default
// component is registered. Member A's Analytics page therefore appears at /analytics without anyone editing
// this file (no shared-file conflicts).
import { useMemo, useState, type ComponentType } from "react";
import { BrowserRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { getLang, setLang, t, availableLangs, type Lang } from "../i18n";

export interface PageRoute {
  path: string;      // e.g. "/analytics" or "/review/:id"
  navKey?: string;   // i18n key for the nav label; omit to hide from the nav
  order?: number;    // nav order
}

interface PageModule {
  default: ComponentType;
  route: PageRoute;
}

const modules = import.meta.glob<PageModule>("../pages/*/index.tsx", { eager: true });
export const pages = Object.values(modules)
  .filter((m) => m.route && m.default)
  .sort((a, b) => (a.route.order ?? 99) - (b.route.order ?? 99));

export function App() {
  const [lang, setLangState] = useState<Lang>(getLang());
  const toggle = useMemo(() => () => {
    const next = availableLangs().find((l) => l !== lang) ?? lang;
    setLang(next);
    setLangState(next);
  }, [lang]);

  return (
    <BrowserRouter>
      <header className="topbar">
        <strong>{t("app.title")}</strong>
        <nav>
          {pages.filter((p) => p.route.navKey).map((p) => (
            <NavLink key={p.route.path} to={p.route.path.replace(/\/:.*$/, "")}>
              {t(p.route.navKey!)}
            </NavLink>
          ))}
        </nav>
        {availableLangs().length > 1 && (
          <button onClick={toggle} aria-label="language">{t("app.switch_language")}</button>
        )}
      </header>
      <main key={lang}>
        <Routes>
          {pages.map((p) => {
            const Page = p.default;
            return <Route key={p.route.path} path={p.route.path} element={<Page />} />;
          })}
          <Route path="*" element={<Navigate to="/upload" replace />} />
        </Routes>
      </main>
      <footer className="disclaimer">{t("app.disclaimer")}</footer>
    </BrowserRouter>
  );
}
