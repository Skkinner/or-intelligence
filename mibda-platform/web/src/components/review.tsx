import { useEffect, useMemo, useRef, useState } from "react";
import { Pause, Play, RotateCcw, ScanSearch } from "lucide-react";
import { Detail, Phase } from "../api";
import { fmtTime, useI18n } from "../i18n";

export function phaseAt(phases: Phase[], t: number): Phase | null {
  for (const p of phases) if (t >= p.start && t < p.end) return p;
  return phases.length && t >= phases[phases.length - 1].end ? phases[phases.length - 1] : null;
}

function nearest(frames: Detail["frames"], t: number) {
  let lo = 0, hi = frames.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (frames[mid].t < t) lo = mid + 1; else hi = mid;
  }
  if (lo > 0 && Math.abs(frames[lo - 1].t - t) <= Math.abs(frames[lo].t - t)) lo -= 1;
  return frames[lo];
}

type Procedure = Detail["procedure"];

/** Detection boxes with the instrument name (from the model's class id via the procedure) and the confidence score. */
export function Boxes({ boxes, procedure }: { boxes: number[][]; procedure: Procedure }) {
  const { b } = useI18n();
  return (
    <div className="boxes">
      {boxes.map((bx, k) => {
        const ins = procedure.instruments[bx[0]];
        if (!ins) return null;
        const conf = bx[5];
        return (
          <div key={k} className="box" style={{ left: `${bx[1] * 100}%`, top: `${bx[2] * 100}%`, width: `${bx[3] * 100}%`, height: `${bx[4] * 100}%`, borderColor: ins.color }}>
            <span className={`box-label ${bx[2] < 0.08 ? "in" : ""}`} style={{ ["--bc" as string]: ins.color }}>
              {b(ins.name)}{conf < 1 && <span className="cf">{conf.toFixed(2)}</span>}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export const SPEEDS = [1, 2, 4, 8, 16, 32];

/** Video or server-side frames, with the detections drawn on top. `t` is controlled by the parent; the player reports its own progress. */
export function Player({ d, t, onTime, speed = 1, showBoxes = true }: { d: Detail; t: number; onTime: (t: number) => void; speed?: number; showBoxes?: boolean }) {
  const { t: tr, b } = useI18n();
  const id = d.case.id;
  const video = d.media?.kind === "video" && d.media.playable;
  const vref = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [ratio, setRatio] = useState(16 / 9);
  const [failed, setFailed] = useState(false);
  const useVideo = video && !failed;
  const tRef = useRef(t);
  tRef.current = t;

  // external seeks (timeline, phase buttons, slider) move the video
  useEffect(() => {
    const v = vref.current;
    if (useVideo && v && Math.abs(v.currentTime - t) > 0.7) v.currentTime = t;
  }, [t, useVideo]);
  useEffect(() => { const v = vref.current; if (v) v.playbackRate = speed; }, [speed, useVideo]);

  // frame mode: the server sends one still per second; a timer advances time
  useEffect(() => {
    if (useVideo || !playing) return;
    const h = setInterval(() => {
      const nt = tRef.current + 0.25 * speed;
      if (nt >= d.duration) { setPlaying(false); onTime(d.duration); } else onTime(nt);
    }, 250);
    return () => clearInterval(h);
  }, [useVideo, playing, speed, d.duration, onTime]);

  useEffect(() => { setPlaying(false); setFailed(false); }, [id]);

  function toggle() {
    const v = vref.current;
    if (useVideo && v) { if (v.paused) { void v.play(); setPlaying(true); } else { v.pause(); setPlaying(false); } }
    else setPlaying((p) => !p);
  }
  const f = useMemo(() => (d.frames.length ? nearest(d.frames, t) : null), [d.frames, t]);
  const name = (i: number) => b(d.procedure.instruments[i]?.name);

  const phase = phaseAt(d.phases, t);
  return (
    <div>
      <div className="player" style={{ aspectRatio: String(ratio) }}>
        {useVideo ? (
          <video ref={vref} src={`/api/cases/${id}/video`} preload="metadata" onError={() => setFailed(true)}
            onLoadedMetadata={(e) => { const v = e.currentTarget; if (v.videoWidth) setRatio(v.videoWidth / v.videoHeight); }}
            onTimeUpdate={(e) => onTime(e.currentTarget.currentTime)} onPause={() => setPlaying(false)} onPlay={() => setPlaying(true)} />
        ) : d.media ? (
          <img className="frame" src={`/api/cases/${id}/frame?t=${Math.floor(t)}`} alt=""
            onLoad={(e) => { const i = e.currentTarget; if (i.naturalWidth) setRatio(i.naturalWidth / i.naturalHeight); }} />
        ) : <div style={{ color: "#fff", padding: 24 }}>{tr("video_missing")}</div>}
        {showBoxes && f && <Boxes boxes={f.boxes} procedure={d.procedure} />}
        <div className="hud">
          <span className="pill-dark"><ScanSearch className="ic" />{f ? f.boxes.length : 0} · {d.procedure.instruments.length ? tr("instruments_used") : tr("phase")}</span>
          {phase && <span className="pill-dark"><span className="dot" />{b(d.procedure.phases[phase.phase]?.name)}</span>}
        </div>
      </div>
      <div className="dock">
        <button className="btn play icon-only" onClick={toggle} aria-label={playing ? tr("pause") : tr("play")} style={{ padding: "8px 16px" }}>
          {playing ? <Pause className="ic" /> : <Play className="ic" />}{playing ? tr("pause") : tr("play")}
        </button>
        <button className="btn" onClick={() => onTime(0)} aria-label={tr("restart")} style={{ padding: 8 }}><RotateCcw className="ic" /></button>
        <input type="range" min={0} max={Math.max(1, Math.floor(d.duration))} step={1} value={Math.min(Math.floor(t), Math.floor(d.duration))}
          onChange={(e) => onTime(Number(e.target.value))} aria-label={tr("time")} />
        <span className="mono">{fmtTime(t)} / {fmtTime(d.duration)}</span>
      </div>
      {showBoxes && f && f.boxes.length > 0 && (
        <div className="legend-inst">
          {[...new Set(f.boxes.map((x) => x[0]))].map((i) => <span key={i}><i className="sw" style={{ background: d.procedure.instruments[i]?.color }} />{name(i)}</span>)}
        </div>
      )}
    </div>
  );
}

export function Timeline({ d, t, onSeek }: { d: Detail; t: number; onSeek: (t: number) => void }) {
  const { t: tr, b } = useI18n();
  const cur = phaseAt(d.phases, t);
  const dur = Math.max(d.duration, 1);
  const pos = (x: number) => `${(100 * x) / dur}%`;
  const click = (e: React.MouseEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const frac = (e.clientX - r.left) / r.width;
    onSeek(Math.min(dur, Math.max(0, (document.dir === "rtl" ? 1 - frac : frac) * dur)));
  };
  const ticks = [0, 1, 2, 3, 4, 5, 6].map((k) => (dur * k) / 6);
  return (
    <div className="glass tl">
      {d.procedure.instruments.map((ins, i) => {
        const ivs = d.intervals.filter((iv) => iv.i === i);
        if (!ivs.length) return null;
        return (
          <div className="tl-row" key={i}>
            <span className="nm">{b(ins.name)}</span>
            <div className="tl-track" onClick={click}>
              {ivs.map((iv, k) => <div key={k} className="tl-bar" title={`${fmtTime(iv.start)} - ${fmtTime(iv.end)}`}
                style={{ insetInlineStart: pos(iv.start), width: `max(2px, ${(100 * (iv.end - iv.start)) / dur}%)`, background: ins.color }} />)}
              <div className="tl-cursor" style={{ insetInlineStart: pos(t) }} />
            </div>
          </div>
        );
      })}
      {d.phases.length > 0 && (
        <div className="tl-row">
          <span className="nm">{tr("phase_row")}</span>
          <div className="tl-track" onClick={click}>
            {d.phases.map((p, k) => {
              const def = d.procedure.phases[p.phase];
              return <div key={k} className={`tl-bar ${p.verified ? "" : "est"} ${p.uncertain ? "unc" : ""} ${p === cur ? "active" : ""}`}
                title={`${b(def?.name)}  ${fmtTime(p.start)} - ${fmtTime(p.end)}`}
                style={{ insetInlineStart: pos(p.start), width: `${(100 * (p.end - p.start)) / dur}%`, background: def?.color }} />;
            })}
            <div className="tl-cursor" style={{ insetInlineStart: pos(t) }} />
          </div>
        </div>
      )}
      <div className="tl-axis"><span /><div>{ticks.map((x, i) => <span key={i}>{fmtTime(x)}</span>)}</div></div>
    </div>
  );
}

export function phaseStatus(p: Phase, tr: (k: string) => string): string {
  if (p.verified) return tr("phase_verified");
  const c = p.conf != null ? ` (${Math.round(100 * p.conf)}%)` : "";
  return (p.uncertain ? tr("phase_uncertain") : tr("phase_estimated")) + c;
}

export function PhaseList({ d, t, onSeek }: { d: Detail; t: number; onSeek: (t: number) => void }) {
  const { t: tr, b } = useI18n();
  const cur = phaseAt(d.phases, t);
  if (!d.phases.length) return <p className="muted">{tr("phases_none")}</p>;
  return (
    <div>
      {d.phases.some((p) => !p.verified) && <div className="alert warn">{tr("phases_estimated_warning")}{!d.complete_operation && <div className="small" style={{ marginTop: 4 }}>{tr("phases_excerpt_note")}</div>}</div>}
      <p className="muted small">{tr("phases_hint")}</p>
      {d.phases.map((p, i) => {
        const def = d.procedure.phases[p.phase];
        return (
          <div key={i} className={`phase-row ${p === cur ? "active" : ""}`}>
            <span><span className="sw" style={{ background: def?.color }} />{b(def?.name)}{p === cur && <span className="live">{tr("phase_playing")}</span>}</span>
            <span className="mono">{fmtTime(p.start)} - {fmtTime(p.end)}</span>
            <span>{fmtTime(p.end - p.start)}</span>
            <span className="muted small">{phaseStatus(p, tr)}</span>
            <button className="btn sm" onClick={() => onSeek(p.start)}>{tr("go")}</button>
          </div>
        );
      })}
    </div>
  );
}
