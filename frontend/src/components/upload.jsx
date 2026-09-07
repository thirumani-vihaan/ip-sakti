import { useRef, useState } from "react";
import { postAnalyze } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";

export function UploadPanel() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [res, setRes] = useState(null);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef();

  async function handleFile(file) {
    if (!file) return;
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
    <div className="panel">
      <div className="section-head">
        <h2>Analyze a document</h2>
        <p>
          Upload a product label, brochure or draft (PDF / TXT / HTML). The text is extracted and checked against
          the official corpus. Your file is analysed once and never added to the knowledge base.
        </p>
      </div>
      <div className={`dropzone ${drag ? "drag" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}>
        <button className="btn" onClick={() => inputRef.current && inputRef.current.click()} disabled={busy}>
          {busy ? "Analyzing..." : "Choose a file"}
        </button>
        <input ref={inputRef} type="file" accept=".pdf,.txt,.md,.html,.htm" style={{ display: "none" }}
          onChange={(e) => { handleFile(e.target.files[0]); e.target.value = ""; }} />
        <p className="hint">or drag &amp; drop — PDF, TXT, HTML (max 5 MB)</p>
      </div>
      {error && <p className="error">{error}</p>}
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
