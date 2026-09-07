import { useState } from "react";
import { postAbsCheck, postClassify } from "../api/client.js";

function Select({ label, testid, value, onChange, options }) {
  return (
    <label className="field">
      {label}
      <select data-testid={testid} value={value || ""} onChange={onChange}>
        {options.map((o) => (
          <option key={o} value={o}>{o || "-- select --"}</option>
        ))}
      </select>
    </label>
  );
}

export function RuleResultCard({ result }) {
  if (!result) return null;
  if (result.status === "insufficient") {
    return (
      <div className="result" data-testid="insufficient">
        <strong>A bit more information needed.</strong> Please provide: {result.missing.join(", ")}
      </div>
    );
  }
  return (
    <div className="result" data-testid="obligation">
      <p style={{ margin: 0 }}>{result.obligation}</p>
      <p className="meta">
        {result.authority || "-"} · forms: {(result.forms || []).join(", ") || "-"} ·
        source: {result.source_id} (v{result.rule_version})
      </p>
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
    <div className="wizard">
      <Select label="Resource origin" testid="resource_origin" value={facts.resource_origin} onChange={set("resource_origin")} options={["", "india", "foreign"]} />
      <Select label="Use" testid="use" value={facts.use} onChange={set("use")} options={["", "commercial", "research", "bio_survey"]} />
      <Select label="Applicant" testid="applicant" value={facts.applicant} onChange={set("applicant")} options={["", "indian_entity", "foreign"]} />
      <Select label="Traditional-knowledge association" testid="tk_association" value={facts.tk_association} onChange={set("tk_association")} options={["", "yes", "no"]} />
      <button className="btn" data-testid="abs-run" onClick={run} disabled={busy}>{busy ? "Checking..." : "Check obligations"}</button>
      {error && <p className="error">{error}</p>}
      <RuleResultCard result={result} />
    </div>
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
    <div className="wizard">
      <Select label="In an authoritative First-Schedule text" testid="in_first_schedule" value={facts.in_first_schedule} onChange={set("in_first_schedule")} options={["", "yes", "no"]} />
      <Select label="Modified from the classical text" testid="modified" value={facts.modified} onChange={set("modified")} options={["", "exact", "modified"]} />
      <Select label="Contains novel actives" testid="novel_actives" value={facts.novel_actives} onChange={set("novel_actives")} options={["", "yes", "no"]} />
      <Select label="Intended use" testid="intended_use" value={facts.intended_use} onChange={set("intended_use")} options={["", "medicine", "food", "cosmetic"]} />
      {facts.novel_actives === "yes" && facts.intended_use === "medicine" && (
        <Select label="Purified plant-derived actives (optional)" testid="plant_derived" value={facts.plant_derived} onChange={set("plant_derived")} options={["", "yes", "no"]} />
      )}
      <button className="btn" data-testid="classify-run" onClick={run} disabled={busy}>{busy ? "Classifying..." : "Classify"}</button>
      {error && <p className="error">{error}</p>}
      <RuleResultCard result={result} />
    </div>
  );
}
