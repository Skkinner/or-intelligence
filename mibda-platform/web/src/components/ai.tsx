import { useCallback, useEffect, useState } from "react";
import { Bot, Download, ImageIcon, Lock, Send, Trash2 } from "lucide-react";
import { api, ApiError, Detail } from "../api";
import { fmtTime, useI18n } from "../i18n";
import { Alert, Spinner } from "./ui";

const WHY: Record<string, string> = { not_approved: "ai_off_not_approved", no_key: "ai_off_no_key", no_package: "ai_off_no_package" };
const errText = (e: unknown) => (e instanceof ApiError ? e.message : String(e));

interface Obs { text: string; evidence: string[] }
interface AiPart { summary: string; observations: Obs[]; limitations: string; model?: string; edited?: boolean }
interface Content { doctor_comments?: string; ai?: AiPart | null; frames?: { t: number; caption: string }[] }
interface Rep { id: number; status: "draft" | "final"; content: Content; tokens_in: number; tokens_out: number; reviewer: string }
interface RepResp { report: Rep | null; ai: { ok: boolean; reason: string } }

function AiBanner({ ai }: { ai: { ok: boolean; reason: string } }) {
  const { t } = useI18n();
  return ai.ok ? <p className="muted small" style={{ display: "flex", gap: 8, alignItems: "center" }}><Lock className="ic" />{t("ai_privacy_note")}</p> : <Alert kind="warn">{t(WHY[ai.reason] ?? "ai_off_no_key")}</Alert>;
}

