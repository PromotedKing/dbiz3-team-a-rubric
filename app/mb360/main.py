"""Mother & Baby 360 — routes of specs/001-alr-core/contracts/http-routes.md (ALR US-1)."""
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import appointment_demo, clock, errors, ui
from . import db as dbmod
from .alr import cases, my_reports, reports, routing, status, thresholds, validation
from .alr import status as status_mod
from .hlt import history

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
GLUCOSE_LABELS = {"fasting": "Fasting", "post_1h": "1 h after meal", "post_2h": "2 h after meal"}

ui.install(TEMPLATES)


def create_app(conn: sqlite3.Connection) -> FastAPI:
    appointment_demo.install(conn, clock.now())
    app = FastAPI(title="Mother & Baby 360")

    @app.middleware("http")
    async def select_language(request: Request, call_next):
        token = ui.use_language(request.cookies.get(ui.LANGUAGE_COOKIE, "vi"))
        try:
            return await call_next(request)
        finally:
            ui._language.reset(token)

    errors.install(app, TEMPLATES)                  # no raw JSON / plain-text error page (15/11/2026)
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")   # TCI theme (D-79, D-80)
    ui.use_connection(conn)

    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

    def has_profile(user_id: str) -> bool:
        return conn.execute("SELECT 1 FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone() is not None

    def instructions(user_id: str) -> list[sqlite3.Row]:
        return conn.execute("SELECT * FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,)).fetchall()

    def page(request: Request, name: str, status: int = 200, **ctx) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(request, name, ctx, status_code=status)

    def report_form(request: Request, user, metric: str, form: dict, errors: dict, status: int = 200):
        flags = {f["metric"]: f for f in instructions(user["user_id"])}
        if metric != "Symptom" and metric not in flags:
            metric = "Symptom"
        ctx = form.get("glucose_context") or None
        card = thresholds.card_text(conn, metric, ctx) if metric in ("Blood pressure", "Urine protein") or ctx else None
        return page(request, "report_form.html", status, user=user, metric=metric, metrics=[m for m in validation.GROUP2 if m in flags], flag=flags.get(metric),
                    card=card, live_rules=thresholds.live_rules(conn, metric), form=form, errors=errors, symptoms=validation.SYMPTOMS, glucose_labels=GLUCOSE_LABELS,
                    urine_scale=thresholds.URINE_SCALE)

    @app.get("/")
    def start():
        return RedirectResponse("/tci", status_code=303)

    @app.post("/language")
    async def change_language(request: Request):
        form = await request.form()
        language = form.get("language")
        if language not in ui.LANGUAGES:
            raise HTTPException(422, "Unsupported language")
        return_to = form.get("return_to") or "/"
        if not return_to.startswith("/") or return_to.startswith("//") or "\\" in return_to or any(ord(c) < 32 for c in return_to):
            return_to = "/"
        response = RedirectResponse(return_to, status_code=303)
        response.set_cookie(ui.LANGUAGE_COOKIE, language, max_age=31536000, path="/", httponly=True,
                            secure=request.url.scheme == "https", samesite="lax")
        return response

    @app.get("/m/{user_id}/instructions", response_class=HTMLResponse)
    def doctor_instructions(request: Request, user_id: str, submitted: int = 0):
        return page(request, "instructions.html", user=mother(user_id), flags=history.instruction_cards(conn, user_id), submitted=submitted)

    @app.get("/m/{user_id}/report", response_class=HTMLResponse)
    def new_report(request: Request, user_id: str, metric: str = "Symptom", glucose_context: str = ""):
        if not has_profile(user_id):
            return RedirectResponse(f"/m/{user_id}/setup", status_code=303)
        form = {"metric": metric, "glucose_context": glucose_context, "symptoms": [],
                "measured_at": clock.now().strftime(validation.FORM_TIME)}
        return report_form(request, mother(user_id), metric, form, {})

    @app.post("/m/{user_id}/report")
    async def submit_report(request: Request, user_id: str):
        user = mother(user_id)
        if not has_profile(user_id):        # ACC BR-006: no week without a profile; was a 500 error (15/11/2026)
            return RedirectResponse(f"/m/{user_id}/setup", status_code=303)
        data = await request.form()
        form = {k: data.get(k, "") for k in ("metric", "systolic", "diastolic", "value", "level", "glucose_context",
                                               "measured_at", "other_symptom_text", "note")}
        form["symptoms"] = data.getlist("symptoms")
        active = {f["metric"] for f in instructions(user_id)}
        now = clock.now()
        errors = validation.validate(form, active, now)
        if errors:
            return report_form(request, user, form["metric"], form, errors, status=422)
        try:
            stored = reports.store_report(conn, user_id, form, now)
            label = thresholds.evaluate(conn, form["metric"], stored["value"], form.get("glucose_context") or None)
            screen, source = routing.route(label, form["symptoms"])
            if source:
                cases.open_case(conn, user_id, stored["report_id"], source, now)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        target = {"S-028": f"/m/{user_id}/reports/{stored['report_id']}/alert",
                  "S-026": f"/m/{user_id}/reports/{stored['report_id']}?submitted=1",
                  "S-027": f"/m/{user_id}/instructions?submitted=1"}[screen]
        return RedirectResponse(target, status_code=303)

    def load_report(user_id: str, report_id: str):
        rep = conn.execute("SELECT * FROM METRIC_REPORT WHERE report_id = ? AND user_id = ?", (report_id, user_id)).fetchone()
        if rep is None:
            raise HTTPException(404, "Unknown report")
        hmr = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE record_id = ?", (rep["health_metric_record_id"],)).fetchone()
        syms = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ?", (report_id,))]
        case = conn.execute("SELECT * FROM CARE_CASE WHERE metric_report_id = ?", (report_id,)).fetchone()
        return rep, hmr, syms, case

    @app.get("/m/{user_id}/reports/{report_id}/alert", response_class=HTMLResponse)
    def metric_alert(request: Request, user_id: str, report_id: str):
        rep, hmr, syms, case = load_report(user_id, report_id)
        if hmr is None:
            raise HTTPException(404, "A symptom report has no metric value")
        flag = conn.execute("SELECT * FROM WATCH_FLAG WHERE flag_id = ?", (rep["watch_flag_id"],)).fetchone()
        guidance = []
        if flag and flag["template_id"]:
            guidance.append(conn.execute("SELECT content FROM GUIDANCE_TEMPLATE WHERE template_id = ?",
                                         (flag["template_id"],)).fetchone()[0])
        if flag and flag["custom_text"]:
            guidance.append(flag["custom_text"])
        if not guidance:   # BR-013: hospital default template
            guidance.append(conn.execute("SELECT content FROM GUIDANCE_TEMPLATE WHERE is_default = 1").fetchone()[0])
        card = thresholds.card_text(conn, hmr["metric"], hmr["glucose_context"])
        lines = [line.strip() for g in guidance for line in g.splitlines() if line.strip()]
        return page(request, "metric_alert.html", user=mother(user_id), rep=rep, hmr=hmr, card=card, guidance=lines, symptoms=syms)

    @app.get("/m/{user_id}/reports/{report_id}", response_class=HTMLResponse)
    def report_status(request: Request, user_id: str, report_id: str, submitted: int = 0):
        rep, hmr, syms, case = load_report(user_id, report_id)
        label = (thresholds.evaluate(conn, hmr["metric"], hmr["value"], hmr["glucose_context"]) if hmr else thresholds.NOT_ASSESSED)
        return status_page(request, user_id, case, submitted, rep=rep, hmr=hmr, symptoms=syms, label=label)

    def status_page(request: Request, user_id: str, case, submitted: int, **ctx):
        """S-026 (ALR US-2): progress, responses or Safety note (BR-011, BR-012)."""
        cid = case["case_id"] if case else None
        responses = status.responses(conn, cid) if cid else []
        return page(request, "report_status.html", user=mother(user_id), case=case, submitted=submitted,
                    steps=status.progress(conn, cid) if cid else [], responses=responses,
                    safety_note=status.show_safety_note(conn, cid) if cid else False,
                    instruction_cards=history.instruction_cards(conn, user_id) if responses else [], **ctx)

    @app.get("/m/{user_id}/cases/{case_id}", response_class=HTMLResponse)
    def chatbot_case(request: Request, user_id: str, case_id: str):
        case = conn.execute("SELECT * FROM CARE_CASE WHERE case_id = ? AND user_id = ? AND case_source = 'Chatbot'",
                            (case_id, user_id)).fetchone()
        if case is None:
            raise HTTPException(404, "Unknown case")
        question = conn.execute("SELECT * FROM CHAT_MESSAGE WHERE message_id = ?", (case["chat_message_id"],)).fetchone()
        return status_page(request, user_id, case, 0, question=question)

    @app.get("/m/{user_id}/my-reports", response_class=HTMLResponse)
    def my_reports_page(request: Request, user_id: str, status: str = "", type: str = ""):
        st = status if status in status_mod.STEPS else None
        ty = type if type in my_reports.TYPES else None
        return page(request, "my_reports.html", user=mother(user_id), rows=my_reports.list_rows(conn, user_id, st, ty),
                    active_status=st or "All", active_type=ty or "All", statuses=status_mod.STEPS, types=my_reports.TYPES)

    from .cli import routes as cli_routes
    cli_routes.register(app, conn)
    from .acc import routes as acc_routes
    acc_routes.register(app, conn)
    from .hlt import routes as hlt_routes
    hlt_routes.register(app, conn)
    from .tml import routes as tml_routes
    tml_routes.register(app, conn)
    from .bot import routes as bot_routes
    bot_routes.register(app, conn)
    return app


app = create_app(dbmod.build())
