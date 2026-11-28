"""BOT FR-012, BR-006 (D-89, proposed): answer a question about the mother's own data from what the sub-app shows her.

The answer is built here, never by the LLM, and is never sent to it (BR-001): chat._earlier passes on general turns only.
It repeats values as the screens show them, adds only simple arithmetic (days until / since, the change from the previous
value, counts) and never says whether a value is normal, high or low. The text is Vietnamese, from the labels in
docs/ui-label-reference.md, one line per fact; the bubble on S-034 links to the screen that shows the data."""
import sqlite3
from datetime import date, datetime, timedelta
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


def _latest_fetal_visit(conn, user_id):
    return conn.execute("""SELECT * FROM VISIT WHERE user_id = ? AND (estimated_fetal_weight IS NOT NULL OR fetal_length IS NOT NULL)
                           ORDER BY visit_date DESC LIMIT 1""", (user_id,)).fetchone()


def fetal(conn, user_id, now, found):
    """D-93: the baby's measures from the latest visit that has them, as on the visit day screen — not the mother's weight."""
    v = _latest_fetal_visit(conn, user_id)
    if v is None:
        return [ui.t("There is no fetal measurement in the app yet.")]
    found["path"] = f"timeline/day/{v['visit_date']}"
    return [ui.t("Latest fetal measurements ({date}): {items}.", date=ui.dmy(v["visit_date"]), items=", ".join(_measures(v)))]


# D-93 (proposed): requests to act for her get a pointer to the screen where she can do it, instead of the LLM.
DO = "The chatbot cannot do this for you. You can do it yourself in the app."


def _pointer(text):
    return lambda conn, user_id, now, found: [ui.t(text)]


def _quote(text: str, n: int = 140) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def _measures(v) -> list[str]:
    return ([ui.t("estimated weight {w} g", w=v["estimated_fetal_weight"])] if v["estimated_fetal_weight"] is not None else []) + \
           ([ui.t("length {l} cm", l=v["fetal_length"])] if v["fetal_length"] is not None else [])


