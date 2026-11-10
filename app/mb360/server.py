"""The v1.0.0 mother app: `python -m uvicorn mb360.server:app --app-dir app`. Real clock, sample mother, TCI session checked on every
sub-app page, data kept in a local file between restarts. mb360.main stays the plain app that the tests build.
On the hosting platform (render.yaml, RENDER is set there): see docs/build/adr-hosting.md."""
import os
from pathlib import Path

from fastapi import Request
from fastapi.responses import RedirectResponse, Response

from . import clock, gate, persona, serial, ui
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


HOSTED = bool(os.environ.get("RENDER"))
STAFF_PASSWORD = os.environ.get("MB360_STAFF_PASSWORD")

clock.use_live()
entry.SECURE_COOKIE = HOSTED
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


@app.middleware("http")
async def public_internet(request: Request, call_next):
    """D-82: password on the pages a stranger must not reach, and a demo that search engines leave out."""
    if gate.is_protected(request.url.path) and not gate.allowed(request.headers.get("authorization"), STAFF_PASSWORD, HOSTED):
        return Response("Cần mật khẩu của nhóm.", status_code=401, media_type="text/plain; charset=utf-8",
                        headers={"WWW-Authenticate": 'Basic realm="Mother & Baby 360", charset="UTF-8"'})
    if request.url.path.startswith("/static/") or serial.locks_itself(request.method, request.url.path):
        response = await call_next(request)
    else:
        async with serial.LOCK:      # one SQLite connection: parallel requests must not mix their transactions
            response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex"
    return response


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
