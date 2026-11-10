"""One SQLite connection serves every request, so two requests must not mix their transactions: they take turns on LOCK.
mb360.server holds it around each request; a chatbot question holds it only while it reads and writes the database,
not while it waits for the LLM service (review 09/11/2026, A2), so the other users are not kept waiting."""
import asyncio
import re

LOCK = asyncio.Lock()
_CHAT_POST = re.compile(r"^/m/[^/]+/chat(/[^/]+)?$")


def locks_itself(method: str, path: str) -> bool:
    """The routes that take LOCK themselves around their database work (bot.routes.handle_ask)."""
    return method == "POST" and bool(_CHAT_POST.match(path))
