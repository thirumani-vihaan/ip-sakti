const BASE = (import.meta.env && import.meta.env.VITE_API_BASE) || "";

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
  if (!res.ok) {
    let detail = "";
    try {
      detail = JSON.stringify(await res.json());
    } catch {
      detail = res.statusText;
    }
    throw new Error(`Request failed (${res.status}): ${detail}`);
  }
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
