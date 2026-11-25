import { FormEvent, useEffect, useState } from "react";
import { LogIn, Sparkles } from "lucide-react";
import { api, ApiError, User } from "../api";
import { useI18n } from "../i18n";
import { Alert } from "../components/ui";

export default function Login({ onSignedIn }: { onSignedIn: (u: User) => void }) {
  const { t, lang, setLang } = useI18n();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [demo, setDemo] = useState(false);
  useEffect(() => { api.get<{ demo: boolean }>("/api/meta").then((m) => setDemo(m.demo)); }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    try { onSignedIn(await api.post<User>("/api/login", { username, password })); }
    catch (x) { setErr(x instanceof ApiError && x.status === 401 ? t("bad_login") : String(x)); }
  }
  async function enterDemo() {
    try { onSignedIn(await api.post<User>("/api/demo")); } catch (x) { setErr(String(x)); }
  }
  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-brand">
          <img src="/mibda_logo_light.svg" alt="" />
          <div><b>مبضع | MIBDA'</b><span className="muted">{t("tagline")}</span></div>
        </div>
        <form className="glass" onSubmit={submit}>
          <div className="row" style={{ justifyContent: "flex-end" }}>
            <button type="button" className={`btn sm ${lang === "en" ? "on" : ""}`} onClick={() => setLang("en")}>English</button>
            <button type="button" className={`btn sm ${lang === "ar" ? "on" : ""}`} onClick={() => setLang("ar")}>العربية</button>
          </div>
          <label className="f">{t("username")}</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
          <label className="f">{t("password")}</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
          {err && <Alert kind="err">{err}</Alert>}
          <div className="row" style={{ marginTop: 18 }}>
            <button className="btn primary" type="submit"><LogIn className="ic" />{t("sign_in")}</button>
            {demo && <button type="button" className="btn" onClick={enterDemo}><Sparkles className="ic" />{t("enter_demo")}</button>}
          </div>
        </form>
        <Alert>{t("edu_notice")}</Alert>
      </div>
    </div>
  );
}
