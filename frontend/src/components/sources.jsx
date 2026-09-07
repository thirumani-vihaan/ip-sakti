import { useEffect, useState } from "react";
import { getSources } from "../api/client.js";

export function SourcesPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getSources().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="empty">Loading sources...</p>;

  return (
    <div className="panel">
      <div className="section-head">
        <h2>Grounded sources</h2>
        <p>
          Every answer is grounded in this version-tracked corpus ({data.count} documents, corpus {data.corpus_version}).
          Status flags show which laws are currently in force, so the assistant never serves outdated law.
        </p>
      </div>
      <div className="card" style={{ overflowX: "auto" }}>
        <table className="sources-table">
          <thead>
            <tr>
              <th>Title</th><th>Authority</th><th>Version</th><th>Effective</th>
              <th>Status</th><th>Jurisdiction</th><th>Link</th>
            </tr>
          </thead>
          <tbody>
            {data.sources.map((s) => (
              <tr key={s.id}>
                <td>{s.title}</td>
                <td>{s.authority_level}</td>
                <td>{s.version}</td>
                <td>{s.effective_date || "-"}</td>
                <td><span className={`pill ${s.status}`}>{s.status.replace(/_/g, " ")}</span></td>
                <td>{s.jurisdiction}</td>
                <td>{s.url ? <a href={s.url} target="_blank" rel="noreferrer">open</a> : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
