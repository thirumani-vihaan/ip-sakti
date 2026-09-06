import { useState } from "react";
import { postChat } from "../api/client.js";
import { ChatMessage } from "../components/chat.jsx";

export default function Chat({ api = postChat }) {
  const [q, setQ] = useState("");
  const [messages, setMessages] = useState([]);
  const [jur, setJur] = useState("india");
  const [sensitive, setSensitive] = useState(false);
  const [lang, setLang] = useState("en");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!q.trim() || busy) return;
    setError("");
    setBusy(true);
    try {
      const resp = await api(q, { jurisdiction: jur, sensitive, language: lang });
      setMessages((m) => [...m, { q, resp }]);
      setQ("");
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat">
      <div className="controls">
        <button data-testid="jur-toggle" onClick={() => setJur(jur === "india" ? "international" : "india")}>
          Jurisdiction: {jur}
        </button>
        <label>
          Language{" "}
          <select data-testid="lang-select" value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="te">Telugu</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={sensitive}
            data-testid="sensitive-toggle"
            onChange={(e) => setSensitive(e.target.checked)}
          />{" "}
          Sensitive-Invention mode
        </label>
      </div>
      <div className="log">
        {error && (
          <p className="error" data-testid="chat-error" role="alert">
            {error}
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i}>
            <p className="q">{m.q}</p>
            <ChatMessage response={m.resp} />
          </div>
        ))}
      </div>
      <div className="composer">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about Ayurveda IP, ABS, or regulation..."
        />
        <button onClick={send} disabled={busy}>{busy ? "Asking…" : "Ask"}</button>
      </div>
    </div>
  );
}
