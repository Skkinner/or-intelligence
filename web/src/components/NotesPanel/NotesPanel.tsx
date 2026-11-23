// Owner: Member D (WBS 5.1.3) — timestamped instructor notes + PDF download.
// TODO(D, 5.1.3):
//  - "Add note at mm:ss" prefilled with the current playhead time -> api.createNote
//  - list sorted by t_sec; click -> onSeek(note.t_sec); delete -> api.deleteNote
//  - report button: window.open(api.reportUrl(videoId, lang)) with an en/ar selector
//  Acceptance: a note added at 12:34 shows at 12:34 on the timeline and in the list; PDF downloads in both languages.
import type { Note } from "../../api/types";
import { t } from "../../i18n";

export interface NotesPanelProps {
  videoId: string;
  currentTime: number;
  notes: Note[];
  onSeek: (seconds: number) => void;
  onChange: (notes: Note[]) => void;
}

export function NotesPanel(props: NotesPanelProps) {
  return (
    <aside>
      <h2>{t("notes.title")}</h2>
      <div className="todo">{t("common.todo", { wbs: `WBS 5.1.3 · Member D · ${props.notes.length} notes` })}</div>
    </aside>
  );
}
