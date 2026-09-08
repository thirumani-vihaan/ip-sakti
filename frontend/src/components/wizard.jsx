import { useState } from "react";
import { postAbsCheck, postClassify } from "../api/client.js";
import { Icon } from "./ui.jsx";

function Select({ label, testid, value, onChange, options }) {
  return (
    <label className="field">
      {label}
      <select data-testid={testid} value={value || ""} onChange={onChange}>
        {options.map((o) => (
          <option key={o} value={o}>{o ? o.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()) : "Select an option…"}</option>
        ))}
      </select>
    </label>
  );
}

export function RuleResultCard({ result }) {
  if (!result) return null;
  if (result.status === "insufficient") {
    return (
      <div className="result" data-testid="insufficient" role="status">
        <Icon name="info" /><div><strong>A bit more information needed.</strong><p>Please provide: {result.missing.join(", ").replace(/_/g, " ")}</p></div>
      </div>
    );
  }
  return (
    <div className="result" data-testid="obligation" role="status">
      <Icon name="shield" /><div><div className="eyebrow">YOUR SOURCED PATHWAY</div><p className="result-obligation">{result.obligation}</p>
      <dl className="result-meta"><div><dt>Responsible authority</dt><dd>{result.authority || "Not specified"}</dd></div><div><dt>Applicable forms</dt><dd>{(result.forms || []).join(", ") || "None specified"}</dd></div></dl>
      <p className="rule-source"><Icon name="book" />{result.source_id}<span>Rule v{result.rule_version}</span></p></div>
    </div>
  );
}

export function AbsWizard({ submit = postAbsCheck }) {
  const [facts, setFacts] = useState({});
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const set = (k) => (e) => setFacts({ ...facts, [k]: e.target.value });
  async function run() {
    setBusy(true);
    setError("");
    try {
      setResult(await submit(facts));
    } catch (e) {
      setError(e.message || "Request failed. Please try again.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="wizard" onSubmit={(e) => { e.preventDefault(); run(); }}>
      <div className="form-heading"><Icon name="leaf" /><div><h2>Tell us about the resource</h2><p>Four details to find the relevant obligation.</p></div></div>
      <Select label="Resource origin" testid="resource_origin" value={facts.resource_origin} onChange={set("resource_origin")} options={["", "india", "foreign"]} />
      <Select label="Use" testid="use" value={facts.use} onChange={set("use")} options={["", "commercial", "research", "bio_survey"]} />
      <Select label="Applicant" testid="applicant" value={facts.applicant} onChange={set("applicant")} options={["", "indian_entity", "foreign"]} />
      <Select label="Traditional-knowledge association" testid="tk_association" value={facts.tk_association} onChange={set("tk_association")} options={["", "yes", "no"]} />
      <div className="form-actions"><span>Rule-based · Source-linked</span><button className="btn btn-accent" data-testid="abs-run" type="submit" disabled={busy}>{busy ? "Checking..." : "Check obligations"}<Icon name="arrow" /></button></div>
      {error && <p className="error" role="alert">{error}</p>}
      <RuleResultCard result={result} />
    </form>
  );
}

export function ClassificationWizard({ submit = postClassify }) {
  const [facts, setFacts] = useState({});
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const set = (k) => (e) => setFacts({ ...facts, [k]: e.target.value });
  async function run() {
    setBusy(true);
    setError("");
    try {
      setResult(await submit(facts));
    } catch (e) {
      setError(e.message || "Request failed. Please try again.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="wizard" onSubmit={(e) => { e.preventDefault(); run(); }}>
      <div className="form-heading"><Icon name="grid" /><div><h2>Tell us about the formulation</h2><p>Answer what you know. We’ll flag what’s missing.</p></div></div>
      <Select label="In an authoritative First-Schedule text" testid="in_first_schedule" value={facts.in_first_schedule} onChange={set("in_first_schedule")} options={["", "yes", "no"]} />
      <Select label="Modified from the classical text" testid="modified" value={facts.modified} onChange={set("modified")} options={["", "exact", "modified"]} />
      <Select label="Contains novel actives" testid="novel_actives" value={facts.novel_actives} onChange={set("novel_actives")} options={["", "yes", "no"]} />
      <Select label="Intended use" testid="intended_use" value={facts.intended_use} onChange={set("intended_use")} options={["", "medicine", "food", "cosmetic"]} />
      {facts.novel_actives === "yes" && facts.intended_use === "medicine" && (
        <Select label="Purified plant-derived actives (optional)" testid="plant_derived" value={facts.plant_derived} onChange={set("plant_derived")} options={["", "yes", "no"]} />
      )}
      <div className="form-actions"><span>Rule-based · Source-linked</span><button className="btn btn-accent" data-testid="classify-run" type="submit" disabled={busy}>{busy ? "Classifying..." : "Classify"}<Icon name="arrow" /></button></div>
      {error && <p className="error" role="alert">{error}</p>}
      <RuleResultCard result={result} />
    </form>
  );
}
