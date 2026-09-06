"""Offline evaluation harness: Recall@k, citation validity, correct-abstention, legal-term
preservation, and p50/p95 latency over the curated testset. Writes eval/report.md.
Exits 0 only if the honest gates are met.
"""
import json
import pathlib
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

RECALL_GATE = 0.8


def _load_cases():
    with open(ROOT / "eval" / "testset.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run() -> int:
    from app.config import Settings
    from app.i18n.translate import translate_preserving
    from app.integrations.fakes import FakeTranslation
    from app.main import build_app
    from app.workflow.schema import ChatRequest

    svc = build_app(Settings()).state.answer_service
    cases = _load_cases()

    latencies, recall_hits, recall_total = [], 0, 0
    abst_hits, abst_total, cit_ok, cit_total = 0, 0, 0, 0
    for case in cases:
        t = time.perf_counter()
        resp = svc.answer(ChatRequest(query=case["query"]))
        latencies.append(time.perf_counter() - t)
        ids = {s.id for s in resp.sources}
        for c in resp.claims:
            cit_total += 1
            if c.source_ids and set(c.source_ids) <= ids:
                cit_ok += 1
        if case["type"] == "answerable":
            recall_total += 1
            docs = {s.id.split("#")[0] for s in resp.sources}
            if case["expected_doc"] in docs:
                recall_hits += 1
        elif case["type"] == "out_of_scope":
            abst_total += 1
            if not resp.claims:
                abst_hits += 1

    recall = recall_hits / recall_total if recall_total else 1.0
    abst = abst_hits / abst_total if abst_total else 1.0
    citv = cit_ok / cit_total if cit_total else 1.0
    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)]

    ltp_text = translate_preserving(FakeTranslation(), "Under Section 3(p), file Form I.", "en", "hi")
    ltp_ok = "Section 3(p)" in ltp_text and "Form I" in ltp_text

    report = (
        "# Evaluation report\n\n"
        f"- Cases: {len(cases)} (answerable {recall_total}, out-of-scope {abst_total})\n"
        f"- Recall@5 (answerable): {recall:.2f}  (gate {RECALL_GATE})\n"
        f"- Citation validity: {citv:.2f}  (fabricated/unsupported = {cit_total - cit_ok})\n"
        f"- Correct abstention (out-of-scope): {abst:.2f}\n"
        f"- Legal-term preservation: {'pass' if ltp_ok else 'FAIL'}\n"
        f"- Latency p50/p95: {p50 * 1000:.1f} ms / {p95 * 1000:.1f} ms\n"
    )
    (ROOT / "eval" / "report.md").write_text(report, encoding="utf-8")
    print(report)

    gates = recall >= RECALL_GATE and citv == 1.0 and abst == 1.0 and ltp_ok
    return 0 if gates else 1


if __name__ == "__main__":
    sys.exit(run())
