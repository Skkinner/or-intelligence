import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Bot, BookOpen, Clock, Crosshair, Download, FileText, Gauge, Layers, MessageSquare, NotebookPen, ScanSearch, Trash2, Workflow } from "lucide-react";
import { api, Card, Detail } from "../api";
import { useAuth } from "../App";
import { AssistantTab, ReportTab, ResourcesTab } from "../components/ai";
import { HBars } from "../components/charts";
import { PhaseTimeline } from "../components/PhaseTimeline";
import { Chip, Glass, Metrics, PageHead, Skeleton } from "../components/ui";
import { phaseAt, PhaseList, Player, SPEEDS, Timeline } from "../components/review";
import { fmtTime, useI18n } from "../i18n";

type Tab = "usage" | "notes" | "export" | "report" | "resources" | "assistant";

export default function Review() {
  const { t, lang, b } = useI18n();
  const nav = useNavigate();
  const params = useParams();
  const [cases, setCases] = useState<Card[]>([]);
  const [d, setD] = useState<Detail | null>(null);
  const [time, setTime] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [tab, setTab] = useState<Tab>("usage");
  const [err, setErr] = useState("");

  useEffect(() => { api.get<Card[]>("/api/cases").then(setCases); }, []);
  const id = params.id ? Number(params.id) : cases[0]?.id;
  const load = useCallback(() => {
    if (!id) return;
    api.get<Detail>(`/api/cases/${id}`).then((x) => { setD(x); setErr(""); }).catch((e) => setErr(String(e.message ?? e)));
  }, [id]);
  useEffect(() => { setD(null); setTime(0); load(); }, [load]);

  // detection statistics over the whole case, from the stored model predictions (nothing is invented)
  const stats = useMemo(() => {
    if (!d || !d.procedure.instruments.length) return [];
    return d.procedure.instruments.map((ins, i) => {
      let frames = 0, sum = 0, n = 0;
      for (const f of d.frames) {
        const bx = f.boxes.filter((x) => x[0] === i);
        if (bx.length) { frames += 1; bx.forEach((x) => { sum += x[5]; n += 1; }); }
      }
      return { i, name: b(ins.name), color: ins.color, presence: d.frames.length ? (100 * frames) / d.frames.length : 0, conf: n ? sum / n : null };
    });
  }, [d, lang]);

  if (!cases.length && !id) return <div className="alert">{t("no_cases")}</div>;
  if (err) return <div className="alert err">{err}</div>;
  const select = (
    <div className="row">
      <label className="f" style={{ margin: 0 }}>{t("case")}</label>
      <select style={{ maxWidth: 440 }} value={id ?? ""} onChange={(e) => nav(`/review/${e.target.value}`)}>
        {cases.map((c) => <option key={c.id} value={c.id}>#{c.id} · {c.title}</option>)}
      </select>
    </div>
  );
  if (!d) return <div className="stack">{select}<Skeleton h={80} /><Skeleton h={320} /></div>;
  const cur = phaseAt(d.phases, time);
  const hasInstr = d.procedure.instruments.length > 0;
  const frame = d.frames.length ? d.frames.reduce((best, f) => (Math.abs(f.t - time) < Math.abs(best.t - time) ? f : best), d.frames[0]) : null;
  const nowConf = frame && frame.boxes.length ? frame.boxes.reduce((a, x) => a + x[5], 0) / frame.boxes.length : null;
  const tabs: { k: Tab; label: string; Icon: typeof Bot }[] = [
    { k: "usage", label: t("tab_usage"), Icon: Gauge }, { k: "notes", label: t("tab_notes"), Icon: NotebookPen }, { k: "export", label: t("tab_export"), Icon: FileText },
    { k: "report", label: t("tab_report"), Icon: Bot }, { k: "resources", label: t("tab_resources"), Icon: BookOpen },
  ];
  if (d.can_ai) tabs.push({ k: "assistant", label: t("tab_assistant"), Icon: MessageSquare });
  const maxUse = Math.max(1, ...d.usage.map((u) => u.active_seconds));

  return (
    <div className="stack">
      {select}
      <PageHead title={d.case.title} subtitle={b(d.procedure.label)} actions={<>
        <Chip kind={d.case.source === "model" ? "ok" : "warn"}>{d.case.source === "model" ? t("src_model") : t("src_annotations")}</Chip>
        {!d.dense && <span className="muted small">{t("sparse_notice")}</span>}
      </>} />

      <Metrics items={hasInstr ? [
        { label: t("duration"), value: fmtTime(d.duration), icon: Clock, tone: "dark" },
        { label: t("entries"), value: String(d.metrics.instrument_entries), icon: Crosshair },
        { label: t("per_min"), value: String(d.metrics.entries_per_min), icon: Gauge, tone: "copper" },
        { label: t("instruments_used"), value: String(d.metrics.instruments_used), icon: ScanSearch },
      ] : [
        { label: t("duration"), value: fmtTime(d.duration), icon: Clock, tone: "dark" },
        { label: t("kpi_phased"), value: String(new Set(d.phases.map((p) => p.phase)).size), icon: Layers, tone: "copper" },
      ]} />

      <div className="viewer">
        <div>
          <Player d={d} t={time} onTime={setTime} speed={speed} />
          <div className="row" style={{ marginTop: 10 }}>
            <span className="muted small">{t("speed")}</span>
            {SPEEDS.map((s) => <button key={s} className={`btn sm ${s === speed ? "on" : ""}`} onClick={() => setSpeed(s)}>{s}x</button>)}
          </div>
        </div>
        <div className="stack">
          <Glass className="now-card" tone="dark" title={t("now") + " · " + fmtTime(time)} icon={Workflow}>
            <div className="small muted">{t("phase")}</div>
            <div className="big">{cur ? b(d.procedure.phases[cur.phase]?.name) : "-"}</div>
            {cur && !cur.verified && <Chip kind="warn">{cur.uncertain ? t("phase_uncertain") : t("phase_estimated")}{cur.conf != null ? ` · ${Math.round(100 * cur.conf)}%` : ""}</Chip>}
            {cur && cur.verified && <Chip kind="good">{t("phase_verified")}</Chip>}
            {hasInstr && <>
              <div className="small muted" style={{ marginTop: 10 }}>{t("visible_now")}</div>
              <div>{frame && frame.boxes.length ? [...new Set(frame.boxes.map((x) => x[0]))].map((i) => <span key={i} className="chip" style={{ background: "rgba(255,255,255,.12)", color: "#fff", borderColor: "rgba(255,255,255,.25)" }}><i className="sw" style={{ background: d.procedure.instruments[i].color, margin: 0 }} />{b(d.procedure.instruments[i].name)}</span>) : <span className="muted">-</span>}</div>
              {nowConf != null && <div className="small muted" style={{ marginTop: 6 }}>{t("live_conf")}: <b className="num" style={{ color: "#fff" }}>{nowConf.toFixed(2)}</b></div>}
            </>}
          </Glass>
          {hasInstr && stats.some((s) => s.presence > 0) && (
            <Glass title={t("live_instr_seen")} subtitle={t("live_conf")} icon={ScanSearch}>
              <HBars max={100} bars={stats.filter((s) => s.presence > 0).map((s) => ({ label: s.name, value: s.presence, color: s.color, right: `${Math.round(s.presence)}%${s.conf != null && s.conf < 1 ? ` · ${s.conf.toFixed(2)}` : ""}` }))} />
            </Glass>
          )}
        </div>
      </div>

      <Glass title={t("phases_title")} subtitle={t("timeline_hint")} icon={Layers}>
        {d.phases.length ? <PhaseTimeline d={d} t={time} onSeek={setTime} /> : <p className="muted">{t("phases_none")}</p>}
      </Glass>
      {hasInstr && <Timeline d={d} t={time} onSeek={setTime} />}

      <Glass title={t("phases_title")} icon={Workflow}><PhaseList d={d} t={time} onSeek={setTime} /></Glass>

      <div className="tabs" role="tablist">
        {tabs.map(({ k, label, Icon }) => <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}><Icon className="ic" />{label}</button>)}
      </div>

      <div className="panel-in" key={tab}>
        {tab === "usage" && (!hasInstr ? <div className="alert">{t("no_instrument_labels")}</div> : (
          <div className="grid g-12">
            <Glass className="span-5" title={t("tab_usage")} subtitle={t("active_seconds")} icon={Gauge}>
              <HBars bars={d.usage.map((u, i) => ({ label: b(d.procedure.instruments[i]?.name), value: u.active_seconds, color: d.procedure.instruments[i]?.color, right: `${Math.round(u.active_seconds)} s` }))} max={maxUse} />
            </Glass>
            <Glass className="span-7" title={t("instrument")} icon={ScanSearch}>
              <div className="tbl-wrap"><table>
                <thead><tr><th>{t("instrument")}</th><th>{t("active_seconds")}</th><th>{t("pct_of_case")}</th><th>{t("segments")}</th><th>{t("first_use")}</th><th>{t("last_use")}</th><th>{t("longest")}</th></tr></thead>
                <tbody>{d.usage.map((u, i) => (
                  <tr key={i}><td><i className="sw" style={{ background: d.procedure.instruments[i]?.color }} />{b(d.procedure.instruments[i]?.name)}</td><td className="num">{u.active_seconds}</td><td>{u.pct_of_case}</td><td>{u.segments}</td>
                    <td className="mono">{u.first_use != null ? fmtTime(u.first_use) : "-"}</td><td className="mono">{u.last_use != null ? fmtTime(u.last_use) : "-"}</td><td>{u.longest_segment}</td></tr>
                ))}</tbody>
              </table></div>
            </Glass>
          </div>
        ))}
        {tab === "notes" && <Notes d={d} time={time} onSeek={setTime} reload={load} />}
        {tab === "export" && (
          <Glass title={t("tab_export")} subtitle={t("pdf_lang_fallback")} icon={FileText}>
            <a href={`/api/cases/${d.case.id}/export.pdf?lang=${lang}`} download className="btn primary"><Download className="ic" />{t("make_pdf")}</a>
          </Glass>
        )}
        {tab === "report" && <ReportTab d={d} now={time} />}
        {tab === "resources" && <ResourcesTab d={d} />}
        {tab === "assistant" && <AssistantTab d={d} />}
      </div>
    </div>
  );
}

function Notes({ d, time, onSeek, reload }: { d: Detail; time: number; onSeek: (t: number) => void; reload: () => void }) {
  const { t } = useI18n();
  const { user } = useAuth();
  const [text, setText] = useState("");
  const add = async () => {
    if (!text.trim()) return;
    await api.post(`/api/cases/${d.case.id}/notes`, { t: time, text });
    setText("");
    reload();
  };
  return (
    <Glass title={t("tab_notes")} icon={NotebookPen}>
      <label className="f">{t("note_at", { t: fmtTime(time) })}</label>
      <textarea rows={3} value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ marginTop: 10 }}><button className="btn primary" onClick={add} disabled={!text.trim()}>{t("add_note")}</button></div>
      <div className="tbl-wrap" style={{ marginTop: 14 }}><table>
        <tbody>
          {d.notes.map((n) => (
            <tr key={n.id}>
              <td className="mono">{fmtTime(n.t)}</td><td><b>{n.author}</b>: {n.text}</td>
              <td><button className="btn sm" onClick={() => onSeek(n.t)}>{t("go")}</button></td>
              <td>{(user.role === "admin" || n.author_id === user.id) && <button className="btn sm" aria-label="Delete" onClick={async () => { await api.del(`/api/cases/${d.case.id}/notes/${n.id}`); reload(); }}><Trash2 className="ic" /></button>}</td>
            </tr>
          ))}
        </tbody>
      </table></div>
    </Glass>
  );
}
