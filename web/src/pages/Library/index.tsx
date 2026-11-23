// Owner: Member D (WBS 5.2.1) — Library search (use case 3).
// TODO(D, 5.2.1):
//  - list videos (api.listVideos): title, duration, status
//  - search form: tool (TOOLS) + min duration -> api.search
//  - results grouped by video; click -> navigate(`/review/${video_id}?t=${start}`)
//  Acceptance: "clipper" on fixtures lists exactly the clipper segments.
import type { PageRoute } from "../../app/App";
import { t } from "../../i18n";

export const route: PageRoute = { path: "/library", navKey: "nav.library", order: 3 };

export default function LibraryPage() {
  return (
    <section>
      <h1>{t("library.title")}</h1>
      <div className="todo">{t("common.todo", { wbs: "WBS 5.2.1 · Member D" })}</div>
    </section>
  );
}
