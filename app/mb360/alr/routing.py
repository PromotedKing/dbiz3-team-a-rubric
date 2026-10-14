"""ALR BR-008 (routing after "Submit report") with BR-002 and BR-007."""
from .thresholds import ABOVE
from .validation import NO_SYMPTOMS


def route(label: str, symptoms: list[str]) -> tuple[str, str | None]:
    """Return (target screen, case source or None)."""
    has_symptom = any(s != NO_SYMPTOMS for s in symptoms)
    if label == ABOVE:
        return "S-028", "Metric report"      # branch 1, with or without symptoms (D-32)
    if has_symptom:
        return "S-026", "Symptom"            # branch 2 (BR-007)
    return "S-027", None                     # branch 3: no case, no status
