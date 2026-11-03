"""The v1.0.0 mother app: `python -m uvicorn mb360.server:app --app-dir app`. Real clock, sample mother, TCI session checked on every
sub-app page, data kept in a local file between restarts. mb360.main stays the plain app that the tests build."""
import os
from pathlib import Path

from fastapi import Request
from fastapi.responses import RedirectResponse, Response

from . import clock, persona, ui
from . import db as dbmod
from .acc import entry
from .bot import llm
from .main import create_app

STATIC = Path(__file__).parent / "static"
DB_FILE = Path(os.environ.get("MB360_DB") or Path(__file__).resolve().parents[2] / ".local" / "mb360-app.sqlite")


def _open():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DB_FILE.exists():
        return dbmod.open_file(str(DB_FILE))
    conn = dbmod.build(str(DB_FILE))
    persona.install(conn, clock.now())
    return conn


clock.use_live()
llm.use_fallback(llm.LocalAnswers)
ui.SHOWCASE = True
conn = _open()
app = create_app(conn)


@app.middleware("http")
async def tci_session(request: Request, call_next):
    """ACC FR-015: every sub-app page needs the session opened from the TCI app; otherwise S-043."""
    parts = request.url.path.split("/")
    if len(parts) > 2 and parts[1] == "m" and not entry.valid_session(conn, request.cookies.get(entry.COOKIE), parts[2], clock.now()):
        return RedirectResponse("/session-expired", status_code=303)
    return await call_next(request)


@app.get("/sw.js")
def service_worker():
    return Response((STATIC / "sw.js").read_text(encoding="utf-8"), media_type="text/javascript", headers={"Service-Worker-Allowed": "/"})


@app.post("/showcase/reset")
def reset_sample_data():
    """Empties the database and adds the sample mother again, so the first-opening flow can be shown once more."""
    conn.execute("PRAGMA foreign_keys = OFF")
    for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'").fetchall():
        conn.execute(f"DELETE FROM {name}")
    conn.execute("PRAGMA foreign_keys = ON")
    dbmod.load_seed(conn)
    persona.install(conn, clock.now())
    response = RedirectResponse("/tci", status_code=303)
    response.delete_cookie(entry.COOKIE)
    return response
