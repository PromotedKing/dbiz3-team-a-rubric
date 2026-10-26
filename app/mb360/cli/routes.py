"""Clinical web routes — specs/002-cli-core/contracts/http-routes.md (S-061, S-064)."""
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock
from . import actions, case_detail, instructions, queue

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
TEMPLATES.env.filters["show_time"] = lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y · %H:%M") if t else ""
TEMPLATES.env.filters["show_date"] = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else ""
FILTERS = ["Not viewed", "Viewed", "Escalated to doctor", "Resolved", "All"]


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    def staff(staff_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM STAFF WHERE staff_id = ?", (staff_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown staff member")
        return row

    def page(request: Request, name: str, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx)

    @app.get("/staff", response_class=HTMLResponse)
    def staff_select(request: Request):
        rows = conn.execute("SELECT staff_id, full_name, role FROM STAFF ORDER BY role DESC, full_name").fetchall()
        return page(request, "staff_select.html", staff_rows=rows)

    @app.get("/staff/{staff_id}/cases", response_class=HTMLResponse)
    def cases(request: Request, staff_id: str, status: str = ""):
        me = staff(staff_id)
        # Default filter: doctor "Escalated to doctor" (CLI-02); nurse "All" (S-061 mockup; spec-CLI §10 Q5 open)
        active = status if status in FILTERS else ("Escalated to doctor" if me["role"] == "Doctor" else "All")
        rows = queue.list_cases(conn, None if active == "All" else active)
        not_viewed = len(queue.list_cases(conn, "Not viewed"))
        badge = queue.doctor_badge(conn, staff_id) if me["role"] == "Doctor" else None
        return page(request, "cases.html", me=me, rows=rows, active=active, filters=FILTERS, not_viewed=not_viewed, badge=badge)

    @app.get("/staff/{staff_id}/cases/{case_id}", response_class=HTMLResponse)
    def case_page(request: Request, staff_id: str, case_id: str, error: str = "", edit: str = ""):
        me = staff(staff_id)
        data = case_detail.load(conn, case_id)
        if data is None:
            raise HTTPException(404, "Unknown case")
        templates = conn.execute("SELECT template_id, title FROM GUIDANCE_TEMPLATE ORDER BY title").fetchall()
        editing = next((f for f in data["flags"] if f["flag_id"] == edit), None) if me["role"] == "Doctor" else None
        return page(request, "case.html", me=me, can=actions.allowed(conn, case_id, staff_id), templates=templates,
                    error=error, editing=editing, group2=instructions.GROUP2, **data)

    def act(staff_id: str, case_id: str, fn, *args, **kw):
        staff(staff_id)
        try:
            fn(conn, case_id, staff_id, clock.now(), *args, **kw)
        except actions.ActionError as e:
            raise HTTPException(e.status, e.message)
        return RedirectResponse(f"/staff/{staff_id}/cases/{case_id}", status_code=303)

    @app.post("/staff/{staff_id}/cases/{case_id}/view")
    def view(staff_id: str, case_id: str):
        return act(staff_id, case_id, actions.mark_viewed)

    @app.post("/staff/{staff_id}/cases/{case_id}/escalate")
    def escalate(staff_id: str, case_id: str):
        return act(staff_id, case_id, actions.escalate)

    @app.post("/staff/{staff_id}/cases/{case_id}/close")
    def close(staff_id: str, case_id: str):
        return act(staff_id, case_id, actions.close_case)

    @app.post("/staff/{staff_id}/cases/{case_id}/instructions")
    async def save_instruction(request: Request, staff_id: str, case_id: str):
        """CLI FR-025 (doctor only, BR-001, BR-006)."""
        staff(staff_id)
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
        return act(staff_id, case_id, actions.send_guidance,
                   template_id=form.get("template_id") or None, custom_text=form.get("custom_text") or None)
