"""BOT FR-012, BR-006 (D-89, proposed): answer a question about the mother's own data from what the sub-app shows her.

The answer is built here, never by the LLM, and is never sent to it (BR-001): chat._earlier passes on general turns only.
It repeats values as the screens show them, adds only simple arithmetic (days until / since, the change from the previous
value, counts) and never says whether a value is normal, high or low. The text is Vietnamese, from the labels in
docs/ui-label-reference.md, one line per fact; the bubble on S-034 links to the screen that shows the data."""
import sqlite3
from datetime import date, datetime
from urllib.parse import quote

from .. import tci_feed, ui
from ..acc import notices
from ..alr.reports import gestational_week

CONTEXT_LABELS = {"fasting": "Fasting", "post_1h": "1 h after meal", "post_2h": "2 h after meal"}   # as on S-025
VISIT_METRICS = ("Blood pressure", "Fetal heart rate", "Weight", "Blood glucose", "Urine protein")   # S-023 order


def _value(r: sqlite3.Row) -> str:
    text = f"{r['value']} {r['unit']}".strip() if r["unit"] else str(r["value"])
    return f"{text} ({ui.t(CONTEXT_LABELS[r['glucose_context']])})" if r["glucose_context"] in CONTEXT_LABELS else text


def _number(text: str) -> float | None:
    try:
        return float(str(text).replace(",", "."))
    except ValueError:
        return None


def _signed(x: float) -> str:
    x = round(x, 1)
    text = f"{abs(x):g}".replace(".", ",")
    return "0" if x == 0 else ("+" if x > 0 else "−") + text


def _change(metric: str, new: sqlite3.Row, old: sqlite3.Row) -> str | None:
    """The difference only, never a judgement (BR-006); None when the values cannot be compared (e.g. urine protein 1+)."""
    if metric == "Blood pressure":
        try:
            (s1, d1), (s0, d0) = (map(int, r["value"].split("/")) for r in (new, old))
        except ValueError:
            return None
        return ui.t("systolic {s}, diastolic {d} mmHg", s=_signed(s1 - s0), d=_signed(d1 - d0))
    a, b = _number(new["value"]), _number(old["value"])
    if a is None or b is None or new["unit"] != old["unit"]:
        return None
    return f"{_signed(a - b)} {new['unit'] or ''}".strip()


def _days(n: int) -> str:
    return ui.t("today") if n == 0 else ui.t("{days} days ago", days=n)


def appointment(conn, user_id, now, _):
    nxt = tci_feed.next_appointment(conn, user_id, now)
    if nxt is None:
        return [ui.t("You have no upcoming appointment in the TCI app.")]
    lines = [ui.t("Your next appointment: {day}, {at}, {place}.", day=ui.t(nxt["long_day"]), at=nxt["at"], place=nxt["place"])]
    days = nxt["days"]
    lines.append(ui.t("That is today.") if days == 0 else ui.t("That is tomorrow.") if days == 1 else ui.t("That is in {days} days.", days=days))
    return lines


def last_visit(conn, user_id, now, _):
    v = conn.execute("SELECT * FROM VISIT WHERE user_id = ? ORDER BY visit_date DESC LIMIT 1", (user_id,)).fetchone()
    if v is None:
        return [ui.t("There is no visit in the app yet.")]
    lines = [ui.t("Your latest visit: {date} ({ago}).", date=ui.dmy(v["visit_date"]), ago=_days((now.date() - date.fromisoformat(v["visit_date"])).days))]
    recs = {r["metric"]: r for r in conn.execute(
        "SELECT * FROM HEALTH_METRIC_RECORD WHERE visit_id = ? AND source = 'From visit'", (v["visit_id"],))}
    items = [f"{ui.t(m)} {_value(recs[m])}" for m in VISIT_METRICS if m in recs]
    if items:
        lines.append(ui.t("Recorded at that visit: {items}.", items="; ".join(items)))
    return lines


def metric(conn, user_id, now, found):
    m = found["metric"]
    rows = conn.execute("""SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ?
                           ORDER BY measured_at DESC, created_at DESC""", (user_id, m)).fetchall()
    name = ui.t(m)
    if not rows:
        return [ui.t("There is no {metric} value in the app yet.", metric=name.lower())]
    new = rows[0]
    lines = [ui.t("Latest {metric}: {value}, {date} ({source}).", metric=name.lower(), value=_value(new), date=ui.show_time(new["measured_at"]),
                  source=ui.t(new["source"]))]
    old = next((r for r in rows[1:] if m != "Blood glucose" or r["glucose_context"] == new["glucose_context"]), None)
    if old is None:
        lines.append(ui.t("This is the only {metric} value in the app.", metric=name.lower()))
        return lines
    lines.append(ui.t("The one before: {value}, {date}.", value=_value(old), date=ui.show_time(old["measured_at"])))
    change = _change(m, new, old)
    if change:
        lines.append(ui.t("Change: {change}.", change=change))
    return lines


def week(conn, user_id, now, _):
    p = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    if p is None:
        return [ui.t("Your pregnancy profile is not set up yet.")]
    edd = date.fromisoformat(p["edd"])
    left = (edd - now.date()).days
    lines = [ui.t("You are in week {week} of your pregnancy.", week=gestational_week(edd, now.date()))]
    lines.append(ui.t("Due date: {edd}, in {days} days.", edd=ui.dmy(edd), days=left) if left > 0 else ui.t("Due date: {date}", date=ui.dmy(edd)))
    return lines


def notices_(conn, user_id, now, _):
    unread = notices.list_for(conn, user_id, notices.UNREAD)
    if not unread:
        return [ui.t("You have no unread notices.")]
    n = unread[0]
    return [ui.t("You have {n} unread notices.", n=len(unread)),
            ui.t("Latest: {title}, {at}.", title=ui.t_known(n["title"]), at=ui.show_time(n["created_at"]))]


def reports(conn, user_id, now, _):
    rows = conn.execute("SELECT status FROM CARE_CASE WHERE user_id = ? AND status <> 'Resolved' ORDER BY created_at DESC", (user_id,)).fetchall()
    if not rows:
        return [ui.t("None of your reports is being handled now.")]
    return [ui.t("Reports being handled: {n}. The latest is {status}.", n=len(rows), status=ui.t(rows[0]["status"]).lower())]


def instructions(conn, user_id, now, _):
    rows = conn.execute("SELECT metric FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,)).fetchall()
    if not rows:
        return [ui.t("Your doctor has no tracking instruction for you now.")]
    return [ui.t("Your doctor asked you to track: {metrics}.", metrics=", ".join(ui.t(r["metric"]).lower() for r in rows))]


ANSWERS = {"appointment": appointment, "last_visit": last_visit, "metric": metric, "week": week, "notices": notices_,
           "reports": reports, "instructions": instructions}
SCREENS = {"appointment": "appointments", "last_visit": "health", "week": "journey", "notices": "notices", "reports": "my-reports",
           "instructions": "instructions"}


def answer(conn: sqlite3.Connection, user_id: str, found: dict, now: datetime) -> str:
    """The lookup answer, one fact per line (FR-012); only the signed-in mother's own rows are read (BR-006)."""
    return "\n".join(ANSWERS[found["topic"]](conn, user_id, now, found))


def link(user_id: str, found: dict | None) -> str | None:
    """The screen that shows the data (S-034 bubble button)."""
    if not found or found.get("topic") not in ANSWERS:
        return None
    if found["topic"] == "metric":
        return f"/m/{user_id}/history?metric={quote(found['metric'])}"
    return f"/m/{user_id}/{SCREENS[found['topic']]}"
