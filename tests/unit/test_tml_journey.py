"""T001 — TML FR-013, BR-007 (S-105 data, specs/011-tml-journey)."""
from mb360.tml import journey
from tests.acc_helpers import NOW


def test_stages_are_those_of_d75():
    assert [(s["name"], s["first"], s["last"]) for s in journey.STAGES] == [
        ("First trimester", 0, 13), ("Second trimester", 14, 27), ("Third trimester", 28, 42), ("Full journey", 0, 42)]


def test_default_stage_is_the_current_one(db, user_id):
    assert journey.load(db, user_id("tci-000123"), None, NOW)["stage"] == "Third trimester"      # Lan: week 28
    j = journey.load(db, user_id("tci-000123"), "not-a-stage", NOW)
    assert j["stage"] == "Third trimester" and j["current"] == 28


def test_weeks_with_content_only_oldest_first(db, user_id):
    j = journey.load(db, user_id("tci-000123"), "Full journey", NOW)
    numbers = [w["week"] for w in j["weeks"]]
    assert numbers == sorted(numbers) and 22 in numbers and 28 in numbers
    assert all(w["visits"] or w["diary"] or w["messages"] for w in j["weeks"])
    assert max(numbers) <= j["current"]                                      # nothing after the current week


def test_stage_limits_the_weeks(db, user_id):
    j = journey.load(db, user_id("tci-000123"), "Second trimester", NOW)
    assert j["weeks"] and all(14 <= w["week"] <= 27 for w in j["weeks"])


def test_counts(db, user_id):
    lan = user_id("tci-000123")
    j = journey.load(db, lan, "Full journey", NOW)
    assert j["counts"]["visits"] == db.execute("SELECT COUNT(*) FROM VISIT WHERE user_id = ?", (lan,)).fetchone()[0]
    assert j["counts"]["diary"] == db.execute("SELECT COUNT(*) FROM DIARY_ENTRY WHERE user_id = ?", (lan,)).fetchone()[0]
    assert j["counts"]["photos"] == sum(len(e["photos"]) for w in j["weeks"] for e in w["diary"])


def test_stage_after_the_current_week_is_not_reached(db, user_id):
    j = journey.load(db, user_id("tci-000133"), "Third trimester", NOW)      # week 24
    assert j["not_reached"] and j["weeks"] == [] and not j["can_export"]


def test_empty_stage_cannot_be_exported(db, user_id):
    lan = user_id("tci-000123")
    j = journey.load(db, lan, "First trimester", NOW)
    assert j["can_export"] == bool(j["weeks"])


def test_only_her_own_content_and_nothing_written(db, user_id):              # BR-007
    lan, other = user_id("tci-000123"), user_id("tci-000133")
    before = db.total_changes
    mine = journey.load(db, lan, "Full journey", NOW)
    theirs = journey.load(db, other, "Full journey", NOW)
    assert db.total_changes == before
    mine_text = {e["text"] for w in mine["weeks"] for e in w["diary"]}
    their_text = {e["text"] for w in theirs["weeks"] for e in w["diary"]}
    assert "The baby kicked a lot today." in mine_text and "The baby kicked a lot today." not in their_text


def test_all_photos_of_an_entry(db, user_id):
    lan = user_id("tci-000123")
    d = db.execute("SELECT diary_id FROM DIARY_ENTRY WHERE user_id = ? AND gestational_week = 28 ORDER BY entry_date LIMIT 1", (lan,)).fetchone()[0]
    db.execute("DELETE FROM DIARY_IMAGE WHERE diary_id = ?", (d,))
    for i, name in ((2, "diary/b.png"), (1, "diary/a.png")):
        db.execute("INSERT INTO DIARY_IMAGE (image_id, diary_id, file, sort_order) VALUES (?, ?, ?, ?)", (name.ljust(36, "0"), d, name, i))
    j = journey.load(db, lan, "Third trimester", NOW)
    entry = next(e for w in j["weeks"] for e in w["diary"] if e["diary_id"] == d)
    assert entry["photos"] == ["diary/a.png", "diary/b.png"]


def test_stage_rows_say_past_current_or_to_come(db, user_id):
    rows = {r["name"]: r for r in journey.load(db, user_id("tci-000133"), None, NOW)["stage_rows"]}     # week 24
    assert rows["First trimester"]["state"] == "Past"
    assert rows["Second trimester"]["state"] == "Current"
    assert rows["Third trimester"]["state"] == "To come"
    assert "Full journey" not in rows