# D-94 (proposed): answers read from the data the mother already sees in the sub-app, as the screens show it. What the
# sub-app does not show her (blood type, history, allergies, the doctor's conclusion) is still not read (BR-006).
def record(conn, user_id, now, found):
    """S-103: record number, hospital record link, due date, height. Asked only for blood type, history or allergies:
    just say they are not in the app."""
    from ..acc import profile
    if found.get("clinical"):
        return [ui.t("Blood type, history and allergies are not shown in the app: please ask your doctor at your next visit.")]
    user = conn.execute("SELECT record_code FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
    p, link_row = profile.load(conn, user_id, now), profile.latest_link(conn, user_id)
    lines = [ui.t("Medical record number: {code}.", code=user["record_code"] or "—")]
    if link_row is not None:
        lines.append(ui.t("Hospital record link: {status}.", status=ui.t(link_row["status"]).lower()))
    if p["edd"]:
        lines.append(ui.t("Due date: {date}", date=ui.dmy(p["edd"])) + ".")
    if p["height_cm"]:
        lines.append(ui.t("Height: {h} cm.", h=p["height_cm"]))
    lines.append(ui.t("Blood type, history and allergies are not shown in the app: please ask your doctor at your next visit."))
    return lines


def visit_notes(conn, user_id, now, found):
    """The latest visit as its day screen shows it: the doctor's note and the baby's measures (not the conclusion)."""
    v = conn.execute("SELECT * FROM VISIT WHERE user_id = ? ORDER BY visit_date DESC LIMIT 1", (user_id,)).fetchone()
    if v is None:
        return [ui.t("There is no visit in the app yet.")]
    found["path"] = f"timeline/day/{v['visit_date']}"
    lines = [ui.t("Your latest visit: {date} ({ago}).", date=ui.dmy(v["visit_date"]),
                  ago=_days((now.date() - date.fromisoformat(v["visit_date"])).days))]
    lines.append(ui.t("Doctor's note: “{note}”", note=_quote(v["doctor_note"])) if v["doctor_note"]
                 else ui.t("The doctor left no note at this visit."))
    if _measures(v):
        lines.append(ui.t("Ultrasound: {items}.", items=", ".join(_measures(v))))
    elif (u := _latest_fetal_visit(conn, user_id)) is not None:       # the latest ultrasound was at an earlier visit
        lines.append(ui.t("Latest fetal measurements ({date}): {items}.", date=ui.dmy(u["visit_date"]), items=", ".join(_measures(u))))
    return lines


PERIODS = {"week": 7, "all": 3650}       # anything else: the 30 days S-025 shows by default (HLT §10 Q12)


def trend(conn, user_id, now, found):
    """S-025 for the period asked: number of readings, average / lowest / highest as the screen computes them, and for
    weight the change from the first to the latest reading. Arithmetic only (BR-006)."""
    from ..hlt import history
    m = found["metric"]
    days = PERIODS.get(found.get("when"), history.DEFAULT_DAYS)
    data = history.load(conn, user_id, m, now.date() - timedelta(days=days), None, None, now)
    rows = data["rows"]
    span = ui.t("the whole pregnancy") if found.get("when") == "all" else ui.t("the last {n} days", n=days)
    if not rows:
        return [ui.t("No {metric} value in {span}.", metric=ui.t(m).lower(), span=span)]
    lines = [ui.t("{metric} in {span}: {n} readings, the latest {value} ({date}).", metric=ui.t(m), span=span, n=len(rows),
                  value=rows[0]["value"], date=ui.show_time(rows[0]["at"]))]
    if data["stats"]:
        unit = rows[0]["value"].split(" ", 1)[1] if " " in rows[0]["value"] else ""
        lines.append(ui.t("Average {avg}, lowest {low}, highest {high} {unit}.", avg=data["stats"]["average"],
                          low=data["stats"]["lowest"], high=data["stats"]["highest"], unit=unit).replace(" .", "."))
    if m == "Weight" and len(rows) > 1:
        first, last = _number(rows[-1]["value"].split()[0]), _number(rows[0]["value"].split()[0])
        if first is not None and last is not None:
            lines.append(ui.t("Change from the first to the latest reading: {change}.", change=f"{_signed(last - first)} kg"))
    return lines


def diary(conn, user_id, now, found):
    """Timeline / day screen: her own entries, quoted (TML)."""
    rows = conn.execute("SELECT * FROM DIARY_ENTRY WHERE user_id = ? ORDER BY entry_date DESC, rowid DESC", (user_id,)).fetchall()
    if not rows:
        return [ui.t("You have no diary entry yet.")]
    if found.get("count"):
        return [ui.t("You have written {n} diary entries; the latest on {date}.", n=len(rows), date=ui.dmy(rows[0]["entry_date"]))]
    when = found.get("when")
    if when in ("yesterday", "today"):
        day = (now.date() - timedelta(days=1 if when == "yesterday" else 0)).isoformat()
        picked = [r for r in rows if r["entry_date"] == day]
        found["path"] = f"timeline/day/{day}"
        if not picked:
            return [ui.t("No diary entry on {date}.", date=ui.dmy(day))]
    elif when == "week":
        since = (now.date() - timedelta(days=7)).isoformat()
        picked = [r for r in rows if r["entry_date"] >= since][:3]
        if not picked:
            return [ui.t("No diary entry in the last 7 days.")]
    else:
        picked = rows[:1]
        found["path"] = f"timeline/day/{rows[0]['entry_date']}"
    return [ui.t("{date} ({mood}): “{entry}”", date=ui.dmy(r["entry_date"]),
                 mood=ui.t_known(r["mood"]).lower() if r["mood"] else "—", entry=_quote(r["text"], 120)) for r in picked]


def family(conn, user_id, now, _):
    """S-105: the latest messages to the baby (TML FR-011 shows them; writing is pending D-03)."""
    rows = conn.execute("SELECT * FROM FAMILY_MESSAGE WHERE user_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 2",
                        (user_id,)).fetchall()
    if not rows:
        return [ui.t("There is no message to the baby yet.")]
    return [ui.t("Message from {author} (week {week}): “{message}”", author=ui.t_known(r["author"]).lower(), week=r["week"],
                 message=_quote(r["text"], 120)) for r in rows]


def staff_reply(conn, user_id, now, _):
    """Màn 10: the latest reply from clinical staff, split as the screen splits it (comment, to-dos, follow-up visit)."""
    r = conn.execute("""SELECT k.case_id FROM STAFF_RESPONSE s JOIN CARE_CASE k ON k.case_id = s.case_id
                        WHERE k.user_id = ? ORDER BY s.sent_at DESC, s.rowid DESC LIMIT 1""", (user_id,)).fetchone()
    resp = notices.latest_response(conn, r["case_id"]) if r else None
    if resp is None:
        return [ui.t("No nurse or doctor has replied to you yet.")]
    parts = notices.parse_response(notices._response_text(resp))
    lines = [ui.t("Latest reply from {role} {name} ({date}):", role=ui.t(resp["responder_role"]).lower(), name=ui.display_name(resp["full_name"]),
                  date=ui.show_time(resp["sent_at"]))]
    if parts["comment"]:
        lines.append("“" + _quote(parts["comment"], 200) + "”")
    if parts["todo"]:
        lines.append(ui.t("To do: {items}.", items="; ".join(parts["todo"])))
    if parts["follow_up"]:
        lines.append(ui.t("Follow-up visit: {when}.", when=parts["follow_up"]))
    return lines


def report_count(conn, user_id, now, _):
    """S-029: how many reports she sent and how many of their cases are still being handled."""
    sent = conn.execute("SELECT COUNT(*) FROM METRIC_REPORT WHERE user_id = ?", (user_id,)).fetchone()[0]
    open_ = conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id = ? AND case_source <> 'Chatbot' AND status <> 'Resolved'",
                         (user_id,)).fetchone()[0]
    return [ui.t("You have sent {n} reports; {k} are being handled now.", n=sent, k=open_)]


