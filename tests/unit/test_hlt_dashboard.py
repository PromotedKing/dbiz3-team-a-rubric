"""T003 — HLT FR-001, FR-005, FR-008, BR-004, BR-005 (S-023 data)."""
from mb360.hlt import dashboard
from tests.acc_helpers import NOW


def test_latest_visit_rows(db, user_id):
    d = dashboard.load(db, user_id("tci-000123"), NOW)
    assert d["visit_date"] == "2026-09-15"
    rows = {r["metric"]: r for r in d["visit_rows"]}
    assert [r["metric"] for r in d["visit_rows"]] == ["Blood pressure", "Fetal heart rate", "Weight", "Blood glucose", "Urine protein"]
    assert (rows["Blood pressure"]["value"], rows["Blood pressure"]["label"], rows["Blood pressure"]["source"]) == ("132/84 mmHg", "Normal", "From visit")
    assert (rows["Urine protein"]["value"], rows["Urine protein"]["label"]) == ("Negative", "Normal")
    assert (rows["Fetal heart rate"]["value"], rows["Fetal heart rate"]["label"], rows["Fetal heart rate"]["reference"]) == ("145 bpm", None, "110–160 bpm")
    assert (rows["Weight"]["value"], rows["Weight"]["label"]) == ("56.5 kg", None)
    assert rows["Blood glucose"]["value"] is None


def test_cards(db, user_id):
    d = dashboard.load(db, user_id("tci-000123"), NOW)
    assert d["instructions"] == ["Blood glucose", "Blood pressure"]
    assert d["handling"] == 2 and d["latest_status"] in ("Not viewed", "Viewed", "Escalated to doctor")


def test_self_tracked_latest_values(db, user_id):
    rows = {r["metric"]: r for r in dashboard.load(db, user_id("tci-000123"), NOW)["self_tracked"]}
    assert (rows["Weight"]["value"], rows["Weight"]["at"]) == ("57.0 kg", "2026-09-27 07:30")
    assert rows["Temperature"]["value"] == "36.8 °C" and rows["Heart rate"]["value"] == "82 bpm"
    assert rows["Sleep"]["value"] == "7 h 30 min"
    assert all(r.get("label") is None for r in rows.values())                  # group 1: no threshold label (BR-003)


def test_no_visit(db, user_id):
    d = dashboard.load(db, user_id("tci-000129"), NOW)                         # Hoàng Thu Trang: no visit
    assert d["visit_date"] is None and d["visit_rows"] == []


def test_reference_range_comes_from_threshold_rule(db, user_id):
    db.execute("UPDATE THRESHOLD_RULE SET threshold_values = '100–170' WHERE purpose = 'Display only'")
    rows = {r["metric"]: r for r in dashboard.load(db, user_id("tci-000123"), NOW)["visit_rows"]}
    assert rows["Fetal heart rate"]["reference"] == "100–170 bpm"
