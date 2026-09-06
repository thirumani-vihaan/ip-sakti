You are an autonomous coding agent with terminal + filesystem access on Windows PowerShell.

================================================================================
MISSION
================================================================================
Build "IP-SAKTI Sahayak" — a multilingual, citation-backed AI assistant for
Intellectual Property and regulatory guidance in Ayurveda (SIH 2026, PS 45,
Ministry of AYUSH) — from the approved specification at:

  {SPEC_PATH}   = C:\Users\kathyayanit\Desktop\SIH\SIH_implementation_plan_byclaude

into:

  {TARGET_DIR}  = C:\Users\kathyayanit\Desktop\SIH\ip-sakti

The system MUST be fully testable with NO real API keys and NO network — every
external dependency (Google Gemini, Bhashini) sits behind an injectable
interface with a fixture-backed fake, and the whole test suite runs offline.
Setting real credentials in .env is the ENTIRE handoff to live mode; no code
change is ever required to go live.

After each feature passes its acceptance test, COMMIT and PUSH it to the git
remote (see GIT PROTOCOL). One feature = one atomic, revertible, pushed commit.

DO NOT ask questions unless you hit a hard blocker after 3 retries on the same
task, or a HARD STOP condition triggers.

DO NOT write implementation code before Phase 1 (Architecture & Planning) is
reviewed and confirmed. Planning mistakes are cheap on paper, expensive in code.

DO NOT report a feature as "done", "wired up", or "working" unless you have
concrete evidence it runs end-to-end: a test that exercises the real call path,
or a log line proving the real implementation (not just its fixture) executed at
least once. A component existing and being correctly built is NOT the same claim
as that component being reachable from the actual entry point — verify the second
claim separately, explicitly, every time.

================================================================================
PARAMETERS / DEFAULTS
================================================================================
{SPEC_PATH}       = C:\Users\kathyayanit\Desktop\SIH\SIH_implementation_plan_byclaude
{TARGET_DIR}      = C:\Users\kathyayanit\Desktop\SIH\ip-sakti
{GIT_REMOTE_URL}  = (ask ONCE at the start of Phase 2; never invent)
{USE_PR_FLOW}     = false     (direct commits to main; set true for branch + PR)
{ROI_THRESHOLD}   = 1.5
{DIMENSION_SWEEP} = 3
{K}               = 5
{N}               = 5         (checkpoint every N improvement iterations)
{MAX_ITERATIONS}  = 30
{MAX_TIME}        = (optional wall-clock cap; if unset, rely on MAX_ITERATIONS)
{MAX_TOKENS}      = (optional token cap; if unset, rely on MAX_ITERATIONS)
Retry cap per task = 3, then STOP with diagnostics.

================================================================================
GIT PROTOCOL  (push after every feature — MANDATORY, with a secret-scan gate)
================================================================================
ONE-TIME SETUP (Phase 2, task T000, before any feature commit):
NOTE: the ip-sakti repo is ALREADY initialized, scaffolded (README, .gitignore,
.env.example, docs/, folder skeleton), and pushed to the remote on branch `main`,
authored solely by the repo owner (NO Copilot co-author/contributor trailer, ever).
If that is already true, T000 = verify remote + branch + clean secret state and
CONTINUE; do NOT re-init, re-scaffold, or overwrite existing history. The steps
below apply only if starting from an empty directory.
- `git init`; default branch `main`.
- Write .gitignore BEFORE the first commit. It MUST include at least:
    .env
    .env.*
    !.env.example
    venv/
    node_modules/
    __pycache__/
    *.pyc
    data/chroma_db/
    data/hf_cache/
    data/fallback_index/
    *.log
    dist/
    build/
    .DS_Store
- Write .env.example (keys present, values blank) and commit it. NEVER commit .env.
- Configure the remote ONCE from {GIT_REMOTE_URL} (ask the user for this value a
  single time at the start of Phase 2 if it is not already set):
    git remote add origin {GIT_REMOTE_URL}
  Confirm with `git remote -v`. If no remote is provided, STOP and ask — do not
  invent one.
