"""T003 — LLM client selection (research R1): fake by default, Gemini only with both settings. No network call."""
import json
import urllib.error
import urllib.request

import pytest

from mb360.bot import llm


def test_fake_client_without_settings(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("MB360_LLM", raising=False)
    monkeypatch.setattr(llm, "ENV_FILE", tmp_path / ".env")       # no .env file
    assert isinstance(llm.get_client(), llm.FakeLLM)


def test_gemini_client_with_both_settings(monkeypatch, tmp_path):
    monkeypatch.delenv("MB360_LLM", raising=False)
    monkeypatch.setattr(llm, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    client = llm.get_client()
    assert isinstance(client, llm.GeminiLLM) and client.model == "test-model"


def test_env_file_is_read(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("MB360_LLM", raising=False)
    env = tmp_path / ".env"
    env.write_text("GEMINI_API_KEY=test-key-not-real\nGEMINI_MODEL=test-model\n", encoding="utf-8")
    monkeypatch.setattr(llm, "ENV_FILE", env)
    assert isinstance(llm.get_client(), llm.GeminiLLM)


def test_force_fake(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    monkeypatch.setenv("MB360_LLM", "fake")
    assert isinstance(llm.get_client(), llm.FakeLLM)


def test_fake_answer_and_last_input():
    fake = llm.FakeLLM()
    assert fake.answer("What should I eat?", {"gestational_week": 20, "earlier": []}) == "[Sample chatbot answer]"
    assert fake.last_input == ("What should I eat?", {"gestational_week": 20, "earlier": []})


class _Resp:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps(self.data).encode("utf-8")


def test_gemini_request_and_answer(monkeypatch):
    sent = []

    def fake_urlopen(req, timeout):
        sent.append((req.full_url, dict(req.header_items()), json.loads(req.data)))
        return _Resp({"candidates": [{"content": {"parts": [{"text": "plan", "thought": True}, {"text": "Mẹ ăn thêm đạm."}]}}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    client = llm.GeminiLLM("test-key-not-real", "gemini-3.5-flash-lite")
    answer = client.answer("Tuần 24 mẹ nên ăn gì?", {"gestational_week": 24, "earlier": [{"question": "Q", "answer": "A"}]})
    assert answer == "Mẹ ăn thêm đạm."
    url, headers, body = sent[0]
    assert url.endswith("/models/gemini-3.5-flash-lite:generateContent") and headers["X-goog-api-key"] == "test-key-not-real"
    assert [c["role"] for c in body["contents"]] == ["user", "model", "user"] and "Tuần thai 24" in body["contents"][-1]["parts"][0]["text"]
    assert "medical record" not in json.dumps(body) and body["generationConfig"]["maxOutputTokens"] > 0


def test_gemini_falls_back_to_interactions_on_404(monkeypatch):
    def fake_urlopen(req, timeout):
        if req.full_url.endswith(":generateContent"):
            raise urllib.error.HTTPError(req.full_url, 404, "not found", {}, None)
        assert req.full_url.endswith("/interactions") and json.loads(req.data)["store"] is False
        return _Resp({"steps": [{"type": "model_output", "content": [{"type": "text", "text": "Trả lời."}]}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert llm.GeminiLLM("k", "m").answer("q", {}) == "Trả lời."


def test_gemini_empty_or_failed_answer_raises(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: _Resp({"candidates": [{"content": {"parts": []}}]}))
    with pytest.raises(ValueError):
        llm.GeminiLLM("k", "m").answer("q", {})
    def quota(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 429, "quota", {}, None)
    monkeypatch.setattr(urllib.request, "urlopen", quota)
    with pytest.raises(urllib.error.HTTPError):
        llm.GeminiLLM("k", "m").answer("q", {})


def test_key_alone_uses_the_default_model(monkeypatch, tmp_path):
    monkeypatch.delenv("MB360_LLM", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(llm, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    assert llm.get_client().model == llm.DEFAULT_MODEL and llm.describe() == f"Gemini · {llm.DEFAULT_MODEL}"