// ---------------------------------------------------------------- AI report
export function ReportTab({ d, now }: { d: Detail; now: number }) {
  const { t, lang } = useI18n();
  const id = d.case.id;
  const [res, setRes] = useState<RepResp | null>(null);
  const [content, setContent] = useState<Content>({});
  const [agree, setAgree] = useState(false);
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");
  const [saved, setSaved] = useState(false);

  const apply = (r: Rep | null, ai?: RepResp["ai"]) => {
    setRes((o) => ({ report: r, ai: ai ?? o?.ai ?? { ok: false, reason: "no_key" } }));
    setContent(r?.content ?? {});
    setAgree(false);
  };
  useEffect(() => { api.get<RepResp>(`/api/cases/${id}/report`).then((r) => apply(r.report, r.ai)); }, [id]);
  if (!res) return null;
  const rep = res.report;
  const final = rep?.status === "final";
  const run = async (label: string, fn: () => Promise<Rep>) => {
    setBusy(label); setErr(""); setSaved(false);
    try { apply(await fn()); } catch (e) { setErr(errText(e)); } finally { setBusy(""); }
  };

  if (!d.can_ai && (!rep || !final)) return <Alert>{t("rep_trainee_none")}</Alert>;
  if (!rep) {
    return (
      <div>
        <p className="muted small">{t("ai_privacy_note")}</p>
        <AiBanner ai={res.ai} />
        <p>{t("rep_none")}</p>
        <div className="row">
          <button className="btn primary" disabled={!res.ai.ok || !!busy} onClick={() => run("gen", () => api.post<Rep>(`/api/cases/${id}/report/generate`, { lang, with_ai: true }))}>{t("rep_generate_ai")}</button>
          <button className="btn" disabled={!!busy} onClick={() => run("draft", () => api.post<Rep>(`/api/cases/${id}/report/generate`, { lang, with_ai: false }))}>{t("rep_draft_no_ai")}</button>
        </div>
        {busy === "gen" && <Spinner label={t("rep_generating")} />}
        {err && <Alert kind="err">{err}</Alert>}
      </div>
    );
  }
  const ai = content.ai;
  const setAi = (patch: Partial<AiPart>) => setContent((c) => ({ ...c, ai: { ...(c.ai as AiPart), ...patch } }));
  const save = (approve: boolean) => run("save", async () => {
    const r = await api.put<Rep>(`/api/cases/${id}/report`, { content, approve, confirmed: agree });
    setSaved(true);
    return r;
  });
  return (
    <div>
      {d.can_ai && <AiBanner ai={res.ai} />}
      <p><b>{final ? t("rep_status_final", { name: rep.reviewer }) : t("rep_status_draft")}</b></p>
      {(rep.tokens_in > 0 || rep.tokens_out > 0) && <p className="muted small">{t("rep_tokens", { i: rep.tokens_in, o: rep.tokens_out })}</p>}

      <details className="glass"><summary><b>{t("rep_analysis_title")}</b></summary>
        <ul>{d.phases.map((p, i) => <li key={i}>{d.procedure.phases[p.phase]?.name[lang]}: {fmtTime(p.start)} - {fmtTime(p.end)}</li>)}
          {d.usage.filter((u) => u.active_seconds > 0).map((u, i) => <li key={"u" + i}>{u.instrument}: {Math.round(u.active_seconds)} s ({u.pct_of_case}%)</li>)}</ul>
        {!d.phases.length && !d.usage.length && t("none")}
      </details>
      <details className="glass" open={d.notes.length > 0}><summary><b>{t("rep_notes_title")}</b></summary>
        {d.notes.length ? d.notes.map((n) => <div key={n.id}><span className="mono">{fmtTime(n.t)}</span> <b>{n.author}</b>: {n.text}</div>) : t("none")}
      </details>

      <label className="f">{t("rep_doctor_comments")}</label>
      <textarea rows={4} disabled={final} value={content.doctor_comments ?? ""} onChange={(e) => setContent({ ...content, doctor_comments: e.target.value })} />

      <h3 style={{ margin: "18px 0 8px", display: "flex", gap: 8, alignItems: "center" }}><Bot className="ic" />{t("rep_ai_section")}</h3>
      {ai ? (
        <div className="glass">
          <p className="muted small">{t("rep_ai_label", { model: ai.model ?? "" })}</p>
          <label className="f">{t("rep_summary")}</label>
          <textarea rows={5} disabled={final} value={ai.summary} onChange={(e) => setAi({ summary: e.target.value })} />
          <label className="f">{t("rep_observations")}</label>
          {ai.observations.map((o, k) => (
            <div className="row" key={k} style={{ marginBottom: 6 }}>
              <div className="grow">
                <input type="text" disabled={final} value={o.text} onChange={(e) => setAi({ observations: ai.observations.map((x, j) => (j === k ? { ...x, text: e.target.value } : x)) })} />
                <span className="muted small">{t("rep_evidence")}: {o.evidence.join(", ")}</span>
              </div>
              {!final && <button className="btn sm" onClick={() => setAi({ observations: ai.observations.filter((_, j) => j !== k) })}>{t("rep_remove")}</button>}
            </div>
          ))}
          <label className="f">{t("rep_limitations")}</label>
          <textarea rows={3} disabled={final} value={ai.limitations} onChange={(e) => setAi({ limitations: e.target.value })} />
        </div>
      ) : <p className="muted">{t("rep_no_ai_yet")}</p>}

      <h3 style={{ margin: "18px 0 8px", display: "flex", gap: 8, alignItems: "center" }}><ImageIcon className="ic" />{t("rep_frames")}</h3>
      <div className="cards">
        {(content.frames ?? []).map((fr, k) => (
          <div className="glass" key={k} style={{ padding: 10 }}>
            <img src={`/api/cases/${id}/report/frame?t=${fr.t}`} alt="" style={{ width: "100%", borderRadius: 10 }} />
            <div className="small">{fmtTime(fr.t)} {fr.caption}</div>
            {!final && <button className="btn sm" onClick={() => setContent({ ...content, frames: (content.frames ?? []).filter((_, j) => j !== k) })}>{t("rep_remove")}</button>}
          </div>
        ))}
      </div>
      {!final && <button className="btn sm" onClick={() => setContent({ ...content, frames: [...(content.frames ?? []), { t: Math.round(now * 10) / 10, caption: "Selected by doctor" }].sort((a, b) => a.t - b.t) })}>{t("rep_add_frame", { t: fmtTime(now) })}</button>}

      {!final && <p><label><input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} /> {t("rep_approve_check")}</label></p>}
      {err && <Alert kind="err">{err}</Alert>}
      {saved && <p className="muted">{t("rep_saved")}</p>}
      <div className="row" style={{ marginTop: 10 }}>
        {!final && <button className="btn" disabled={!!busy} onClick={() => save(false)}>{t("rep_save")}</button>}
        {!final && <button className="btn primary" disabled={!!busy || !agree} onClick={() => save(true)}>{t("rep_approve")}</button>}
        {!final && d.can_ai && <button className="btn" disabled={!res.ai.ok || !!busy} onClick={() => run("gen", () => api.post<Rep>(`/api/cases/${id}/report/generate`, { lang, with_ai: true }))}>{t("rep_regenerate")}</button>}
        {final && d.can_ai && <button className="btn" disabled={!!busy} onClick={() => run("reopen", () => api.post<Rep>(`/api/cases/${id}/report/reopen`))}>{t("rep_reopen")}</button>}
        <a href={`/api/cases/${id}/report.pdf?lang=${lang}`} download><button className="btn"><Download className="ic" />{t("rep_download")}</button></a>
      </div>
      {busy === "gen" && <Spinner label={t("rep_generating")} />}
      {final && <p className="muted small">{t("rep_final_locked")}</p>}
    </div>
  );
}

