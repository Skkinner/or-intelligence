// Owner: Member D (WBS 5.1.1). Hand-written mirror of contracts C5/C6.
// TODO(D, 5.1.1): run `npm run gen:api` to generate src/api/schema.d.ts from contracts/openapi.yaml and
// re-export from there so the types can never drift from the contract.

export type ToolName = "grasper" | "bipolar" | "hook" | "scissors" | "clipper" | "irrigator";
export const TOOLS: ToolName[] = ["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"];

export type VideoStatusValue = "queued" | "processing" | "done" | "failed";

export interface Segment { start: number; end: number; mean_conf: number }

export interface Stats {
  total_s: number;
  switches: number;
  per_tool_s: Partial<Record<ToolName, number>>;
  per_tool_segments: Partial<Record<ToolName, number>>;
}

export interface Timeline {
  video_id: string;
  duration_s: number;
  sample_fps: number;
  tools: Partial<Record<ToolName, Segment[]>>;
  stats: Stats;
  params: Record<string, unknown>;
}

export interface VideoSummary { id: string; title: string; status: VideoStatusValue; duration_s: number | null; created_at: string }
export interface VideoStatus { id: string; status: VideoStatusValue; progress: number; error?: string | null }
export interface Note { id: number; video_id: string; t_sec: number; text: string; author: string; created_at: string }
export interface NoteCreate { t_sec: number; text: string; author?: string }
export interface SearchHit { video_id: string; start: number; end: number; tool: ToolName }
export interface AnalyticsResponse {
  cases: { video_id: string; stats: Stats }[];
  aggregate: { mean_per_tool_s?: Partial<Record<ToolName, number>>; mean_switches?: number };
}
