import { useState } from "react";
import Chat from "./pages/Chat.jsx";
import { CompareTool } from "./components/compare.jsx";
import { AbsWizard, ClassificationWizard } from "./components/wizard.jsx";
import { SourcesPanel } from "./components/sources.jsx";
import { UploadPanel } from "./components/upload.jsx";
import { RoadmapPanel } from "./components/roadmap.jsx";

const TABS = [
  ["assistant", "Assistant"],
  ["classify", "Classify"],
  ["abs", "ABS check"],
  ["compare", "Compare"],
  ["roadmap", "Roadmap"],
  ["analyze", "Analyze doc"],
  ["sources", "Sources"],
];

export default function App() {
  const [tab, setTab] = useState("assistant");
  return (
    <div className="app">
      <header className="site-header">
        <div className="container">
          <div className="brand">
            <div className="brand-mark">IP</div>
            <div>
              <div className="brand-name">IP-SAKTI Sahayak</div>
              <div className="brand-sub">Ayurveda IP &amp; regulatory assistant</div>
            </div>
          </div>
          <div className="header-spacer" />
          <span className="header-badge">Citation-grounded — abstains when unsure</span>
        </div>
      </header>

      <div className="disclaimer-banner">
        Informational guidance, not legal advice. Consult a qualified professional.
      </div>

      {tab === "assistant" && (
        <section className="hero">
          <div className="container">
            <div className="eyebrow">SIH 2026 — Ministry of AYUSH</div>
            <h1>Trustworthy IP &amp; regulatory guidance for Ayurveda</h1>
            <p>
              Every answer is grounded in an official, version-tracked corpus and linked to the exact source.
              When the law does not cover your question, it says so — and points you to a human facilitator.
            </p>
            <div className="guarantees">
              <span className="guarantee"><b>No claim</b> without a citation</span>
              <span className="guarantee"><b>Current law</b> by default</span>
              <span className="guarantee"><b>Fails safe</b> — abstains, never guesses</span>
              <span className="guarantee"><b>India &amp; International</b> kept separate</span>
              <span className="guarantee"><b>Multilingual</b> — EN / HI / TE</span>
            </div>
          </div>
        </section>
      )}

      <nav className="tabs">
        <div className="container">
          {TABS.map(([id, label]) => (
            <button key={id} className={`tab ${tab === id ? "active" : ""}`} onClick={() => setTab(id)}>
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main>
        <div className="container">
          {tab === "assistant" && <Chat />}
          {tab === "classify" && (
            <div className="panel">
              <div className="section-head">
                <h2>Formulation classifier</h2>
                <p>Classify your formulation (classical, proprietary, phytopharmaceutical, new drug, nutraceutical or cosmetic) and see the licensing pathway. It asks only what it needs.</p>
              </div>
              <div className="card"><ClassificationWizard /></div>
            </div>
          )}
          {tab === "abs" && (
            <div className="panel">
              <div className="section-head">
                <h2>ABS compliance helper</h2>
                <p>Check Access &amp; Benefit-Sharing obligations for using a biological resource, with the responsible authority and forms.</p>
              </div>
              <div className="card"><AbsWizard /></div>
            </div>
          )}
          {tab === "compare" && (
            <div className="panel">
              <div className="section-head">
                <h2>Compare two options</h2>
                <p>Two grounded answers side by side — useful for India vs international, or two protection strategies. The answer-sets stay visibly separate.</p>
              </div>
              <div className="card"><CompareTool /></div>
            </div>
          )}
          {tab === "roadmap" && <RoadmapPanel />}
          {tab === "analyze" && <UploadPanel />}
          {tab === "sources" && <SourcesPanel />}
        </div>
      </main>

      <footer className="site-footer">
        <div className="container">
          <div><strong>IP-SAKTI Sahayak</strong> — grounded, multilingual Ayurveda IP guidance.</div>
          <div className="muted">Informational guidance, not legal advice.</div>
        </div>
      </footer>
    </div>
  );
}
