# Notes: local versus internet (Session 11)

What had to change, or failed, when the app moved from a team machine to the internet. Add a row for every error met during deployment and every failure found when testing from outside. Each failure found from outside also becomes one EARS line in `spec.md` (Session 11 requires at least one; the spec owner adds it).

## Found before deploying

| Problem | Effect on the internet | Fix |
|---|---|---|
| The app used the server's clock | A server in UTC is 7 hours behind Vietnam, so "today" and measured times were wrong | `clock.use_live()` uses UTC+7, whatever the server's time zone |
| The reset button, `/staff` and `/tci/accounts` were open | A stranger could wipe the data or act as a nurse | Shared password from `MB360_STAFF_PASSWORD`; closed on the platform if it is not set (D-82) |
| One SQLite connection shared by parallel requests | Two visitors at once could mix their transactions | `mb360.server` runs one request at a time |
| Session cookie sent over plain HTTP too | The session could leak on an insecure connection | The cookie is marked Secure on the platform |
| The "sample data" notice showed only beside the phone frame | A visitor on a phone could read sample medical text as real | Notice on the TCI home screen |
| Search engines could index a page carrying the hospital's name | A student demo could look like an official page | `X-Robots-Tag: noindex` on every response |

## Found during deployment

| Date | Error or log line | Cause | Fix |
|---|---|---|---|
| | | | |

## Found testing from outside (phone on mobile data)

| Date | Tester, device | Step | What happened | EARS line added |
|---|---|---|---|---|
| | | | | |