def readings(conn, user_id, now, found):
    """D-95: "Còn lần trước nữa?" after a metric → her three latest readings of it, as S-025 lists them."""
    m = found["metric"]
    rows = conn.execute("""SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ?
                           ORDER BY measured_at DESC, created_at DESC LIMIT 3""", (user_id, m)).fetchall()
    if not rows:
        return [ui.t("There is no {metric} value in the app yet.", metric=ui.t(m).lower())]
    return [ui.t("Your latest {metric} readings: {items}.", metric=ui.t(m).lower(),
                 items="; ".join(f"{_value(r)} ({ui.show_time(r['measured_at'])})" for r in rows))]


ANSWERS = {"appointment": appointment, "last_visit": last_visit, "metric": metric, "week": week, "notices": notices_,
           "reports": reports, "instructions": instructions, "fetal": fetal, "see_visit_notes": visit_notes,
           "act_booking": _pointer("Booking, changing or cancelling an appointment is done in the TCI app. Your appointments are here."),
           "act_report": _pointer(DO), "act_diary": _pointer(DO), "act_reminders": _pointer(DO),
           "see_record": record, "trend": trend, "see_diary": diary, "see_family": family, "see_staff_reply": staff_reply,
           "see_report_count": report_count, "readings": readings}
SCREENS = {"appointment": "appointments", "last_visit": "health", "week": "journey", "notices": "notices", "reports": "my-reports",
           "instructions": "instructions", "fetal": "timeline", "see_visit_notes": "health", "act_booking": "appointments",
           "act_report": "report", "act_diary": "diary/new", "act_reminders": "settings/notifications", "see_record": "profile",
           "see_diary": "timeline", "see_family": "journey", "see_staff_reply": "notices", "see_report_count": "my-reports"}


def answer(conn: sqlite3.Connection, user_id: str, found: dict, now: datetime) -> str:
    """The lookup answer, one fact per line (FR-012); only the signed-in mother's own rows are read (BR-006)."""
    return "\n".join(ANSWERS[found["topic"]](conn, user_id, now, found))


def link(user_id: str, found: dict | None) -> str | None:
    """The screen that shows the data (S-034 bubble button)."""
    if not found or found.get("topic") not in ANSWERS:
        return None
    if found["topic"] in ("metric", "trend", "readings"):
        return f"/m/{user_id}/history?metric={quote(found['metric'])}"
    return f"/m/{user_id}/{found.get('path') or SCREENS[found['topic']]}"
