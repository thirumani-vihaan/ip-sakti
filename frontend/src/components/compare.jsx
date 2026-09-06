import { useState } from "react";
import { postCompare } from "../api/client.js";
import { ChatMessage } from "./chat.jsx";

export function CompareTool({ submit = (a, b) => postCompare(a, b) }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [res, setRes] = useState(null);
  return (
    <div className="compare">
      <h3>Compare options</h3>
      <input data-testid="cmp-a" value={a} onChange={(e) => setA(e.target.value)} placeholder="Option A" />
      <input data-testid="cmp-b" value={b} onChange={(e) => setB(e.target.value)} placeholder="Option B" />
      <button data-testid="compare-run" onClick={async () => setRes(await submit(a, b))}>Compare</button>
      {res && (
        <div className="cmp-grid">
          <div><h4>A</h4><ChatMessage response={res.a} /></div>
          <div><h4>B</h4><ChatMessage response={res.b} /></div>
        </div>
      )}
    </div>
  );
}