// ---------------------------------------------------------------- related literature
interface Ref {
  pmid: string; title: string; authors: string[]; journal: string; date: string; doi: string; topic: string; matched: string[];
  category: string; url: string; summary: string;
}

export function ResourcesTab({ d }: { d: Detail }) {
  const { t } = useI18n();
  const id = d.case.id;
  const [items, setItems] = useState<Ref[] | null>(null);
  const [at, setAt] = useState<number | null>(null);
  const [custom, setCustom] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [hide, setHide] = useState<Set<string>>(new Set());
  const load = useCallback(() => api.get<{ items: Ref[] | null; fetched_at: number | null }>(`/api/cases/${id}/refs`).then((r) => { setItems(r.items); setAt(r.fetched_at); }), [id]);
  useEffect(() => { void load(); }, [load]);
  const search = async (refresh: boolean) => {
    setBusy(true); setErr("");
    try { const r = await api.post<{ items: Ref[]; fetched_at: number }>(`/api/cases/${id}/refs/search`, { custom, refresh }); setItems(r.items); setAt(r.fetched_at); setCustom(""); }
    catch (e) { setErr(t("res_error", { e: errText(e) })); } finally { setBusy(false); }
  };
  const cats = [...new Set((items ?? []).map((i) => i.category))].sort();
  return (
    <div>
      <p className="muted small">{t("res_source_note")}</p>
      {d.can_ai && (
        <>
          <div className="row">
            <button className="btn primary" disabled={busy} onClick={() => search(true)}>{items ? t("res_refresh") : t("res_find")}</button>
            <div className="grow"><input type="text" placeholder={t("res_custom")} value={custom} onChange={(e) => setCustom(e.target.value)} /></div>
            <button className="btn" disabled={busy || !custom.trim()} onClick={() => search(false)}>{t("res_custom_btn")}</button>
          </div>
          {busy && <Spinner label={t("res_searching")} />}
        </>
      )}
      {err && <Alert kind="err">{err}</Alert>}
      {items === null ? <Alert>{t("res_none")}</Alert> : items.length === 0 ? <Alert>{t("res_empty")}</Alert> : (
        <>
          <p className="muted small">{t("res_fetched", { n: items.length, d: at ? new Date(at * 1000).toLocaleString() : "" })}</p>
          <div className="row" style={{ marginBottom: 10 }}>
            {cats.map((c) => <label key={c}><input type="checkbox" checked={!hide.has(c)} onChange={() => setHide((h) => { const n = new Set(h); if (n.has(c)) n.delete(c); else n.add(c); return n; })} /> {t("res_cat_" + c)}</label>)}
          </div>
          {items.filter((r) => !hide.has(r.category)).map((r) => (
            <div className="ref" key={r.pmid}>
              <a href={r.url} target="_blank" rel="noreferrer"><b>{r.title}</b></a>
              <div className="muted small">{r.authors.slice(0, 5).join(", ")}{r.authors.length > 5 ? " et al." : ""} · {r.journal} · {r.date} · PMID {r.pmid} · {t("res_cat_" + r.category)}</div>
              <p>{r.summary || t("res_no_abstract")}</p>
              <div className="muted small"><b>{t("res_relevance")}:</b> {t("res_found_for", { topic: r.topic })}. {r.matched.length ? t("res_matched", { terms: r.matched.join(", ") }) : t("res_no_match")}</div>
              <a href={r.url} target="_blank" rel="noreferrer">{t("res_open")}</a>{r.doi && <> · <a href={`https://doi.org/${r.doi}`} target="_blank" rel="noreferrer">DOI</a></>}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- research assistant
interface Msg { id: number; role: "user" | "assistant"; content: string; sources: { label: string; text: string }[]; tokens_in: number; tokens_out: number }

export function AssistantTab({ d }: { d: Detail }) {
  const { t } = useI18n();
  const id = d.case.id;
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [hasRefs, setHasRefs] = useState(true);
  const [ai, setAi] = useState<{ ok: boolean; reason: string }>({ ok: false, reason: "no_key" });
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  useEffect(() => {
    api.get<{ messages: Msg[]; has_refs: boolean }>(`/api/cases/${id}/chat`).then((r) => { setMsgs(r.messages); setHasRefs(r.has_refs); });
    api.get<RepResp>(`/api/cases/${id}/report`).then((r) => setAi(r.ai));
  }, [id]);
  if (!d.can_ai) return <Alert>{t("ai_doctors_only")}</Alert>;
  const send = async (text: string) => {
    if (!text.trim()) return;
    setBusy(true); setErr(""); setQ("");
    setMsgs((m) => [...m, { id: -1, role: "user", content: text, sources: [], tokens_in: 0, tokens_out: 0 }]);
    try { setMsgs((await api.post<{ messages: Msg[] }>(`/api/cases/${id}/chat`, { question: text })).messages); }
    catch (e) { setErr(errText(e)); } finally { setBusy(false); }
  };
  return (
    <div>
      <AiBanner ai={ai} />
      <p className="muted small">{t("chat_disclaimer")}</p>
      {!hasRefs && <p className="muted small">{t("chat_no_refs")}</p>}
      <div className="row">{[1, 2, 3, 4].map((k) => <button key={k} className="btn sm" disabled={!ai.ok || busy} onClick={() => send(t(`chat_s${k}`))}>{t(`chat_s${k}`)}</button>)}</div>
      <div className="chat">
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.content}
            {m.role === "assistant" && (m.sources.length > 0 ? (
              <details style={{ marginTop: 8 }}><summary className="small">{t("chat_sources")}</summary>
                {m.sources.map((s) => <div key={s.label} className="small"><b>[{s.label}]</b> {s.text}</div>)}</details>
            ) : !m.content.startsWith("⚠️") && <div className="muted small" style={{ marginTop: 6 }}>{t("chat_uncited")}</div>)}
            {m.tokens_in > 0 && <div className="muted small">{t("chat_tokens", { i: m.tokens_in, o: m.tokens_out })}</div>}
          </div>
        ))}
        {busy && <Spinner label={t("chat_thinking")} />}
      </div>
      {err && <Alert kind="err">{err}</Alert>}
      <form className="row" onSubmit={(e) => { e.preventDefault(); void send(q); }}>
        <div className="grow"><input type="text" disabled={!ai.ok || busy} placeholder={t("chat_input")} value={q} onChange={(e) => setQ(e.target.value)} /></div>
        <button className="btn primary" type="submit" disabled={!ai.ok || busy || !q.trim()} aria-label="Send"><Send className="ic" /></button>
        {msgs.length > 0 && <button type="button" className="btn" onClick={async () => { await api.del(`/api/cases/${id}/chat`); setMsgs([]); }}><Trash2 className="ic" />{t("chat_clear")}</button>}
      </form>
    </div>
  );
}
