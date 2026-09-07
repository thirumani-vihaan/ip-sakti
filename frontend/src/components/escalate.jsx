import { useState } from "react";
import { postEscalate } from "../api/client.js";

export function EscalateModal({ query, onClose }) {
  const [contact, setContact] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError("");
    try {
      setResult(await postEscalate({ query, contact: contact || undefined }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-scrim" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Escalate to a human IP facilitator">
        <h3>Escalate to a human IP facilitator</h3>
        {!result ? (
          <>
            <p className="muted" style={{ marginTop: 0 }}>
              We will prepare a referral for a human facilitator. An optional contact is echoed back for your reference only and is not stored.
            </p>
            <p style={{ fontSize: 13 }}><strong>Query:</strong> {query}</p>
            <input type="text" placeholder="Optional: your email or phone" value={contact}
              onChange={(e) => setContact(e.target.value)} />
            {error && <p className="error" style={{ marginTop: 10 }}>{error}</p>}
            <div className="msg-actions" style={{ marginTop: 14 }}>
              <button className="btn" onClick={submit} disabled={busy}>{busy ? "Preparing..." : "Prepare referral"}</button>
              <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
            </div>
          </>
        ) : (
          <>
            <p style={{ marginTop: 0 }}>Your reference id:</p>
            <p className="ref-id">{result.reference_id}</p>
            <p style={{ marginTop: 12 }}>{result.message}</p>
            <p style={{ marginTop: 8 }}><strong>{result.facilitator}</strong></p>
            <ul style={{ fontSize: 13, color: "var(--muted)" }}>
              {result.next_steps.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
            <div className="msg-actions"><button className="btn" onClick={onClose}>Done</button></div>
          </>
        )}
      </div>
    </div>
  );
}
