// Owner: Member A (WBS 5.2.2) — Analytics dashboard (use case 5). Auto-registered at /analytics.
// Edit ONLY files inside web/src/pages/Analytics/.
import { useEffect, useMemo, useState } from "react";
import classes from "@contracts/classes.json";
import type { PageRoute } from "../../app/App";
import { api } from "../../api/client";
import { TOOLS, type AnalyticsResponse, type ToolName, type VideoSummary } from "../../api/types";
import { t } from "../../i18n";
import { computeSummary, toCsv, toRows, type CaseRow } from "./transform";

export const route: PageRoute = { path: "/analytics", navKey: "nav.analytics", order: 4 };

const COLORS = classes.colors as Record<ToolName, string>;

function formatSeconds(sec: number): string {
  const s = Math.round(sec);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

export default function AnalyticsPage() {
  const [videos, setVideos] = useState<VideoSummary[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .listVideos()
      .then((vs) => {
        if (!active) return;
        const doneVideos = vs.filter((v) => v.status === "done");
        const list = doneVideos.length > 0 ? doneVideos : vs;
        setVideos(list);
        setSelectedIds(list.map((v) => v.id));
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    if (selectedIds.length === 0) {
      setData({ cases: [], aggregate: {} });
      return;
    }
    api
      .analytics(selectedIds)
      .then((res) => {
        if (active) setData(res);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      active = false;
    };
  }, [selectedIds]);

  const rows: CaseRow[] = useMemo(() => (data ? toRows(data, videos) : []), [data, videos]);
  const summary = useMemo(() => computeSummary(rows), [rows]);

  const toggleCase = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const selectAll = () => setSelectedIds(videos.map((v) => v.id));
  const clearAll = () => setSelectedIds([]);

  const handleExportCsv = () => {
    const csvContent = "\uFEFF" + toCsv(rows);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `or-intelligence-analytics-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const maxStackedSeconds = useMemo(() => {
    let max = 1;
    for (const r of rows) {
      const sum = TOOLS.reduce((acc, tool) => acc + r.per_tool_s[tool], 0);
      if (sum > max) max = sum;
    }
    return max;
  }, [rows]);

  const maxSwitches = useMemo(() => {
    let max = 1;
    for (const r of rows) {
      if (r.switches > max) max = r.switches;
    }
    return max;
  }, [rows]);

  return (
    <section className="analytics-page" style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <h1 style={{ margin: 0 }}>{t("analytics.title")}</h1>
        <button
          type="button"
          onClick={handleExportCsv}
          disabled={rows.length === 0}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: 8,
            border: "1px solid #0f766e",
            background: rows.length === 0 ? "#cbd5e1" : "#0f766e",
            color: "#fff",
            fontWeight: 600,
            cursor: rows.length === 0 ? "not-allowed" : "pointer",
          }}
        >
          {t("analytics.export_csv")}
        </button>
      </div>

      {error && (
        <div role="alert" style={{ padding: "0.75rem 1rem", borderRadius: 8, background: "#fdecec", color: "#b91c1c" }}>
          {error}
        </div>
      )}

      {/* Case Multi-Select Panel */}
      <div
        style={{
          background: "#fff",
          border: "1px solid #dde3ea",
          borderRadius: 12,
          padding: "1rem 1.25rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2 style={{ fontSize: "1.05rem", margin: 0 }}>{t("analytics.select_cases")}</h2>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              type="button"
              onClick={selectAll}
              style={{ padding: "0.25rem 0.65rem", borderRadius: 6, border: "1px solid #cbd5e1", background: "#f8fafc", cursor: "pointer", fontSize: "0.82rem" }}
            >
              All ({videos.length})
            </button>
            <button
              type="button"
              onClick={clearAll}
              style={{ padding: "0.25rem 0.65rem", borderRadius: 6, border: "1px solid #cbd5e1", background: "#f8fafc", cursor: "pointer", fontSize: "0.82rem" }}
            >
              None
            </button>
          </div>
        </div>
        {loading ? (
          <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>Loading cases…</p>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
            {videos.map((v) => {
              const checked = selectedIds.includes(v.id);
              return (
                <label
                  key={v.id}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.45rem",
                    padding: "0.4rem 0.75rem",
                    borderRadius: 999,
                    border: checked ? "1px solid #0f766e" : "1px solid #cbd5e1",
                    background: checked ? "#e2f3f0" : "#f8fafc",
                    cursor: "pointer",
                    fontSize: "0.88rem",
                    fontWeight: checked ? 600 : 400,
                  }}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleCase(v.id)}
                    style={{ accentColor: "#0f766e" }}
                  />
                  <span>{v.title || v.id}</span>
                  {v.duration_s != null && (
                    <span style={{ color: "#64748b", fontSize: "0.78rem" }}>({formatSeconds(v.duration_s)})</span>
                  )}
                </label>
              );
            })}
          </div>
        )}
      </div>

      {/* KPI Summary Cards */}
      {rows.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.85rem" }}>
          <div style={{ background: "#fff", border: "1px solid #dde3ea", borderRadius: 12, padding: "0.9rem 1.1rem" }}>
            <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{t("analytics.select_cases")}</div>
            <div style={{ fontSize: "1.45rem", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{summary.count}</div>
          </div>
          <div style={{ background: "#fff", border: "1px solid #dde3ea", borderRadius: 12, padding: "0.9rem 1.1rem" }}>
            <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{t("review.stats")} (Mean Duration)</div>
            <div style={{ fontSize: "1.45rem", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
              {summary.mean_total_s}s ({formatSeconds(summary.mean_total_s)})
            </div>
          </div>
          <div style={{ background: "#fff", border: "1px solid #dde3ea", borderRadius: 12, padding: "0.9rem 1.1rem" }}>
            <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{t("review.switches")} (Mean)</div>
            <div style={{ fontSize: "1.45rem", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{summary.mean_switches}</div>
          </div>
        </div>
      )}

      {/* Charts Grid: 1) Stacked Bar of Per-Tool Seconds per Case, 2) Line Chart of Switches across Cases */}
      {rows.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "1rem" }}>
          {/* Stacked Bar Chart */}
          <div style={{ background: "#fff", border: "1px solid #dde3ea", borderRadius: 12, padding: "1.1rem 1.25rem" }}>
            <h2 style={{ fontSize: "1.05rem", margin: "0 0 0.75rem" }}>{t("review.time_per_tool")} (s)</h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem", marginBottom: "0.85rem", fontSize: "0.8rem" }}>
              {TOOLS.map((tool) => (
                <span key={tool} style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                  <i style={{ width: 10, height: 10, borderRadius: 3, background: COLORS[tool], display: "inline-block" }} />
                  {t(`tool.${tool}`)}
                </span>
              ))}
            </div>
            <div style={{ display: "grid", gap: "0.65rem" }} role="img" aria-label={t("review.time_per_tool")}>
              {rows.map((r) => {
                const totalActive = TOOLS.reduce((acc, tool) => acc + r.per_tool_s[tool], 0);
                return (
                  <div key={r.video_id} style={{ display: "grid", gap: "0.25rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.84rem" }}>
                      <strong>{r.title || r.video_id}</strong>
                      <span style={{ color: "#64748b", fontVariantNumeric: "tabular-nums" }}>
                        {totalActive.toFixed(1)}s active / {r.total_s}s total
                      </span>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        height: 22,
                        borderRadius: 6,
                        overflow: "hidden",
                        background: "#f1f5f9",
                        border: "1px solid #e2e8f0",
                      }}
                    >
                      {TOOLS.map((tool) => {
                        const sec = r.per_tool_s[tool];
                        if (sec <= 0) return null;
                        const widthPct = (sec / maxStackedSeconds) * 100;
                        return (
                          <div
                            key={tool}
                            title={`${t(`tool.${tool}`)}: ${sec}s`}
                            style={{
                              width: `${widthPct}%`,
                              background: COLORS[tool],
                              height: "100%",
                              transition: "width 0.2s",
                            }}
                          />
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Line Chart of Tool Switches across Cases Ordered by Date */}
          <div style={{ background: "#fff", border: "1px solid #dde3ea", borderRadius: 12, padding: "1.1rem 1.25rem" }}>
            <h2 style={{ fontSize: "1.05rem", margin: "0 0 0.75rem" }}>{t("review.switches")}</h2>
            {(() => {
              const width = 460;
              const height = 190;
              const padL = 38;
              const padR = 24;
              const padT = 20;
              const padB = 38;
              const plotW = width - padL - padR;
              const plotH = height - padT - padB;
              const points = rows.map((r, idx) => {
                const x = rows.length === 1 ? padL + plotW / 2 : padL + (idx / (rows.length - 1)) * plotW;
                const y = padT + plotH - (r.switches / maxSwitches) * plotH;
                return { x, y, row: r };
              });
              const polylinePoints = points.map((p) => `${p.x},${p.y}`).join(" ");

              return (
                <svg
                  viewBox={`0 0 ${width} ${height}`}
                  style={{ width: "100%", height: "auto", overflow: "visible", direction: "ltr" }}
                  role="img"
                  aria-label={t("review.switches")}
                >
                  {/* Horizontal Grid Lines */}
                  {[0, 0.5, 1].map((frac) => {
                    const y = padT + plotH * (1 - frac);
                    const val = Math.round(maxSwitches * frac);
                    return (
                      <g key={frac}>
                        <line x1={padL} y1={y} x2={width - padR} y2={y} stroke="#e2e8f0" strokeDasharray="3 3" />
                        <text x={padL - 6} y={y + 4} textAnchor="end" fontSize="10" fill="#64748b">
                          {val}
                        </text>
                      </g>
                    );
                  })}
                  {/* Line */}
                  {points.length > 1 && (
                    <polyline fill="none" stroke="#0f766e" strokeWidth="2.5" points={polylinePoints} />
                  )}
                  {/* Nodes and Labels */}
                  {points.map((p) => (
                    <g key={p.row.video_id}>
                      <circle cx={p.x} cy={p.y} r={5} fill="#0f766e" stroke="#fff" strokeWidth="1.5">
                        <title>{`${p.row.video_id}: ${p.row.switches}`}</title>
                      </circle>
                      <text x={p.x} y={p.y - 9} textAnchor="middle" fontSize="10" fontWeight="600" fill="#0f172a">
                        {p.row.switches}
                      </text>
                      <text x={p.x} y={height - 10} textAnchor="middle" fontSize="10" fill="#475569">
                        {p.row.video_id}
                      </text>
                    </g>
                  ))}
                </svg>
              );
            })()}
          </div>
        </div>
      )}

      {/* Comparison Statistics Table */}
      <div
        style={{
          background: "#fff",
          border: "1px solid #dde3ea",
          borderRadius: 12,
          overflowX: "auto",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "1px solid #dde3ea" }}>
              <th style={{ padding: "0.65rem 0.9rem", textAlign: "start" }}>Case</th>
              <th style={{ padding: "0.65rem 0.9rem", textAlign: "end" }}>Total (s)</th>
              <th style={{ padding: "0.65rem 0.9rem", textAlign: "end" }}>{t("review.switches")}</th>
              {TOOLS.map((tool) => (
                <th key={tool} style={{ padding: "0.65rem 0.9rem", textAlign: "end" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
                    <i style={{ width: 8, height: 8, borderRadius: "50%", background: COLORS[tool], display: "inline-block" }} />
                    {t(`tool.${tool}`)} (s)
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.video_id} style={{ borderBottom: "1px solid #eef2f6" }}>
                <td style={{ padding: "0.65rem 0.9rem", fontWeight: 600 }}>{r.video_id}</td>
                <td style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>{r.total_s}</td>
                <td style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>{r.switches}</td>
                {TOOLS.map((tool) => (
                  <td key={tool} style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>
                    {r.per_tool_s[tool]}
                  </td>
                ))}
              </tr>
            ))}
            {rows.length > 1 && (
              <tr style={{ background: "#f8fafc", fontWeight: 700, borderTop: "2px solid #dde3ea" }}>
                <td style={{ padding: "0.65rem 0.9rem" }}>Mean ({summary.count} cases)</td>
                <td style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>
                  {summary.mean_total_s}
                </td>
                <td style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>
                  {summary.mean_switches}
                </td>
                {TOOLS.map((tool) => (
                  <td key={tool} style={{ padding: "0.65rem 0.9rem", textAlign: "end", fontVariantNumeric: "tabular-nums" }}>
                    {summary.mean_per_tool_s[tool]}
                  </td>
                ))}
              </tr>
            )}
            {rows.length === 0 && (
              <tr>
                <td colSpan={3 + TOOLS.length} style={{ padding: "1.5rem", textAlign: "center", color: "#64748b" }}>
                  No cases selected.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

