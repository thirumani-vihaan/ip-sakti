import { useState } from "react";
import { postCompare } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";

export function CompareTool({ submit = (a, b) => postCompare(a, b) }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    setBusy(true);
    setError("");
    try {
      setRes(await submit(a, b));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="compare">
      <div className="grid-2">
        <input data-testid="cmp-a" value={a} onChange={(e) => setA(e.target.value)} placeholder="Option A" />
        <input data-testid="cmp-b" value={b} onChange={(e) => setB(e.target.value)} placeholder="Option B" />
      </div>
      <div style={{ marginTop: 12 }}>
        <button className="btn" data-testid="compare-run" onClick={run} disabled={busy}>
          {busy ? "Comparing..." : "Compare"}
        </button>
      </div>
      {error && <p className="error" style={{ marginTop: 12 }}>{error}</p>}
      {res && (
        <div className="cmp-grid">
          <div>
            <h4>Option A</h4>
            <span className={`jur-tag jur-${res.a.jurisdiction}`}>{res.a.jurisdiction}</span>
            <ChatMessage response={res.a} />
          </div>
          <div>
            <h4>Option B</h4>
            <span className={`jur-tag jur-${res.b.jurisdiction}`}>{res.b.jurisdiction}</span>
            <ChatMessage response={res.b} />
          </div>
        </div>
      )}
    </div>
  );
}
