"""T003 — LLM client selection (research R1): fake by default, Gemini only with both settings. No network call."""
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
