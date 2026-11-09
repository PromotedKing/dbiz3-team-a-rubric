"""T003 — TML FR-003 – FR-006, FR-012, BR-003, BR-008 (week data of S-048)."""
from datetime import date

from mb360.tml import weeks

TODAY = date(2026, 9, 27)


def test_current_week_and_range(db, user_id):
    w = weeks.load_week(db, user_id("tci-000123"), None, TODAY)
    assert (w["week"], w["current"], w["start"], w["end"]) == (28, 28, date(2026, 9, 27), date(2026, 10, 3))
    assert (w["prev"], w["next"]) == (27, 29)


def test_week_26_visit_and_indicators(db, user_id):
    w = weeks.load_week(db, user_id("tci-000123"), 26, TODAY)
    assert (w["start"], w["end"]) == (date(2026, 9, 13), date(2026, 9, 19))
    assert [v["visit_date"] for v in w["visits"]] == ["2026-09-15"]
    v = w["visits"][0]
    assert v["ultrasound_image"] is None and v["fetal_length"] is None
    assert [d["day"] for d in w["days"]] == ["2026-09-15"]
    rows = w["days"][0]["rows"]
    assert {(r["metric"], r["value"], r["source"]) for r in rows} == {
        ("Blood pressure", "132/84 mmHg", "From visit"), ("Fetal heart rate", "145 bpm", "From visit"),
        ("Urine protein", "Negative", "From visit"), ("Weight", "56.5 kg", "From visit")}
    assert all("label" not in r for r in rows)                                 # BR-008: no threshold check added


def test_week_22_ultrasound_card(db, user_id):
    v = weeks.load_week(db, user_id("tci-000123"), 22, TODAY)["visits"][0]
    assert (v["ultrasound_image"], v["fetal_length"], v["estimated_fetal_weight"], v["ultrasound_report_date"]) == \
        ("us/VIS-002.jpg", 27, 480, "2026-08-18")


def test_week_28_diary_messages_no_visit(db, user_id):
    w = weeks.load_week(db, user_id("tci-000123"), 28, TODAY)
    assert w["visits"] == []                                                   # "No visit this week." (BR-003)
    assert [d["day"] for d in w["days"]] == ["2026-09-27"]
    assert ("Weight", "57.0 kg", "Self-entered") in {(r["metric"], r["value"], r["source"]) for r in w["days"][0]["rows"]}
    assert sorted(e["mood"] for e in w["diary"]) == ["Calm", "Happy"] and all(e["photo"] for e in w["diary"])
    assert [m["author"] for m in w["messages"]] == ["Mother", "Father"]


def test_week_27_lists_reported_values(db, user_id):
    w = weeks.load_week(db, user_id("tci-000123"), 27, TODAY)
    assert [d["day"] for d in w["days"]] == ["2026-09-26", "2026-09-25"]       # newest day first (Q17)
    assert {(r["value"], r["source"]) for d in w["days"] for r in d["rows"]} == {("150/95 mmHg", "Doctor-assigned"), ("128/82 mmHg", "Doctor-assigned")}


def test_prefetch_and_limits(db, user_id):
    lan = user_id("tci-000123")
    weeks.clear(lan)
    weeks.load_week(db, lan, 28, TODAY)
    assert {(lan, 27), (lan, 28), (lan, 29)} <= set(weeks.CACHE)               # FR-004
    assert weeks.load_week(db, lan, 0, TODAY)["prev"] is None
    assert weeks.load_week(db, lan, 42, TODAY)["next"] is None


def test_day_of_week_progress_and_trimester():
    edd = date(2026, 12, 20)
    assert weeks.day_of_week(edd, date(2026, 9, 27)) == 0 and weeks.day_of_week(edd, date(2026, 9, 30)) == 3
    assert weeks.progress(edd, date(2026, 9, 27)) == 70 and weeks.progress(edd, date(2027, 2, 1)) == 100
    assert weeks.progress(edd, date(2026, 1, 1)) == 0
    assert [weeks.trimester(w) for w in (0, 13, 14, 27, 28, 42)] == ["First trimester", "First trimester", "Second trimester",
                                                                     "Second trimester", "Third trimester", "Third trimester"]


def test_week_days_marks_today_future_and_content():
    w = {"start": date(2026, 9, 27), "days": [{"day": "2026-09-27", "rows": [{}, {}]}], "visits": [{"visit_date": "2026-09-28"}],
         "diary": [{"entry_date": "2026-09-27", "text": "Hello", "mood": "Calm"}]}
    days = weeks.week_days(w, date(2026, 9, 28))
    assert [d["short"] for d in days] == ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    assert (days[0]["has_diary"], days[0]["mood"], days[0]["diary_texts"], days[0]["row_count"]) == (True, "Calm", ["Hello"], 2)
    assert days[1]["is_today"] and days[1]["has_visit"] and not days[1]["future"]
    assert days[2]["future"] and not days[0]["future"]