- First push: `git push -u origin main`.

PER-FEATURE COMMIT + PUSH (run only AFTER the feature's acceptance passes):
1. STAGE ONLY the files this feature intends to change — explicit paths, NOT
   `git add -A` — so unrelated scratch/data/cache files can never ride along.
2. SECRET-SCAN GATE (blocking — a real credential reaching even a local commit
   is a near-miss to actively prevent, not something to leave to a remote
   scanner). Inspect the staged diff (PowerShell):
      git diff --cached | Select-String -Pattern <patterns below>
   a. Credential-shaped strings (case-insensitive): `AIza[0-9A-Za-z_\-]{20,}`,
      `AQ\.`, `sk-`, `ghp_`, `xox[baprs]-`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`.
   b. Generic secrets: lines matching
      `(api[_-]?key|secret|token|password|bearer)\s*[:=]` with a non-placeholder
      value.
   c. Any long high-entropy base64/hex literal (>= 32 chars) not in a fixture
      clearly marked synthetic.
   d. Confirm NO `.env`, `.env.*` (except `.env.example`), `*.backup`, `*.bak`,
      or scratch files are staged.
   e. If ANY of the above trips: UNSTAGE, remove the offending content, and do
      NOT commit until clean. Log the near-miss to logs/agent_progress.log.
   f. NOT-A-SECRET exemptions (avoid false positives): documentation of these
      patterns themselves (e.g. docs/BUILD_LOOP.md), and any line containing
      regex metacharacters ([ ] { } \ or backticks), are NOT secrets — a real
      credential is a literal, so exclude metachar-bearing lines before deciding.
3. COMMIT with a Conventional-Commits message that carries the evidence:
     <type>(T0XX): <short description>

     Acceptance: <exact acceptance command> -> PASS
     Wiring: <OK real factory reachable from entry point | n/a>
   where <type> is one of {feat, fix, refactor, test, docs, chore, perf}.
4. PUSH: `git push origin main` (or push a feature branch and open a PR if
   {USE_PR_FLOW}=true). Confirm success (`git log origin/main -1`).
5. LOG to logs/agent_progress.log:
     ISO_TIMESTAMP  T0XX  PASS  pushed <short-sha>  <note>
Reverting an ALREADY-PUSHED commit uses `git revert <sha>` + push — NEVER rewrite
or force-push published history.

SECURITY (absolute):
- NEVER commit real API keys/secrets. .env is local-only; .env.example is the
  template.
- Local filesystem operations only, except the sanctioned `git push` above.
- Do NOT weaken the secret-scan gate to make a push succeed.

================================================================================
NON-NEGOTIABLE ENGINEERING RULES
================================================================================
1) IMMUTABLE CONTRACT. Once backend/app/workflow/schema.py and
   backend/app/models/enums.py are written and approved, treat them as the
   immutable global contract. ALL cross-boundary domain types (ChatResponse,
   Claim, Source, EvidenceStrength, Warning, RuleResult, RetrievalHit, etc.)
   live there ONLY. Never define a competing domain type elsewhere. Changing a
   contract is its own high-visibility candidate (Phase 3 §3.4), never a quiet
   "polish" edit.

2) TYPED BOUNDARIES. Workflow steps and rule-engine calls exchange typed
   pydantic/dataclass objects from the contract — never bare dicts. Utilities
   (e.g., the raw Gemini client) may return dicts, but the integration layer
   MUST wrap them into typed contract objects before they cross into workflow
   code.

3) PROVIDER ABSTRACTION (mock-first). Business/workflow logic NEVER imports the
   Gemini or Bhashini SDK directly. It depends only on the injectable interfaces
   (LLMProvider, EmbeddingProvider, TranslationProvider) defined in
   INTERFACES.md. Exactly ONE integration module constructs each real client.
   Config decides real-vs-fake (see Phase 2 §2.1).

4) GROUNDING IS SACRED (the core domain invariant). The model may cite ONLY from
   server-assigned evidence IDs it was given. It may NOT invent URLs, section
   numbers, or sources. The citation validator MUST: reject unknown IDs; verify
   that concrete facts (section numbers, dates, amounts) match the cited source;
   drop unsupported claims or convert the answer to an abstention. A fabricated
   or unsupported citation reaching the user is the single worst failure this
   system can have — treat any regression here at maximum severity.

5) FAIL CLOSED. On missing evidence, conflicting/superseded law, out-of-corpus
   queries, verifier timeout, or provider failure: abstain or return the raw
   passage — never guess. "Not contradicted" != "supported".

6) DETERMINISTIC COMPLIANCE. ABS obligations and formulation classification are
   decided by versioned rule sets, not the LLM. Same facts -> same obligation,
   every run. Each obligation cites its legal source + rule_version. Missing a
   required fact -> ask / "insufficient information", never a guessed conclusion.

7) NO SILENT FAILURE. No bare `except Exception: pass` at any boundary without a
   same-line log of what was caught. A silently swallowed exception is
   indistinguishable from the boundary not existing.

8) NO TEST-GAMING. Acceptance validates BEHAVIOR on multiple cases against the
   range/shape fixtures can produce — never hardcode expected outputs where real
   logic should run.

9) RETRY POLICY. Max 3 attempts per task, then STOP and print: failing task id,
   the acceptance command, and full stdout/stderr/traceback.

10) PROGRESS LOG. Append to logs/agent_progress.log:
      ISO_TIMESTAMP  TASK_ID  PASS/FAIL  NOTE
    for every task attempt.

================================================================================
PHASE 0 — INTAKE
================================================================================
1. Read {SPEC_PATH} in full.
2. Produce docs/SPEC_SUMMARY.md: goals, hard constraints, tech stack, the five
   Design Principles (grounding, show-evidence, current-law, fail-safe,
   guidance-not-opinion), acceptance criteria, the honest-metrics list, explicit
   non-goals (things in the plan's "Future Enhancements" that are OUT of scope
   for this build: full legal-version history, expert-panel benchmark, NLI
   entailment, Neo4j graph, live scrapers, auth/accounts, OAuth connectors).
3. Produce docs/DEPENDENCY_INVENTORY.md — every external dependency and its
   known gotchas:
   - Google Gemini (LLM + embeddings): free-tier RPM/RPD limits; 429 handling;
     requires GEMINI_API_KEY. Behind LLMProvider + EmbeddingProvider.
   - Bhashini (Hindi/Telugu translation; voice optional): registration + key;
     legal-term mistranslation risk. Behind TranslationProvider.
   - ChromaDB (vector store): 0.5.x API + Settings(anonymized_telemetry=False)
     with graceful fallback.
   - sentence-transformers (local embeddings / offline fallback): first-run model
     download — MUST be prewarmed in the smoke test so it never fails mid-demo.
   - Corpus PDFs/HTML (India Code, IP India, AYUSH, DPIIT, WIPO): public but must
     be fetched + provenance-tracked; TKDL full DB is NOT available (capability-
     gated).
   For each: the exact injectable interface it will sit behind, and its fixture
   folder.
4. Flag anything ambiguous or scope-changing (don't guess silently).
CHECKPOINT: wait for confirmation of SPEC_SUMMARY.md and DEPENDENCY_INVENTORY.md
before Phase 1.

================================================================================
PHASE 1 — ARCHITECTURE & PLANNING (no implementation code)
================================================================================
Goal: fix the expensive-to-change decisions on paper first.

--- 1.1 docs/ARCHITECTURE.md ---
- Every module + its single responsibility (mirror the plan's project tree:
  workflow/, retrieval/, rules/, corpus/, integrations/, i18n/, offline/,
  api/, models/; and the React frontend).
- The data flow of the answer workflow: understand -> route -> resolve refs ->
  hybrid retrieve -> generate (grounded) -> validate citations -> evidence
  strength / abstain. What is sync vs async; where state lives; who owns it
  (prefer immutable state + explicit transitions).
- Every module boundary called out explicitly (that's where integration bugs
  live).
- For the streaming answer path, state the concurrency model in prose: status
  events stream first; the FINAL prose is only rendered AFTER citation
  validation completes (never stream unvalidated claims).

--- 1.2 docs/INTERFACES.md ---
Define the exact contract at every boundary before implementing:
- Function signatures / message shapes.
- The immutable data schemas (ChatResponse, Claim, Source, RetrievalHit,
  RuleResult, EvidenceStrength, Warning) — see plan §6.
- For EVERY dependency in DEPENDENCY_INVENTORY.md: the injectable interface it
  sits behind (LLMProvider, EmbeddingProvider, TranslationProvider,
  VectorStore, KeywordIndex), AND the ONE real entry point
  (backend/app/main.py build_app()/lifespan) where the real implementation is
  constructed and injected. Write that named target down now.
- Error contract per boundary: which errors can cross, who handles vs
  propagates. Forbid bare `except Exception: pass` without a same-line log.

--- 1.3 docs/TASK_PLAN.md ---
- The ordered task list below (T000..T025) with explicit dependencies.
- Mark each task's RISK (novelty/uncertainty). Order HIGH-risk earlier. The
  HIGH-risk pieces here are: citation validator (T009), hybrid fusion tuning
  (T007), temporal current-law filter (T012), offline fallback wiring (T013),
  deterministic rule engine reproducibility (T014). Spike the risky assumption
  before the full build where warranted.
- Include the explicit final wiring task (T011 + a dedicated check): "wire every
  provider interface into build_app() and add one test per dependency proving
  the real factory is reachable from the real entry point."

--- 1.4 docs/RISK_LOG.md ---
- Concrete ways this build can go wrong (corpus quality, Gemini rate limits,
  legal-term mistranslation, citation hallucination, chunk-context loss) + a
  mitigation each (spike, extra fixtures, design choice, or accept+monitor).

CHECKPOINT: present ARCHITECTURE.md, INTERFACES.md, TASK_PLAN.md, RISK_LOG.md
together. Wait for confirmation before ANY implementation. This is the single
most important checkpoint.

================================================================================
PHASE 2 — BASELINE BUILD (mock-first, follows the plan, pushes per feature)
================================================================================
Implement TASK_PLAN.md in order against the INTERFACES.md contracts. If reality
forces a deviation, STOP, update INTERFACES.md/ARCHITECTURE.md, note it in
RISK_LOG.md, then continue — never drift silently.

--- 2.1 Mock-first external-dependency protocol ---
For EVERY dependency (Gemini LLM, Gemini embeddings, Bhashini, and the vector /
keyword stores), using the interface from INTERFACES.md:
1. Write the REAL integration completely (real client, request/response shapes,
   error handling, retry/backoff, 429 handling) — production code, not a TODO.
2. Call it ONLY through the injectable interface. Workflow code never imports the
   SDK directly.
3. Build a fixture-backed fake of the same interface:
   - fixtures/{dependency}/ with synthetic samples: normal, edge (empty, huge,
     unicode/Devanagari/Telugu, code-mixed), and error (timeout, 429, 5xx,
     malformed).
   - the fake samples randomly by default; deterministically via seed when a
     test needs a specific scenario.
   - it can force failure modes on request (e.g. FakeLLM(force_error="timeout")).
4. Config decides which loads: if the real credential env var is set -> real;
   else -> fixture-backed fake, logging clearly that fixture mode is active
   (never silently pretend to be live).
5. Document the swap in docs/REAL_API_SETUP.md: exact env vars, where to get each
   credential, and confirmation that no code change is needed.

--- 2.2 Dependency pinning + preflight + smoke test ---
- Backend: use Python 3.11 (`py -3.11 -m venv venv`). requirements.in (ranges) -> install -> tools/smoke_test_deps.py ->
  freeze requirements.lock.txt; requirements.txt = "-r requirements.lock.txt".
  When a dependency is migrated, update requirements.in in the SAME commit.
- smoke_test_deps.py: load .env; set HF cache dirs; import key libs; Chroma
  PersistentClient with Settings(anonymized_telemetry=False) (graceful
  fallback); PREWARM the sentence-transformers embedding model (force download)
  so retrieval never fails later; exit 0/1.
- tools/preflight_check.py: validate dirs/files; ensure a sample corpus exists
  (else build it from fixtures); import schema + instantiate a ChatResponse;
  run smoke test; Gemini check = WARN if key empty, FAIL if key set but the call
  fails. Run preflight before the task loop; stop if it fails.
- Frontend: `npm ci` reproducible; `npm run build` must pass. Component/behaviour
  tests use Vitest + React Testing Library (jsdom, offline, mock API client); the
  click-a-citation -> source-drawer flow may use Playwright headless. Frontend
  acceptance is fixture-based and never requires a live backend.
- Corpus: the offline test suite runs on a small COMMITTED sample corpus fixture.
  The REAL corpus is built separately by scripts/fetch_corpus.py, which downloads
  the public statutes/guidelines listed in the plan and records provenance + hash
  + licence per document. This fetch is NOT on the offline test path and never
  gates the suite — but corpus quality is the main real-world variable, so treat
  fetch + provenance as a first-class, reviewable step (its own commit).

--- 2.3 CONCRETE TASK LIST (T000..T025) ---
Each task: implement the file(s), write a behavior-based acceptance script under
tools/acceptance/T0XX.py (exit 0/1, fixture-only, NO real keys), run it via
tools/run_acceptance.py, and on PASS -> COMMIT + PUSH (GIT PROTOCOL). On FAIL ->
retry <=3 then STOP with diagnostics.

  T000  Repo init: git init, .gitignore, .env.example, remote, first push;
        folder skeleton + __init__.py; logs/.  [risk: low]
  T001  Immutable contracts: workflow/schema.py (ChatResponse, Claim, Source,
        RetrievalHit, RuleResult, EvidenceStrength, Warning) + models/enums.py
        (Jurisdiction, ForceState, EvidenceStrength, FormulationType, Domain).
        Acceptance: import + instantiate each; round-trip serialize.  [HIGH]
  T002  Provider interfaces + fixture fakes: LLMProvider, EmbeddingProvider,
        TranslationProvider; FakeLLM/FakeEmbeddings/FakeTranslation from
        fixtures/. Acceptance: fakes satisfy the interface; force_error works.
        [HIGH]
  T003  Corpus manifest + ingestion: manifest.json schema (provenance, licence,
        status, authority, effective_date); PDF (PyMuPDF)/HTML (bs4) -> raw text;
        a small committed sample corpus fixture; scripts/fetch_corpus.py builds
        the REAL corpus with provenance (its own commit, off the offline test
        path). Acceptance: ingest sample -> N docs with full provenance; licence
        field enforced.  [med]
  T004  Legal-aware chunking: split on section/heading; keep proviso/explanation
        with parent; carry section+jurisdiction+effective_date metadata; tables/
        forms separate. Acceptance: known statute -> chunks keep section context.
        [med]
  T005  Embeddings + vector store: EmbeddingProvider (Gemini real / local fake) +
        Chroma wrapper behind VectorStore. Acceptance: index sample -> semantic
        query returns expected chunk (fake embeddings, deterministic).  [med]
  T006  Keyword index (BM25) behind KeywordIndex. Acceptance: "Section 3(p)"
        exact query outranks semantic-only noise.  [med]
  T007  Hybrid retrieval + reference resolver: resolve exact Section/Form/Act
        first; RRF-fuse vector+keyword; jurisdiction + as_of eligibility BEFORE
        ranking; authority as tie-break. Acceptance: multi-case Recall@k on the
        curated fixture set >= agreed gate.  [HIGH]
  T008  Grounded generation: prompt uses ONLY server-assigned evidence IDs via
        LLMProvider; returns atomic claims + evidence IDs. Acceptance (fake LLM):
        output references only supplied IDs.  [med]
  T009  Citation validator (CORE): reject unknown evidence IDs; deterministic
        checks of section numbers/dates/amounts vs source; drop unsupported ->
        abstain; render only after validation. Acceptance (multi-case): valid ->
        pass; invented ID -> rejected; wrong section number -> flagged; no-support
        -> abstain.  [HIGHEST]
  T010  Evidence strength + abstention: composite strength (coverage, exact-
        section, agreement, authority, recency); abstain on out-of-corpus / low
        coverage / conflict. Acceptance: out-of-corpus query -> abstain;
        strong-match -> "high".  [HIGH]
  T011  /api/chat + WIRING: assemble the workflow; wire REAL providers in
        build_app() behind the credential flag. Acceptance: call app via its real
        entry point; assert the real factory path is constructed (grep + an
        integration test), fixtures still used for the call.  [HIGH]
  T012  Temporal current-law: ForceState + effective_date + as_of (default
        today); retrieval returns in-force version; "law as of" in response;
        conflict -> warn/abstain. Acceptance: repealed provision filtered;
        in-force returned; as_of honored.  [HIGH]
  T013  Offline / resilience: local fallback index; extractive-only answer
        (passages + citations, no generation) on LLM failure; provider circuit
        breaker + health; answer_mode label (live | extractive | cached); cached
        approved demo answers used ONLY as an outage fallback and visibly
        labelled (never the primary path). Acceptance: force LLM outage ->
        extractive cited answer, answer_mode="extractive"; cached path labelled.
        [HIGH]
  T014  Deterministic rule engine + rule sets: rules/dsl.py, engine.py,
        abs_rules.py, classification_rules.py; each rule cites source+version;
        missing required fact -> "insufficient information". Acceptance: same
        input -> same obligation across 100 runs; every obligation cites a
        source; missing fact -> asks.  [HIGH]
  T015  Domain router: multi-label domains + mandatory triggers (biological
        resource + commercial -> ABS always) + ambiguity protocol. Acceptance:
        cross-domain query hits >=2 domains; trigger fires; unevaluated domain
        disclosed in warnings.  [med]
  T016  /api/abs/check + /api/classify endpoints over the rule engine.
        Acceptance: ABS + classification flows return sourced results incl.
        insufficient-info path.  [med]
  T017  i18n glossary + translate: locked bilingual legal glossary; preserve
        statute names/section numbers verbatim; Hindi + Telugu via
        TranslationProvider; abstain if translation changes a compliance input.
        Acceptance (fake translation): statute refs preserved; glossary terms
        locked.  [med]
  T018  /api/roadmap + /api/compare over the validated answer object (reuse
        ValidatedClaims — no second generation). Acceptance: roadmap/comparison
        cells carry validated evidence IDs.  [med]
  T019  Sensitive-Invention mode: local/extractive-only, NO external LLM calls;
        warning before any external send. Acceptance: sensitive flag -> zero
        LLMProvider(real) calls.  [med]
  T020  PDF export from the validated object (no re-generation); includes corpus
        version, "law as of", sources, disclaimer. Acceptance: exported PDF ==
        on-screen validated answer.  [low]
  T021  Frontend chat: Chat page, ChatMessage with inline citation chips,
        SourceDrawer, EvidenceStrengthBadge, LawAsOfBadge, AnswerModeBadge,
        AbstentionNotice; white neo-brutalist theme. Acceptance: cited answer
        renders; clicking a citation opens the exact passage.  [med]
  T022  Frontend wizards: ClassificationWizard + ABSWizard (exact question flows
        from plan §10-11), Result cards. Acceptance: each branch -> correct
        result; unknown -> insufficient-info.  [med]
  T023  Frontend roadmap/comparison/jurisdiction toggle/sensitive toggle/language
        selector/disclaimer banner. Acceptance: jurisdiction toggle changes
        results; sensitive toggle enforced.  [low]
  T024  Eval harness + smoke: eval/testset.jsonl (stratified + out-of-scope +
        adversarial), eval/run_eval.py (Recall@k, citation validity, correct-
        abstention, legal-term preservation, p50/p95), tests/smoke_demo.py (full
        path). Acceptance: run_eval + smoke_demo both pass on fixtures.  [med]
  T025  Deployment: docker-compose (frontend, backend, chromadb + healthcheck);
        scripts/verify_release.py (corpus count/hash at startup); README +
        REAL_API_SETUP.md. Acceptance: `docker compose up` healthy; startup
        integrity check passes.  [med]

--- 2.4 Wiring verification (mandatory before the Phase-2 checkpoint) ---
For every provider interface in INTERFACES.md:
1. Grep-confirm the REAL implementation's constructor is called at least once
   OUTSIDE its own module and outside tests — in build_app()/lifespan.
2. If not, the integration does not exist from the user's perspective — fix
   before "done", not as follow-up.
3. Keep one integration-shaped test per dependency that builds the app via its
   real entry point with the real factory supplied and asserts the real
   implementation was instantiated (call itself may use fixtures).
4. Record ✅/❌ + grep evidence next to each dependency in TASK_PLAN.md.

CHECKPOINT: v1 exists, matches the architecture (deviations logged), passes all
acceptance tests on fixtures only (zero credentials), passes §2.4 wiring
verification, every feature committed AND pushed. Wait for "continue" before
Phase 3.

================================================================================
PHASE 3 — MEASURED IMPROVEMENT LOOP
================================================================================
--- 3.0 Baseline metrics ---
Capture docs/METRICS.md across the dimensions below. Before trusting any number,
confirm the instrumentation actually covers what it claims (e.g., end-to-end
latency times every hop from user action to rendered answer, not just the first
and last). Every iteration re-runs the same fixture-based suite. Anything not
measurable this way goes to docs/FUTURE_IDEAS.md, not the loop.

--- 3.1 Dimension taxonomy (every dimension gets a real candidate at least once
        per {DIMENSION_SWEEP}=3 iterations; track in docs/BACKLOG.md) ---
 1. GROUNDING / CITATION INTEGRITY — % of claims with a validated supporting
    citation; fabricated/unsupported-citation count (target 0); correct-
    abstention vs false-abstention. This is dimension ZERO in spirit: any
    regression here (a previously-grounded answer now emitting an unsupported
    claim) is a maximum-severity CORRECTNESS bug that stops the loop (see 3.3).
 2. CORRECTNESS — bugs, wrong edge cases, spec deviations; failing/flaky tests.
 3. LEGAL FIDELITY — current-law (as_of) correctness; deterministic-rule
    reproducibility; legal-term preservation across Hindi/Telugu.
 4. RETRIEVAL QUALITY — Recall@k, exact-reference hit rate, authority ordering.
 5. PERFORMANCE — p50/p95 latency; separate genuine processing time from
    time-spent-waiting-on-429/backoff so a quota hit isn't read as a regression.
 6. RELIABILITY / RESILIENCE — fault-injection pass rate; offline/extractive
    fallback correctness; circuit-breaker behavior.
 7. SECURITY — input validation, prompt-injection boundary (retrieved text is
    data, never instructions), secret handling, dependency CVEs.
 8. ERROR HANDLING & EDGE CASES — empty/huge/malformed/Devanagari/Telugu/code-
    mixed inputs; edge-fixture coverage %.
 9. OBSERVABILITY — % of failure paths logging actionable context; specifically
    % of `except` blocks that log the caught exception's content.
10. UX / ERGONOMICS — clarity of source drawer, evidence-strength labelling,
    abstention messaging, wizard flows.
11. CODE QUALITY / MAINTAINABILITY — duplication, complexity, boundaries.
12. TEST DEPTH — % of documented edge/error fixtures actually exercised.
13. COST EFFICIENCY — Gemini call count + tokens per answer; caching wins.
14. DOCUMENTATION — README/REAL_API_SETUP accuracy vs code.
15. WIRING INTEGRITY — for every provider interface, is the real implementation
    still reachable from build_app() after this iteration? Rerun §2.4 checks
    EVERY iteration regardless of the iteration's target dimension; a regression
    is a maximum-severity CORRECTNESS bug that stops the loop.

--- 3.2 Each iteration ---
1. GENERATE up to 5 scoped candidates, drawing from underrepresented dimensions
   first. Each: dimension, one-line description, Impact(1-10), Confidence(0-1),
   Effort(1-10), predicted_ROI = (Impact x Confidence) / Effort.
2. SELECT the single highest predicted_ROI above {ROI_THRESHOLD}=1.5. If none
   clears the bar, go to Phase 4.
3. IMPLEMENT exactly ONE change (independently measurable + revertible). All
   testing stays fixture-based. A contract change is flagged, never silent.
4. RE-MEASURE the full suite, INCLUDING dimensions 1 and 15 every iteration
   regardless of the target (a refactor can silently drop the real wire or break
   grounding).
5. LOG to docs/IMPROVEMENT_LOG.md (append-only):
     iteration | dimension | change | predicted_ROI | measured_delta | decision
6. DECIDE: improved (or a real qualitative win, no regression) -> keep, COMMIT +
   PUSH (GIT PROTOCOL). Flat/worse -> revert, mark "no-op" in BACKLOG.md (never
   retried).

--- 3.3 Stopping conditions (ANY ends the loop; HARD beats SOFT) ---
a. SOFT — rolling ROI over last {K}=5 iterations < {ROI_THRESHOLD}.
b. SOFT — no candidate clears the ROI bar across any dimension.
c. HARD — {MAX_ITERATIONS}=30 reached.
d. HARD — {MAX_TIME} / {MAX_TOKENS} budget reached.
e. HARD — 3 consecutive reverted/no-op iterations.
f. HARD — a GROUNDING (dim 1) or WIRING (dim 15) regression: stop IMMEDIATELY,
   before evaluating any other condition, and fix it as the very next action.
Report which condition triggered the stop.

--- 3.4 Guardrails ---
- Never modify immutable contract files as "polish"; it's its own high-visibility
  candidate.
- Never require a real credential to pass a test, ever. Live-only candidates are
  implemented behind the fixture pattern and noted in REAL_API_SETUP.md for a
  live spot-check after keys are added.
- Every kept change = its own atomic commit (message carries dimension +
  predicted ROI + measured delta) AND is pushed.
- CHECKPOINT every {N}=5 iterations: print iteration #, metrics vs baseline,
  dimension coverage, top of backlog; wait for "continue" (a real pause).

================================================================================
PHASE 4 — WRAP-UP
================================================================================
Produce docs/FINAL_REPORT.md:
- baseline vs final metrics, side by side, by dimension.
- every kept change with measured impact; every reverted/no-op candidate.
- remaining BACKLOG items that never cleared the ROI bar.
- which stopping condition ended the loop.
- confirmation the full suite passes on fixtures only (zero credentials).
- confirmation ARCHITECTURE.md/INTERFACES.md still match the code (deviations
  reconciled).
- the load-bearing line: §2.4/§3.1-15 wiring verification passes for EVERY
  dependency, listed individually; and grounding (dim 1) shows zero fabricated/
  unsupported citations on the eval set.
Confirm REAL_API_SETUP.md is current: every env var, where to get each
credential, and that setting them is the entire remaining step to go live.
Confirm every feature and every kept improvement is committed AND pushed
(git log origin/main is clean and current).

Wait for sign-off.

BEGIN NOW at Phase 0.
