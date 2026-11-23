// Owner: Member D (WBS 5.1.2 player + timeline, 5.1.3 notes, 5.2.1 reads ?t= to seek on load).
// TODO(D, 5.1.2): load timeline, render <VideoPlayer> + <Timeline> + stats panel; click bar -> seek.
// TODO(D, 5.1.3): add <NotesPanel> and the PDF download button (en/ar).
// TODO(D, 5.2.1): read ?t=<seconds> from the URL and seek once the video is ready.
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import type { PageRoute } from "../../app/App";
import { api } from "../../api/client";
import type { Timeline as TimelineData } from "../../api/types";
import { Timeline } from "../../components/Timeline/Timeline";
import { VideoPlayer, type VideoPlayerHandle } from "../../components/VideoPlayer/VideoPlayer";
import { t } from "../../i18n";

export const route: PageRoute = { path: "/review/:id?", navKey: "nav.review", order: 2 };

export default function ReviewPage() {
  const { id = "fixture_case_01" } = useParams();
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [now, setNow] = useState(0);
  const player = useRef<VideoPlayerHandle>(null);

  useEffect(() => {
    api.getTimeline(id).then(setTimeline).catch(console.error);
  }, [id]);

  return (
    <section>
      <h1>{t("review.title")} · {id}</h1>
      <VideoPlayer ref={player} src={api.videoFileUrl(id)} onTimeUpdate={setNow} />
      {timeline && <Timeline timeline={timeline} currentTime={now} onSeek={(s) => player.current?.seek(s)} />}
    </section>
  );
}
