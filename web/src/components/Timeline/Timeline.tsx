// Owner: Member D (WBS 5.1.2) — interactive instrument timeline.  ⚠ critical integration point
//
// TODO(D, 5.1.2):
//  - one lane per tool; bars from timeline.tools; colours from contracts/classes.json (done below)
//  - mm:ss axis ticks; playhead at currentTime; zoom 1x–8x + horizontal scroll for 90-min videos
//  - click bar -> onSeek(segment.start); keyboard ←/→ = previous/next segment of the selected tool
//  - highlight unusual patterns (e.g. irrigation > 60 s, dense switching windows)
//  - note markers (5.1.3)
//  Acceptance: click seeks within ±0.5 s; 90-min timeline scrolls at 60 fps; Vitest component tests pass.
import classes from "@contracts/classes.json";
import { TOOLS, type Timeline as TimelineData } from "../../api/types";
import { t } from "../../i18n";

const COLORS = classes.colors as Record<string, string>;

export interface TimelineProps {
  timeline: TimelineData;
  currentTime: number;
  onSeek: (seconds: number) => void;
}

export function Timeline({ timeline, currentTime, onSeek }: TimelineProps) {
  const pct = (s: number) => `${(100 * s) / Math.max(timeline.duration_s, 1)}%`;
  return (
    <div className="timeline" role="group" aria-label="instrument timeline">
      {TOOLS.map((tool) => (
        <div key={tool} style={{ display: "flex", alignItems: "center", gap: 8, height: 22 }}>
          <span style={{ width: 90, fontSize: 12 }}>{t(`tool.${tool}`)}</span>
          <div style={{ position: "relative", flex: 1, height: 14, background: "#e2e8f0" }}>
            {(timeline.tools[tool] ?? []).map((seg) => (
              <button
                key={seg.start}
                title={`${tool} ${seg.start}s–${seg.end}s`}
                onClick={() => onSeek(seg.start)}
                style={{ position: "absolute", left: pct(seg.start), width: pct(seg.end - seg.start),
                  top: 0, bottom: 0, background: COLORS[tool], border: 0, padding: 0, cursor: "pointer" }}
              />
            ))}
            <div style={{ position: "absolute", left: pct(currentTime), top: -2, bottom: -2, width: 2, background: "#0f172a" }} />
          </div>
        </div>
      ))}
    </div>
  );
}
