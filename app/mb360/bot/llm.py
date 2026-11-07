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


class LocalAnswers:
    """The v1.0.0 app's answers when no Gemini key is set: short general advice in Vietnamese, chosen by topic. Sample text, Pending SME (D-81)."""
    name = "local"
    CLOSING = " Mẹ hỏi thêm bác sĩ ở lần khám tới nếu cần nhé."
    TOPICS = (
        (("mất ngủ", "khó ngủ", "ngủ"), "Mẹ thử nằm nghiêng, kê gối giữa hai chân và sau lưng, đi ngủ đúng giờ và hạn chế uống nhiều nước ngay trước khi ngủ. Một chút vận động nhẹ ban ngày cũng giúp dễ ngủ hơn."),
        (("tập thể dục", "vận động", "yoga", "đi bộ"), "Nếu bác sĩ không dặn gì khác, mẹ có thể đi bộ nhẹ, tập yoga bầu hoặc bơi, khoảng 30 phút mỗi ngày. Mẹ tránh động tác dễ ngã hoặc nằm ngửa lâu, và dừng lại khi thấy mệt."),
        (("chuột rút",), "Khi bị chuột rút, mẹ duỗi thẳng chân, kéo mũi bàn chân về phía người và xoa bóp nhẹ. Ban ngày mẹ nhớ uống đủ nước, vận động nhẹ và ăn thực phẩm giàu canxi."),
        (("ốm nghén", "nghén"), "Mẹ thử chia nhỏ bữa ăn, ăn chút bánh khô ngay khi thức dậy và tránh mùi gây khó chịu. Gừng và uống từng ngụm nước nhỏ cũng có thể giúp dễ chịu hơn."),
        (("sữa", "cho con bú"), "Cho bé bú sớm và thường xuyên là cách tốt nhất để có nhiều sữa. Mẹ nhớ uống đủ nước, ăn đủ bữa và nghỉ ngơi khi có thể."),
        (("rạn da", "kem rạn", "vết rạn", "stretch mark"), "Rạn da khi mang thai rất thường gặp. Mẹ giữ ẩm da hằng ngày, uống đủ nước và tăng cân từ từ theo lời bác sĩ. Trước khi mua kem trị rạn, mẹ hỏi bác sĩ xem thành phần có an toàn khi mang thai không."),
        (("ăn", "dinh dưỡng", "thực phẩm", "uống"), "Mẹ nên ăn đa dạng: đạm từ thịt nạc, trứng, cá ít thuỷ ngân; sắt và canxi từ rau xanh đậm, sữa; thêm trái cây và ngũ cốc nguyên hạt. Mẹ tránh đồ sống, tái và rượu bia."),
    )
    GENERAL = "Đây là câu hỏi chung về thai kỳ. Mẹ nên giữ lịch khám đều, ăn uống đủ chất, nghỉ ngơi hợp lý và ghi lại những gì muốn hỏi để trao đổi với bác sĩ."

    def answer(self, question: str, context: dict) -> str:
        from .classify import has_any
        body = next((answer for words, answer in self.TOPICS if has_any(question, list(words))), self.GENERAL)
        return body + self.CLOSING


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


_fallback = FakeLLM


def use_fallback(client_class) -> None:
    """The client used when no Gemini key is set (mb360.server: LocalAnswers; tests: FakeLLM)."""
    global _fallback
    _fallback = client_class


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
    return GeminiLLM(key, model) if key and model else _fallback()
