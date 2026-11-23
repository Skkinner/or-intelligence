// Owner: Member D (WBS 5.1.1). Single API client used by every page (including Member A's Analytics).
//
// MOCK MODE (VITE_API_MOCK=1, the default until C's API lands): answers from tests/fixtures so the whole UI
// can be built before the backend exists.
import type {
  AnalyticsResponse, Note, NoteCreate, SearchHit, Timeline, ToolName, VideoStatus, VideoSummary,
} from "./types";
import timeline01 from "@fixtures/sample_timeline.json";
import timeline02 from "@fixtures/sample_timeline_case02.json";
import notesFixture from "@fixtures/sample_notes.json";

export const MOCK = (import.meta.env.VITE_API_MOCK ?? "1") === "1";

const mockTimelines: Record<string, Timeline> = {
  [timeline01.video_id]: timeline01 as Timeline,
  [timeline02.video_id]: timeline02 as Timeline,
};

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) throw new Error(`${init?.method ?? "GET"} ${path} -> ${res.status}`);
  return (res.status === 204 ? undefined : await res.json()) as T;
}

export const api = {
  listVideos(): Promise<VideoSummary[]> {
    if (MOCK) {
      return Promise.resolve(Object.values(mockTimelines).map((tl) => ({
        id: tl.video_id, title: tl.video_id, status: "done", duration_s: tl.duration_s,
        created_at: "2026-11-23T00:00:00Z",
      })));
    }
    return http("/api/videos");
  },

  async uploadVideo(file: File, title?: string): Promise<{ id: string; status: "queued" }> {
    if (MOCK) return { id: timeline01.video_id, status: "queued" };
    const body = new FormData();
    body.append("file", file);
    if (title) body.append("title", title);
    return http("/api/videos", { method: "POST", body });
  },

  getStatus(id: string): Promise<VideoStatus> {
    if (MOCK) return Promise.resolve({ id, status: "done", progress: 1 });
    return http(`/api/videos/${id}`);
  },

  videoFileUrl(id: string): string {
    return `/api/videos/${id}/file`;
  },

  getTimeline(id: string): Promise<Timeline> {
    if (MOCK) return Promise.resolve(mockTimelines[id] ?? (timeline01 as Timeline));
    return http(`/api/videos/${id}/timeline`);
  },

  listNotes(id: string): Promise<Note[]> {
    if (MOCK) return Promise.resolve((notesFixture as Note[]).filter((n) => n.video_id === id));
    return http(`/api/videos/${id}/notes`);
  },

  createNote(id: string, note: NoteCreate): Promise<Note> {
    if (MOCK) {
      return Promise.resolve({ id: Date.now(), video_id: id, author: "instructor",
        created_at: new Date().toISOString(), ...note });
    }
    return http(`/api/videos/${id}/notes`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(note),
    });
  },

  deleteNote(id: string, noteId: number): Promise<void> {
    if (MOCK) return Promise.resolve();
    return http(`/api/videos/${id}/notes/${noteId}`, { method: "DELETE" });
  },

  reportUrl(id: string, lang: "en" | "ar"): string {
    return `/api/videos/${id}/report.pdf?lang=${lang}`;
  },

  search(tool: ToolName, minS = 0): Promise<SearchHit[]> {
    if (MOCK) {
      const hits = Object.values(mockTimelines).flatMap((tl) =>
        (tl.tools[tool] ?? []).filter((s) => s.end - s.start >= minS)
          .map((s) => ({ video_id: tl.video_id, start: s.start, end: s.end, tool })));
      return Promise.resolve(hits);
    }
    return http(`/api/search?tool=${tool}&min_s=${minS}`);
  },

  analytics(videoIds: string[]): Promise<AnalyticsResponse> {
    if (MOCK) {
      return Promise.resolve({
        cases: videoIds.filter((v) => mockTimelines[v]).map((v) => ({ video_id: v, stats: mockTimelines[v].stats })),
        aggregate: {},
      });
    }
    return http(`/api/analytics?video_ids=${videoIds.join(",")}`);
  },
};
