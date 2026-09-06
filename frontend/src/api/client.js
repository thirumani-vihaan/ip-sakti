const BASE = (import.meta.env && import.meta.env.VITE_API_BASE) || "";

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
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
