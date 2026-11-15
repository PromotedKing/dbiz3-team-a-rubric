"""BOT FR-006, FR-010, FR-011, BR-002, BR-005: classify a question (research R2).

Order: danger phrase → needs_nurse (+ danger); personal-health marker or symptom / medicine word → needs_nurse; a data
lookup (FR-012, D-89 proposed) → lookup, or needs_nurse when it also asks what the value means (BR-002, BR-006); no
pregnancy-topic word → out_of_scope; otherwise general. A symptom is checked before the topic so that a question about
the mother's own health is offered to a nurse instead of being declined (BR-002).

Words match whole words only ("ăn" does not match "khăn", "eat" does not match "weather"); an English entry may take
-s / -es / -ed / -ing, and an entry ending in "*" matches any ending. A question typed without Vietnamese accents is
compared without accents ("ra mau" matches "ra máu"); a question with accents keeps them, so "an toàn" never reads as
"ăn". The word lists are provisional (keywords.json, Pending SME — BOT Q2, Q12, Q14) and are read on each call."""
import json
import re
import unicodedata
from pathlib import Path

KEYWORDS_FILE = Path(__file__).with_name("keywords.json")


def _lists() -> dict:
    return json.loads(Path(KEYWORDS_FILE).read_text(encoding="utf-8"))


def plain(text: str) -> str:
    """Lower case, without Vietnamese accents (đ → d)."""
    text = unicodedata.normalize("NFD", (text or "").lower().replace("đ", "d"))
    return unicodedata.normalize("NFC", "".join(c for c in text if unicodedata.category(c) != "Mn"))


def _pattern(phrase: str) -> str:
    stem = phrase.rstrip("*")
    words = r"\s+".join(re.escape(w) for w in stem.split())
    tail = r"\w*" if phrase.endswith("*") else r"(?:s|es|ed|ing)?(?!\w)"
    return r"(?<!\w)" + words + tail


def has_any(text: str, phrases: list[str]) -> bool:
    """True when the question contains one of the phrases as whole words (accent rule above)."""
    lowered = (text or "").lower()
    accentless = lowered == plain(lowered)
    for p in phrases:
        p = p.lower()
        if accentless:
            if re.search(_pattern(plain(p)), lowered):
                return True
        elif re.search(_pattern(p), lowered):
            return True
    return False


def lookup(text: str, k: dict | None = None) -> dict | None:
    """FR-012: the data-lookup topic of a question ({"topic": …, "metric": …}), or None. A topic matches when the question
    has one of its words and every cue group of one of its "needs" lines (keywords.json → app_lookups)."""
    k = (k or _lists()).get("app_lookups")
    if not k:
        return None
    for t in k["topics"]:
        if has_any(text, t["words"]) and any(all(has_any(text, k["cues"][g]) for g in line) for line in t["needs"]):
            return {"topic": t["topic"], **({"metric": t["metric"]} if "metric" in t else {})}
    return None


def classify(text: str) -> dict:
    k = _lists()
    if has_any(text, k["danger_phrases"]):
        return {"category": "needs_nurse", "danger": True}
    if has_any(text, k["personal_health_markers"]) or has_any(text, k["symptom_words"]):
        return {"category": "needs_nurse", "danger": False}
    found = lookup(text, k)
    if found:
        if has_any(text, k["app_lookups"]["interpretation"]):     # what the value means → nurse (BR-002, BR-006)
            return {"category": "needs_nurse", "danger": False}
        return {"category": "lookup", "danger": False, "lookup": found}
    if not has_any(text, k["pregnancy_topics"]):
        return {"category": "out_of_scope", "danger": False}
    return {"category": "general", "danger": False}
