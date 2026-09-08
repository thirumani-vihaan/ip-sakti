import { useState } from "react";
import Chat from "./pages/Chat.jsx";
import { CompareTool } from "./components/compare.jsx";
import { AbsWizard, ClassificationWizard } from "./components/wizard.jsx";
import { SourcesPanel } from "./components/sources.jsx";
import { UploadPanel } from "./components/upload.jsx";
import { RoadmapPanel } from "./components/roadmap.jsx";
import { BotanicalFolio, Icon } from "./components/ui.jsx";

const TABS = [
  ["assistant", "Assistant", "spark"],
  ["classify", "Classify", "grid"],
  ["abs", "ABS check", "leaf"],
  ["compare", "Compare", "compare"],
  ["roadmap", "Roadmap", "route"],
  ["analyze", "Analyze doc", "upload"],
  ["sources", "Sources", "book"],
];

function ToolFrame({ number, eyebrow, title, description, children, note }) {
  return (
    <div className="panel tool-panel">
      <div className="section-head">
        <div className="eyebrow"><span className="section-number">{number}</span>{eyebrow}</div>
        <h1>{title}</h1><p>{description}</p>
      </div>
      <div className="tool-layout">
        <div className="card tool-form">{children}</div>
        <aside className="tool-note"><Icon name="book" /><h3>A little context.<br />A clearer direction.</h3><p>{note}</p><div className="note-rule" /><span><Icon name="shield" /> Source-linked results</span><p className="small">If key facts are missing, we ask for them. We don’t fill in the gaps.</p></aside>
      </div>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("assistant");
  const [hasConversation, setHasConversation] = useState(false);
  function navigateTabs(e, index) {
    let next;
    if (e.key === "ArrowRight") next = (index + 1) % TABS.length;
    if (e.key === "ArrowLeft") next = (index + TABS.length - 1) % TABS.length;
    if (e.key === "Home") next = 0;
    if (e.key === "End") next = TABS.length - 1;
    if (next !== undefined) {
      e.preventDefault();
      setTab(TABS[next][0]);
      document.getElementById(`tab-${TABS[next][0]}`)?.focus();
    }
  }
  return (
    <div className="app">
      <a className="skip-link" href="#workspace">Skip to workspace</a>
      <header className="site-header">
        <div className="container">
          <button className="brand" onClick={() => setTab("assistant")} aria-label="IP-SAKTI Sahayak home">
            <span className="brand-mark"><Icon name="leaf" /></span>
            <span><span className="brand-name">IP–SAKTI <span>Sahayak</span></span><span className="brand-sub">TRADITION. PROTECTION. PROVENANCE.</span></span>
          </button>
          <div className="header-right"><span className="edition">TEAM SAKTI <span>/</span> SIH 2025</span><span className="header-badge"><i />Offline workspace</span></div>
        </div>
      </header>
      <div className="disclaimer-banner"><Icon name="info" /><span>Made for informed decisions. <strong>Informational guidance, not legal advice.</strong></span></div>

      {tab === "assistant" && !hasConversation && (
        <section className="hero" aria-labelledby="hero-heading">
          <div className="container hero-grid">
            <div className="hero-copy">
              <div className="eyebrow"><span className="gold-line" /> AYURVEDA KNOWLEDGE, THOUGHTFULLY PROTECTED</div>
              <h1 id="hero-heading">Ancient wisdom.<br />Evidence for<br /><em>what’s next.</em></h1>
              <p>Your guide to traditional-knowledge IP and regulation.<br className="desktop-break" /> Grounded in official sources. Clear about its limits.</p>
              <a className="hero-link" href="#question"><span>Begin with a question</span><Icon name="arrow" /></a>
            </div>
            <BotanicalFolio />
          </div>
          <div className="container"><div className="guarantees"><span><Icon name="book" /><b>No claim without a citation</b></span><span><Icon name="shield" />Abstains instead of guessing</span><span><Icon name="globe" />English · हिन्दी · తెలుగు</span></div></div>
        </section>
      )}

      <nav className="tabs" aria-label="Research tools">
        <div className="container" role="tablist" aria-label="Workspace tools">
          {TABS.map(([id, label, icon], index) => (
            <button key={id} id={`tab-${id}`} role="tab" aria-selected={tab === id} aria-controls="workspace" tabIndex={tab === id ? 0 : -1} className={`tab ${tab === id ? "active" : ""}`} onClick={() => setTab(id)} onKeyDown={(e) => navigateTabs(e, index)}><Icon name={icon} />{label}{tab === id && <span className="tab-dot" />}</button>
          ))}
        </div>
      </nav>
      <main id="workspace" tabIndex={-1} role="tabpanel" aria-labelledby={`tab-${tab}`}>
        <div className="container">
          {tab === "assistant" && <Chat onConversationChange={setHasConversation} />}
          {tab === "classify" && <ToolFrame number="02" eyebrow="FIND YOUR REGULATORY PATH" title="Every formulation has a starting point." description="Understand your formulation’s category and its licensing pathway. Start with what you know." note="A classical formulation and a novel plant-derived medicine can follow very different pathways. These four details help identify the relevant category."><ClassificationWizard /></ToolFrame>}
          {tab === "abs" && <ToolFrame number="03" eyebrow="ACCESS & BENEFIT-SHARING" title="Shared knowledge. Shared responsibility." description="Explore your obligations when using a biological resource, including the responsible authority and applicable forms." note="Where your resource comes from, who is using it, and why it is being used all matter. We keep the authority, forms, and rule version together."><AbsWizard /></ToolFrame>}
          {tab === "compare" && <div className="panel tool-panel"><div className="section-head"><div className="eyebrow"><span className="section-number">04</span>TWO OPTIONS. ONE CLEARER PICTURE.</div><h1>See the distinction.</h1><p>Explore two protection strategies or jurisdictions side by side. Each answer keeps its own sources, evidence, and boundaries.</p></div><div className="card tool-form"><CompareTool /></div></div>}
          {tab === "roadmap" && <RoadmapPanel />}
          {tab === "analyze" && <UploadPanel />}
          {tab === "sources" && <SourcesPanel />}
        </div>
      </main>
      <footer className="site-footer">
        <div className="container"><div className="footer-brand"><Icon name="leaf" /><strong>Knowledge deserves provenance.</strong></div><div>Team SAKTI · SIH 2025 · PS 26045<br /><span>Ministry of AYUSH problem statement</span></div><div className="footer-note">Built to inform. Not to replace a professional.<br /><span>Local fixture corpus · No external AI calls</span></div></div>
      </footer>
    </div>
  );
}
