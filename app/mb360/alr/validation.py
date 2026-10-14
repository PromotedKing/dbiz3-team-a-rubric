"""S-025A form rules: ALR FR-011, FR-013, FR-014, BR-006, BR-017.

No numeric range is checked: valid ranges are open (ALR §10 Q9, D-16)."""
from datetime import datetime

from .thresholds import URINE_SCALE

GROUP2 = ("Blood pressure", "Blood glucose", "Urine protein")
NO_SYMPTOMS = "No symptoms"
SYMPTOMS = [NO_SYMPTOMS, "Vaginal bleeding", "Severe abdominal pain", "Waters breaking or fluid leakage",
            "Severe headache, dizziness or blurred vision", "Absence of fetal movement", "Palpitations", "Other"]
GLUCOSE_CONTEXTS = ("fasting", "post_1h", "post_2h")
FORM_TIME = "%Y-%m-%dT%H:%M"   # HTML datetime-local


def parse_time(text: str) -> datetime:
    return datetime.strptime(text, FORM_TIME)


def validate(form: dict, active_metrics: set[str], now: datetime | None = None) -> dict[str, str]:
    errors: dict[str, str] = {}
    metric = form.get("metric") or ""
    if metric != "Symptom" and metric not in active_metrics:
        errors["metric"] = "Choose a metric from your Doctor's instructions, or report symptoms."

    symptoms = list(form.get("symptoms") or [])
    if not symptoms:
        errors["symptoms"] = "Please select your symptoms"
    elif any(s not in SYMPTOMS for s in symptoms):
        errors["symptoms"] = "Choose symptoms from the list."
    elif NO_SYMPTOMS in symptoms and len(symptoms) > 1:
        errors["symptoms"] = '"No symptoms" cannot be combined with other symptoms.'

    other = (form.get("other_symptom_text") or "").strip()
    if "Other" in symptoms and not other:
        errors["other_symptom_text"] = "Describe the other symptom."
    elif other and "Other" not in symptoms:
        errors["other_symptom_text"] = 'Only when "Other" is selected.'
    elif len(other) > 100:
        errors["other_symptom_text"] = "At most 100 characters."

    measured = form.get("measured_at") or ""
    try:
        when = parse_time(measured)
        # HLT §6 / schema ck_hmr_measured_before_created: a measurement is recorded after it is taken.
        if now is not None and when > now:
            errors["measured_at"] = "The measured time cannot be later than now."
    except ValueError:
        errors["measured_at"] = "Enter the measured time."

    if metric == "Blood pressure":
        for field in ("systolic", "diastolic"):
            if not (form.get(field) or "").strip().isdigit():
                errors[field] = "Enter a whole number (mmHg)."
    elif metric == "Blood glucose":
        try:
            float(form.get("value") or "")
        except ValueError:
            errors["value"] = "Enter a number (mmol/L)."
        if form.get("glucose_context") not in GLUCOSE_CONTEXTS:
            errors["glucose_context"] = "Choose the measurement time."
    elif metric == "Urine protein":
        if form.get("level") not in URINE_SCALE:
            errors["level"] = "Choose a level."
    return errors
