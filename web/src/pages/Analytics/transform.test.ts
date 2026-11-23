// Owner: Member A (WBS 5.2.2)
import { describe, expect, it } from "vitest";
import timeline from "@fixtures/sample_timeline.json";
import { toCsv, toRows } from "./transform";
import type { Stats } from "../../api/types";

const data = { cases: [{ video_id: timeline.video_id, stats: timeline.stats as Stats }], aggregate: {} };

describe("analytics transform", () => {
  it("keeps per-tool totals from the API JSON and fills unused tools with 0", () => {
    const [row] = toRows(data);
    expect(row.per_tool_s.hook).toBe(timeline.stats.per_tool_s.hook);
    expect(row.per_tool_s.bipolar).toBe(0);
  });

  it("exports a CSV header with every tool", () => {
    const csv = toCsv(toRows(data));
    expect(csv.split("\n")[0]).toContain("irrigator_s");
  });

  // TODO(A, 5.2.2): add a test with 3 fixture cases (acceptance criterion).
});
