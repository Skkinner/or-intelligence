// Owner: Member A (WBS 5.2.2)
import { describe, expect, it } from "vitest";
import timeline01 from "@fixtures/sample_timeline.json";
import timeline02 from "@fixtures/sample_timeline_case02.json";
import { computeSummary, toCsv, toRows } from "./transform";
import { TOOLS, type AnalyticsResponse, type Stats, type VideoSummary } from "../../api/types";

const dataSingle: AnalyticsResponse = {
  cases: [{ video_id: timeline01.video_id, stats: timeline01.stats as Stats }],
  aggregate: {},
};

const syntheticCase03Stats: Stats = {
  total_s: 150.0,
  switches: 9,
  per_tool_s: {
    grasper: 110.0,
    bipolar: 18.0,
    hook: 60.0,
    scissors: 8.0,
    clipper: 15.0,
    irrigator: 20.0,
  },
  per_tool_segments: {
    grasper: 3,
    bipolar: 2,
    hook: 2,
    scissors: 1,
    clipper: 2,
    irrigator: 1,
  },
};

const dataThreeCases: AnalyticsResponse = {
  cases: [
    { video_id: timeline01.video_id, stats: timeline01.stats as Stats },
    { video_id: timeline02.video_id, stats: timeline02.stats as Stats },
    { video_id: "fixture_case_03", stats: syntheticCase03Stats },
  ],
  aggregate: {},
};

describe("analytics transform", () => {
  it("keeps per-tool totals from the API JSON and fills unused tools with 0", () => {
    const [row] = toRows(dataSingle);
    expect(row.per_tool_s.hook).toBe(timeline01.stats.per_tool_s.hook);
    expect(row.per_tool_s.bipolar).toBe(0);
  });

  it("correctly transforms 3 fixture cases with exact per-tool totals matching API JSON", () => {
    const rows = toRows(dataThreeCases);
    expect(rows).toHaveLength(3);

    for (let i = 0; i < dataThreeCases.cases.length; i++) {
      const src = dataThreeCases.cases[i];
      const row = rows[i];
      expect(row.video_id).toBe(src.video_id);
      expect(row.total_s).toBe(src.stats.total_s);
      expect(row.switches).toBe(src.stats.switches);
      for (const tool of TOOLS) {
        expect(row.per_tool_s[tool]).toBe(src.stats.per_tool_s[tool] ?? 0);
      }
    }
  });

  it("orders cases chronologically by created_at when video summaries are provided", () => {
    const videos: VideoSummary[] = [
      { id: "fixture_case_01", title: "Case 1", status: "done", duration_s: 120, created_at: "2026-11-24T12:00:00Z" },
      { id: "fixture_case_02", title: "Case 2", status: "done", duration_s: 120, created_at: "2026-11-23T09:00:00Z" },
      { id: "fixture_case_03", title: "Case 3", status: "done", duration_s: 150, created_at: "2026-11-24T08:00:00Z" },
    ];
    const rows = toRows(dataThreeCases, videos);
    expect(rows.map((r) => r.video_id)).toEqual(["fixture_case_02", "fixture_case_03", "fixture_case_01"]);
  });

  it("computes aggregate summary statistics across cases", () => {
    const rows = toRows(dataThreeCases);
    const summary = computeSummary(rows);
    expect(summary.count).toBe(3);
    expect(summary.mean_total_s).toBe(130);
    expect(summary.mean_switches).toBe(9);
    expect(summary.mean_per_tool_s.grasper).toBeCloseTo((98 + 120 + 110) / 3, 2);
  });

  it("exports a CSV header with every tool and valid rows for 3 cases", () => {
    const rows = toRows(dataThreeCases);
    const csv = toCsv(rows);
    const lines = csv.split("\n");
    expect(lines).toHaveLength(4);
    expect(lines[0]).toBe("video_id,total_s,switches,grasper_s,bipolar_s,hook_s,scissors_s,clipper_s,irrigator_s");
    expect(lines[1]).toBe("fixture_case_01,120,11,98,0,55,4,13,15");
    expect(lines[2]).toBe("fixture_case_02,120,7,120,10,45,0,14,15");
    expect(lines[3]).toBe("fixture_case_03,150,9,110,18,60,8,15,20");
  });
});

