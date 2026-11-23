// Owner: Member A (WBS 5.2.2). Pure data transformations for the Analytics page (unit-tested with Vitest).
import { TOOLS, type AnalyticsResponse, type ToolName } from "../../api/types";

export interface CaseRow {
  video_id: string;
  total_s: number;
  switches: number;
  per_tool_s: Record<ToolName, number>;
}

/** Flatten an analytics response into one row per case with every tool present (0 if unused). */
export function toRows(data: AnalyticsResponse): CaseRow[] {
  return data.cases.map(({ video_id, stats }) => ({
    video_id,
    total_s: stats.total_s,
    switches: stats.switches,
    per_tool_s: Object.fromEntries(TOOLS.map((tool) => [tool, stats.per_tool_s[tool] ?? 0])) as Record<ToolName, number>,
  }));
}

/** CSV for "Export CSV". TODO(A, 5.2.2): confirm Excel opens it correctly (BOM + separator). */
export function toCsv(rows: CaseRow[]): string {
  const header = ["video_id", "total_s", "switches", ...TOOLS.map((tool) => `${tool}_s`)];
  const lines = rows.map((r) => [r.video_id, r.total_s, r.switches, ...TOOLS.map((tool) => r.per_tool_s[tool])].join(","));
  return [header.join(","), ...lines].join("\n");
}
