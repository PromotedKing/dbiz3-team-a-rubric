"""LLM clients for the chatbot (research R1; D-76; team decision 26/10/2026).

FakeLLM is the default: no network, no key — tests and every laptop work with it. GeminiLLM (Google AI Studio)
is used only when GEMINI_API_KEY and GEMINI_MODEL are set in the environment or in the local, git-ignored `.env`.
MB360_LLM=fake forces the fake client. Only the question, the earlier turns of the conversation and the
gestational week are ever passed in (BR-001)."""
import json
import os
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
SYSTEM_PROMPT = (
    "You are the first-line assistant of the Mother & Baby 360 app of Thu Cuc Hospital. Answer only general questions "
    "about pregnancy, prenatal care, nutrition and postpartum wellness, briefly and in the language of the question. "
    "Politely decline any other topic. Never diagnose, never interpret the mother's own symptoms or results, never "
    "give a personal treatment; say that a nurse or doctor should be consulted instead."
)


class FakeLLM:
    name = "fake"

    def __init__(self):
        self.last_input = None

    def answer(self, question: str, context: dict) -> str:
        self.last_input = (question, context)
        return "[Sample chatbot answer]"


class GeminiLLM:
    name = "gemini"
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str, timeout: float = 20.0):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def answer(self, question: str, context: dict) -> str:
        contents = []
        for turn in context.get("earlier", []):
            contents.append({"role": "user", "parts": [{"text": turn["question"]}]})
            contents.append({"role": "model", "parts": [{"text": turn["answer"]}]})
        contents.append({"role": "user", "parts": [{"text": f"(Gestational week {context.get('gestational_week')}) {question}"}]})
        body = json.dumps({"systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}, "contents": contents}).encode("utf-8")
        req = urllib.request.Request(self.URL.format(model=self.model), data=body, method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()


def _env_file_values() -> dict:
    values = {}
    try:
        for line in Path(ENV_FILE).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return values


def get_client():
    if os.environ.get("MB360_LLM") == "fake":
        return FakeLLM()
    file_values = _env_file_values()
    key = os.environ.get("GEMINI_API_KEY") or file_values.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL") or file_values.get("GEMINI_MODEL")
    return GeminiLLM(key, model) if key and model else FakeLLM()
