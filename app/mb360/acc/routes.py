"""ACC onboarding routes — specs/005-acc-onboarding/contracts/http-routes.md (S-001, S-104, S-007 / S-046, S-008)."""
import sqlite3
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock, ui
from ..alr.reports import gestational_week
from ..hlt import dashboard
from . import entry, setup

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
        return page(request, "home.html", user=user, given_name=user["full_name"].split()[-1],
                    week=gestational_week(date.fromisoformat(profile["edd"]), clock.now().date()), edd=profile["edd"],
                    flags=[f["metric"] for f in flags], handling=handling,
                    d=dashboard.load(conn, user_id, clock.now()))    # self-tracked cards and latest status (S-008 #8, #12 – #15)

    @app.get("/m/{user_id}/profile", response_class=HTMLResponse)
    def profile(request: Request, user_id: str):
        """Profile tab (ui-label-reference §9). S-103 itself is ACC US-3, not built yet."""
        user = mother(user_id)
        row = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
        week = gestational_week(date.fromisoformat(row["edd"]), clock.now().date()) if row else None
        return page(request, "profile.html", user=user, week=week)

    @app.get("/tci/booking", response_class=HTMLResponse)
    def tci_booking(request: Request, user_id: str = Query("", alias="from")):
        """Appointments tab: the TCI app's booking flow, no screen in the sub-app (spec-APT BR-001, BR-003)."""
        back = f"/m/{user_id}/home" if user_id and conn.execute(
            "SELECT 1 FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone() else ""
        return page(request, "tci_booking.html", back=back)
