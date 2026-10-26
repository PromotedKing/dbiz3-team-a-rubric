"""Shared helpers for the ACC tests (feature specs/005-acc-onboarding)."""
from datetime import datetime

NOW = datetime(2026, 9, 27, 10, 0)


def new_identity(**kw):
    """An invented TCI identity that is not in the seed."""
    base = {"tci_account_ref": "tci-test-001", "full_name": "Trịnh Thị Test", "date_of_birth": "1997-05-20",
            "sex": "Female", "phone": "0900000199", "record_code": "TC-09999"}
    base.update(kw)
    return base


def seed_identity(db, tci_ref):
    u = db.execute("SELECT * FROM USER_ACCOUNT WHERE tci_account_ref = ?", (tci_ref,)).fetchone()
    return {k: u[k] for k in ("tci_account_ref", "full_name", "date_of_birth", "sex", "phone", "record_code")}


def count(db, table, where="1 = 1", args=()):
    return db.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", args).fetchone()[0]
