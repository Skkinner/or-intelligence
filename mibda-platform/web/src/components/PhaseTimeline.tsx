import { Detail, Phase } from "../api";
import { fmtTime, useI18n } from "../i18n";
import { phaseAt, phaseStatus } from "./review";

/** Horizontal surgical timeline: one segment per phase, width = duration, current phase highlighted, playhead on top. */
export function PhaseTimeline({ d, t, onSeek }: { d: Pick<Detail, "phases" | "procedure" | "duration">; t: number; onSeek: (t: number) => void }) {
  const { t: tr, b } = useI18n();
  const dur = Math.max(d.duration, 1);
  const cur = phaseAt(d.phases, t);
  const ci = cur ? d.phases.indexOf(cur) : -1;
  const ticks = [0, 1, 2, 3, 4, 5, 6].map((k) => (dur * k) / 6);
  const used = [...new Set(d.phases.map((p) => p.phase))];
  const seg = (p: Phase, i: number) => {
    const def = d.procedure.phases[p.phase];
    const w = ((p.end - p.start) / dur) * 100;
    return (
      <button key={i} className={`ptl-seg ${i === ci ? "active" : ""} ${ci >= 0 && i > ci ? "future" : ""} ${p.uncertain ? "unc" : ""} ${p.verified ? "" : "est"}`}
        style={{ width: `${w}%`, background: def?.color }} onClick={() => onSeek(p.start)} title={`${b(def?.name)} · ${fmtTime(p.start)} – ${fmtTime(p.end)} · ${phaseStatus(p, tr)}`}>
        {w > 7 && <span className="in"><b>{b(def?.name)}</b><span>{fmtTime(p.start)} · {fmtTime(p.end - p.start)}</span></span>}
      </button>
    );
  };
  return (
    <div className="ptl">
      <div className="ptl-track">
        {d.phases.map(seg)}
        <div className="ptl-head" style={{ insetInlineStart: `${Math.min(100, (100 * t) / dur)}%` }} />
      </div>
      <div className="ptl-axis">{ticks.map((x, i) => <span key={i}>{fmtTime(x)}</span>)}</div>
      <div className="ptl-legend">{used.map((k) => <span key={k}><i className="sw" style={{ background: d.procedure.phases[k]?.color }} />{b(d.procedure.phases[k]?.name)}</span>)}</div>
    </div>
  );
}
