import { useEffect, useState } from "react";
import { postChat, exportPdf } from "../api/client.js";
import { ChatMessage, SourceDrawer } from "../components/chat.jsx";
import { EscalateModal } from "../components/escalate.jsx";
import { Icon } from "../components/ui.jsx";

const HISTORY_KEY = "ipsakti_history_v1";
const EXAMPLES = [
  { topic: "PATENTABILITY", icon: "shield", query: "Is a traditional-knowledge Ayurvedic formulation patentable under Section 3(p)?" },
  { topic: "BIODIVERSITY", icon: "leaf", query: "Do I need State Biodiversity Board approval to sell a biological resource commercially?" },
  { topic: "GEOGRAPHICAL INDICATIONS", icon: "globe", query: "How do I protect a regional product name with a geographical indication?" },
];

export default function Chat({ api = postChat, onConversationChange }) {
  const [q, setQ] = useState("");
  const [messages, setMessages] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      return Array.isArray(saved) ? saved.filter((m) => m && typeof m.q === "string" && m.resp && !m.sensitive).slice(-20) : [];
    } catch { return []; }
  });
  const [jur, setJur] = useState("india");
  const [sensitive, setSensitive] = useState(false);
  const [lang, setLang] = useState("en");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [escalateQuery, setEscalateQuery] = useState(null);
  const [ledgerSource, setLedgerSource] = useState(null);
  const latest = messages[messages.length - 1]?.resp;
  const Heading = messages.length ? "h1" : "h2";

  useEffect(() => { onConversationChange?.(messages.length > 0); }, [messages.length, onConversationChange]);
  useEffect(() => {
    try {
      // Sensitive-Invention conversations must never be persisted to disk.
      localStorage.setItem(HISTORY_KEY, JSON.stringify(messages.filter((m) => !m.sensitive).slice(-20)));
    } catch { /* Storage may be unavailable in private browsing. */ }
  }, [messages]);

  async function ask(text) {
    const query = (text ?? q).trim();
    if (!query || busy) return;
    setError("");
    setBusy(true);
    try {
      const resp = await api(query, { jurisdiction: jur, sensitive, language: lang });
      setMessages((m) => [...m, { q: query, resp, sensitive }]);
      setQ("");
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally { setBusy(false); }
  }
  async function handleExport(resp) {
    try {
      const blob = await exportPdf(resp);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "ip-sakti-answer.pdf";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch (err) { setError(err.message); }
  }
  function clearHistory() {
    setMessages([]);
    try { localStorage.removeItem(HISTORY_KEY); } catch { /* Storage may be unavailable. */ }
  }

  return (
    <div className="research-layout">
      <div className="chat">
        <div className="desk-heading">
          <div><div className="eyebrow"><span className="section-number">01</span>YOUR RESEARCH DESK</div><Heading>{messages.length ? "Follow the evidence." : "What would you like to protect?"}</Heading></div>
          {messages.length > 0 && <button className="btn btn-ghost btn-sm" onClick={clearHistory}>Clear history</button>}
        </div>
        {messages.length === 0 && <p className="desk-intro">Start with your question. Leave with a source you can check.</p>}
        <div className="log" role="log" aria-live="polite" aria-label="Conversation">
          {messages.map((m, i) => (
            <div className="qa" key={i}>
              <div className="question-heading"><span>YOUR QUESTION</span>{m.sensitive && <span><Icon name="lock" />Not saved</span>}</div>
              <p className="q">{m.q}</p>
              <ChatMessage response={m.resp} onExport={handleExport} onEscalate={() => setEscalateQuery(m.q)} />
            </div>
          ))}
        </div>
        {error && <div className="error" data-testid="chat-error" role="alert"><Icon name="info" /><div><strong>We couldn’t complete that request.</strong><p>{error}</p><span>Your question is still here. Please try again.</span></div></div>}
        {busy && <div className="loading-card" role="status"><span className="loading-orbit"><Icon name="search" /></span><div><strong>Following the citation thread…</strong><p>Checking the local corpus for supporting evidence.</p><div className="loading-lines"><i /><i /></div></div></div>}
        <form className={`ask-card ${busy ? "is-busy" : ""}`} onSubmit={(e) => { e.preventDefault(); ask(); }}>
          <label className="composer-label" htmlFor="question"><Icon name="spark" />{messages.length ? "CONTINUE YOUR RESEARCH" : "A GOOD QUESTION IS THE FIRST STEP"}</label>
          <textarea id="question" aria-label="Your Ayurveda IP or regulatory question" value={q} maxLength={2000} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); ask(); } }} placeholder="Ask about Ayurveda IP, ABS, or regulation..." rows={3} />
          <div className="composer-bottom">
            <div className="controls">
              <button type="button" className="chip-toggle" data-testid="jur-toggle" aria-pressed={jur === "international"} onClick={() => setJur(jur === "india" ? "international" : "india")} aria-label={`Jurisdiction: ${jur}. Switch jurisdiction`}><Icon name="globe" />{jur === "india" ? "India" : "International"}</button>
              <label className="language-control"><span className="sr-only">Language</span><span aria-hidden="true">अ / A</span><select data-testid="lang-select" value={lang} onChange={(e) => setLang(e.target.value)}><option value="en">English</option><option value="hi">हिन्दी · Hindi</option><option value="te">తెలుగు · Telugu</option><option value="auto">Auto-detect</option></select></label>
            </div>
            <button className="btn btn-accent ask-button" type="submit" disabled={busy || !q.trim()}><span>{busy ? "Asking..." : "Ask"}</span><Icon name="arrow" /></button>
          </div>
          <div className="privacy-row"><label><input type="checkbox" checked={sensitive} data-testid="sensitive-toggle" onChange={(e) => setSensitive(e.target.checked)} /><Icon name="lock" />Sensitive-Invention mode</label><span>{sensitive ? "This conversation won’t be saved" : "Enter to ask · Shift + Enter for a new line"}</span></div>
        </form>
        {lang !== "en" && <p className="language-note"><Icon name="info" />Offline: legal terms localised via glossary; full translation needs Bhashini. No external translation is called.</p>}
        {messages.length === 0 && (
          <section className="examples" aria-label="Example questions">
            <div className="examples-label"><span>A FEW USEFUL STARTING POINTS</span><span>Choose a question <Icon name="arrow" /></span></div>
            <div className="example-grid">{EXAMPLES.map((ex) => <button className="example-card" key={ex.topic} onClick={() => ask(ex.query)} disabled={busy}><span className="example-topic"><Icon name={ex.icon} />{ex.topic}</span><span className="example-question">{ex.query}</span><Icon name="arrow" className="example-arrow" /></button>)}</div>
          </section>
        )}
        <div className="workspace-footnote"><Icon name="shield" />Informational guidance only. Consult a qualified professional before acting.</div>
      </div>
      <aside className="research-aside">
        {latest?.sources?.length > 0 ? <div className="ledger"><div className="eyebrow"><Icon name="book" />CITATIONS LEDGER</div><h3>Go to the source.</h3><p className="small">Exact passages behind your latest answer.</p><ol>{latest.sources.map((source, i) => <li key={source.id}><button onClick={() => setLedgerSource(source)}><span className="ledger-number">{String(i + 1).padStart(2, "0")}</span><span><strong>{source.title}</strong><small>{source.authority?.replace(/_/g, " ")} · {source.status?.replace(/_/g, " ")}</small></span><Icon name="arrow" /></button></li>)}</ol><div className="ledger-version">CORPUS {latest.corpus_version} · AS OF {latest.as_of}</div></div> : <div className="evidence-standard"><div className="eyebrow"><Icon name="shield" />THE EVIDENCE STANDARD</div><h3>Confidence starts<br />with a citation.</h3><ol><li><span>01</span><div><strong>Grounded, not generated</strong><p>Guidance begins with the official, version-tracked corpus.</p></div></li><li><span>02</span><div><strong>Every claim, traceable</strong><p>Open a citation to read the exact supporting passage.</p></div></li><li><span>03</span><div><strong>A safe “I don’t know”</strong><p>No supporting evidence? We abstain and offer a human pathway.</p></div></li></ol><div className="standard-signoff"><Icon name="leaf" /><span>Less guesswork.<br /><em>More grounded decisions.</em></span></div></div>}
        <div className="offline-note"><span className="status-dot" /><div><strong>Local by design</strong><p>Offline fixture providers. No external AI calls. Sensitive mode keeps chats out of saved history.</p></div></div>
      </aside>
      <SourceDrawer source={ledgerSource} onClose={() => setLedgerSource(null)} />
      {escalateQuery !== null && <EscalateModal query={escalateQuery} onClose={() => setEscalateQuery(null)} />}
    </div>
  );
}
