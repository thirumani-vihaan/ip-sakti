"""Real Google Gemini providers (instance-scoped `google-genai` client).

The client is created lazily on first use and cached on the instance, so there is
NO global module state to race under FastAPI's threadpool. Constructors stay cheap
and offline-safe; only the first real generate()/embed() call needs the SDK + network.
"""
from __future__ import annotations

import math
import re

from app.integrations.provider import ProviderError
from app.workflow.schema import Claim, RetrievalHit

# split a paragraph into sentences on end punctuation followed by whitespace
_SENT_RE = re.compile(r"(?<=[.!?])\s+")
_CITE_RE = re.compile(r"\[([^\]]+)\]")


class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai  # lazy
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        try:
            client = self._get_client()
            resp = client.models.generate_content(model=self.model, contents=prompt)
        except Exception as e:  # translate SDK/network errors so the pipeline can degrade
            raise ProviderError(f"gemini generate failed: {e}", retryable=True) from e
        text = (getattr(resp, "text", "") or "").strip()
        if not text:
            return []
        # Model abstains explicitly when the evidence does not answer the question;
        # returning no claims lets the pipeline fail closed into a clean abstention.
        if text.upper().startswith("INSUFFICIENT_EVIDENCE"):
            return []
        allowed = {h.evidence_id for h in evidence}
        return _to_claims(text, allowed)

    def generate_next_steps(self, query: str, claims: list[Claim]) -> list['NextStep']:
        from app.workflow.schema import NextStep
        import json
        if not claims:
            return []
            
        prompt = (
            f"Based on the following query and legal advice, provide 1 to 2 highly actionable next steps for the user.\n\n"
            f"Query: {query}\n"
            f"Advice:\n" + "\n".join(f"- {c.text}" for c in claims) + "\n\n"
            "Return the output as a clean JSON array of objects. Do not include markdown blocks or any other text.\n"
            "Each object MUST have the following string fields:\n"
            "- 'label': A short, actionable title (e.g. 'Register Patent').\n"
            "- 'description': A one-sentence explanation.\n"
            "- 'url': A link to an official Indian portal (e.g. 'https://ipindia.gov.in'). If not applicable, use '#'."
        )
        
        try:
            client = self._get_client()
            resp = client.models.generate_content(model=self.model, contents=prompt)
            text = (getattr(resp, "text", "") or "").strip()
            # strip possible markdown json block
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            if not isinstance(data, list):
                return []
                
            steps = []
            for item in data[:2]:  # max 2 steps
                steps.append(NextStep(
                    label=str(item.get("label", "Next Step")),
                    description=str(item.get("description", "")),
                    url=str(item.get("url", "#"))
                ))
            return steps
        except Exception as e:
            import traceback
            traceback.print_exc()
            # next steps are progressive enhancement; swallow errors to not fail the main answer
            return []


class GeminiEmbeddings:
    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai  # lazy
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            client = self._get_client()
            resp = client.models.embed_content(model=self.model, contents=texts)  # batched
            return [_l2_normalise(list(e.values)) for e in resp.embeddings]
        except Exception as e:
            raise ProviderError(f"gemini embed failed: {e}", retryable=True) from e


def _l2_normalise(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]  # so dot == cosine downstream


def _to_claims(text: str, allowed: set[str]) -> list[Claim]:
    """Break the response into atomic sentence-level claims, each carrying only the
    server-assigned citation ids found within it. Falls back to a single pooled claim
    if the model did not cite per-sentence, so we never lose content."""
    claims: list[Claim] = []
    for sentence in _SENT_RE.split(text):
        s = sentence.strip()
        if not s:
            continue
        cited = [m for m in _CITE_RE.findall(s) if m in allowed]
        if cited:
            claims.append(Claim(text=s, source_ids=cited))
    if claims:
        return claims
    # no per-sentence citations: keep the whole answer as one claim with pooled ids
    pooled = [m for m in _CITE_RE.findall(text) if m in allowed]
    return [Claim(text=text, source_ids=pooled)]

