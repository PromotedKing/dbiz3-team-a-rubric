"""Shared helpers for the US-1 integration tests."""
from markupsafe import escape

from mb360.ui import t


def vi(label: str, **fields) -> str:
    """On-screen text of an English label, HTML-escaped as in the page (docs/ui-label-reference.md, D-79)."""
    return str(escape(t(label, **fields)))


WRITTEN =["HEALTH_METRIC_RECORD", "METRIC_REPORT", "REPORT_SYMPTOM", "CARE_CASE", "CASE_STATUS_HISTORY"]


def counts(db):
    return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in WRITTEN}


def bp_form(systolic, diastolic, symptoms, other=""):
    return {"metric": "Blood pressure", "systolic": str(systolic), "diastolic": str(diastolic),
            "measured_at": "2026-09-27T09:00", "symptoms": symptoms, "other_symptom_text": other, "note": ""}


def latest_report(db, uid):
    return db.execute("SELECT * FROM METRIC_REPORT WHERE user_id = ? ORDER BY submitted_at DESC, rowid DESC LIMIT 1",
                      (uid,)).fetchone()


def case_of(db, report_id):
    return db.execute("SELECT * FROM CARE_CASE WHERE metric_report_id = ?", (report_id,)).fetchone()
