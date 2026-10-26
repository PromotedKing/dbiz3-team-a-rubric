"""TML routes — specs/007-tml-timeline/contracts/http-routes.md (S-048, S-051 / S-052)."""
import sqlite3
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock
from . import diary, weeks

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
TEMPLATES.env.filters["dmy"] = lambda d: (d if isinstance(d, date) else datetime.strptime(d[:10], "%Y-%m-%d")).strftime("%d/%m/%Y") if d else ""


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
        return page(request, "timeline.html", user=user, w=w, saved=saved, media_exists=media_exists)

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
