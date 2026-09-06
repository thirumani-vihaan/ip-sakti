"""Real Bhashini (ULCA) translation. httpx imported lazily; not exercised offline.

Live spot-check required after credentials are set (see docs/REAL_API_SETUP.md).
"""
from __future__ import annotations

from app.integrations.provider import ProviderError


class BhashiniTranslation:
    INFERENCE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    def __init__(self, user_id: str, ulca_key: str | None, inference_key: str):
        self.user_id = user_id
        self.ulca_key = ulca_key
        self.inference_key = inference_key

    def translate(self, text: str, src: str, tgt: str) -> str:
        if src == tgt:
            return text
        try:
            import httpx  # lazy
            headers = {
                "Authorization": self.inference_key,
                "userID": self.user_id,
                "ulcaApiKey": self.ulca_key or "",
            }
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {"language": {"sourceLanguage": src, "targetLanguage": tgt}},
                    }
                ],
                "inputData": {"input": [{"source": text}]},
            }
            resp = httpx.post(self.INFERENCE_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["pipelineResponse"][0]["output"][0]["target"]
        except Exception as e:
            raise ProviderError(f"bhashini translate failed: {e}", retryable=True) from e
