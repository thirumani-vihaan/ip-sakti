import { useState } from "react";
import { Icon, useDialog } from "./ui.jsx";

const EV_DESC = { high: "Strong source support, not a guarantee of legal applicability", moderate: "Some source support; review the cited passages", limited: "Limited or uncertain source support" };
const DISCLAIMER = "Informational guidance, not legal advice. Consult a qualified professional.";

export function EvidenceStrengthBadge({ level }) {
  return <span className={`badge ev-${level}`} data-testid="evidence-strength" title={EV_DESC[level] || ""}><Icon name={level === "high" ? "shield" : "info"} />Evidence: {level || "unavailable"}</span>;
}
export function LawAsOfBadge({ asOf }) {
  return <span className="badge asof" data-testid="law-as-of">Current Law</span>;
}
export function AnswerModeBadge({ mode }) {
  return <span className="badge mode" data-testid="answer-mode">{mode?.replace(/_/g, " ") || "mode unavailable"}</span>;
}
export function AbstentionNotice({ warnings }) {
  return <div className="abstain" data-testid="abstention"><span className="abstain-icon"><Icon name="shield" /></span><div><div className="eyebrow">A SAFER ANSWER IS AN HONEST LIMIT</div><h3>No citation-supported answer.</h3><p>There isn’t enough evidence in the available corpus to answer responsibly. Rather than guess, we’ll stop here.</p>{warnings.length > 0 && <details className="warning-details"><summary>Why we paused</summary><ul>{warnings.map((w, i) => <li key={i}><span>{w.code}</span>{w.message}</li>)}</ul></details>}</div></div>;
}
export function SourceDrawer({ source, onClose }) {
  const ref = useDialog(onClose, !!source);
  if (!source) return null;
  return <><div className="drawer-scrim" onClick={onClose} /><aside ref={ref} tabIndex={-1} className="drawer" data-testid="source-drawer" role="dialog" aria-modal="true" aria-label="Source passage"><button className="close-x" onClick={onClose} aria-label="close"><Icon name="close" /></button><div className="eyebrow"><Icon name="book" />THE SOURCE, NOT A SUMMARY</div><h2>{source.title}</h2><div className="badges"><span className={`pill ${source.status}`}>{source.status?.replace(/_/g, " ")}</span><span className="badge asof">{source.authority}</span></div><dl className="source-metadata"><div><dt>Section</dt><dd>{source.section || "Whole document"}</dd></div><div><dt>Law as of</dt><dd>{source.as_of}</dd></div><div><dt>Effective date</dt><dd>{source.effective_date || "Not specified"}</dd></div></dl><div className="excerpt-heading">EXACT CORPUS PASSAGE</div><blockquote className="excerpt">{source.local_excerpt}</blockquote><div className="source-id">Source ID · {source.id}</div>{source.document_hash && <details className="source-hash"><summary>Document fingerprint</summary><code>{source.document_hash}</code></details>}{source.url && <a className="btn btn-ghost official-link" href={source.url} target="_blank" rel="noreferrer">Open official source<Icon name="external" /></a>}<p className="small">The passage is available locally. Opening the official website requires an internet connection.</p></aside></>;
}

export function ChatMessage({ response, onEscalate, onExport }) {
  const [open, setOpen] = useState(null);
  const byId = Object.fromEntries((response.sources || []).map((s) => [s.id, s]));
  const claims = (response.claims || []).filter((c) => c.source_ids?.length && c.source_ids.every((id) => byId[id]));
  const missingCitations = claims.length !== (response.claims || []).length;
  const warnings = [...(response.warnings || []), ...(missingCitations ? [{ code: "missing_citation", message: "A claim was withheld because its supporting source is unavailable." }] : [])];
  const escalate = warnings.some((w) => w.code === "escalate_available");
  return (
    <article className={`message ${claims.length ? "grounded-message" : "abstained-message"}`} data-testid="chat-message">
      <div className="answer-heading"><span className="answer-mark"><Icon name={claims.length ? "spark" : "shield"} /></span><div><strong>{claims.length ? "Source-grounded guidance" : "Evidence comes first."}</strong><span>{claims.length ? `${claims.length} cited ${claims.length === 1 ? "claim" : "claims"} · ${response.jurisdiction || "unspecified jurisdiction"}` : "No speculation. No unsupported claims."}</span></div></div>
      <div className="badges"><EvidenceStrengthBadge level={response.evidence_strength} /><AnswerModeBadge mode={response.answer_mode} /><LawAsOfBadge asOf={response.as_of} /></div>
      {claims.length ? <div className="claims">{claims.map((claim, i) => <section className="claim" key={i}><div className="claim-index"><span>{String(i + 1).padStart(2, "0")}</span><span>CITED CLAIM</span></div><p lang={response.language === "auto" ? undefined : response.language}>{claim.text}</p><div className="citation-thread"><span className="thread-label"><Icon name="book" />SUPPORTED BY</span><div className="citation-chips">{claim.source_ids.map((sid) => <button key={sid} className="cite" data-testid={`cite-${sid}`} onClick={() => setOpen(byId[sid])} title={`Read exact passage: ${byId[sid].title}`}><span>{byId[sid].title}</span><Icon name="arrow" /></button>)}</div></div></section>)}</div> : <AbstentionNotice warnings={warnings} />}
      {claims.length > 0 && warnings.length > 0 && <div className="answer-warnings">{warnings.map((w, i) => <p key={i}><Icon name="info" /><span>{w.message}</span></p>)}</div>}
      {!claims.length && escalate && onEscalate && <div className="escalate-cta"><div><strong>A human can help with the next step.</strong><p>Prepare a referral to an IP facilitator.</p></div><button className="btn btn-accent btn-sm" onClick={onEscalate}>Escalate to a facilitator<Icon name="arrow" /></button></div>}
      <div className="answer-note"><Icon name="shield" />{DISCLAIMER}</div>
      <div className="msg-actions">{onExport && claims.length > 0 && <button className="btn btn-ghost btn-sm" onClick={() => onExport(missingCitations ? { ...response, claims, warnings } : response)}><Icon name="download" />Download PDF</button>}{claims.length > 0 && escalate && onEscalate && <button className="btn btn-accent btn-sm" onClick={onEscalate}>Escalate to a facilitator<Icon name="arrow" /></button>}<span className="corpus-note">Corpus {response.corpus_version || "unavailable"}</span></div>
      <SourceDrawer source={open} onClose={() => setOpen(null)} />
    </article>
  );
}
