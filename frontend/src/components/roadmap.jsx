import { useState } from "react";
import { postRoadmap } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";
import { Icon } from "./ui.jsx";

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
    <div className="panel tool-panel">
      <div className="section-head">
        <div className="eyebrow"><span className="section-number">05</span>YOUR IP ROADMAP</div>
        <h1>A thoughtful path from idea to action.</h1>
        <p>A prioritised, cited walkthrough across patentability &amp; TK-risk, Access &amp; Benefit-Sharing, and brand / GI protection for your idea.</p>
      </div>
      <form className="card roadmap-composer" onSubmit={(e) => { e.preventDefault(); run(); }}>
        <label className="field" htmlFor="roadmap-query">Start with your idea</label>
        <textarea id="roadmap-query" value={q} onChange={(e) => setQ(e.target.value)} rows={3} maxLength={2000} placeholder="Describe your product or idea..." />
        <div className="form-actions"><span><Icon name="globe" />India · Three perspectives, one roadmap</span><button type="submit" className="btn btn-accent" disabled={busy || !q.trim()}>{busy ? "Building..." : "Build roadmap"}<Icon name="route" /></button></div>
      </form>
      {!res && <div className="roadmap-preview">{[["shield", "Patentability & TK", "Understand the traditional-knowledge boundary."], ["leaf", "Access & benefit-sharing", "Identify biological-resource obligations."], ["globe", "Brand & GI protection", "Explore protection for identity and origin."]].map(([icon, title, text], i) => <div key={title}><span className="step-num">{String(i + 1).padStart(2, "0")}</span><Icon name={icon} /><h3>{title}</h3><p>{text}</p></div>)}</div>}
      {error && <p className="error" role="alert">{error}</p>}
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
