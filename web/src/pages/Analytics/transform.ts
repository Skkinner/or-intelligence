// Owner: Member A (WBS 5.2.2). Pure data transformations for the Analytics page (unit-tested with Vitest).
import { TOOLS, type AnalyticsResponse, type ToolName, type VideoSummary } from "../../api/types";

export interface CaseRow {
  video_id: string;
  title?: string;
  created_at?: string;
  total_s: number;
  switches: number;
  per_tool_s: Record<ToolName, number>;
  per_tool_segments: Record<ToolName, number>;
}

/** Flatten an analytics response into one row per case with every tool present (0 if unused). */
export function toRows(data: AnalyticsResponse, videos: VideoSummary[] = []): CaseRow[] {
  const byId = new Map(videos.map((v) => [v.id, v]));
  const rows = data.cases.map(({ video_id, stats }) => {
    const meta = byId.get(video_id);
    return {
      video_id,
      ...(meta?.title ? { title: meta.title } : {}),
      ...(meta?.created_at ? { created_at: meta.created_at } : {}),
      total_s: stats.total_s,
      switches: stats.switches,
      per_tool_s: Object.fromEntries(TOOLS.map((tool) => [tool, stats.per_tool_s[tool] ?? 0])) as Record<ToolName, number>,
      per_tool_segments: Object.fromEntries(
        TOOLS.map((tool) => [tool, stats.per_tool_segments?.[tool] ?? 0]),
      ) as Record<ToolName, number>,
    };
  });

  if (videos.length > 0) {
    rows.sort((a, b) => {
      const da = a.created_at ?? "";
      const db = b.created_at ?? "";
      return da.localeCompare(db) || a.video_id.localeCompare(b.video_id);
    });
  }
  return rows;
}

/** Compute mean total_s, mean switches, and mean per-tool seconds across the provided rows. */
export function computeSummary(rows: CaseRow[]): {
  count: number;
  mean_total_s: number;
  mean_switches: number;
  mean_per_tool_s: Record<ToolName, number>;
} {
  const n = rows.length;
  if (n === 0) {
    return {
      count: 0,
      mean_total_s: 0,
      mean_switches: 0,
      mean_per_tool_s: Object.fromEntries(TOOLS.map((tool) => [tool, 0])) as Record<ToolName, number>,
    };
  }
  const sumTotal = rows.reduce((acc, r) => acc + r.total_s, 0);
  const sumSwitches = rows.reduce((acc, r) => acc + r.switches, 0);
  const meanPerTool = Object.fromEntries(
    TOOLS.map((tool) => {
      const sum = rows.reduce((acc, r) => acc + r.per_tool_s[tool], 0);
      return [tool, Number((sum / n).toFixed(2))];
    }),
  ) as Record<ToolName, number>;

  return {
    count: n,
    mean_total_s: Number((sumTotal / n).toFixed(2)),
    mean_switches: Number((sumSwitches / n).toFixed(2)),
    mean_per_tool_s: meanPerTool,
  };
}

function escapeCsvCell(val: string | number): string {
  const str = String(val);
  if (/[",\r\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/** CSV for "Export CSV", formatted for clean opening in Excel (comma-separated, RFC 4180 escaping). */
export function toCsv(rows: CaseRow[]): string {
  const header = ["video_id", "total_s", "switches", ...TOOLS.map((tool) => `${tool}_s`)];
  const lines = rows.map((r) =>
    [
      escapeCsvCell(r.video_id),
      escapeCsvCell(r.total_s),
      escapeCsvCell(r.switches),
      ...TOOLS.map((tool) => escapeCsvCell(r.per_tool_s[tool])),
    ].join(","),
  );
  return [header.join(","), ...lines].join("\n");
}

