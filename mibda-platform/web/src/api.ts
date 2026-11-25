export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function call<T>(method: string, url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method,
    credentials: "same-origin",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const d = await res.json();
      msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail ?? d);
    } catch { /* not JSON */ }
    throw new ApiError(res.status, msg);
  }
  return (await res.json()) as T;
}

export const api = {
  get: <T,>(url: string) => call<T>("GET", url),
  post: <T,>(url: string, body: unknown = {}) => call<T>("POST", url, body),
  put: <T,>(url: string, body: unknown) => call<T>("PUT", url, body),
  del: <T,>(url: string) => call<T>("DELETE", url),
};

export type Lang = "en" | "ar";
export interface User { id: number; username: string; display_name: string; role: "trainee" | "instructor" | "admin" }
export interface Bi { en: string; ar: string }
export interface Strip { w: number; color: string; verified: boolean }
export interface Card {
  id: number; title: string; source: string; duration: number; tags: string; procedure: { id: string; label: Bi };
  strip: Strip[]; usage: Record<string, number>; instruments_used: number | null; phased: boolean; trainee?: string | null;
}
export interface Phase { phase: number; start: number; end: number; conf: number | null; verified: boolean; uncertain: boolean }
export interface Detail {
  case: { id: number; title: string; source: string; media_kind: string; tags: string; trainee_id: number | null; owner_id: number | null };
  procedure: { id: string; label: Bi; instruments: { name: Bi; color: string }[]; phases: { name: Bi; color: string }[] };
  duration: number; dense: boolean; media: { kind: string; playable: boolean } | null; complete_operation: boolean; phase_source: string | null;
  frames: { t: number; phase: number | null; boxes: number[][] }[];
  intervals: { i: number; start: number; end: number }[];
  phases: Phase[];
  usage: { instrument: string; active_seconds: number; pct_of_case: number; segments: number; first_use: number | null; last_use: number | null; longest_segment: number }[];
  metrics: { duration_s: number; instrument_entries: number; entries_per_min: number; instruments_used: number };
  notes: { id: number; t: number; text: string; author: string; author_id: number }[];
  can_ai: boolean; can_manage: boolean;
}
