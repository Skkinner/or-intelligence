// Owner: Member A (WBS 5.2.2) — Analytics dashboard (use case 5). Auto-registered at /analytics.
// Edit ONLY files inside web/src/pages/Analytics/. Need a chart library? Open a PR that touches only
// web/package.json + package-lock.json and ask Member D to approve it.
//
// TODO(A, 5.2.2):
//  - multi-select videos (api.listVideos) -> api.analytics(ids)   (mock mode until C's 4.2.2 lands)
//  - stacked bar: per-tool seconds per case; line: switches across cases; stats table
//  - "Export CSV" using toCsv() from ./transform
//  Acceptance: 3 fixture cases show per-tool totals equal to the API JSON; CSV opens in Excel.
import { useEffect, useState } from "react";
import type { PageRoute } from "../../app/App";
import { api } from "../../api/client";
import type { AnalyticsResponse } from "../../api/types";
import { t } from "../../i18n";
import { toRows } from "./transform";

export const route: PageRoute = { path: "/analytics", navKey: "nav.analytics", order: 4 };

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);

  useEffect(() => {
    api.listVideos().then((vs) => api.analytics(vs.map((v) => v.id))).then(setData).catch(console.error);
  }, []);

  return (
    <section>
      <h1>{t("analytics.title")}</h1>
      <div className="todo">{t("common.todo", { wbs: "WBS 5.2.2 · Member A" })}</div>
      {data && <pre>{JSON.stringify(toRows(data), null, 2)}</pre>}
    </section>
  );
}
