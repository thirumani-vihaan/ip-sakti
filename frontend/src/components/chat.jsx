import { useState } from "react";

export function EvidenceStrengthBadge({ level }) {
  const color = { high: "#00c26e", moderate: "#ff7a1a", limited: "#777" }[level] || "#777";
  return (
    <span className="badge" style={{ background: color }} data-testid="evidence-strength">
      Evidence: {level}
    </span>
  );
}

export function LawAsOfBadge({ asOf }) {
  return <span className="badge" data-testid="law-as-of">law as of {asOf}</span>;
}

export function AnswerModeBadge({ mode }) {
  return <span className="badge" data-testid="answer-mode">{mode}</span>;
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
    <aside className="drawer" data-testid="source-drawer">
      <button onClick={onClose} aria-label="close">x</button>
      <h3>{source.title} {source.section || ""}</h3>
      <p className="meta">{source.status} · law as of {source.as_of} · {source.authority}</p>
      <pre className="excerpt">{source.local_excerpt}</pre>
      {source.url && (
        <a href={source.url} target="_blank" rel="noreferrer">official source</a>
      )}
    </aside>
  );
}

export function ChatMessage({ response }) {
  const [open, setOpen] = useState(null);
  const byId = Object.fromEntries((response.sources || []).map((s) => [s.id, s]));

  if (!response.claims || response.claims.length === 0) {
    return (
      <div className="message">
        <AbstentionNotice warnings={response.warnings || []} />
        <div className="badges"><LawAsOfBadge asOf={response.as_of} /></div>
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
      <SourceDrawer source={open} onClose={() => setOpen(null)} />
    </div>
  );
}
