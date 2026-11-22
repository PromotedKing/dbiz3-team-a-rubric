"""Clinical web routes — specs/002-cli-core/contracts/http-routes.md (S-061, S-064)."""
import sqlite3
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import ui
from .. import clock
from . import actions, case_detail, dashboard, instructions, notices, queue, signin

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
ui.install(TEMPLATES)
FILTERS = ["Not viewed", "Viewed", "Escalated to doctor", "Resolved", "All"]


class NotSignedIn(Exception):
    """No staff session: the page goes to the sign-in form (D-107)."""


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    @app.exception_handler(NotSignedIn)
    async def to_sign_in(request: Request, exc: NotSignedIn):
        return RedirectResponse("/staff", status_code=303)

    def staff(request: Request, staff_id: str) -> sqlite3.Row:
        """D-107: the signed-in staff member. The role comes from the session, never from {id}; an {id} that is not the
        session's own staff_id is refused with 403 and no case data (spec-CLI §5.3 E-4)."""
        me = signin.session(conn, request.cookies.get(signin.COOKIE))
        if me is None:
            raise NotSignedIn()
        if me["staff_id"] != staff_id:
            raise HTTPException(403, "This page belongs to another staff member.")   # spec-CLI E-4
        return conn.execute("SELECT * FROM STAFF WHERE staff_id = ?", (staff_id,)).fetchone()

    def page(request: Request, name: str, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx)

    @app.get("/staff", response_class=HTMLResponse)
    def staff_sign_in_page(request: Request):
        """S-054 / S-060 (no mockup): sign-in by username + shared team password (D-107, D-82)."""
        me = signin.session(conn, request.cookies.get(signin.COOKIE))
        if me is not None:
            return RedirectResponse(f"/staff/{me['staff_id']}/dashboard", status_code=303)
        return page(request, "staff_login.html", me=None, error=False, login="")

    @app.post("/staff", response_class=HTMLResponse)
    async def staff_sign_in(request: Request):
        form = await request.form()
        login = (form.get("login") or "").strip()
        row = signin.sign_in(conn, login, form.get("password"))
        if row is None:
            return TEMPLATES.TemplateResponse(request, "staff_login.html", {"me": None, "error": True, "login": login}, status_code=401)
        response = RedirectResponse(f"/staff/{row['staff_id']}/dashboard", status_code=303)
        response.set_cookie(signin.COOKIE, signin.token(row["staff_id"], row["role"]), httponly=True, samesite="lax",
                            secure=signin.SECURE_COOKIE)
        return response

    @app.post("/staff/logout")
    def staff_sign_out():
        response = RedirectResponse("/staff", status_code=303)
        response.delete_cookie(signin.COOKIE)
        return response

    def filters(source: str, start: str, end: str) -> dict:
        def day(text):
            try:
                return date.fromisoformat(text) if text else None
            except ValueError:
                return None
        return {"source": source if source in dashboard.SOURCES else None, "start": day(start), "end": day(end)}

    @app.get("/staff/{staff_id}")
    def staff_home(request: Request, staff_id: str):
        staff(request, staff_id)
        return RedirectResponse(f"/staff/{staff_id}/dashboard", status_code=303)

    @app.get("/staff/{staff_id}/dashboard", response_class=HTMLResponse)
    def staff_dashboard(request: Request, staff_id: str, source: str = "", start: str = Query("", alias="from"), end: str = Query("", alias="to")):
        """D-85: overview of the cases, every number opens the cases behind it."""
        me = staff(request, staff_id)
        f = filters(source, start, end)
        rows = dashboard.cases(conn, clock.now(), viewer=staff_id, **f)          # BR-010
        mine = dashboard.cases(conn, clock.now(), doctor_id=staff_id, viewer=staff_id, **f) if me["role"] == "Doctor" else None
        return page(request, "staff_dashboard.html", me=me, s=dashboard.summary(rows, staff_id, mine), f=f, sources=dashboard.SOURCES,
                    badge=notices.count(conn, staff_id, me["role"]), nav="dashboard", updated=clock.now())

    @app.get("/staff/{staff_id}/notifications", response_class=HTMLResponse)
    def staff_notifications(request: Request, staff_id: str):
        """S-059 inside the clinical web (D-109, ALR-03): read from the cases, nothing stored (DM-32)."""
        me = staff(request, staff_id)
        if me["role"] == "Nurse":     # D-105: no Notifications for the nurse — her signal is the Priority list (D-104)
            return RedirectResponse(f"/staff/{staff_id}/cases", status_code=303)
        return page(request, "staff_notices.html", me=me, rows=notices.lines(conn, staff_id, me["role"], clock.now()),
                    badge=notices.count(conn, staff_id, me["role"]), nav="notifications", updated=clock.now())

    @app.get("/staff/{staff_id}/board", response_class=HTMLResponse)
    def staff_board(request: Request, staff_id: str, source: str = "", start: str = Query("", alias="from"), end: str = Query("", alias="to")):
        """D-85: the cases in columns by status; a card opens its case."""
        me = staff(request, staff_id)
        f = filters(source, start, end)
        return page(request, "staff_board.html", me=me, columns=dashboard.board(dashboard.cases(conn, clock.now(), viewer=staff_id, **f)), f=f,
                    sources=dashboard.SOURCES, badge=notices.count(conn, staff_id, me["role"]), nav="board")

    @app.get("/staff/{staff_id}/cases", response_class=HTMLResponse)
    def cases(request: Request, staff_id: str, status: str = "", flag: str = "", sort: str = ""):
        """S-061 (nurse) and S-061D (doctor): one page, the role view comes from STAFF.role (D-103, D-107)."""
        me = staff(request, staff_id)
        # D-104: the nurse sorts by "Priority" (default) or "Newest"; the doctor only "Newest" (S-061D #7, §9 Q1 open)
        order = (sort if sort in (queue.PRIORITY, queue.NEWEST) else queue.PRIORITY) if me["role"] == "Nurse" else queue.NEWEST
        # Default filter: doctor "Escalated to doctor" (CLI-02); nurse "Not viewed", the cases waiting for her (D-102, spec-CLI §10 Q5)
        active = status if status in FILTERS else ("Escalated to doctor" if me["role"] == "Doctor" else "Not viewed")
        flag = flag if flag in dashboard.FLAGS else ""
        if flag:                               # opened from "Needs attention" on the dashboard: every open case of that group
            active = "All"
            ids = dashboard.flagged_ids(dashboard.cases(conn, clock.now(), viewer=staff_id), flag)
        rows = queue.list_cases(conn, None if active == "All" else active, viewer=staff_id, order=order)
        if flag:
            rows = [r for r in rows if r["case_id"] in ids]
        # the count sits on the role's own chip: nurse "Not viewed (n)" (S-061 #6), doctor "Escalated to doctor (n)" (S-061D #6)
        counted = "Escalated to doctor" if me["role"] == "Doctor" else "Not viewed"
        badge = notices.count(conn, staff_id, me["role"])
        return page(request, "cases.html", me=me, rows=rows, active=active, filters=FILTERS, counted=counted,
                    count=len(queue.list_cases(conn, counted, viewer=staff_id)), badge=badge, order=order,
                    sorts=(queue.PRIORITY, queue.NEWEST), flag=flag, flag_label=dashboard.FLAGS[flag][0] if flag else None, nav="cases")

    @app.get("/staff/{staff_id}/cases/{case_id}", response_class=HTMLResponse)
    def case_page(request: Request, staff_id: str, case_id: str, error: str = "", edit: str = "", updated: int = 0):
        me = staff(request, staff_id)
        data = case_detail.load(conn, case_id)
        if data is None:
            raise HTTPException(404, "Unknown case")
        case_row = conn.execute("SELECT user_id, assigned_doctor_id, status FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
        mine = actions.visible_users(conn, staff_id, clock.now().date())      # BR-010
        if mine is not None and case_row["user_id"] not in mine and not (
                case_row["assigned_doctor_id"] is None and case_row["status"] == "Escalated to doctor"):   # BR-011 step 4
            raise HTTPException(403, "This mother is not in your care (spec-CLI BR-010)")
        templates = conn.execute("SELECT template_id, title FROM GUIDANCE_TEMPLATE ORDER BY title").fetchall()
        editing = next((f for f in data["flags"] if f["flag_id"] == edit), None) if me["role"] == "Doctor" else None
        return page(request, "case.html", me=me, can=actions.allowed(conn, case_id, staff_id), templates=templates,
                    error=error, editing=editing, group2=instructions.GROUP2, updated=updated,
                    must_escalate=actions.must_escalate(conn, case_id),    # BR-012
                    routing=actions.route_to(conn, case_row["user_id"], clock.now().date()),   # FR-026, FR-027
                    covering=me["role"] == "Doctor" and case_row["assigned_doctor_id"] == staff_id   # S-064D 4B
                    and actions.responsible_doctor(conn, case_row["user_id"], clock.now().date()) not in (None, staff_id),
                    badge=notices.count(conn, staff_id, me["role"]), **data)

    def act(request: Request, staff_id: str, case_id: str, fn, *args, **kw):
        staff(request, staff_id)
        try:
            fn(conn, case_id, staff_id, clock.now(), *args, **kw)
        except actions.ActionError as e:
            if e.status != 409:
                raise HTTPException(e.status, e.message)
            # 409: the case moved on, e.g. another screen already did this → show it as it is now
            return RedirectResponse(f"/staff/{staff_id}/cases/{case_id}?updated=1", status_code=303)
        return RedirectResponse(f"/staff/{staff_id}/cases/{case_id}", status_code=303)

    @app.post("/staff/{staff_id}/cases/{case_id}/view")
    def view(request: Request, staff_id: str, case_id: str):
        return act(request, staff_id, case_id, actions.mark_viewed)

    @app.post("/staff/{staff_id}/cases/{case_id}/escalate")
    def escalate(request: Request, staff_id: str, case_id: str):
        return act(request, staff_id, case_id, actions.escalate)

    @app.post("/staff/{staff_id}/cases/{case_id}/close")
    def close(request: Request, staff_id: str, case_id: str):
        return act(request, staff_id, case_id, actions.close_case)

    @app.post("/staff/{staff_id}/cases/{case_id}/instructions")
    async def save_instruction(request: Request, staff_id: str, case_id: str):
        """CLI FR-025 (doctor only, BR-001, BR-006)."""
        staff(request, staff_id)
        case = conn.execute("SELECT user_id FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
        if case is None:
            raise HTTPException(404, "Unknown case")
        form = await request.form()
        try:
            instructions.save_instruction(conn, case["user_id"], staff_id, clock.now(), form.get("metric") or "",
                                          note=form.get("note"), template_id=form.get("template_id") or None,
                                          custom_text=form.get("custom_text"))
        except actions.ActionError as e:
            raise HTTPException(e.status, e.message)
        return RedirectResponse(f"/staff/{staff_id}/cases/{case_id}", status_code=303)

    @app.post("/staff/{staff_id}/cases/{case_id}/guidance")
    async def guidance(request: Request, staff_id: str, case_id: str):
        form = await request.form()
        return act(request, staff_id, case_id, actions.send_guidance,
                   template_id=form.get("template_id") or None, custom_text=form.get("custom_text") or None)
