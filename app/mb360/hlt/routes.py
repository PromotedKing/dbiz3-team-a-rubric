"""HLT routes — specs/006-hlt-dashboard/contracts/http-routes.md (S-023, S-024)."""
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock
from . import dashboard, self_tracked

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
TEMPLATES.env.filters["show_time"] = lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y · %H:%M") if t else ""
TEMPLATES.env.filters["dmy"] = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else ""


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

    def page(request: Request, name: str, status: int = 200, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx, status_code=status)

    @app.get("/m/{user_id}/health", response_class=HTMLResponse)
    def health(request: Request, user_id: str, refreshed: int = 0, saved: int = 0):
        return page(request, "health.html", user=mother(user_id), d=dashboard.load(conn, user_id, clock.now()),
                    refreshed=refreshed, saved=saved)

    def form_page(request: Request, user, form: dict, errors: dict, status: int = 200):
        return page(request, "self_tracked.html", status, user=user, form=form, errors=errors)

    @app.get("/m/{user_id}/self-tracked", response_class=HTMLResponse)
    def self_tracked_form(request: Request, user_id: str):
        now = clock.now().strftime(self_tracked.FORM_TIME)   # "Measured at" prefilled with now (S-024 #6)
        form = {"weight_at": now, "temperature_at": now, "heart_rate_at": now}
        return form_page(request, mother(user_id), form, {})

    @app.post("/m/{user_id}/self-tracked", response_class=HTMLResponse)
    async def self_tracked_save(request: Request, user_id: str):
        user = mother(user_id)
        form = {k: v for k, v in (await request.form()).items()}
        try:
            self_tracked.save(conn, user_id, form, clock.now())
        except self_tracked.EntryError as e:
            return form_page(request, user, form, e.errors, 422)
        return RedirectResponse(f"/m/{user_id}/health?saved=1", status_code=303)
