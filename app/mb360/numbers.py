"""A number typed by the mother: "58,5" and "58.5" both read as 58.5 (Vietnamese phones type a comma); nan, inf and
values of 0 or less are refused. This is a format check, not a clinical range (D-16 and D-80 U18 stay open until the SME answers)."""
import math

NOT_A_NUMBER = "Enter a number."
NOT_POSITIVE = "Enter a number greater than 0."


def read(text: str | None) -> tuple[str | None, str | None]:
    """(value written with a dot, error label); both None when the field is empty."""
    text = (text or "").strip().replace(",", ".")
    if not text:
        return None, None
    try:
        number = float(text)
    except ValueError:
        return None, NOT_A_NUMBER
    if not math.isfinite(number):
        return None, NOT_A_NUMBER
    if number <= 0:
        return None, NOT_POSITIVE
    return text, None
