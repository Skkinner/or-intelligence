import { useEffect, useMemo, useState } from "react";
import { Activity, Clock, Flame, Layers, RotateCcw, Table2 } from "lucide-react";
import { api, Card, Detail } from "../api";
import { HBars } from "../components/charts";
import { PhaseTimeline } from "../components/PhaseTimeline";
import { Alert, Chip, Glass, PageHead, Skeleton } from "../components/ui";
import { phaseAt, phaseStatus, Player, SPEEDS } from "../components/review";
import { fmtTime, useI18n } from "../i18n";

interface Analytics {
  time_per_phase: number[]; library_median: number[] | null; library_n: number; heatmap: number[][];
  rows: { phase: number; start: number; end: number; conf: number | null; verified: boolean; uncertain: boolean; main_instruments: number[] }[];
}

/** Where the operation is, phase by phase, with playback. Phase boundaries come from the case (annotations or estimator). */
export default function Tracker() {
  const { t, b } = useI18n();
  const [cases, setCases] = useState<Card[]>([]);
  const [id, setId] = useState<number | null>(null);
  const [d, setD] = useState<Detail | null>(null);
  const [time, setTime] = useState(0);
  const [speed, setSpeed] = useState(4);
  const [an, setAn] = useState<Analytics | null>(null);

  useEffect(() => { api.get<Card[]>("/api/cases").then((c) => { setCases(c); if (c.length) setId(c[0].id); }); }, []);
  useEffect(() => { if (id) { setD(null); setAn(null); setTime(0); api.get<Detail>(`/api/cases/${id}`).then(setD); api.get<Analytics>(`/api/cases/${id}/analytics`).then(setAn); } }, [id]);
  const cur = useMemo(() => {
    if (!d) return null;
    for (const p of d.phases) if (time >= p.start && time < p.end) return p;
    return d.phases.length && time >= d.phases[d.phases.length - 1].end ? d.phases[d.phases.length - 1] : null;
  }, [d, time]);
  const frame = useMemo(() => d?.frames.reduce((best, f) => (Math.abs(f.t - time) < Math.abs(best.t - time) ? f : best), d.frames[0]), [d, time]);

  if (!cases.length) return <div className="alert">{t("no_cases")}</div>;
  const select = (
    <div className="row">
      <label className="f" style={{ margin: 0 }}>{t("case")}</label>
      <select style={{ maxWidth: 440 }} value={id ?? ""} onChange={(e) => setId(Number(e.target.value))}>
        {cases.map((c) => <option key={c.id} value={c.id}>#{c.id} · {c.title}</option>)}
      </select>
    </div>
  );
  if (!d) return <div className="stack">{select}<Skeleton h={90} /><Skeleton h={320} /></div>;
  if (!d.phases.length) return <div className="stack">{select}<Alert kind="warn">{t("no_phase_source")}</Alert></div>;

  const idx = cur ? d.phases.indexOf(cur) : -1;
  const inPhase = cur ? Math.max(0, time - cur.start) : 0;
  const present = [...new Set((frame?.boxes ?? []).map((x) => x[0]))];
  const total = d.duration || 1;
  const hasInstr = d.procedure.instruments.length > 0;
  const estimated = d.phases.some((p) => !p.verified);

  return (
    <div className="stack">
      {select}
      <PageHead title={d.case.title} subtitle={t("tracker_sub")} actions={<>
        <Chip kind="ok">{b(d.procedure.label)}</Chip>
        <Chip kind={estimated ? "warn" : "good"}>{estimated ? t("ps_estimated") : t("ps_annotation")}</Chip>
      </>} />
      {estimated && <Alert kind="warn">{t("phases_estimated_warning")}</Alert>}

      <div className="steps">
        {d.phases.map((p, i) => {
          const def = d.procedure.phases[p.phase];
          const state = i < idx ? "done" : i === idx ? "active" : "";
          return (
            <button key={i} className={`step ${state}`} onClick={() => setTime(p.start)}>
              <div className="n">{String(i + 1).padStart(2, "0")}</div>
              <div className="nm">{b(def?.name)}</div>
              <div className="tm">{fmtTime(p.end - p.start)}{!p.verified ? " ≈" : ""}</div>
            </button>
          );
        })}
      </div>

      <div className="viewer">
        <div>
          <Player d={d} t={time} onTime={setTime} speed={speed} />
          <div className="row" style={{ marginTop: 10 }}>
            <button className="btn sm" onClick={() => setTime(0)}><RotateCcw className="ic" />{t("restart")}</button>
            <span className="muted small">{t("speed")}</span>
            {SPEEDS.map((s) => <button key={s} className={`btn sm ${s === speed ? "on" : ""}`} onClick={() => setSpeed(s)}>{s}x</button>)}
          </div>
        </div>
        <Glass className="now-card" tone="dark" title={t("current_phase")} icon={Activity}>
          <div className="big">{cur ? b(d.procedure.phases[cur.phase]?.name) : "-"}</div>
          {cur && <div className="small muted">{phaseStatus(cur, t)}</div>}
          <div style={{ margin: "14px 0 4px" }}>{t("now")}: <b className="num">{fmtTime(time)}</b> / {fmtTime(d.duration)}</div>
          <div className="progress" style={{ background: "rgba(255,255,255,.15)" }}><span style={{ width: `${Math.min(100, (100 * time) / total)}%` }} /></div>
          {cur && <div className="small">{fmtTime(inPhase)} / {fmtTime(cur.end - cur.start)} · {t("phase_col_dur")}</div>}
          {present.length > 0 && <div className="small" style={{ marginTop: 10 }}><span className="muted">{t("visible_now")}: </span>{present.map((i) => b(d.procedure.instruments[i]?.name)).join(", ")}</div>}
        </Glass>
      </div>

      <Glass title={t("phases_title")} subtitle={t("timeline_hint")} icon={Layers}><PhaseTimeline d={d} t={time} onSeek={setTime} /></Glass>

      {an && (
        <div className="grid g-12">
          <Glass className={hasInstr ? "span-6" : "span-12"} title={t("time_per_phase")} subtitle={an.library_median ? t("library_median", { n: an.library_n }) : t("reference_needs_cases")} icon={Clock}>
            <HBars bars={d.procedure.phases.map((p, i) => ({ label: b(p.name), value: an.time_per_phase[i], color: p.color, right: `${fmtTime(an.time_per_phase[i])}${an.library_median ? ` · ${fmtTime(an.library_median[i])}` : ""}` }))}
              max={Math.max(1, ...an.time_per_phase, ...(an.library_median ?? [0]))} />
          </Glass>
          {hasInstr && (
            <Glass className="span-6" title={t("tool_phase_heatmap")} subtitle={t("heatmap_hint")} icon={Flame}>
              <div className="heat" style={{ gridTemplateColumns: `84px repeat(${d.procedure.phases.length}, 1fr)` }}>
                <span />{d.procedure.phases.map((_, i) => <span key={i} className="c muted">{i + 1}</span>)}
                {d.procedure.instruments.map((ins, r) => (
                  <div key={r} style={{ display: "contents" }}>
                    <span className="small" style={{ alignSelf: "center" }}>{b(ins.name)}</span>
                    {d.procedure.phases.map((_, c) => {
                      const v = an.heatmap[r]?.[c] ?? 0;
                      return <span key={c} className="c" title={`${v.toFixed(0)}%`} style={{ background: `rgba(92,6,28,${(v / 100) * 0.9 + 0.04})`, color: v > 45 ? "#fff" : "var(--ink)" }}>{Math.round(v)}</span>;
                    })}
                  </div>
                ))}
              </div>
            </Glass>
          )}
          <Glass className="span-12" title={t("phase")} icon={Table2}>
            <div className="tbl-wrap"><table>
              <thead><tr><th>{t("phase")}</th><th>{t("start")}</th><th>{t("end")}</th><th>{t("duration")}</th><th>{t("phase_source")}</th>{hasInstr && <th>{t("main_instruments")}</th>}<th /></tr></thead>
              <tbody>
                {an.rows.map((r, i) => (
                  <tr key={i} className={cur && r.start === cur.start ? "cur" : ""}>
                    <td><i className="sw" style={{ background: d.procedure.phases[r.phase]?.color }} />{b(d.procedure.phases[r.phase]?.name)}</td>
                    <td className="mono">{fmtTime(r.start)}</td><td className="mono">{fmtTime(r.end)}</td><td>{fmtTime(r.end - r.start)}</td>
                    <td className="small">{phaseStatus(r, t)}</td>
                    {hasInstr && <td>{r.main_instruments.map((k) => b(d.procedure.instruments[k]?.name)).join(", ")}</td>}
                    <td><button className="btn sm" onClick={() => setTime(r.start)}>{t("go")}</button></td>
                  </tr>
                ))}
              </tbody>
            </table></div>
          </Glass>
        </div>
      )}
    </div>
  );
}
