"""Minimal sign-in of the hosted app (D-82): HTTP Basic with one shared password from the environment, for the pages a stranger
must not reach. Real staff accounts stay open until spec-CLI §10 Q11 is answered. Without a password the pages are open on a
team machine and closed on the hosting platform, so a forgotten setting never exposes them."""
import base64
import secrets

PROTECTED = ("/staff", "/showcase", "/tci/accounts")


def is_protected(path: str) -> bool:
    return any(path == p or path.startswith(p + "/") for p in PROTECTED)


def allowed(authorization: str | None, password: str | None, hosted: bool) -> bool:
    if not password:
        return not hosted
    scheme, _, value = (authorization or "").partition(" ")
    if scheme.lower() != "basic":
        return False
    try:
        _, _, given = base64.b64decode(value, validate=True).decode("utf-8").partition(":")
    except ValueError:
        return False
    return secrets.compare_digest(given.encode("utf-8"), password.encode("utf-8"))
