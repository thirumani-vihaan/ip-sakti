import { useState } from "react";
import { postRoadmap } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";

export function RoadmapPanel() {
  const [q, setQ] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    if (!q.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      setRes(await postRoadmap(q, { jurisdiction: "india" }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="section-head">
        <h2>IP roadmap</h2>
        <p>A prioritised, cited walkthrough across patentability &amp; TK-risk, Access &amp; Benefit-Sharing, and brand / GI protection for your idea.</p>
      </div>
      <div className="card">
        <div className="composer">
          <input value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()}
            placeholder="Describe your product or idea..." />
          <button className="btn" onClick={run} disabled={busy}>{busy ? "Building..." : "Build roadmap"}</button>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {res && (
        <div className="roadmap-steps">
          {res.steps.map((s, i) => (
            <div className="step" key={i}>
              <div className="step-num">{i + 1}</div>
              <div>
                <div className="step-title">{s.title}</div>
                <ChatMessage response={s.answer} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
