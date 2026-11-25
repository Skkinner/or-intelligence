import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { LayoutGrid, Rows3, Search } from "lucide-react";
import { api, Card } from "../api";
import { CaseCard, Glass, PageHead, Skeleton } from "../components/ui";
import { fmtTime, useI18n } from "../i18n";

export default function Library() {
  const { t, b } = useI18n();
  const [cases, setCases] = useState<Card[] | null>(null);
  const [q, setQ] = useState("");
  const [src, setSrc] = useState("all");
  const [view, setView] = useState<"cards" | "table">("cards");
  useEffect(() => { api.get<Card[]>("/api/cases").then(setCases); }, []);
  const rows = useMemo(() => (cases ?? []).filter((c) => {
    if (src !== "all" && c.source !== src) return false;
    return !q.trim() || `${c.title} ${c.tags}`.toLowerCase().includes(q.trim().toLowerCase());
  }), [cases, q, src]);
  if (!cases) return <div className="stack"><Skeleton h={70} /><Skeleton h={260} /></div>;
  if (cases.length === 0) return <div className="alert">{t("no_cases_start")}</div>;
  return (
    <div className="stack">
      <PageHead title={t("nav_library")} subtitle={t("n_results", { n: rows.length })} />
      <Glass>
        <div className="row">
          <div className="grow" style={{ position: "relative" }}>
            <Search className="ic" style={{ position: "absolute", insetInlineStart: 14, top: 13, color: "var(--muted)" }} />
            <input type="search" style={{ paddingInlineStart: 40 }} placeholder={t("search_hint")} value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <select style={{ width: 210 }} value={src} onChange={(e) => setSrc(e.target.value)}>
            <option value="all">{t("all")}</option>
            <option value="annotations">{t("src_annotations_short")}</option>
            <option value="model">{t("src_model")}</option>
          </select>
          <button className="btn" onClick={() => setView(view === "cards" ? "table" : "cards")}>{view === "cards" ? <Rows3 className="ic" /> : <LayoutGrid className="ic" />}{view === "cards" ? t("view_table") : t("view_cards")}</button>
        </div>
      </Glass>
      {view === "cards" ? (
        <div className="cards">{rows.map((c) => <CaseCard key={c.id} c={c} />)}</div>
      ) : (
        <Glass>
          <div className="tbl-wrap"><table>
            <thead><tr><th>#</th><th>{t("title")}</th><th>{t("duration")}</th><th>{t("source")}</th><th>{t("trainee")}</th><th>{t("tags")}</th><th /></tr></thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td className="num">{c.id}</td><td><b>{c.title}</b><div className="muted small">{b(c.procedure.label)}</div></td><td className="mono">{fmtTime(c.duration)}</td>
                  <td>{c.source === "model" ? t("src_model") : t("src_annotations_short")}</td><td>{c.trainee ?? "-"}</td><td>{c.tags}</td>
                  <td><Link to={`/review/${c.id}`} className="btn sm">{t("open_case")}</Link></td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </Glass>
      )}
    </div>
  );
}
