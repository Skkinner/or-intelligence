import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { BrowserRouter, NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Activity, Gauge, Languages, LayoutDashboard, LibraryBig, LogOut, Menu, Radio, Settings as Cog, Stethoscope, X } from "lucide-react";
import { api, ApiError, User } from "./api";
import { useI18n } from "./i18n";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Library from "./pages/Library";
import Review from "./pages/Review";
import Tracker from "./pages/Tracker";
import Live from "./pages/Live";
import Settings from "./pages/Settings";

interface AuthCtx { user: User; signOut: () => Promise<void> }
const Auth = createContext<AuthCtx>(null as unknown as AuthCtx);
export const useAuth = () => useContext(Auth);

function Shell({ user, onSignOut }: { user: User; onSignOut: () => Promise<void> }) {
  const { t, lang, setLang } = useI18n();
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  useEffect(() => setOpen(false), [loc.pathname]);
  const nav = [
    { to: "/", Icon: LayoutDashboard, label: t("nav_dashboard") },
    { to: "/live", Icon: Radio, label: t("nav_live") },
    { to: "/tracker", Icon: Activity, label: t("nav_tracker") },
    { to: "/library", Icon: LibraryBig, label: t("nav_library") },
    { to: "/review", Icon: Stethoscope, label: t("nav_review") },
    { to: "/settings", Icon: Cog, label: t("nav_settings") },
  ];
  return (
    <Auth.Provider value={{ user, signOut: onSignOut }}>
      <div className={`app ${open ? "open" : ""}`}>
        <div className="topbar">
          <button className="btn sm" onClick={() => setOpen(true)} aria-label="Menu"><Menu className="ic" /></button>
          <img src="/mibda_logo_light.svg" alt="" /><b>مبضع | MIBDA'</b>
        </div>
        <div className="scrim" onClick={() => setOpen(false)} />
        <aside className="side">
          <div className="brand">
            <img src="/mibda_logo_dark.svg" alt="" />
            <div><b>مبضع | MIBDA'</b></div>
            <button className="btn sm" style={{ marginInlineStart: "auto", display: open ? "inline-flex" : "none" }} onClick={() => setOpen(false)} aria-label="Close"><X className="ic" /></button>
          </div>
          <nav className="nav">
            {nav.map(({ to, Icon, label }) => (
              <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive || (to === "/review" && loc.pathname.startsWith("/review")) ? "active" : "")}>
                <Icon className="ic" />{label}
              </NavLink>
            ))}
          </nav>
          <div className="side-foot">
            <div className="profile">
              <span className="avatar">{user.display_name.slice(0, 1).toUpperCase()}</span>
              <div><b>{user.display_name}</b><span>{t("role_" + user.role)}</span></div>
            </div>
            <div className="row">
              <button className="btn sm" onClick={() => setLang(lang === "en" ? "ar" : "en")}><Languages className="ic" />{lang === "en" ? "العربية" : "English"}</button>
              <button className="btn sm" onClick={onSignOut}><LogOut className="ic" />{t("sign_out")}</button>
            </div>
          </div>
        </aside>
        <main className="main" key={loc.pathname.split("/")[1]}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live" element={<Live />} />
            <Route path="/tracker" element={<Tracker />} />
            <Route path="/library" element={<Library />} />
            <Route path="/review" element={<Review />} />
            <Route path="/review/:id" element={<Review />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Auth.Provider>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  useEffect(() => {
    api.get<User>("/api/me").then(setUser).catch((e) => { if (e instanceof ApiError) setUser(null); });
  }, []);
  const signOut = useCallback(async () => { await api.post("/api/logout"); setUser(null); }, []);
  if (user === undefined) return null;
  return (
    <BrowserRouter>
      {user ? <Shell user={user} onSignOut={signOut} /> : <Login onSignedIn={setUser} />}
    </BrowserRouter>
  );
}

export { Gauge };
