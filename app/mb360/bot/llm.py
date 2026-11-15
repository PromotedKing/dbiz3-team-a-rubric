"""LLM clients for the chatbot (research R1; D-76, D-83, D-84).

get_client() picks, in this order: FakeLLM when MB360_LLM=fake; GroqLLM (Groq's free plan, D-84) when GROQ_API_KEY is
set; GeminiLLM (Google AI Studio, D-83) when GEMINI_API_KEY is set; otherwise the fallback — FakeLLM for the tests and
mb360.main, LocalAnswers (a few written answers, no network) for mb360.server. Keys are read from the environment or the
local, git-ignored `.env`, never from the repository. Only the question, the earlier general turns of the conversation and
the gestational week are ever passed in (BR-001; BOT §5.3 E-3)."""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
SYSTEM_PROMPT = (
    "You are the first-line assistant of the Mother & Baby 360 app of Thu Cuc Hospital. Answer only general questions "
    "about pregnancy, prenatal care, nutrition and postpartum wellness, briefly and in the language of the question. "
    "Politely decline any other topic. Never diagnose, never interpret the mother's own symptoms or results, never "
    "give a personal treatment or a medicine dose; say that a nurse or doctor should be consulted instead. "
    "When suggesting foods, suggest only foods widely accepted as safe in pregnancy; never suggest a food whose safety in "
    "pregnancy is debated or that pregnant women are usually told to limit (for example liver), and if the mother asks "
    "about such a food, say that she should ask her doctor. "   # added 15/11/2026 after a live Groq answer suggested liver; wording Pending SME
    "Address the user as 'mẹ'. Keep every answer under 70 words (at most 450 characters), in plain sentences without markdown."
)


class FakeLLM:
    name = "fake"

    def __init__(self):
        self.last_input = None

    def answer(self, question: str, context: dict) -> str:
        self.last_input = (question, context)
        return "[Sample chatbot answer]"


class LocalAnswers:
    """The v1.0.0 app's answers when no Groq or Gemini key is set: short general advice in Vietnamese, chosen by topic. Sample text, Pending SME (D-81)."""
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
    """Google AI Studio (Gemini API, free tier possible; D-76, D-83). Only general questions reach it (BR-002) and only the
    question, the earlier general turns and the gestational week are sent (BR-001). The Interactions API is tried first; if
    the Interactions API answers 404, the older generateContent is used. Any failure raises, so the chat shows "Retry" (BOT §10 Q10)."""
    name = "gemini"
    BASE = "https://generativelanguage.googleapis.com/v1beta"
    MAX_TOKENS = 600

    def __init__(self, api_key: str, model: str, timeout: float = 15.0):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def _post(self, url: str, body: dict, extra: dict | None = None) -> dict:
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key, **(extra or {})})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _turns(question: str, context: dict) -> list[tuple[str, str]]:
        turns = []
        for t in context.get("earlier", []):
            turns += [("user", t["question"]), ("model", t["answer"])]
        week = context.get("gestational_week")
        return turns + [("user", f"(Tuần thai {week}) {question}" if week is not None else question)]

    def _interaction(self, turns) -> str:
        """Interactions API, the one Google documents for new projects (reference checked 07/11/2026); stateless (store: false)."""
        *earlier, (_, question) = turns
        transcript = "".join(f"{'Mẹ hỏi' if role == 'user' else 'Trợ lý trả lời'}: {text}\n" for role, text in earlier)
        data = self._post(f"{self.BASE}/interactions", {
            "model": self.model, "system_instruction": SYSTEM_PROMPT, "store": False,
            "input": (f"Các lượt trước trong cuộc trò chuyện:\n{transcript}\nCâu hỏi mới: {question}" if transcript else question),
            "generation_config": {"max_output_tokens": self.MAX_TOKENS}})
        if data.get("output_text"):
            return data["output_text"]
        texts = []
        for step in data.get("steps") or []:
            if step.get("type") == "model_output":
                content = step.get("content")
                texts = [content] if isinstance(content, str) else [c.get("text", "") for c in content or [] if c.get("type") == "text"]
        return "".join(texts)

    def _generate_content(self, turns) -> str:
        """The older generateContent endpoint, still supported for existing integrations."""
        data = self._post(f"{self.BASE}/models/{self.model}:generateContent", {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": role, "parts": [{"text": text}]} for role, text in turns],
            "generationConfig": {"maxOutputTokens": self.MAX_TOKENS}})
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts if not p.get("thought"))

    def answer(self, question: str, context: dict) -> str:
        turns = self._turns(question, context)
        try:
            text = self._interaction(turns)
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            text = self._generate_content(turns)
        if not text.strip():
            raise ValueError("empty answer from Gemini")
        return text.strip()


