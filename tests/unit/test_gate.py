"""D-82: the password on the pages a stranger must not reach, and the clock of the hosted app."""
import base64
from datetime import datetime, timedelta, timezone

import pytest

from mb360 import clock, gate


def basic(password: str) -> str:
    return "Basic " + base64.b64encode(f"nhom:{password}".encode()).decode()


@pytest.mark.parametrize("path", ["/staff", "/staff/abc/cases", "/showcase/reset", "/tci/accounts"])
def test_protected_pages(path):
    assert gate.is_protected(path)


@pytest.mark.parametrize("path", ["/", "/tci", "/tci/open", "/m/abc/home", "/static/app.js", "/staffing"])
def test_the_mothers_pages_stay_open(path):
    assert not gate.is_protected(path)


def test_right_password_only():
    assert gate.allowed(basic("mật-khẩu"), "mật-khẩu", hosted=True)
    assert not gate.allowed(basic("sai"), "mật-khẩu", hosted=True)
    assert not gate.allowed(None, "mật-khẩu", hosted=False)
    assert not gate.allowed("Bearer abc", "mật-khẩu", hosted=True)
    assert not gate.allowed("Basic không-phải-base64", "mật-khẩu", hosted=True)


def test_without_a_password_open_on_a_team_machine_closed_when_hosted():
    assert gate.allowed(None, None, hosted=False)
    assert not gate.allowed(None, None, hosted=True)
    assert not gate.allowed(basic(""), "", hosted=True)


def test_live_clock_is_vietnam_time():
    clock.reset()
    clock.use_live()
    try:
        expected = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=7)
        assert abs(clock.now() - expected) < timedelta(minutes=2)
    finally:
        clock.reset()
