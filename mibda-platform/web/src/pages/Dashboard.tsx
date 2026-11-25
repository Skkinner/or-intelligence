import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Clock, Film, Layers, LineChart, ScanSearch, Stethoscope, Target } from "lucide-react";
import { api, Bi, Card } from "../api";
import { useAuth } from "../App";
import { AreaChart, Donut, HBars } from "../components/charts";
import { CaseCard, Glass, Hero, Metrics, Skeleton } from "../components/ui";
import { fmtTime, useI18n } from "../i18n";

interface Data {
  kpis: { cases: number; total_duration: number; phased: number; procedures_ready: number; procedures_total: number };
  recent: Card[];
  usage: { name: Bi; color: string; seconds: number }[];
  phase_defs: Record<string, { name: Bi; color: string }[]>;
  phase_totals: Record<string, number[]>;
  series: { id: number; duration: number; entries_per_min: number | null; instrument_entries: number | null }[];
  phase_accuracy: number | null;
  detector_metrics: Record<string, unknown> | null;
  detector: { weights: string; available: boolean; classes: string[] };
}

export default function Dashboard() {
  const { t, b } = useI18n();
  const { user } = useAuth();
  const [d, setD] = useState<Data | null>(null);
  useEffect(() => { api.get<Data>("/api/dashboard").then(setD); }, []);
  if (!d) return <div className="stack"><Skeleton h={150} /><Skeleton h={90} /><Skeleton h={220} /></div>;
  const k = d.kpis;
  const totalUse = d.usage.reduce((a, u) => a + u.seconds, 0);
  // the procedure with the most phase time drives the phase donut (real totals across the library)
  const pid = Object.entries(d.phase_totals).sort((x, y) => y[1].reduce((a, c) => a + c, 0) - x[1].reduce((a, c) => a + c, 0))[0]?.[0];
  const defs = pid ? d.phase_defs[pid] : [];
  const phaseSegs = pid ? d.phase_totals[pid].map((v, i) => ({ label: b(defs[i]?.name), value: v, color: defs[i]?.color ?? "#CD7F32" })).filter((s) => s.value > 0) : [];
  const phaseTotal = phaseSegs.reduce((a, s) => a + s.value, 0);
  const epm = d.series.filter((s) => s.entries_per_min != null).map((s) => ({ label: `#${s.id}`, value: s.entries_per_min as number, tip: `#${s.id} · ${s.entries_per_min} / min · ${s.instrument_entries} ${t("entries")}` }));
  const durations = d.series.map((s) => ({ label: `#${s.id}`, value: Math.round(s.duration / 60 * 10) / 10, tip: `#${s.id} · ${fmtTime(s.duration)}` }));

  return (
    <div className="stack">
      <Hero title={t("welcome", { name: user.display_name })} subtitle={t("dash_sub")} chips={
        <div className="row" style={{ position: "relative" }}>
          <Link to="/tracker" className="btn" style={{ background: "#fff" }}><Activity className="ic" />{t("nav_tracker")}</Link>
          <Link to="/live" className="btn" style={{ background: "rgba(255,255,255,.16)", color: "#fff", borderColor: "rgba(255,255,255,.35)" }}><ScanSearch className="ic" />{t("nav_live")}</Link>
        </div>} />

      <Metrics items={[
        { label: t("cases"), value: String(k.cases), hint: t("kpi_cases_hint"), icon: Film, tone: "dark" },
        { label: t("total_duration"), value: fmtTime(k.total_duration), hint: t("kpi_time_hint"), icon: Clock },
        { label: t("kpi_phased"), value: String(k.phased), hint: t("kpi_phased_hint"), icon: Layers, tone: "copper" },
        { label: t("kpi_procedures"), value: `${k.procedures_ready} / ${k.procedures_total}`, hint: t("kpi_procedures_hint"), icon: Stethoscope },
      ]} />

      <div className="grid g-12">
        <Glass className="span-7" hover title={t("usage_all")} subtitle={t("live_instruments_now")} icon={Target}>
          {totalUse > 0 ? <HBars bars={d.usage.map((u) => ({ label: b(u.name), value: u.seconds, color: u.color, right: `${(u.seconds / 60).toFixed(1)} ${t("minutes")}` }))} /> : <p className="muted">{t("no_instrument_labels")}</p>}
        </Glass>

        <Glass className="span-5" hover title={t("phases_title")} subtitle={t("time_per_phase")} icon={Layers}>
          {phaseSegs.length ? (
            <div className="donut-wrap">
              <Donut segs={phaseSegs} center={fmtTime(phaseTotal)} centerSub={t("total_duration")} size={150} />
              <div className="legend" style={{ flexDirection: "column", flex: 1, minWidth: 140, marginTop: 0 }}>
                {phaseSegs.map((s) => <span key={s.label}><i style={{ background: s.color }} />{s.label} · {Math.round((100 * s.value) / phaseTotal)}%</span>)}
              </div>
            </div>
          ) : <p className="muted">{t("phases_none")}</p>}
        </Glass>

        <Glass className="span-12" hover title={t("per_min")} subtitle={t("entries")} icon={LineChart}>
          {epm.length >= 2 ? <AreaChart data={epm} unit=" / min" /> : durations.length >= 2 ? <AreaChart data={durations} unit=" min" /> : <p className="muted">{t("reference_needs_cases")}</p>}
        </Glass>
      </div>

      {d.recent.length > 0 ? (
        <>
          <h2 style={{ marginTop: 10 }}>{t("recent_cases")}</h2>
          <div className="cards">{d.recent.map((c) => <CaseCard key={c.id} c={c} />)}</div>
        </>
      ) : <div className="alert">{t("no_cases_start")}</div>}
    </div>
  );
}
