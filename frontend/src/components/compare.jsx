import { useState } from "react";
import { postCompare } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";

export function CompareTool({ submit = (a, b, opts) => postCompare(a, b, opts) }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [jurA, setJurA] = useState("india");
  const [jurB, setJurB] = useState("india");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    setBusy(true);
    setError("");
    try {
      setRes(await submit(a, b, { jurisdiction_a: jurA, jurisdiction_b: jurB }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="compare">
      <div className="grid-2">
        <div>
          <input data-testid="cmp-a" value={a} onChange={(e) => setA(e.target.value)} placeholder="Option A" />
          <label className="field" style={{ marginTop: 8 }}>
            Jurisdiction A
            <select data-testid="cmp-jur-a" value={jurA} onChange={(e) => setJurA(e.target.value)}>
              <option value="india">India</option>
              <option value="international">International</option>
            </select>
          </label>
        </div>
        <div>
          <input data-testid="cmp-b" value={b} onChange={(e) => setB(e.target.value)} placeholder="Option B" />
          <label className="field" style={{ marginTop: 8 }}>
            Jurisdiction B
            <select data-testid="cmp-jur-b" value={jurB} onChange={(e) => setJurB(e.target.value)}>
              <option value="india">India</option>
              <option value="international">International</option>
            </select>
          </label>
        </div>
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
