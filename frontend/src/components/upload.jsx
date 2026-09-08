import { useRef, useState } from "react";
import { postAnalyze } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";
import { Icon } from "./ui.jsx";

export function UploadPanel() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [res, setRes] = useState(null);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef();

  async function handleFile(file) {
    if (!file || busy) return;
    if (file.size > 5 * 1024 * 1024) { setError("Please choose a file no larger than 5 MB."); return; }
    setBusy(true);
    setError("");
    setRes(null);
    try {
      setRes(await postAnalyze(file, "india"));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel tool-panel">
      <div className="section-head">
        <div className="eyebrow"><span className="section-number">06</span>FROM DOCUMENT TO EVIDENCE</div>
        <h1>A second look. A grounded perspective.</h1>
        <p>
          Upload a product label, brochure or draft (PDF / TXT / HTML). The text is extracted and checked against
          the official corpus. Your file is analysed once and never added to the knowledge base.
        </p>
      </div>
      <div className={`dropzone ${drag ? "drag" : ""}`}
        aria-busy={busy}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}>
        <div className="upload-illustration"><Icon name="book" /><span><Icon name="search" /></span></div>
        <h2>Bring your document to the research desk.</h2>
        <p className="muted">A product label, a brochure, or your next idea.<br />We’ll look for the evidence behind it.</p>
        <button className="btn btn-accent" onClick={() => inputRef.current && inputRef.current.click()} disabled={busy}>
          <Icon name="upload" />
          {busy ? "Analyzing..." : "Choose a file"}
        </button>
        <input ref={inputRef} type="file" aria-label="Document to analyze" accept=".pdf,.txt,.md,.html,.htm" style={{ display: "none" }}
          onChange={(e) => { handleFile(e.target.files[0]); e.target.value = ""; }} />
        <p className="hint">or drag &amp; drop · PDF, TXT, Markdown, HTML · Up to 5 MB</p>
      </div>
      <div className="upload-assurances"><span><Icon name="lock" />Analyzed once</span><span><Icon name="shield" />Not added to the corpus</span><span><Icon name="book" />Source-linked analysis</span></div>
      {error && <p className="error" role="alert">{error}</p>}
      {res && (
        <div className="card">
          <p className="muted" style={{ marginTop: 0 }}>Extracted from <strong>{res.filename}</strong>:</p>
          <div className="preview">{res.extracted_preview}...</div>
          <h4 style={{ marginTop: 16 }}>Grounded analysis</h4>
          <ChatMessage response={res.analysis} />
        </div>
      )}
    </div>
  );
}
