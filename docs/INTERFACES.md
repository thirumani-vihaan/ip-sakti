# INTERFACES

The exact contracts at every boundary. Types live in `workflow/schema.py` + `models/enums.py` (immutable once approved).

## Enums (`models/enums.py`)
```
Jurisdiction     = INDIA | INTERNATIONAL
ForceState       = IN_FORCE | NOT_YET_IN_FORCE | REPEALED
EvidenceStrength = HIGH | MODERATE | LIMITED
FormulationType  = CLASSICAL | PROPRIETARY | NEW_DRUG | PHYTOPHARMACEUTICAL | NUTRACEUTICAL | COSMETIC
Domain           = PATENT | GI_TRADEMARK | ABS | REGULATORY | TK_RISK | INTERNATIONAL
AnswerMode       = LIVE | EXTRACTIVE | CACHED
```

## Domain contract (`workflow/schema.py`, pydantic v2)
```
# INVARIANT: Source.id == the server-assigned evidence_id from RetrievalHit.
# The model only ever sees/cites these ids; it cannot invent new ones.
Source(BaseModel):
  id: str; title: str; section: str|None; page: int|None; url: str|None
  local_excerpt: str; status: ForceState; authority: str
  effective_date: date|None; as_of: date; document_hash: str
Claim(BaseModel):
  text: str; source_ids: list[str]                 # must be non-empty for a supported claim
RetrievalHit(BaseModel):
  evidence_id: str; text: str; score: float; source: Source
RuleResult(BaseModel):
  obligation: str|None; authority: str|None; forms: list[str]
  source_id: str|None; rule_version: str|None
  status: Literal["decided","insufficient"]; missing: list[str]
Warning(BaseModel):
  code: str; message: str
ChatResponse(BaseModel):
  claims: list[Claim]; sources: list[Source]; warnings: list[Warning]
  answer_mode: AnswerMode
  evidence_strength: EvidenceStrength
  jurisdiction: Jurisdiction; language: str; as_of: date; corpus_version: str
```

## Injectable interfaces (Protocols) and their fixture fakes
```
LLMProvider:          generate(prompt, evidence: list[RetrievalHit]) -> list[Claim]
                      real=GeminiLLM   fake=FakeLLM(fixtures/llm/, force_error=...)
EmbeddingProvider:    embed(texts: list[str]) -> list[list[float]]
                      real=GeminiEmbeddings  fake=FakeEmbeddings (deterministic, seeded)
TranslationProvider:  translate(text, src, tgt) -> str   (preserves locked glossary terms)
                      real=BhashiniTranslation  fake=FakeTranslation(fixtures/translation/)
VectorStore:          upsert(hits) / query(vector, k, filters) -> list[RetrievalHit]
                      impl=ChromaVectorStore (local; test uses ephemeral persist dir)
KeywordIndex:         add(docs) / search(query, k) -> list[RetrievalHit]
                      impl=BM25Index (rank-bm25)
```

## The ONE real entry point
`backend/app/main.py :: build_app(settings) -> FastAPI`
- Reads `config.Settings`; for each provider, constructs the REAL impl iff its credential env var is set, else the fixture-backed fake (logging fixture mode).
- Injects providers into the workflow + routes. This is the single place real factories are constructed; a per-dependency test asserts the real factory is reachable from here (loop §2.4).

## Error contract per boundary
- Provider calls raise typed `ProviderError` (with `retryable: bool`); `integrations/provider.py` handles timeout/429/5xx with backoff + circuit breaker, then either returns a degraded result or raises `ProviderError(retryable=False)` which the workflow turns into `answer_mode=extractive` or an abstention.
- `citation_validator` never raises on bad model output — it drops the claim and records a `Warning`; if no supported claim remains → abstention ChatResponse.
- `rules/engine` returns `RuleResult(status="insufficient", missing=[...])` rather than raising when facts are absent.
- **Forbidden:** bare `except Exception: pass` at any boundary without a same-line log of the caught error.