def describe_error(e: Exception) -> str:
    """One log line: the HTTP status and Google's own error message, without the request (no key, no question)."""
    if isinstance(e, urllib.error.HTTPError):
        try:
            detail = json.loads(e.read().decode("utf-8", "replace")).get("error", {})
            return f"HTTP {e.code} {detail.get('status') or detail.get('code') or ''}: {str(detail.get('message', ''))[:300]} [{e.url.split('?')[0]}]"
        except Exception:
            return f"HTTP {e.code} [{e.url.split('?')[0]}]"
    return f"{type(e).__name__}: {str(e)[:300]}"


class GroqLLM:
    """Groq's free plan (D-84): OpenAI-style chat completions, no card needed. Same rules as GeminiLLM: only general
    questions, only the question, the earlier general turns and the gestational week (BR-001, BR-002); any failure raises."""
    name = "groq"
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MAX_TOKENS = 1024        # reasoning models count their thinking here too

    def __init__(self, api_key: str, model: str, timeout: float = 15.0):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def answer(self, question: str, context: dict) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for t in context.get("earlier", []):
            messages += [{"role": "user", "content": t["question"]}, {"role": "assistant", "content": t["answer"]}]
        week = context.get("gestational_week")
        messages.append({"role": "user", "content": f"(Tuần thai {week}) {question}" if week is not None else question})
        body = {"model": self.model, "messages": messages, "max_completion_tokens": self.MAX_TOKENS}
        req = urllib.request.Request(self.URL, data=json.dumps(body).encode("utf-8"), method="POST", headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "mb360-chatbot/1.0"})       # Groq's edge refuses the default Python agent
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data["choices"][0]["message"].get("content") or "").strip()
        if not text:
            raise ValueError("empty answer from Groq")
        return text


DEFAULT_MODEL = "gemini-3.5-flash-lite"          # Google's suggestion for new projects, free tier (checked 07/11/2026)
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"     # on Groq's free plan (checked 07/11/2026)


def describe() -> str:
    """For the panel beside the phone: which chatbot answers."""
    client = get_client()
    if isinstance(client, GroqLLM):
        return f"Groq · {client.model}"
    return f"Gemini · {client.model}" if isinstance(client, GeminiLLM) else client.name


_fallback = FakeLLM


def use_fallback(client_class) -> None:
    """The client used when no Groq or Gemini key is set (mb360.server: LocalAnswers; tests: FakeLLM)."""
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
    def setting(name):
        return os.environ.get(name) or file_values.get(name)

    if setting("GROQ_API_KEY"):          # D-84: Groq first, it is free
        return GroqLLM(setting("GROQ_API_KEY"), setting("GROQ_MODEL") or GROQ_DEFAULT_MODEL)
    if setting("GEMINI_API_KEY"):
        return GeminiLLM(setting("GEMINI_API_KEY"), setting("GEMINI_MODEL") or DEFAULT_MODEL)
    return _fallback()


if __name__ == "__main__":          # uv run python app/mb360/bot/llm.py  → one test question, to check the key
    client = get_client()
    print("client:", describe())
    try:
        print(client.answer("Tuần 24 mẹ nên ăn thêm gì?", {"gestational_week": 24, "earlier": []}))
    except urllib.error.HTTPError as e:
        print("Refused:", e.code, e.read().decode("utf-8", "replace")[:300])
