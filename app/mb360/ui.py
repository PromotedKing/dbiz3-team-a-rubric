"""On-screen text and the shared app shell (docs/ui-label-reference.md, D-27, D-79).

Templates and routes keep the English labels used in every document. t() looks each label up in the
"UI label reference" table of docs/ui-label-reference.md, the only file with Vietnamese UI text, so the
wording is changed there and nowhere else. A label missing from the table is shown in English and
recorded in MISSING (the tests fail on it).
"""
import re
from datetime import datetime
from pathlib import Path

REF = Path(__file__).resolve().parents[2] / "docs" / "ui-label-reference.md"
MISSING: set[str] = set()
_TRAIL = re.compile(r"\s*\([^()]*\)\s*$")
_FIELD = re.compile(r"\{(\w+)\}")

# 5-tab bar (ui-label-reference §11, D-80): key, label, path under /m/{user_id}/
TABS = (("home", "Home", "home"), ("timeline", "Timeline", "timeline"), ("chatbot", "Chatbot", "chat"),
        ("doctor", "From doctor", "notices"), ("profile", "Profile", "profile"))
_conn = None


def use_connection(conn) -> None:
    """The database behind the tab bar's unread badge."""
    global _conn
    _conn = conn


def unread(user_id: str) -> int:
    """Unread notifications of the mother (NOTIFICATION.read_at, ACC FR-025): badge on the "From doctor" tab."""
    return _conn.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE user_id = ? AND read_at IS NULL", (user_id,)).fetchone()[0]


def _pairs(en: str, vi: str):
    """(English, Vietnamese) pairs of one table row: the whole cell, its "(UI: …)" form and each " / " part."""
    ui = None
    m = re.search(r"\(UI: ([^)]*)\)", en)
    if m:
        ui, en = m.group(1), en[:m.start()].strip()
    if _TRAIL.search(en) and not _TRAIL.search(vi):      # notes such as "(D-73)" or "(entity: Watch-Flag)"
        en = _TRAIL.sub("", en)
    if _TRAIL.search(vi) and not _TRAIL.search(en):      # "Mẹ & Bé 360 (tile)"
        vi = _TRAIL.sub("", vi)
    for e in filter(None, (en, ui)):
        yield e, vi
        es, vs = e.split(" / "), vi.split(" / ")
        if len(es) > 1 and len(es) == len(vs):
            yield from zip(es, vs)


def load(path: Path = REF) -> tuple[dict[str, str], list[tuple[re.Pattern, str]], list[tuple[str, str, str]]]:
    """Read every 3-column row under "## UI label reference": exact labels, {field} patterns, conflicts."""
    labels: dict[str, str] = {}
    conflicts = []
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## UI label reference"
            continue
        cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if not inside or len(cells) != 3 or set(cells[1]) <= set("-: ") or cells[1] == "English (used in documents)":
            continue
        for en, vi in _pairs(cells[1], cells[2]):
            if en in labels and labels[en] != vi:
                conflicts.append((en, labels[en], vi))
                continue
            labels.setdefault(en, vi)
    patterns = []
    for en, vi in labels.items():
        if _FIELD.search(en):
            rx = "".join(f"(?P<{p}>.+?)" if i % 2 else re.escape(p) for i, p in enumerate(_FIELD.split(en)))
            patterns.append((re.compile(rx + r"\Z"), vi, len(_FIELD.sub("", en))))
    patterns.sort(key=lambda p: -p[2])               # most specific row first: "Report {code} resolved" before "Report {code}"
    return labels, [p[:2] for p in patterns], conflicts


LABELS, PATTERNS, CONFLICTS = load()


def t(text, **fields) -> str:
    """Vietnamese text of an English label; t("Week {n}", n=28) fills the fields."""
    if text is None or text == "":
        return ""
    s = str(text)
    if fields:
        if s not in LABELS:
            MISSING.add(s)
        return LABELS.get(s, s).format(**fields)
    if s in LABELS:
        return LABELS[s]
    for rx, vi in PATTERNS:
        m = rx.match(s)
        if m:
            return vi.format(**{k: LABELS.get(v, v) for k, v in m.groupdict().items()})
    MISSING.add(s)
    return s


def t_list(text: str | None) -> str:
    """A ", "-joined list of labels (symptoms on S-029, S-061, S-064)."""
    return ", ".join(t(p) for p in text.split(", ")) if text else ""


def t_known(text: str | None) -> str:
    """Stored text that may be a fixed system message (chatbot decline, notification title): translated only if it is a label.
    Values inside a {field} row are translated too; anything else is shown as stored and is not a missing label."""
    if not text:
        return ""
    if text in LABELS:
        return LABELS[text]
    for rx, vi in PATTERNS:
        m = rx.match(text)
        if m:
            return vi.format(**{k: t_known(v) for k, v in m.groupdict().items()})
    return text


def t_parts(text: str | None) -> str:
    """A stored " · "-joined line (notification subtitle), each part through t_known."""
    return " · ".join(t_known(p) for p in text.split(" · ")) if text else ""


def initials(full_name: str) -> str:
    parts = full_name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else full_name[:2].upper()


def dmy(d) -> str:
    """D-27: dd/mm/yyyy, from a date or a "YYYY-MM-DD…" text."""
    if not d:
        return ""
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")


def show_time(text: str | None) -> str:
    """D-27: dd/mm/yyyy · HH:mm, from a "YYYY-MM-DD HH:MM" text."""
    return datetime.strptime(text, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y · %H:%M") if text else ""


def install(templates) -> None:
    """Give a Jinja2Templates instance the label lookup, the shared formats and the shell helpers."""
    env = templates.env
    env.globals.update(_=t, TABS=TABS, initials=initials, unread=unread)
    env.filters.update(t=t, t_list=t_list, t_known=t_known, t_parts=t_parts, dmy=dmy, show_date=dmy, show_time=show_time)
