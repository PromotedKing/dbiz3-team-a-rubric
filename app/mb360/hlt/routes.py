"""HLT routes — specs/006-hlt-dashboard/contracts/http-routes.md (S-023, S-024)."""
import sqlite3
from pathlib import Path

from datetime import date

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import ui
from .. import clock
from . import dashboard, history, self_tracked

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
ui.install(TEMPLATES)
CONTEXT_LABELS = {"fasting": "Fasting", "post_1h": "1 h after meal", "post_2h": "2 h after meal"}


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

    @app.get("/m/{user_id}/history", response_class=HTMLResponse)
    def metric_history(request: Request, user_id: str, metric: str = "", context: str = "",
                       start: str = Query("", alias="from"), end: str = Query("", alias="to")):
        """S-025: HLT US-4, FR-009 – FR-012."""
        def day(text: str) -> date | None:
            try:
                return date.fromisoformat(text)
            except ValueError:
                return None

        if metric == "Blood glucose" and not context:      # Ánh 3.B.3: one timing at a time by default (thresholds differ, SR-002)
            context = "fasting"
        return page(request, "history.html", user=mother(user_id), metrics=history.METRICS,
                    h=history.load(conn, user_id, metric, day(start), day(end), "" if context == "all" else context, clock.now()),
                    contexts=list(CONTEXT_LABELS.items()), context_labels=CONTEXT_LABELS)

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
