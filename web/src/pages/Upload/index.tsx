// Owner: Member D (WBS 5.1.1) — Upload page.
// TODO(D, 5.1.1):
//  - drag-and-drop + file picker -> api.uploadVideo
//  - poll api.getStatus every 2 s, show progress bar (t("upload.processing", {percent}))
//  - on status "done" navigate to /review/<id>; on "failed" show the error
import type { PageRoute } from "../../app/App";
import { t } from "../../i18n";

export const route: PageRoute = { path: "/upload", navKey: "nav.upload", order: 1 };

export default function UploadPage() {
  return (
    <section>
      <h1>{t("upload.title")}</h1>
      <div className="todo">{t("common.todo", { wbs: "WBS 5.1.1 · Member D" })}</div>
    </section>
  );
}
