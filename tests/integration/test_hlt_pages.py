"""T005 — HLT US-1 #1 - #4, US-2 #1 - #3, BR-001 (S-023, S-024 pages)."""
import re

from mb360.acc import entry, setup
from tests.acc_helpers import NOW, new_identity


def text(html):
    return re.sub(r"<[^>]+>", " ", html)


def test_health_metrics_page(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/health").text
    for t in ("Health metrics", "Latest visit results", "From visit", "Visit date 15/09/2026 · not editable",
              "132/84 mmHg", "Normal", "145 bpm", "(reference range 110–160 bpm)", "56.5 kg", "Negative",
              "2 metrics: Blood glucose, Blood pressure", "2 reports being handled", "Self-entered",
              "57.0 kg", "36.8 °C", "82 bpm", "7 h 30 min", "27/09/2026 · 07:30", "+ Enter self-tracked metrics"):
        assert t in page, t
    assert f'href="/m/{lan}/instructions"' in page and f'href="/m/{lan}/my-reports"' in page
    assert "<input" not in page                                     # visit values are read-only (BR-001)
    assert "alert" not in text(page).lower()


def test_refresh_confirmation(client, user_id):
    assert "Data updated." in client.get(f"/m/{user_id('tci-000123')}/health", params={"refreshed": 1}).text


def test_no_visit_empty_state(client, db):
    uid = entry.agree(db, new_identity(), True, NOW)
    setup.save(db, uid, {"date_type": "EDD", "date": "2026-12-20"}, NOW)
    assert "No visit results yet." in client.get(f"/m/{uid}/health").text


def test_self_tracked_form(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/self-tracked").text
    for t in ("Enter self-tracked metrics", "Weight", "Temperature", "Heart rate", "Sleep", "Measured at", "Bedtime", "Wake-up time", "Save metrics"):
        assert t in page, t
    for absent in ('name="blood_pressure"', 'name="systolic"', 'name="glucose"', 'name="urine', 'name="fetal', 'name="height'):
        assert absent not in page
    assert "alert" not in text(page).lower()


def test_save_and_errors(client, user_id):
    lan = user_id("tci-000123")
    r = client.post(f"/m/{lan}/self-tracked", data={"weight": "57.4", "weight_at": "2026-09-27T09:00"})
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/health?saved=1"
    page = client.get(r.headers["location"]).text
    assert "Metrics saved" in page and "57.4 kg" in page
    bad = client.post(f"/m/{lan}/self-tracked", data={"weight": "abc", "weight_at": "2026-09-27T09:00"})
    assert bad.status_code == 422 and 'data-error-for="weight"' in bad.text


def test_home_links_to_health(client, user_id):
    lan = user_id("tci-000123")
    assert f'href="/m/{lan}/health"' in client.get(f"/m/{lan}/home").text
