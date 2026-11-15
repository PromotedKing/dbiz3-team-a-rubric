"""Friendly error screen for every route (15/11/2026).

Without it, an HTTPException reached the browser as raw JSON ({"detail": …}) and an unexpected error as plain text, which
a phone in dark mode shows as white text in the corner of a black page — seen when two devices used the same session and
the slower one repeated an action (BOT hand-off) the faster one had already done. The status code is kept; the page says
what happened in Vietnamese and offers a way back."""
import logging
import re

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import ui

LOG = logging.getLogger("mb360")
MESSAGES = {
    400: "Some of the information sent is not valid. Go back and try again.",
    403: "This is not available for this account.",
    404: "This page or item is no longer available.",
    409: "This was already changed, maybe on another screen. Open it again to see the latest state.",
    422: "Some of the information sent is not valid. Go back and try again.",
}
OTHER = "Something went wrong. Please try again."
_MOTHER = re.compile(r"^/m/([^/]+)/")
_STAFF = re.compile(r"^/staff/([^/]+)/")


def where(path: str) -> tuple[str, str]:
    """The screen to go back to: the mother's Home, the staff member's case list, or the TCI app."""
    if m := _MOTHER.match(path):
        return f"/m/{m.group(1)}/home", "Go to Home"
    if m := _STAFF.match(path):
        return f"/staff/{m.group(1)}/cases", "Go to the case list"
    return "/tci", "Back to TCI app"


def detail_text(detail) -> str | None:
    """The exception's own message only when it can be shown in Vietnamese: a known label or Vietnamese text."""
    if not isinstance(detail, str) or not detail:
        return None
    shown = ui.t_known(detail)
    if shown != detail or not detail.isascii():
        return shown
    return None


def install(app: FastAPI, templates: Jinja2Templates) -> None:
    def render(request: Request, status: int, message: str, detail: str | None):
        home_url, home_label = where(request.url.path)
        return templates.TemplateResponse(request, "error.html", {"status": status, "message": message, "detail": detail,
                                                                  "home_url": home_url, "home_label": home_label},
                                          status_code=status)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        response = render(request, exc.status_code, MESSAGES.get(exc.status_code, OTHER), detail_text(exc.detail))
        for key, value in (exc.headers or {}).items():
            response.headers[key] = value
        return response

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        LOG.exception("unhandled error on %s %s", request.method, request.url.path)     # path only: no form data, no cookie
        return render(request, 500, OTHER, None)
