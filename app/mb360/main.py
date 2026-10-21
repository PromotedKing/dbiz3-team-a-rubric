"""Mother & Baby 360 — routes of specs/001-alr-core/contracts/http-routes.md (ALR US-1)."""
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from . import clock
from . import db as dbmod
from .alr import cases, my_reports, reports, routing, status, thresholds, validation
from .alr import status as status_mod

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
# On-screen symptom wording (docs/ui-label-reference.md, D-73); stored values stay as in the schema.
SYMPTOM_LABELS = {
    "Waters breaking or fluid leakage": "Waters breaking / fluid leakage",
    "Severe headache, dizziness or blurred vision": "Severe headache / dizziness / blurred vision",
}
GLUCOSE_LABELS = {"fasting": "Fasting", "post_1h": "1 h after meal", "post_2h": "2 h after meal"}


def show_time(text: str | None) -> str:
    """D-27: dd/mm/yyyy · HH:mm."""
    return datetime.strptime(text, reports.DB_TIME).strftime("%d/%m/%Y · %H:%M") if text else ""


TEMPLATES.env.filters["show_time"] = show_time
TEMPLATES.env.filters["symptom_label"] = lambda s: SYMPTOM_LABELS.get(s, s)


def create_app(conn: sqlite3.Connection) -> FastAPI:
    app = FastAPI(title="Mother & Baby 360")

    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

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
        return page(request, "report_form.html", status, user=user, metric=metric, metrics=list(flags), flag=flags.get(metric),
                    card=card, form=form, errors=errors, symptoms=validation.SYMPTOMS, glucose_labels=GLUCOSE_LABELS,
                    urine_scale=thresholds.URINE_SCALE)

    @app.get("/", response_class=HTMLResponse)
    def select_mother(request: Request):
        mothers = conn.execute("SELECT user_id, full_name, record_code FROM USER_ACCOUNT ORDER BY full_name").fetchall()
        return page(request, "select_mother.html", mothers=mothers)

    @app.get("/m/{user_id}/instructions", response_class=HTMLResponse)
    def doctor_instructions(request: Request, user_id: str, submitted: int = 0):
        return page(request, "instructions.html", user=mother(user_id), flags=instructions(user_id), submitted=submitted)

    @app.get("/m/{user_id}/report", response_class=HTMLResponse)
    def new_report(request: Request, user_id: str, metric: str = "Symptom", glucose_context: str = ""):
        form = {"metric": metric, "glucose_context": glucose_context, "symptoms": [],
                "measured_at": clock.now().strftime(validation.FORM_TIME)}
        return report_form(request, mother(user_id), metric, form, {})

    @app.post("/m/{user_id}/report")
    async def submit_report(request: Request, user_id: str):
        user = mother(user_id)
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
        return page(request, "metric_alert.html", user=mother(user_id), rep=rep, hmr=hmr, card=card, guidance=guidance)

    @app.get("/m/{user_id}/reports/{report_id}", response_class=HTMLResponse)
    def report_status(request: Request, user_id: str, report_id: str, submitted: int = 0):
        rep, hmr, syms, case = load_report(user_id, report_id)
        label = (thresholds.evaluate(conn, hmr["metric"], hmr["value"], hmr["glucose_context"]) if hmr else thresholds.NOT_ASSESSED)
        return status_page(request, user_id, case, submitted, rep=rep, hmr=hmr, symptoms=syms, label=label)

    def status_page(request: Request, user_id: str, case, submitted: int, **ctx):
        """S-026 (ALR US-2): progress, responses or Safety note (BR-011, BR-012)."""
        cid = case["case_id"] if case else None
        return page(request, "report_status.html", user=mother(user_id), case=case, submitted=submitted,
                    steps=status.progress(conn, cid) if cid else [], responses=status.responses(conn, cid) if cid else [],
                    safety_note=status.show_safety_note(conn, cid) if cid else False, **ctx)

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
    return app


app = create_app(dbmod.build())
