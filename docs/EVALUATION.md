# Evaluation & Readiness

How IP-SAKTI Sahayak measures up on the problem statement evaluation axes and a
demo-readiness checklist. All numbers are reproducible offline via `eval/run_eval.py`.

## 1. The four evaluation axes
| Axis | How we address it | Result |
|---|---|---|
| **Answer accuracy (retrieval recall)** | Hybrid retrieval + exact-reference resolution over a curated, in-force corpus. This measures whether the correct source is retrieved, not a human-graded answer score. | Recall@5 = **1.00** on the 18-case set. |
| **Citation correctness (grounding integrity)** | Grounding invariant (`Source.id == evidence_id`) + a validator that drops unknown ids and Section/Form reference mismatches. This verifies citation *integrity* — every citation resolves to a real cited passage and asserted section/form refs appear in it. Full semantic entailment (NLI) is future work. | Citation integrity = **1.00**; fabricated/unknown ids = **0**. |
| **Safe abstention** | Relevance gate (per-hit topical filtering) + fail-closed abstention; low-confidence and out-of-scope answers surface an escalation path. | Correct abstention = **1.00** (incl. a prompt-injection case). |
| **Multilingual quality** | Statute/section references preserved verbatim; offline localises legal terms via a locked glossary (Romanised HI/TE) for English answers; full neural translation is via Bhashini when configured. | Term preservation = **pass**. |

Latency (fixtures): p50/p95 in single-digit milliseconds. Live latency depends on the
Gemini/Bhashini endpoints.

## 2. Retrieval & citation correctness
- 18 curated queries across all six domains (incl. India-vs-international) plus
  adversarial/out-of-scope cases — see `eval/testset.jsonl`.
- Every claim cites only server-assigned evidence ids; the model cannot invent a source.
- Out-of-corpus queries abstain with a confidence flag instead of guessing.
- Citations are hand-verifiable: each source carries title, section, official URL, and a
  local excerpt shown in the source drawer.

## 3. Formulation classifier
- Six categories, each an unambiguous test case in `tools/acceptance/T033.py`.
- Ambiguity handling: missing required facts return `insufficient` with the exact
  fields to provide (`T014`), and the phytopharmaceutical vs new-drug distinction uses
  an optional fact so the wizard asks the minimum number of questions.

## 4. Jurisdiction separation
- India vs International are filtered separately; international instruments (TRIPS, PCT,
  Nagoya) never surface under an India query and vice-versa (`T005`, `T027`).
- The compare tool renders two answer-sets as visibly separate blocks with jurisdiction tags.

## 5. ABS / TKDL logic
- Section 7 (Indian entity, State Biodiversity Board, Form I) vs the foreign-applicant
  path (National Biodiversity Authority) are distinguished deterministically (`T014`).
- TK checks are pointers for expert review; the app does not claim direct TKDL database
  access (TKDL is not freely public) — stated in the README and the DPIIT/TKDL source.

## 6. Guardrails & compliance
- "Information, not legal advice" disclaimer on every answer, as a banner, and as an
  `X-Disclaimer` response header.
- Escalation-to-human-facilitator path triggers on abstention/low-confidence (`T032`).
- Input sanitization + prompt-injection heuristic (`T029`); per-client rate limiting
  (`T035`); request-id headers for audit; no accounts (privacy by design).

## 7. Multilingual
- Round-trip in HI and TE preserves statute names/section numbers (`T017`, `T026`).
- Script-based auto-detection routes Devanagari->HI and Telugu->TE (`T028`).

## 8. Reproducing the numbers
```
cd backend
python ..\eval\run_eval.py            # prints metrics; exits 0 only if gates hold
python tests\smoke_demo.py            # end-to-end over every endpoint
for /l %i in (1,1,35) do python ..\tools\run_acceptance.py T0%i   # acceptance suite
```

## Honesty notes
Metrics are reported with sample size (18 eval cases, 14-document corpus) and are not
presented as guarantees. Specific scoping we are explicit about:

- **"Recall" measures retrieval, not human-judged answer quality.** It checks the
  expected source is in the top-k.
- **Citation validation checks integrity, not entailment.** It guarantees a citation
  resolves to a real cited passage and that asserted Section/Form refs appear there;
  it does not yet verify the claim is semantically entailed by the passage (NLI is
  roadmap). Grounding still prevents fabricated sources.
- **Offline multilingual is term-level.** With no Bhashini key, we localise legal
  terminology via a locked glossary and preserve statute references; fluent
  native-script Q&A (inbound retrieval in Hindi/Telugu) requires Bhashini and is on
  the roadmap.
- **Retrieval is in-memory by default.** `InMemoryVectorStore` backs the demo;
  `ChromaVectorStore` (cosine) is the persistent implementation for scale-up.
- **PDF export renders server-derived metadata.** Sources are authenticated against the
  corpus and claims must cite them; client warnings/strength/corpus-version are dropped
  or recomputed. A per-answer signed provenance token (byte-exact) is a roadmap item.

The corpus is a curated demonstration subset; the same pipeline scales to a larger
corpus without code changes.
