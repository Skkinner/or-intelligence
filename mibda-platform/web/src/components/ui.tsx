import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ArrowUpRight, Info, Lock, LucideIcon, XCircle } from "lucide-react";
import { Card, Strip } from "../api";
import { fmtTime, useI18n } from "../i18n";

export function Hero({ title, subtitle, chips }: { title: string; subtitle?: string; chips?: ReactNode }) {
  return (
    <div className="hero">
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
      {chips}
    </div>
  );
}

export function PageHead({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: ReactNode }) {
  return (
    <div className="page-head">
      <div className="t"><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>
      {actions && <div className="row">{actions}</div>}
    </div>
  );
}

export const Chip = ({ children, kind = "" }: { children: ReactNode; kind?: string }) => <span className={`chip ${kind}`}>{children}</span>;

export interface MetricItem { label: string; value: string; hint?: string; icon?: LucideIcon; tone?: "" | "dark" | "copper" }

export function Metrics({ items }: { items: MetricItem[] }) {
  return (
    <div className="metrics">
      {items.map((m) => (
        <div className={`metric ${m.tone ?? ""}`} key={m.label}>
          <span className="ghost" />
          <div className="l">{m.icon && <m.icon className="ic" />}{m.label}</div>
          <div className="v num">{m.value}</div>
          {m.hint && <div className="h">{m.hint}</div>}
        </div>
      ))}
    </div>
  );
}

/** Glass panel with an optional icon + title + subtitle header. */
export function Glass({ title, subtitle, icon: Icon, action, tone = "", className = "", hover = false, children }: {
  title?: string; subtitle?: string; icon?: LucideIcon; action?: ReactNode; tone?: "" | "dark"; className?: string; hover?: boolean; children: ReactNode;
}) {
  return (
    <section className={`glass ${tone} ${hover ? "hover" : ""} ${className}`}>
      {(title || Icon) && (
        <div className="card-h">
          {Icon && <span className="ico"><Icon className="ic" /></span>}
          <div><h3>{title}</h3>{subtitle && <p>{subtitle}</p>}</div>
          {action && <div className="act">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

export function PhaseStrip({ strip }: { strip: Strip[] }) {
  const total = strip.reduce((a, s) => a + s.w, 0) || 1;
  return (
    <div className="strip">
      {strip.map((s, i) => <span key={i} className={s.verified ? "" : "est"} style={{ width: `${(100 * s.w) / total}%`, background: s.color }} />)}
    </div>
  );
}

export function CaseCard({ c }: { c: Card }) {
  const { t, b } = useI18n();
  return (
    <div className="glass hover case-card">
      <div className="img" style={{ backgroundImage: `url(/api/cases/${c.id}/thumb)` }}>
        <span className="lock"><Lock className="ic" />{t("preview_protected")}</span>
      </div>
      <div className="b">
        <div className="t">#{c.id} · {c.title}</div>
        <div className="muted small">{b(c.procedure.label)}</div>
        <PhaseStrip strip={c.strip} />
        <div>
          <Chip>{fmtTime(c.duration)}</Chip>
          <Chip kind={c.source === "model" ? "ok" : "warn"}>{c.source === "model" ? t("src_model") : t("src_annotations_short")}</Chip>
        </div>
        <div style={{ marginTop: "auto", paddingTop: 10 }}>
          <Link to={`/review/${c.id}`} className="btn sm" style={{ width: "100%" }}>{t("open_case")}<ArrowUpRight className="ic" /></Link>
        </div>
      </div>
    </div>
  );
}

export function Alert({ kind = "", children }: { kind?: "" | "warn" | "err"; children: ReactNode }) {
  const Icon = kind === "err" ? XCircle : kind === "warn" ? AlertTriangle : Info;
  return <div className={`alert ${kind}`}><Icon className="ic" style={{ marginTop: 3 }} /><div>{children}</div></div>;
}

export const Spinner = ({ label }: { label?: string }) => <div className="muted"><span className="spin" />{label}</div>;

export const Skeleton = ({ h = 96, n = 1 }: { h?: number; n?: number }) => (
  <div className="stack">{Array.from({ length: n }, (_, i) => <div key={i} className="skel" style={{ minHeight: h }} />)}</div>
);
