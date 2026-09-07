import { useState } from "react";

const _EV_DESC = { high: "Strong support", moderate: "Some support", limited: "Weak / uncertain" };
const DISCLAIMER = "Informational guidance, not legal advice. Consult a qualified professional.";

export function EvidenceStrengthBadge({ level }) {
  return (
    <span className={`badge ev-${level}`} data-testid="evidence-strength" title={_EV_DESC[level] || ""}>
      Evidence: {level}
    </span>
  );
}

export function LawAsOfBadge({ asOf }) {
  return <span className="badge asof" data-testid="law-as-of">law as of {asOf}</span>;
}

export function AnswerModeBadge({ mode }) {
  return <span className="badge mode" data-testid="answer-mode">{mode}</span>;
}

export function AbstentionNotice({ warnings }) {
  return (
    <div className="abstain" data-testid="abstention">
      <strong>No citation-supported answer.</strong>
      <ul>
        {warnings.map((w, i) => (
          <li key={i}>[{w.code}] {w.message}</li>
        ))}
      </ul>
    </div>
  );
}

export function SourceDrawer({ source, onClose }) {
  if (!source) return null;
  return (
    <>
      <div className="drawer-scrim" onClick={onClose} />
      <aside className="drawer" data-testid="source-drawer" role="dialog" aria-label="Source passage">
        <button className="close-x" onClick={onClose} aria-label="close">x</button>
        <h3>{source.title} {source.section || ""}</h3>
        <p className="meta">{source.status} - law as of {source.as_of} - {source.authority}</p>
        <pre className="excerpt">{source.local_excerpt}</pre>
        {source.url && (
          <p style={{ marginTop: 12 }}>
            <a href={source.url} target="_blank" rel="noreferrer">Open official source</a>
          </p>
        )}
      </aside>
    </>
  );
}

function hasEscalation(response) {
  return (response.warnings || []).some((w) => w.code === "escalate_available");
}

export function ChatMessage({ response, onEscalate, onExport }) {
  const [open, setOpen] = useState(null);
  const byId = Object.fromEntries((response.sources || []).map((s) => [s.id, s]));
  const escalate = hasEscalation(response);

  if (!response.claims || response.claims.length === 0) {
    return (
      <div className="message" data-testid="chat-message">
        <AbstentionNotice warnings={response.warnings || []} />
        <div className="badges" style={{ marginTop: 10, marginBottom: 0 }}>
          <LawAsOfBadge asOf={response.as_of} />
        </div>
        {escalate && onEscalate && (
          <div className="escalate-cta">
            <span>This is out-of-scope or low-confidence - a human IP facilitator can help.</span>
            <button className="btn btn-accent btn-sm" onClick={onEscalate}>Escalate to a facilitator</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="message" data-testid="chat-message">
      <div className="badges">
        <EvidenceStrengthBadge level={response.evidence_strength} />
        <AnswerModeBadge mode={response.answer_mode} />
        <LawAsOfBadge asOf={response.as_of} />
      </div>
      {response.claims.map((c, i) => (
        <p key={i} className="claim">
          {c.text}{" "}
          {c.source_ids.map((sid) => (
            <button
              key={sid}
              className="cite"
              data-testid={`cite-${sid}`}
              onClick={() => setOpen(byId[sid])}
            >
              [{sid}]
            </button>
          ))}
        </p>
      ))}
      <div className="answer-note">{DISCLAIMER}</div>
      <div className="msg-actions">
        {onExport && (
          <button className="btn btn-ghost btn-sm" onClick={() => onExport(response)}>Download PDF</button>
        )}
        {escalate && onEscalate && (
          <button className="btn btn-accent btn-sm" onClick={onEscalate}>Escalate to a facilitator</button>
        )}
      </div>
      <SourceDrawer source={open} onClose={() => setOpen(null)} />
    </div>
  );
}
