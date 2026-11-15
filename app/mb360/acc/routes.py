"""ACC onboarding routes — specs/005-acc-onboarding/contracts/http-routes.md (S-001, S-104, S-007 / S-046, S-008)."""
import sqlite3
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import appointment_demo, clock, persona, tci_booking, tci_feed, ui
from ..alr.reports import gestational_week
from ..alr.validation import GROUP2
from ..hlt import dashboard
from ..tml import weeks
from . import entry, notices, profile, setup

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
ui.install(TEMPLATES)
IDENTITY = ("tci_account_ref", "full_name", "date_of_birth", "sex", "phone", "record_code")
GUIDE_PAGES = [   # 3 pages, as Màn 13 of the UI package; text pending (spec-ACC §10 Q20)
    ("Follow your pregnancy with Thu Cuc doctors", "Visit results update on their own. Report a metric or symptom and clinical staff will view and respond."),
    ("Keep every moment of your pregnancy", "Your visits, ultrasound images and diary, week by week, ready to keep as an album."),
    ("Answers whenever you need them", "Ask the chatbot general questions about pregnancy. For anything about your own health, it passes you to a nurse."),
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

    def signed_in(user_id: str, step: str) -> RedirectResponse:
        """Opened from the TCI app: the session goes with the browser (FR-015)."""
        response = go(user_id, step)
        response.set_cookie(entry.COOKIE, entry.latest_session(conn, user_id) or "", httponly=True, samesite="lax", secure=entry.SECURE_COOKIE)
        return response

    async def identity_of(request: Request) -> dict:
        form = await request.form()
        ident = {k: (form.get(k) or "").strip() for k in IDENTITY}
        ident["tci_account_ref"] = ident["tci_account_ref"] or f"tci-sim-{uuid.uuid4().hex[:8]}"
        return ident

    host_account, remember_host = tci_booking.register(app, conn, page)

    @app.get("/tci", response_class=HTMLResponse)
    def tci_home(request: Request):
        """Màn 1: the home screen of the TCI app, signed in as one account."""
        return page(request, "tci_home.html", account=host_account(request), fields=IDENTITY)

    @app.get("/tci/accounts", response_class=HTMLResponse)
    def tci_accounts(request: Request):
        """Test tool: open the sub-app as another TCI account (spec-ACC §10 Q9 is still open)."""
        accounts = conn.execute("SELECT * FROM USER_ACCOUNT ORDER BY full_name").fetchall()
        return page(request, "tci_accounts.html", accounts=accounts, fields=IDENTITY)

    @app.post("/tci/open", response_class=HTMLResponse)
    async def tci_open(request: Request):
        ident = await identity_of(request)
        outcome, user_id = entry.open_subapp(conn, ident, clock.now())
        if outcome == "not_female":
            return page(request, "not_female.html")
        if outcome == "consent":
            return page(request, "consent.html", ident=ident, error=None)
        return remember_host(signed_in(user_id, outcome), user_id)

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
        return signed_in(user_id, "guide")

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
        return page(request, "setup.html", status, user=user, form=form, errors=errors, card=card, today=clock.now().date(), trimester_of=weeks.trimester)

    @app.get("/m/{user_id}/setup", response_class=HTMLResponse)
    def setup_get(request: Request, user_id: str, date_type: str = "EDD", date: str = ""):
        user = mother(user_id)
        if entry.next_step(conn, user_id) == "home":   # BR-006
            return go(user_id, "home")
        prefill = tci_feed.hospital_edd(conn, user_id) if date_type == "EDD" and "date" not in request.query_params else ""
        form = {"date_type": date_type, "date": date or prefill or ""}
        if user_id == persona.USER:
            first_visit = conn.execute("SELECT MIN(visit_date) FROM VISIT WHERE user_id=?", (user_id,)).fetchone()[0]
            form["first_visit_date"] = first_visit or ""
        return setup_page(request, user, form, {})

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
    def home(request: Request, user_id: str, saved: int = 0):
        user = mother(user_id)
        appointment_demo.create_reminders(conn, clock.now(), user_id)
        profile = conn.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
        if profile is None:                          # BR-006
            return go(user_id, "setup")
        flags = conn.execute("SELECT metric FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,)).fetchall()
        handling = conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id = ? AND status <> 'Resolved'", (user_id,)).fetchone()[0]
        today, edd = clock.now().date(), date.fromisoformat(profile["edd"])
        week = gestational_week(edd, today)
        return page(request, "home.html", user=user, given_name=user["full_name"].split()[-1], saved=saved, today_iso=today.isoformat(),
                    week=week, week_day=weeks.day_of_week(edd, today), edd=profile["edd"], days_left=(edd - today).days,
                    progress=weeks.progress(edd, today), trimester=weeks.trimester(week),
                    flags=[m for m in GROUP2 if m in {f["metric"] for f in flags}], handling=handling, unread_count=ui.unread(user_id),
                    appointment=tci_feed.next_appointment(conn, user_id, clock.now()), latest_notice=notices.home_notice(conn, user_id),
                    diary_today=conn.execute("SELECT 1 FROM DIARY_ENTRY WHERE user_id = ? AND entry_date = ?",
                                             (user_id, today.isoformat())).fetchone() is not None,
                    d=dashboard.load(conn, user_id, clock.now()))    # self-tracked cards and latest status (S-008 #8, #12 – #15)

    @app.get("/m/{user_id}/notices", response_class=HTMLResponse)
    def notices_page(request: Request, user_id: str, type: str = "", unread: bool = False):
        """S-009 behind the "From doctor" tab (D-80): FR-025."""
        mother(user_id)
        appointment_demo.create_reminders(conn, clock.now(), user_id)
        active = type if type in notices.TYPES else ""
        unread_only = unread or type == notices.UNREAD
        return page(request, "notices.html", user=mother(user_id),
                    rows=notices.cards_for(conn, user_id, active, unread_only=unread_only), active=active,
                    types=notices.TYPES, unread_count=notices.unread_count(conn, user_id), unread_only=unread_only)

    @app.post("/m/{user_id}/notices/read-all")
    def notices_read_all(user_id: str):
        mother(user_id)
        notices.mark_all_read(conn, user_id, clock.now())
        return RedirectResponse(f"/m/{user_id}/notices", status_code=303)

    @app.get("/m/{user_id}/notices/{notification_id}")
    def notice_open(request: Request, user_id: str, notification_id: str):
        """FR-026: marks it read. An answer from clinical staff opens Màn 10 (U9); anything else its target (S-009 SR-001)."""
        user = mother(user_id)
        target = notices.open_notice(conn, user_id, notification_id, clock.now())
        if target is None:
            raise HTTPException(404, "Unknown notification")
        d = notices.detail(conn, user_id, notification_id)
        if d is None:
            return RedirectResponse(target, status_code=303)
        return page(request, "notice_detail.html", user=user, d=d, target=target)

    @app.post("/m/{user_id}/close")
    def close_app(request: Request, user_id: str):
        """S-083 "Close app": FR-019 ends the sub-app session, FR-021 clears its cookie; the TCI account stays signed in."""
        mother(user_id)
        entry.end_session(conn, request.cookies.get(entry.COOKIE), user_id, clock.now())
        response = RedirectResponse("/tci", status_code=303)
        response.delete_cookie(entry.COOKIE)
        return response

    @app.get("/session-expired", response_class=HTMLResponse)
    def session_expired(request: Request):
        """S-043. Sessions are not checked before Session 11 (no sign-in); reachable from the demo start page."""
        return page(request, "expired.html", 401)

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
        if profile.load(conn, user_id, clock.now())["edd"] is None:    # BR-006, like the GET; was a 500 error (15/11/2026)
            return go(user_id, "setup")
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

    @app.get("/m/{user_id}/appointments", response_class=HTMLResponse)
    def appointments(request: Request, user_id: str, tab: str = "current"):
        user = mother(user_id)
        if not entry.valid_session(conn, request.cookies.get(entry.COOKIE), user_id, clock.now()):
            raise HTTPException(404, "Appointment list not found")
        current, past = tci_feed.appointments(conn, user_id, clock.now())
        history = tab == "history"
        return page(request, "appointments.html", user=user, rows=past if history else current,
                    history=history, today=clock.now().date().isoformat())
