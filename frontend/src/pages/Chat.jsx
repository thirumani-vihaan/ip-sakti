import { useEffect, useState } from "react";
import { postChat, exportPdf } from "../api/client.js";
import { ChatMessage } from "../components/chat.jsx";
import { EscalateModal } from "../components/escalate.jsx";

const HISTORY_KEY = "ipsakti_history_v1";
const EXAMPLES = [
  "Can I patent a modified Triphala formulation?",
  "Do I need NBA approval to sell a herbal extract commercially?",
  "How do I protect a regional Ayurvedic product name?",
];

export default function Chat({ api = postChat }) {
  const [q, setQ] = useState("");
  const [messages, setMessages] = useState([]);
  const [jur, setJur] = useState("india");
  const [sensitive, setSensitive] = useState(false);
  const [lang, setLang] = useState("en");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [escalateQuery, setEscalateQuery] = useState(null);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      if (Array.isArray(saved)) setMessages(saved);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(messages.slice(-20)));
    } catch { /* ignore */ }
  }, [messages]);

  async function ask(text) {
    const query = (text ?? q).trim();
    if (!query || busy) return;
    setError("");
    setBusy(true);
    try {
      const resp = await api(query, { jurisdiction: jur, sensitive, language: lang });
      setMessages((m) => [...m, { q: query, resp }]);
      setQ("");
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  function send() {
    return ask();
  }

  async function handleExport(resp) {
    try {
      const blob = await exportPdf(resp);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ip-sakti-answer.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  }

  function clearHistory() {
    setMessages([]);
    try { localStorage.removeItem(HISTORY_KEY); } catch { /* ignore */ }
  }

  return (
    <div className="chat">
      <div className="controls">
        <button className="chip-toggle" data-testid="jur-toggle" aria-pressed={jur === "international"}
          onClick={() => setJur(jur === "india" ? "international" : "india")}>
          Jurisdiction: {jur}
        </button>
        <label>
          Language{" "}
          <select data-testid="lang-select" value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="te">Telugu</option>
            <option value="auto">Auto-detect</option>
          </select>
        </label>
        <label>
          <input type="checkbox" checked={sensitive} data-testid="sensitive-toggle"
            onChange={(e) => setSensitive(e.target.checked)} />
          Sensitive-Invention mode
        </label>
        {messages.length > 0 && (
          <button className="btn btn-ghost btn-sm" onClick={clearHistory} style={{ marginLeft: "auto" }}>
            Clear history
          </button>
        )}
      </div>

      {messages.length === 0 && (
        <div className="card" style={{ background: "var(--surface-2)" }}>
          <p className="muted" style={{ marginTop: 0 }}>Try an example:</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {EXAMPLES.map((ex) => (
              <button key={ex} className="chip-toggle" onClick={() => ask(ex)}>{ex}</button>
            ))}
          </div>
        </div>
      )}

      <div className="log">
        {error && (
          <p className="error" data-testid="chat-error" role="alert">{error}</p>
        )}
        {messages.map((m, i) => (
          <div className="qa" key={i}>
            <p className="q">{m.q}</p>
            <ChatMessage response={m.resp} onExport={handleExport} onEscalate={() => setEscalateQuery(m.q)} />
          </div>
        ))}
      </div>

      <div className="composer">
        <input value={q} onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about Ayurveda IP, ABS, or regulation..." />
        <button className="btn" onClick={send} disabled={busy}>{busy ? "Asking..." : "Ask"}</button>
      </div>

      {escalateQuery !== null && (
        <EscalateModal query={escalateQuery} onClose={() => setEscalateQuery(null)} />
      )}
    </div>
  );
}
