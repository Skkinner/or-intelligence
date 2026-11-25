import { ReactNode, useId, useRef, useState } from "react";

/** Brand-coloured SVG charts (no chart library): smooth area, donut, ring and horizontal bars with themed tooltips. */

function smooth(pts: [number, number][]): string {
  if (pts.length < 2) return pts.length ? `M${pts[0][0]},${pts[0][1]}` : "";
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] ?? p2;
    const c1: [number, number] = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2: [number, number] = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0]},${c1[1]} ${c2[0]},${c2[1]} ${p2[0]},${p2[1]}`;
  }
  return d;
}

export interface Pt { label: string; value: number; tip?: string }

export function AreaChart({ data, height = 190, color = "#5C061C", accent = "#CD7F32", unit = "" }: { data: Pt[]; height?: number; color?: string; accent?: string; unit?: string }) {
  const id = useId().replace(/:/g, "");
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const W = 560, H = height, pl = 34, pr = 10, pt = 14, pb = 26;
  const max = Math.max(1, ...data.map((d) => d.value)) * 1.15;
  const x = (i: number) => pl + (data.length <= 1 ? (W - pl - pr) / 2 : (i * (W - pl - pr)) / (data.length - 1));
  const y = (v: number) => pt + (1 - v / max) * (H - pt - pb);
  const pts = data.map((d, i) => [x(i), y(d.value)] as [number, number]);
  const line = smooth(pts);
  const area = pts.length > 1 ? `${line} L${pts[pts.length - 1][0]},${H - pb} L${pts[0][0]},${H - pb} Z` : "";
  const ticks = [0, 0.5, 1].map((f) => (f * max) / 1.15);
  const onMove = (e: React.MouseEvent) => {
    const r = ref.current!.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    let best = 0;
    pts.forEach((p, i) => { if (Math.abs(p[0] - px) < Math.abs(pts[best][0] - px)) best = i; });
    setHover(best);
  };
  if (!data.length) return null;
  return (
    <div className="chart" ref={ref} onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img">
        <defs>
          <linearGradient id={`g${id}`} x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor={color} stopOpacity=".32" /><stop offset="1" stopColor={color} stopOpacity="0" /></linearGradient>
        </defs>
        <g className="gl">{ticks.map((v, i) => <line key={i} x1={pl} x2={W - pr} y1={y(v)} y2={y(v)} />)}</g>
        <g className="axis">
          {ticks.map((v, i) => <text key={i} x={pl - 8} y={y(v) + 3} textAnchor="end">{Math.round(v)}</text>)}
          {data.map((d, i) => (data.length <= 8 || i % Math.ceil(data.length / 8) === 0) && <text key={i} x={x(i)} y={H - 6} textAnchor="middle">{d.label}</text>)}
        </g>
        {area && <path d={area} fill={`url(#g${id})`} />}
        <path d={line} fill="none" stroke={color} strokeWidth="2.6" strokeLinecap="round" />
        {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r={hover === i ? 6 : 3.5} fill={hover === i ? accent : "#fff"} stroke={hover === i ? "#fff" : accent} strokeWidth="2" />)}
        {hover != null && <line x1={pts[hover][0]} x2={pts[hover][0]} y1={pt} y2={H - pb} stroke={accent} strokeWidth="1" strokeDasharray="3 3" />}
      </svg>
      {hover != null && <div className="chart-tip" style={{ left: `${(pts[hover][0] / W) * 100}%`, top: `${(pts[hover][1] / H) * 100}%` }}>{data[hover].tip ?? `${data[hover].label}: ${data[hover].value}${unit}`}</div>}
    </div>
  );
}

export interface Seg { label: string; value: number; color: string }

export function Donut({ segs, size = 150, center, centerSub }: { segs: Seg[]; size?: number; center?: ReactNode; centerSub?: ReactNode }) {
  const [hov, setHov] = useState<number | null>(null);
  const total = segs.reduce((a, s) => a + s.value, 0);
  const r = 46, c = 2 * Math.PI * r;
  let off = 0;
  return (
    <div className="donut" style={{ width: size, height: size }}>
      <svg viewBox="0 0 120 120" width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(92,6,28,.08)" strokeWidth="13" />
        {total > 0 && segs.map((s, i) => {
          const len = (s.value / total) * c;
          const el = <circle key={i} cx="60" cy="60" r={r} fill="none" stroke={s.color} strokeWidth={hov === i ? 16 : 13} strokeDasharray={`${Math.max(0, len - 2)} ${c}`} strokeDashoffset={-off} strokeLinecap="round"
            onMouseEnter={() => setHov(i)} onMouseLeave={() => setHov(null)} style={{ transition: "stroke-width .2s", cursor: "default" }} />;
          off += len;
          return el;
        })}
      </svg>
      <div className="donut-c"><div>
        <div className="num" style={{ fontSize: "1.25rem" }}>{hov != null ? `${Math.round((100 * segs[hov].value) / (total || 1))}%` : center}</div>
        <div className="muted small">{hov != null ? segs[hov].label : centerSub}</div>
      </div></div>
    </div>
  );
}

export function Ring({ value, size = 120, label, color = "#CD7F32" }: { value: number; size?: number; label?: ReactNode; color?: string }) {
  const r = 48, c = 2 * Math.PI * r, v = Math.min(1, Math.max(0, value));
  return (
    <div className="donut" style={{ width: size, height: size }}>
      <svg viewBox="0 0 120 120" width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,.15)" strokeWidth="10" />
        <circle cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="10" strokeLinecap="round" strokeDasharray={`${v * c} ${c}`} />
      </svg>
      <div className="donut-c"><div><div className="num" style={{ fontSize: "1.5rem" }}>{Math.round(v * 100)}%</div>{label && <div className="small" style={{ opacity: 0.75 }}>{label}</div>}</div></div>
    </div>
  );
}

export interface Bar { label: string; value: number; color: string; right?: string }

export function HBars({ bars, max }: { bars: Bar[]; max?: number }) {
  const m = max ?? Math.max(1, ...bars.map((b) => b.value));
  return (
    <div className="hbars">
      {bars.map((b, i) => (
        <div className="hbar" key={i}>
          <div className="top"><span>{b.label}</span><span className="muted num small">{b.right ?? Math.round(b.value)}</span></div>
          <div className="tr"><i style={{ width: `${Math.max(2, (100 * b.value) / m)}%`, background: b.color, animationDelay: `${i * 60}ms` }} /></div>
        </div>
      ))}
    </div>
  );
}
