import { useState } from "react";
import { postAbsCheck, postClassify } from "../api/client.js";

function Select({ label, testid, value, onChange, options }) {
  return (
    <label className="field">
      {label}{" "}
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
        <strong>Insufficient information.</strong> Please provide: {result.missing.join(", ")}
      </div>
    );
  }
  return (
    <div className="result" data-testid="obligation">
      <p>{result.obligation}</p>
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
  const set = (k) => (e) => setFacts({ ...facts, [k]: e.target.value });
  return (
    <div className="wizard">
      <h3>ABS compliance</h3>
      <Select label="Resource origin" testid="resource_origin" value={facts.resource_origin} onChange={set("resource_origin")} options={["", "india", "foreign"]} />
      <Select label="Use" testid="use" value={facts.use} onChange={set("use")} options={["", "commercial", "research", "bio_survey"]} />
      <Select label="Applicant" testid="applicant" value={facts.applicant} onChange={set("applicant")} options={["", "indian_entity", "foreign"]} />
      <Select label="TK association" testid="tk_association" value={facts.tk_association} onChange={set("tk_association")} options={["", "yes", "no"]} />
      <button data-testid="abs-run" onClick={async () => setResult(await submit(facts))}>Check</button>
      <RuleResultCard result={result} />
    </div>
  );
}

export function ClassificationWizard({ submit = postClassify }) {
  const [facts, setFacts] = useState({});
  const [result, setResult] = useState(null);
  const set = (k) => (e) => setFacts({ ...facts, [k]: e.target.value });
  return (
    <div className="wizard">
      <h3>Formulation classification</h3>
      <Select label="In First-Schedule text" testid="in_first_schedule" value={facts.in_first_schedule} onChange={set("in_first_schedule")} options={["", "yes", "no"]} />
      <Select label="Modified" testid="modified" value={facts.modified} onChange={set("modified")} options={["", "exact", "modified"]} />
      <Select label="Novel actives" testid="novel_actives" value={facts.novel_actives} onChange={set("novel_actives")} options={["", "yes", "no"]} />
      <Select label="Intended use" testid="intended_use" value={facts.intended_use} onChange={set("intended_use")} options={["", "medicine", "food", "cosmetic"]} />
      <button data-testid="classify-run" onClick={async () => setResult(await submit(facts))}>Classify</button>
      <RuleResultCard result={result} />
    </div>
  );
}
