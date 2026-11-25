import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Clock, Crosshair, Film, Layers, Save, SlidersHorizontal, Square, Upload, Zap } from "lucide-react";
import { api, ApiError, Detail, Phase } from "../api";
import { Boxes, Timeline } from "../components/review";
import { PhaseTimeline } from "../components/PhaseTimeline";
import { Alert, Chip, Glass, Metrics, PageHead, Spinner } from "../components/ui";
import { fmtTime, useI18n } from "../i18n";

interface Info { ready: boolean; procedure: Detail["procedure"]; has_phase_model: boolean; samples: string[]; retention_days: number }
interface Snap {
  id: string; status: "running" | "done" | "stopped" | "error"; error: string; duration: number; n_frames: number; progress: number;
  latest: { t: number; phase: number | null; boxes: number[][]; seq: number } | null; seen: number[]; phase: number | null; seconds: number;
  name: string; saved_case: number | null; instruments_seen?: number[];
  chart?: { intervals: Detail["intervals"]; phases: Phase[] };
}

export default function Live() {
  const { t, b } = useI18n();
  const [info, setInfo] = useState<Info | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [sample, setSample] = useState("");
  const [rate, setRate] = useState(3);
  const [conf, setConf] = useState(0.25);
  const [snap, setSnap] = useState<Snap | null>(null);
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");
  const [title, setTitle] = useState("");
  const [consent, setConsent] = useState(false);
  const [saveMsg, setSaveMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const jobRef = useRef<string | null>(null);

  useEffect(() => { api.get<Info>("/api/live/info").then(setInfo); }, []);

  // poll while the analysis runs, so the page updates as results arrive
  useEffect(() => {
    if (!snap || snap.status !== "running") return;
    const h = setInterval(async () => {
      try { const s = await api.get<Snap>(`/api/live/${snap.id}`); if (jobRef.current === s.id) setSnap(s); }
      catch (e) { setErr(e instanceof ApiError ? e.message : String(e)); }
    }, 500);
    return () => clearInterval(h);
  }, [snap?.id, snap?.status]);

  if (!info) return null;
  const proc = info.procedure;
  const running = snap?.status === "running";

  async function start() {
    setErr(""); setSaveMsg(null); setSnap(null); setConsent(false);
    try {
      let body: Record<string, unknown> = { rate, conf };
      if (file) {
        setBusy("upload");
        const up = await fetch(`/api/live/upload?name=${encodeURIComponent(file.name)}`, { method: "POST", credentials: "same-origin", body: file });
        if (!up.ok) throw new ApiError(up.status, (await up.json().catch(() => ({ detail: up.statusText }))).detail);
        const u = await up.json();
        body = { ...body, token: u.token, name: u.name };
        setTitle(u.name);
      } else { body = { ...body, sample }; setTitle(sample); }
      const { id } = await api.post<{ id: string }>("/api/live/start", body);
      jobRef.current = id;
      setSnap(await api.get<Snap>(`/api/live/${id}`));
    } catch (e) { setErr(e instanceof ApiError ? e.message : String(e)); } finally { setBusy(""); }
  }
  async function stop() { if (snap) await api.post(`/api/live/${snap.id}/stop`); }
  async function save() {
    if (!snap) return;
    try { const r = await api.post<{ case_id: number }>(`/api/live/${snap.id}/save`, { title, consent }); setSaveMsg({ ok: true, text: t("live_saved", { id: r.case_id }) }); setSnap({ ...snap, saved_case: r.case_id }); }
    catch (e) { setSaveMsg({ ok: false, text: e instanceof ApiError && e.status === 422 ? t("live_need_consent") : String(e) }); }
  }

  const latest = snap?.latest;
  const active = [...new Set((latest?.boxes ?? []).map((x) => x[0]))];
  const phase = snap?.phase ?? null;
  const chartD = snap?.chart ? ({ procedure: proc, intervals: snap.chart.intervals, phases: snap.chart.phases, duration: snap.duration || 1 } as unknown as Detail) : null;
  const finished = snap && snap.status !== "running" && snap.status !== "error";
  const status = running ? { label: "LIVE", cls: "live" } : snap?.status === "done" ? { label: t("live_frames"), cls: "" } : null;

  return (
    <div className="stack">
      <PageHead title={t("live_title")} subtitle={t("live_sub")} actions={running && <Chip kind="warn"><span className="spin" style={{ margin: 0 }} />{snap?.n_frames} · {Math.round(100 * (snap?.progress ?? 0))}%</Chip>} />

      {!info.ready ? <Alert kind="warn">{t("live_need_weights")}</Alert> : (
        <Glass title={t("live_start")} subtitle={t("live_sub")} icon={SlidersHorizontal}>
          <div className="row">
            <div className="grow">
              <label className="f"><Upload className="ic" style={{ verticalAlign: "-2px" }} /> {t("video_file")}</label>
              <input type="file" accept=".mp4,.mov,.avi,.mkv" disabled={running} onChange={(e) => { setFile(e.target.files?.[0] ?? null); setSample(""); }} />
            </div>
            {info.samples.length > 0 && (
              <div className="grow">
                <label className="f"><Film className="ic" style={{ verticalAlign: "-2px" }} /> {t("live_sample")}</label>
                <select value={sample} disabled={running || !!file} onChange={(e) => setSample(e.target.value)}>
                  <option value="">-</option>
                  {info.samples.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            )}
          </div>
          <div className="row">
            <div className="grow"><label className="f">{t("live_rate")} · {rate}</label><input type="range" min={1} max={8} step={0.5} value={rate} disabled={running} onChange={(e) => setRate(Number(e.target.value))} style={{ width: "100%" }} /></div>
            <div className="grow"><label className="f">{t("live_conf")} · {conf.toFixed(2)}</label><input type="range" min={0.1} max={0.9} step={0.05} value={conf} disabled={running} onChange={(e) => setConf(Number(e.target.value))} style={{ width: "100%" }} /></div>
          </div>
          <div className="row" style={{ marginTop: 16 }}>
            <button className="btn primary" disabled={running || !!busy || !(file || sample)} onClick={start}><Zap className="ic" />{t("live_start")}</button>
            {running && <button className="btn" onClick={stop}><Square className="ic" />{t("pause")}</button>}
            {busy === "upload" && <Spinner label={t("video_file")} />}
          </div>
        </Glass>
      )}
      {err && <Alert kind="err">{err}</Alert>}
      {snap?.status === "error" && <Alert kind="err">{snap.error}</Alert>}

      {snap && snap.status !== "error" && (
        <>
          {info.has_phase_model && (
            <div className="steps">
              {proc.phases.map((p, i) => (
                <div key={i} className={`step ${i === phase ? "active" : snap.seen.includes(i) ? "done" : ""}`}>
                  <div className="n">{String(i + 1).padStart(2, "0")}</div><div className="nm">{b(p.name)}</div>
                </div>
              ))}
            </div>
          )}
          <div className="viewer">
            <div>
              <div className="player" style={{ aspectRatio: "16/9" }}>
                {latest && <img className="frame" src={`/api/live/${snap.id}/frame?seq=${latest.seq}`} alt="" />}
                {latest && <Boxes boxes={latest.boxes} procedure={proc} />}
                <div className="hud">
                  <span className="pill-dark"><span className={`dot ${running ? "live" : ""}`} />{running ? "LIVE · AI" : status?.label ?? ""}</span>
                  <span className="pill-dark"><Crosshair className="ic" />{latest?.boxes.length ?? 0}</span>
                </div>
              </div>
              <div className="dock">
                <span className="mono">{fmtTime(latest?.t ?? 0)} / {fmtTime(snap.duration)}</span>
                <div className="progress" style={{ flex: 1, margin: 0, background: "rgba(255,255,255,.15)" }}><span style={{ width: `${100 * snap.progress}%` }} /></div>
                <span className="mono">{Math.round(100 * snap.progress)}%</span>
              </div>
            </div>
            <Glass className="now-card" title={t("live_now_phase")} icon={Layers} subtitle={running ? t("live_sub") : undefined}>
              <div className="big">{phase != null ? b(proc.phases[phase]?.name) : "-"}</div>
              <div className="muted small" style={{ textTransform: "uppercase", fontWeight: 650, letterSpacing: ".05em" }}>{t("live_instruments_now")}</div>
              <div style={{ margin: "8px 0 14px" }}>
                {active.length ? active.map((i) => (
                  <span key={i} className="chip" style={{ background: proc.instruments[i].color + "22", borderColor: proc.instruments[i].color, color: "var(--ink)" }}>
                    <i className="sw" style={{ background: proc.instruments[i].color, margin: 0 }} />{b(proc.instruments[i].name)}
                    {latest?.boxes.filter((x) => x[0] === i).map((x) => x[5].toFixed(2)).join(" · ")}
                  </span>
                )) : <Chip kind="dim">{t("live_none_now")}</Chip>}
              </div>
              <div className="muted small">{t("live_frames")}: <b className="num">{snap.n_frames}</b> · {snap.seconds}s</div>
            </Glass>
          </div>
          {chartD && chartD.phases.length > 0 && <Glass title={t("phases_title")} icon={Layers}><PhaseTimeline d={chartD} t={latest?.t ?? 0} onSeek={() => undefined} /></Glass>}
          {chartD && chartD.intervals.length > 0 && <Timeline d={chartD} t={latest?.t ?? 0} onSeek={() => undefined} />}
        </>
      )}

      {finished && snap && (
        <>
          <Metrics items={[
            { label: t("live_frames"), value: String(snap.n_frames), hint: t("live_frames_hint", { s: Math.round(snap.seconds) }), icon: Film, tone: "dark" },
            { label: t("live_instr_seen"), value: String(snap.instruments_seen?.length ?? 0), hint: (snap.instruments_seen ?? []).map((i) => b(proc.instruments[i].name)).join(", ") || "-", icon: Crosshair },
            { label: t("live_duration"), value: fmtTime(snap.duration), icon: Clock, tone: "copper" },
          ]} />
          {snap.chart && snap.chart.phases.length > 0 && <p className="muted small">{t("live_phase_note")}</p>}
          <Glass title={t("live_save")} icon={Save}>
            {snap.saved_case ? (
              <div className="row">{t("live_saved", { id: snap.saved_case })} <Link to={`/review/${snap.saved_case}`} className="btn sm">{t("open_case")}</Link></div>
            ) : (
              <>
                <label className="f">{t("title")}</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
                <p><label><input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} /> {t("consent_text")}</label></p>
                <button className="btn primary" onClick={save}><Save className="ic" />{t("live_save")}</button>
              </>
            )}
            {saveMsg && <Alert kind={saveMsg.ok ? "" : "err"}>{saveMsg.text}</Alert>}
          </Glass>
        </>
      )}
    </div>
  );
}
