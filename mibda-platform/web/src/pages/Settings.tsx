import { useEffect, useState } from "react";
import { Languages, LogOut, ShieldCheck, UserRound } from "lucide-react";
import { api } from "../api";
import { useAuth } from "../App";
import { Alert, Glass, PageHead } from "../components/ui";
import { useI18n } from "../i18n";

export default function Settings() {
  const { t, lang, setLang } = useI18n();
  const { user, signOut } = useAuth();
  const [meta, setMeta] = useState<{ ai: { ok: boolean; reason: string } } | null>(null);
  useEffect(() => { api.get<{ ai: { ok: boolean; reason: string } }>("/api/meta").then(setMeta); }, []);
  const why: Record<string, string> = { not_approved: "ai_off_not_approved", no_key: "ai_off_no_key", no_package: "ai_off_no_package" };
  return (
    <div className="stack" style={{ maxWidth: 760 }}>
      <PageHead title={t("nav_settings")} />
      <Glass title={t("language")} icon={Languages}>
        <div className="row">
          <button className={`btn ${lang === "en" ? "on" : ""}`} onClick={() => setLang("en")}>English</button>
          <button className={`btn ${lang === "ar" ? "on" : ""}`} onClick={() => setLang("ar")}>العربية</button>
        </div>
      </Glass>
      <Glass title={user.display_name} subtitle={t("role_" + user.role)} icon={UserRound}>
        <button className="btn" onClick={signOut}><LogOut className="ic" />{t("sign_out")}</button>
      </Glass>
      {meta && (
        <Glass title="AI" icon={ShieldCheck}>
          {meta.ai.ok ? <Alert>{t("ai_privacy_note")}</Alert> : <Alert kind="warn">{t(why[meta.ai.reason] ?? "ai_off_no_key")}</Alert>}
        </Glass>
      )}
    </div>
  );
}
