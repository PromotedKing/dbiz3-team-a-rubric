"""ACC onboarding routes — specs/005-acc-onboarding/contracts/http-routes.md (S-001, S-104, S-007 / S-046, S-008)."""
import sqlite3
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock, ui
from ..alr.reports import gestational_week
from ..hlt import dashboard
from ..tml import weeks
from . import entry, notices, profile, setup

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
ui.install(TEMPLATES)
IDENTITY = ("tci_account_ref", "full_name", "date_of_birth", "sex", "phone", "record_code")
GUIDE_PAGES = [   # proposed in screen-spec S-104 #3; text pending (spec-ACC §10 Q20)
    ("Health dashboard", "See the results of your visits and the metrics your doctor asked you to watch."),
    ("Report a metric or symptom", "Tell the care team when a watched metric or a symptom worries you."),
    ("Pregnancy timeline & diary", "Follow your pregnancy week by week and keep your memories."),
    ("Health chatbot", "Ask general questions about pregnancy and baby care."),
]


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    def page(request: Request, name: str, status: int = 200, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx, status_code=status)

    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

    def go(user_id: str, step: str) -> RedirectResponse:
        return RedirectResponse(f"/m/{user_id}/{step}", status_code=303)

    async def identity_of(request: Request) -> dict:
        form = await request.form()
        ident = {k: (form.get(k) or "").strip() for k in IDENTITY}
        ident["tci_account_ref"] = ident["tci_account_ref"] or f"tci-sim-{uuid.uuid4().hex[:8]}"
        return ident

    @app.get("/tci", response_class=HTMLResponse)
    def tci_home(request: Request):
        accounts = conn.execute("SELECT * FROM USER_ACCOUNT ORDER BY full_name").fetchall()
        return page(request, "tci_home.html", accounts=accounts, fields=IDENTITY)

    @app.post("/tci/open", response_class=HTMLResponse)
    async def tci_open(request: Request):
        ident = await identity_of(request)
        outcome, user_id = entry.open_subapp(conn, ident, clock.now())
        if outcome == "not_female":
            return page(request, "not_female.html")
        if outcome == "consent":
            return page(request, "consent.html", ident=ident, error=None)
        return go(user_id, outcome)

    @app.post("/tci/consent", response_class=HTMLResponse)
    async def tci_consent(request: Request):
        form = await request.form()
        ident = await identity_of(request)
        if form.get("action") == "later":           # BR-004: nothing is saved
            return RedirectResponse("/tci", status_code=303)
        try:
            user_id = entry.agree(conn, ident, form.get("agree") == "on", clock.now())
        except entry.EntryError as e:
            return page(request, "consent.html", 422, ident=ident, error=e)
        return go(user_id, "guide")

    @app.get("/m/{user_id}/guide", response_class=HTMLResponse)
    def guide(request: Request, user_id: str, page_no: int = 1, page: int = 0):
        n = min(max(page or page_no, 1), len(GUIDE_PAGES))
        title, text = GUIDE_PAGES[n - 1]
        return TEMPLATES.TemplateResponse(request, "guide.html", {"user": mother(user_id), "n": n, "total": len(GUIDE_PAGES),
                                                                  "title": title, "text": text})

    @app.get("/m/{user_id}/guide/done")
    def guide_done(user_id: str):
        mother(user_id)
        return go(user_id, entry.next_step(conn, user_id))

    def setup_page(request: Request, user, form: dict, errors: dict, status: int = 200):
        card = None
        if form.get("date_type") in ("EDD", "LMP") and form.get("date"):
            try:
                card = setup.calculate(form["date_type"], date.fromisoformat(form["date"]), clock.now().date())
                if "date" in setup.validate({**form, "height_cm": "", "weight_kg": "", "first_visit_date": ""}, clock.now().date()):
                    card = None
            except ValueError:
                card = None
        return page(request, "setup.html", status, user=user, form=form, errors=errors, card=card, today=clock.now().date())

    @app.get("/m/{user_id}/setup", response_class=HTMLResponse)
    def setup_get(request: Request, user_id: str, date_type: str = "EDD", date: str = ""):
        user = mother(user_id)
        if entry.next_step(conn, user_id) == "home":   # BR-006
            return go(user_id, "home")
        return setup_page(request, user, {"date_type": date_type, "date": date}, {})

    @app.post("/m/{user_id}/setup", response_class=HTMLResponse)
    async def setup_post(request: Request, user_id: str):
        user = mother(user_id)
        if entry.next_step(conn, user_id) == "home":
            return go(user_id, "home")
        form = {k: v for k, v in (await request.form()).items()}
        try:
            setup.save(conn, user_id, form, clock.now())
        except setup.SetupError as e:
            return setup_page(request, user, form, e.errors, 422)
        return go(user_id, "home")

    @app.get("/m/{user_id}/home", response_class=HTMLResponse)
    def home(request: Request, user_id: str):
        user = mother(user_id)
        profile = conn.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
        if profile is None:                          # BR-006
            return go(user_id, "setup")
        flags = conn.execute("SELECT metric FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,)).fetchall()
        handling = conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id = ? AND status <> 'Resolved'", (user_id,)).fetchone()[0]
        today, edd = clock.now().date(), date.fromisoformat(profile["edd"])
        week = gestational_week(edd, today)
        return page(request, "home.html", user=user, given_name=user["full_name"].split()[-1],
                    week=week, week_day=weeks.day_of_week(edd, today), edd=profile["edd"], days_left=(edd - today).days,
                    progress=weeks.progress(edd, today), trimester=weeks.trimester(week),
                    flags=[f["metric"] for f in flags], handling=handling, unread_count=ui.unread(user_id),
                    diary_today=conn.execute("SELECT 1 FROM DIARY_ENTRY WHERE user_id = ? AND entry_date = ?",
                                             (user_id, today.isoformat())).fetchone() is not None,
                    d=dashboard.load(conn, user_id, clock.now()))    # self-tracked cards and latest status (S-008 #8, #12 – #15)

    @app.get("/m/{user_id}/notices", response_class=HTMLResponse)
    def notices_page(request: Request, user_id: str, type: str = ""):
        """S-009 behind the "From doctor" tab (D-80): FR-025."""
        active = type if type in notices.TYPES or type == notices.UNREAD else ""
        return page(request, "notices.html", user=mother(user_id), rows=notices.list_for(conn, user_id, active), active=active,
                    types=notices.TYPES, unread_count=notices.unread_count(conn, user_id), unread_filter=notices.UNREAD)

    @app.post("/m/{user_id}/notices/read-all")
    def notices_read_all(user_id: str):
        mother(user_id)
        notices.mark_all_read(conn, user_id, clock.now())
        return RedirectResponse(f"/m/{user_id}/notices", status_code=303)

    @app.get("/m/{user_id}/notices/{notification_id}")
    def notice_open(user_id: str, notification_id: str):
        """FR-026: marks it read and opens its target (S-009 SR-001)."""
        mother(user_id)
        target = notices.open_notice(conn, user_id, notification_id, clock.now())
        if target is None:
            raise HTTPException(404, "Unknown notification")
        return RedirectResponse(target, status_code=303)

    @app.get("/session-expired", response_class=HTMLResponse)
    def session_expired(request: Request):
        """S-043. Sessions are not checked before Session 11 (no sign-in); reachable from the demo start page."""
        return page(request, "expired.html")

    @app.get("/m/{user_id}/profile", response_class=HTMLResponse)
    def profile_page(request: Request, user_id: str, saved: int = 0):
        """S-103: ACC US-3 #1, FR-023."""
        return page(request, "profile.html", user=mother(user_id), p=profile.load(conn, user_id, clock.now()), saved=saved)

    def edit_form(request: Request, user, form: dict, errors: dict, status: int = 200):
        return page(request, "edit_profile.html", status, user=user, p=profile.load(conn, user["user_id"], clock.now()), form=form, errors=errors)

    @app.get("/m/{user_id}/profile/edit", response_class=HTMLResponse)
    def profile_edit(request: Request, user_id: str):
        """S-011: ACC US-3 #2, FR-024."""
        user = mother(user_id)
        p = profile.load(conn, user_id, clock.now())
        if p["edd"] is None:                         # BR-006
            return go(user_id, "setup")
        return edit_form(request, user, {"edd": p["edd"], "height_cm": "" if p["height_cm"] is None else p["height_cm"]}, {})

    @app.post("/m/{user_id}/profile/edit", response_class=HTMLResponse)
    async def profile_save(request: Request, user_id: str):
        user = mother(user_id)
        form = {k: v for k, v in (await request.form()).items()}
        try:
            profile.save(conn, user_id, form, clock.now())
        except profile.ProfileError as e:
            return edit_form(request, user, form, e.errors, 422)
        return RedirectResponse(f"/m/{user_id}/profile?saved=1", status_code=303)

    @app.get("/m/{user_id}/settings/notifications", response_class=HTMLResponse)
    def notification_settings(request: Request, user_id: str):
        """S-010."""
        return page(request, "notif_settings.html", user=mother(user_id), prefs=profile.preferences(conn, user_id))

    @app.post("/m/{user_id}/settings/notifications", response_class=HTMLResponse)
    async def notification_toggle(request: Request, user_id: str):
        user = mother(user_id)
        form = await request.form()
        try:
            profile.set_switch(conn, user_id, form.get("key") or "", form.get("value") == "1", clock.now())
        except profile.ProfileError:
            return page(request, "notif_settings.html", 422, user=user, prefs=profile.preferences(conn, user_id))
        return RedirectResponse(f"/m/{user_id}/settings/notifications", status_code=303)

    @app.get("/tci/booking", response_class=HTMLResponse)
    def tci_booking(request: Request):
        """"Book" tab of the simulated TCI host: the TCI app's booking flow, no screen in the sub-app (spec-APT BR-001)."""
        return page(request, "tci_booking.html")
