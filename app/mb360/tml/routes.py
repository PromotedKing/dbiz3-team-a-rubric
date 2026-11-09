"""TML routes — specs/007-tml-timeline/contracts/http-routes.md (S-048, S-051 / S-052)."""
import sqlite3
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import ui
from .. import clock
from . import diary, weeks

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
ui.install(TEMPLATES)


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

    def page(request: Request, name: str, status: int = 200, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx, status_code=status)

    def media_exists(rel: str | None) -> bool:
        return bool(rel) and (Path(diary.MEDIA_DIR) / rel).is_file()

    @app.get("/m/{user_id}/timeline", response_class=HTMLResponse)
    def timeline(request: Request, user_id: str, week: int | None = None, saved: int = 0):
        user = mother(user_id)
        w = weeks.load_week(conn, user_id, week, clock.now().date())
        if w is None:
            return RedirectResponse(f"/m/{user_id}/setup", status_code=303)
        today = clock.now().date()
        strip = weeks.week_days(w, today)
        return page(request, "timeline.html", user=user, w=w, saved=saved, media_exists=media_exists, strip=strip,
                    today_cell=next((d for d in strip if d["is_today"]), None))

    @app.get("/m/{user_id}/timeline/day/{day}", response_class=HTMLResponse)
    def timeline_day(request: Request, user_id: str, day: str):
        """One day of the week view (D-75, D-80): the same data as S-048, read-only."""
        user = mother(user_id)
        edd_row = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
        if edd_row is None:
            return RedirectResponse(f"/m/{user_id}/setup", status_code=303)
        try:
            when = date.fromisoformat(day)
        except ValueError:
            raise HTTPException(404, "Unknown day")
        edd, today = date.fromisoformat(edd_row[0]), clock.now().date()
        n = weeks.current_week(edd, when)
        if when > today or not weeks.FIRST_WEEK <= n <= weeks.LAST_WEEK:
            raise HTTPException(404, "Unknown day")
        w = weeks.load_week(conn, user_id, n, today)
        cell = next(d for d in weeks.week_days(w, today) if d["iso"] == day)
        return page(request, "day.html", user=user, day=cell, week=n, week_day=weeks.day_of_week(edd, when), media_exists=media_exists,
                    visits=[v for v in w["visits"] if v["visit_date"] == day],
                    rows=next((d["rows"] for d in w["days"] if d["day"] == day), []),
                    diary=[e for e in w["diary"] if e["entry_date"] == day])

    def form_page(request: Request, user, form: dict, errors: dict, status: int = 200):
        edd = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user["user_id"],)).fetchone()
        current = weeks.current_week(date.fromisoformat(edd[0]), clock.now().date()) if edd else None
        return page(request, "diary_form.html", status, user=user, form=form, errors=errors, moods=diary.MOODS,
                    current=current, today=clock.now().date())

    @app.get("/m/{user_id}/diary/new", response_class=HTMLResponse)
    def diary_new(request: Request, user_id: str):
        return form_page(request, mother(user_id), {}, {})

    @app.post("/m/{user_id}/diary", response_class=HTMLResponse)
    async def diary_save(request: Request, user_id: str):
        user = mother(user_id)
        form = await request.form()
        photos = [(f.filename, await f.read()) for f in form.getlist("photos") if hasattr(f, "read")]
        try:
            diary.save(conn, user_id, form.get("text") or "", form.get("mood") or None, photos, clock.now())
        except diary.DiaryError as e:
            return form_page(request, user, {"text": form.get("text") or "", "mood": form.get("mood") or ""}, e.errors, 422)
        return RedirectResponse(f"/m/{user_id}/timeline?saved=1", status_code=303)

    @app.get("/media/{path:path}")
    def media(path: str):
        base = Path(diary.MEDIA_DIR).resolve()
        target = (base / path).resolve()
        if base not in target.parents or not target.is_file():
            raise HTTPException(404, "Not found")
        return FileResponse(target)
