import { useEffect, useState } from "react";
import { getSources } from "../api/client.js";
import { Icon } from "./ui.jsx";

export function SourcesPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [jurisdiction, setJurisdiction] = useState("all");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setError("");
    getSources().then((value) => { if (active) setData(value); }).catch((e) => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [attempt]);
  const sources = (data?.sources || []).filter((s) => (jurisdiction === "all" || s.jurisdiction === jurisdiction) && `${s.title} ${s.authority_level} ${s.id}`.toLowerCase().includes(query.toLowerCase()));
  return (
    <div className="panel tool-panel">
      <div className="section-head"><div className="eyebrow"><span className="section-number">07</span>THE CITATIONS LEDGER</div><h1>Trust begins at the source.</h1><p>No black box. Explore the version-tracked corpus behind the guidance, with legal status and provenance kept in view.</p></div>
      {error ? <div className="card empty-state source-unavailable" role="alert"><Icon name="book" /><div className="eyebrow">THE SOURCE CONNECTION IS UNAVAILABLE</div><h3>The ledger couldn’t be opened.</h3><p>We won’t substitute unverified documents. The local server needs to provide<br className="desktop-break" /> the corpus catalogue before we can display it.</p><details><summary>Connection details</summary><p className="small">{error}</p></details><button className="btn btn-ghost" onClick={() => setAttempt((n) => n + 1)}>Try again<Icon name="arrow" /></button></div> : !data ? <div className="loading-card" role="status"><Icon name="book" /><div><strong>Loading sources...</strong><div className="loading-lines"><i /><i /></div></div></div> : <>
        <div className="corpus-stats"><div><Icon name="book" /><strong>{data.count}</strong><span>corpus documents</span></div><div><Icon name="shield" /><strong>{data.sources.filter((s) => s.status === "in_force").length}</strong><span>in force</span></div><div><Icon name="route" /><strong>{data.corpus_version}</strong><span>tracked corpus version</span></div><div className="corpus-principle"><span className="gold-line" /><p>Not just an answer.<br /><em>A trail you can follow.</em></p></div></div>
        <div className="card sources-card">
          <div className="sources-toolbar"><label className="source-search"><Icon name="search" /><input aria-label="Search corpus sources" placeholder="Find a source, authority, or document…" value={query} onChange={(e) => setQuery(e.target.value)} /></label><label className="field"><span className="sr-only">Filter sources by jurisdiction</span><select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}><option value="all">All jurisdictions</option><option value="india">India</option><option value="international">International</option></select></label></div>
          <div className="table-scroll" tabIndex={0} role="region" aria-label="Corpus documents table">
            <table className="sources-table"><caption className="sr-only">Version-tracked legal sources and their status</caption><thead><tr><th scope="col">Document / source</th><th scope="col">Authority</th><th scope="col">Version</th><th scope="col">Effective</th><th scope="col">Status</th><th scope="col">Jurisdiction</th><th scope="col"><span className="sr-only">Official link</span></th></tr></thead><tbody>{sources.map((s, i) => <tr key={s.id}><td><div className="document-name"><span className="document-number">{String(i + 1).padStart(2, "0")}</span><div><strong>{s.title}</strong><small>{s.id}</small></div></div></td><td className="authority-cell">{s.authority_level?.replace(/_/g, " ")}</td><td>{s.version}</td><td>{s.effective_date || "—"}</td><td><span className={`pill ${s.status}`}>{s.status.replace(/_/g, " ")}</span></td><td className="jurisdiction-cell">{s.jurisdiction}</td><td>{s.url ? <a className="source-link" aria-label={`Open official source: ${s.title}`} href={s.url} target="_blank" rel="noreferrer"><Icon name="external" /></a> : "—"}</td></tr>)}</tbody></table>
          </div>
          {sources.length === 0 && <div className="empty-state"><Icon name="search" /><h3>No matching sources.</h3><p>Try a different document name or jurisdiction.</p><button className="btn btn-ghost btn-sm" onClick={() => { setQuery(""); setJurisdiction("all"); }}>Reset filters</button></div>}
          <div className="table-footer"><span role="status">{sources.length} of {data.count} documents</span><span><Icon name="info" />Official links open online; the corpus is local.</span></div>
        </div>
      </>}
    </div>
  );
}
