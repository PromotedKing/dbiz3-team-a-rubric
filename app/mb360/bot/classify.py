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


_CLAUSE = re.compile(r"[,.;:!?\n]|\b(?:nhưng|nhung|mà|but|however)\b")
_WORD = re.compile(r"[\w']+")


def danger_hits(text: str, phrases: list[str], negation: dict | None) -> tuple[bool, bool]:
    """(an affirmed danger phrase, a denied one) — BOT §10 Q15, D-91 (proposed).

    A danger phrase is denied only when, in the same clause, a negator ("không", "chưa", "not", "no" …) comes right
    before it, with at most four filler words between ("không bị", "không hề có", "don't have any"). Anything else
    stays a danger sign, the safe side: "không biết có bị ra máu không", "không còn ra máu" (it bled before) and
    "không ra máu nhưng đau bụng dữ dội" (the second sign is not denied). A phrase that is itself negative ("không
    đạp", "no fetal movement") is matched as a whole, so its own "không" never denies it."""
    lowered = (text or "").lower()
    accentless = lowered == plain(lowered)
    form = plain if accentless else (lambda s: s.lower())
    negators = [form(n).split() for n in (negation or {}).get("negators", [])]
    fillers = {form(f) for f in (negation or {}).get("fillers", [])}
    affirmed = denied = False
    for p in phrases:
        for m in re.finditer(_pattern(form(p)), lowered):
            clause = _CLAUSE.split(lowered[:m.start()])[-1]
            words = _WORD.findall(clause)
            i, skipped = len(words), 0
            while i and skipped < 4 and words[i - 1] in fillers:
                i, skipped = i - 1, skipped + 1
            if negators and any(n and words[max(i - len(n), 0):i] == n for n in negators):
                denied = True
            else:
                affirmed = True
    return affirmed, denied


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


def general_framing(text: str, k: dict | None = None) -> bool:
    """D-92 (proposed, BOT §10 Q18): the question asks about a danger sign in general, not about the mother right now.

    True when it says so ("mình hỏi chung", "just asking") or asks for knowledge about a third person or a case ("bà bầu
    bị chảy máu là dấu hiệu gì", "nếu vỡ ối thì cần làm gì") — and nothing in it says the sign is hers or happening now
    ("em bị", "mình đang", "từ sáng", "my"). A bare "chảy máu là bị gì?" is neither, so it keeps the danger notice."""
    g = (k or _lists()).get("general_framing")
    if not g:
        return False
    rest = (text or "").lower()
    for d in g["disclaimers"]:                       # "không phải em bị" says the opposite of "em bị"
        rest = re.sub(_pattern(plain(d) if rest == plain(rest) else d.lower()), " ", rest)
    if has_any(rest, g["first_person"]) or has_any(rest, g["current"]):
        return False
    return has_any(text, g["explicit"]) or (has_any(text, g["knowledge"]) and has_any(text, g["third_person"]))


def danger_topic(text: str) -> bool:
    """The question names a danger sign, affirmed or not (S-034 adds the hotline line under a general answer, D-92)."""
    k = _lists()
    return any(danger_hits(text, k["danger_phrases"], k.get("negation")))


def classify(text: str) -> dict:
    k = _lists()
    affirmed, denied = danger_hits(text, k["danger_phrases"], k.get("negation"))
    general = (affirmed or denied) and general_framing(text, k)
    if affirmed and not general:
        return {"category": "needs_nurse", "danger": True}
    if not general and (has_any(text, k["personal_health_markers"]) or has_any(text, k["symptom_words"])
                        or has_any(text, k.get("emotional_markers", []))        # worry, sadness, crying → nurse (D-93)
                        or has_any(text, k.get("nurse_requests", []))):         # "gọi y tá cho em" → the nurse offer (D-93)
        return {"category": "needs_nurse", "danger": False}
    found = lookup(text, k)
    if found:
        if has_any(text, k["app_lookups"]["interpretation"]):     # what the value means → nurse (BR-002, BR-006)
            return {"category": "needs_nurse", "danger": False}
        return {"category": "lookup", "danger": False, "lookup": found}
    if not (denied or general) and not has_any(text, k["pregnancy_topics"]):    # a named danger sign is a pregnancy topic
        return {"category": "out_of_scope", "danger": False}
    return {"category": "general", "danger": False}
