"""BOT FR-006, FR-010, FR-011, BR-002, BR-005: classify a question (research R2).

Order: danger phrase → needs_nurse (+ danger); personal-health marker → needs_nurse; no pregnancy-topic word →
out_of_scope; otherwise general. The word lists are provisional (keywords.json, Pending SME — BOT Q2, Q12, Q14)
and are read on each call, so a change to the file changes the behaviour."""
import json
from pathlib import Path

KEYWORDS_FILE = Path(__file__).with_name("keywords.json")


def _lists() -> dict:
    return json.loads(Path(KEYWORDS_FILE).read_text(encoding="utf-8"))


def classify(text: str) -> dict:
    t = (text or "").lower()
    k = _lists()
    if any(p.lower() in t for p in k["danger_phrases"]):
        return {"category": "needs_nurse", "danger": True}
    if any(p.lower() in t for p in k["personal_health_markers"]):
        return {"category": "needs_nurse", "danger": False}
    if not any(p.lower() in t for p in k["pregnancy_topics"]):
        return {"category": "out_of_scope", "danger": False}
    return {"category": "general", "danger": False}
