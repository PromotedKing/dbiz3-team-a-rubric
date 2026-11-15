"""Output check of an LLM answer before the mother sees it (BOT BR-002, BR-005; spec-BOT §10 Q16).

The question is checked before the LLM (classify.py); this module checks the answer after it. An answer is held back,
and FALLBACK_TEXT is shown instead, when it
- gives a medicine dose ("500 mg", "2 viên"),
- reads like a diagnosis of the mother ("chẩn đoán", "mẹ đang bị"),
- suggests a food or medicine on the watch list, unless the same sentence tells her to avoid or limit it.

The word lists are in keywords.json under "answer_checks" — a team draft, Pending SME, like the question lists. The raw
answer and the reasons stay in AI_RESPONSE_LOG (FR-004), so a held-back answer can be reviewed."""
import re

from . import classify

FALLBACK_TEXT = "I can't give a safe answer to this question here. Please ask your doctor or a nurse."
_SENTENCE = re.compile(r"[.!?;\n]+")


def _checks() -> dict:
    return classify._lists().get("answer_checks", {})


def check(answer: str) -> list[str]:
    """The reasons to hold the answer back; an empty list when it can be shown."""
    k, text, reasons = _checks(), answer or "", []
    if any(re.search(p, text, re.IGNORECASE) for p in k.get("dose_patterns", [])):
        reasons.append("dose")
    if classify.has_any(text, k.get("diagnosis_phrases", [])):
        reasons.append("diagnosis")
    avoid = k.get("avoid_words", [])
    for sentence in _SENTENCE.split(text):
        if classify.has_any(sentence, k.get("watch_list", [])) and not classify.has_any(sentence, avoid):
            reasons.append("watch_list")
            break
    return reasons
