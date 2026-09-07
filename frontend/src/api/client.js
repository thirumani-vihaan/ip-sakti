const BASE = (import.meta.env && import.meta.env.VITE_API_BASE) || "";

async function checkOk(res) {
  if (!res.ok) {
    let detail = "";
    try {
      detail = JSON.stringify(await res.json());
    } catch {
      detail = res.statusText;
    }
    throw new Error(`Request failed (${res.status}): ${detail}`);
  }
  return res;
}

async function post(path, body) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (err) {
    throw new Error(`Network error contacting the server: ${err.message}`);
  }
  await checkOk(res);
  return res.json();
}

async function get(path) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`);
  } catch (err) {
    throw new Error(`Network error contacting the server: ${err.message}`);
  }
  await checkOk(res);
  return res.json();
}

export function postChat(query, opts = {}) {
  return post("/api/chat", { query, ...opts });
}
export function postAbsCheck(facts) {
  return post("/api/abs/check", facts);
}
export function postClassify(facts) {
  return post("/api/classify", facts);
}
export function postCompare(a, b, opts = {}) {
  return post("/api/compare", { option_a: a, option_b: b, ...opts });
}
export function postRoadmap(query, opts = {}) {
  return post("/api/roadmap", { query, ...opts });
}
export function postEscalate(payload) {
  return post("/api/escalate", payload);
}
export function getSources() {
  return get("/api/sources");
}
export function getSearch(q, { jurisdiction = "india", k = 5 } = {}) {
  const params = new URLSearchParams({ q, jurisdiction, k: String(k) });
  return get(`/api/search?${params.toString()}`);
}

export async function postAnalyze(file, jurisdiction = "india") {
  const fd = new FormData();
  fd.append("file", file);
  let res;
  try {
    res = await fetch(`${BASE}/api/analyze?jurisdiction=${jurisdiction}`, { method: "POST", body: fd });
  } catch (err) {
    throw new Error(`Network error uploading the document: ${err.message}`);
  }
  await checkOk(res);
  return res.json();
}

export async function exportPdf(response) {
  let res;
  try {
    res = await fetch(`${BASE}/api/export/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(response),
    });
  } catch (err) {
    throw new Error(`Network error exporting PDF: ${err.message}`);
  }
  await checkOk(res);
  return res.blob();
}
