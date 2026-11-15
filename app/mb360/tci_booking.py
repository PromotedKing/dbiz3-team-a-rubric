"""Appointment storage and routes for the simulated TCI host."""
import hashlib
import hmac
import json
import secrets
import sqlite3
import uuid
from datetime import datetime, time, timedelta

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from . import clock, tci_feed
from .acc import entry

TABLE = tci_feed.APPOINTMENTS
FACILITY = "Bệnh viện Thu Cúc"
SPECIALTY = "Sản khoa"
FEE = 300_000  # Illustrative only
STAMP = "%Y-%m-%d %H:%M"
START, END = time(7), time(20)
DDL = f"""CREATE TABLE IF NOT EXISTS {TABLE} (
    appointment_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, facility TEXT NOT NULL,
    doctor_id TEXT, specialty TEXT NOT NULL, reason TEXT NOT NULL, appointment_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Pending','Confirmed','Cancelled','Completed')),
    estimated_fee INTEGER, reminder_at TEXT, reminder_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL, cancelled_at TEXT, visit_id TEXT UNIQUE
)"""


def same_day_slot(now):
    """Keep the 16:00 example in the morning and the appointment in hours."""
    preferred = now.replace(hour=16, minute=0, second=0, microsecond=0)
    close = now.replace(hour=20, minute=0, second=0, microsecond=0)
    return min(close, max(preferred, now + timedelta(hours=1)))


def install(conn, now):
    conn.execute(DDL)
    for visit in conn.execute("SELECT visit_id,user_id,visit_date,facility,visit_type FROM VISIT"):
        at = f"{visit['visit_date']} 09:00"
        conn.execute(f"""INSERT OR IGNORE INTO {TABLE}
                        (appointment_id,user_id,facility,specialty,reason,appointment_at,status,created_at,visit_id)
                        VALUES (?,?,?,?,?,?,'Completed',?,?)""",
                     (str(uuid.uuid5(uuid.NAMESPACE_URL, f"tci-visit/{visit['visit_id']}")), visit["user_id"],
                      visit["facility"], SPECIALTY, visit["visit_type"], at, at, visit["visit_id"]))
    for row in conn.execute(f"SELECT * FROM {tci_feed.TABLE} WHERE next_appointment IS NOT NULL"):
        at = row["next_appointment"]
        # Lan's historical feed entry already has a completed VISIT.
        if conn.execute("SELECT 1 FROM VISIT WHERE user_id=? AND visit_date=?",
                        (row["user_id"], at[:10])).fetchone() and at < now.strftime(STAMP):
            continue
        doctor = conn.execute("""SELECT doctor_id FROM PATIENT_ASSIGNMENT WHERE user_id=? AND valid_from<=?
                                 AND (valid_to IS NULL OR valid_to>=?) ORDER BY valid_from DESC LIMIT 1""",
                              (row["user_id"], at[:10], at[:10])).fetchone()
        conn.execute(f"""INSERT OR IGNORE INTO {TABLE}
                        (appointment_id,user_id,facility,doctor_id,specialty,reason,appointment_at,status,created_at,reminder_at,reminder_enabled)
                        VALUES (?,?,?,?,?,?,?,'Confirmed',?,?,1)""",
                     (str(uuid.uuid5(uuid.NAMESPACE_URL, f"tci-upcoming/{row['user_id']}")), row["user_id"],
                      row["appointment_place"], doctor[0] if doctor else None, SPECIALTY, "Khám thai", at, now.strftime(STAMP),
                      (datetime.fromisoformat(at).date() - timedelta(days=1)).isoformat() + " 00:00"))
    conn.commit()


def register(app, conn, page):
    key = secrets.token_bytes(32)

    def remember(response, user):
        response.set_cookie("tci_demo_account", f"{user}.{signed(user)}", httponly=True,
                            samesite="lax", secure=entry.SECURE_COOKIE)
        return response

    def account(request):
        cookie = request.cookies.get("tci_demo_account", "")
        user, _, signature = cookie.partition(".")
        if user and hmac.compare_digest(signed(user), signature):
            row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id=?", (user,)).fetchone()
            if row is not None:
                return row
        return tci_feed.host_account(conn)

    def owner(request):
        user = account(request)
        if user is None:
            raise HTTPException(403, "Chưa có tài khoản TCI.")
        return user

    def doctors():
        return conn.execute("SELECT staff_id,full_name FROM STAFF WHERE role='Doctor' ORDER BY full_name").fetchall()

    def validate(data, now):
        try:
            when = datetime.strptime(f"{data['day']} {data['time']}", STAMP)
        except (KeyError, ValueError):
            raise HTTPException(422, "Chọn ngày và giờ khám hợp lệ.")
        if when <= now or (when.date() - now.date()).days > 30 or not START <= when.time() <= END:
            raise HTTPException(422, "Chọn giờ tương lai trong 07:00–20:00 và trong vòng 30 ngày.")
        reason = str(data.get("reason", "")).strip()
        if not reason or len(reason) > 200 or data.get("facility") != FACILITY or data.get("specialty") != SPECIALTY:
            raise HTTPException(422, "Kiểm tra cơ sở, chuyên khoa và lý do khám.")
        choices = doctors()
        if data.get("mode") == "specialty" and choices:
            doctor = choices[0]
        elif data.get("mode") == "doctor":
            doctor = next((row for row in choices if row["staff_id"] == data.get("doctor")), None)
        else:
            doctor = None
        if doctor is None:
            raise HTTPException(422, "Chọn bác sĩ hợp lệ.")
        return when, reason, doctor

    def signed(payload):
        return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()

    def return_path(request, user):
        uid = user["user_id"]
        token = request.cookies.get(entry.COOKIE)
        expected = signed(f"mb360-return/{uid}/{token}")
        if entry.valid_session(conn, token, uid, clock.now()) and hmac.compare_digest(
            request.cookies.get("tci_mb360_return", ""), expected
        ):
            return f"/m/{uid}/appointments"
        return None

    @app.get("/tci/appointments")
    def appointments(request: Request, tab: str = "current", source: str = ""):
        if source == "mb360":
            token = request.cookies.get(entry.COOKIE)
            session_user = conn.execute("SELECT user_id FROM SESSION WHERE session_token=?", (token,)).fetchone()
            if session_user and entry.valid_session(conn, token, session_user[0], clock.now()):
                uid = session_user[0]
                response = remember(RedirectResponse("/tci/appointments", status_code=303), uid)
                response.set_cookie("tci_mb360_return", signed(f"mb360-return/{uid}/{token}"),
                                    httponly=True, samesite="lax", secure=entry.SECURE_COOKIE)
                return response
        user = owner(request)
        current, past = tci_feed.appointments(conn, user["user_id"], clock.now())
        history = tab == "history"
        return page(request, "tci_appointments.html", rows=past if history else current,
                    history=history, account=user, return_path=return_path(request, user))

    @app.get("/tci/booking")
    def booking(request: Request, source: str = ""):
        user = owner(request)
        token = request.cookies.get(entry.COOKIE)
        session_user = conn.execute("SELECT user_id FROM SESSION WHERE session_token=?", (token,)).fetchone()
        handoff = source == "mb360" and session_user and entry.valid_session(conn, token, session_user[0], clock.now())
        if handoff:
            user = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id=?", (session_user[0],)).fetchone()
        response = page(request, "tci_booking.html", account=user, doctors=doctors(), facility=FACILITY,
                        specialty=SPECIALTY, fee=FEE, today=clock.now().date())
        if handoff:
            remember(response, user["user_id"])
            response.set_cookie("tci_mb360_return", signed(f"mb360-return/{user['user_id']}/{token}"),
                                httponly=True, samesite="lax", secure=entry.SECURE_COOKIE)
        return response

    @app.post("/tci/booking")
    async def preview(request: Request):
        user = owner(request)
        data = dict(await request.form())
        when, reason, doctor = validate(data, clock.now())
        payload = json.dumps({"form": data, "user": user["user_id"], "id": str(uuid.uuid4())})
        return page(request, "tci_booking_confirm.html", account=user, payload=payload, signature=signed(payload),
                    when=when, doctor=doctor, reason=reason, facility=FACILITY, specialty=SPECIALTY, fee=FEE,
                    reminder_day=max(clock.now(), when - timedelta(days=1)).date(),
                    reminder_time=max(clock.now(), when - timedelta(days=1)).strftime("%H:%M"))

    @app.post("/tci/booking/confirm")
    async def confirm(request: Request):
        user = owner(request)["user_id"]
        form = await request.form()
        payload = str(form.get("payload", ""))
        if not hmac.compare_digest(signed(payload), str(form.get("signature", ""))):
            raise HTTPException(400, "Xác nhận đặt lịch không hợp lệ.")
        draft = json.loads(payload)
        if draft["user"] != user:
            raise HTTPException(403, "Lịch hẹn không thuộc tài khoản hiện tại.")
        now = clock.now()
        conn.execute(DDL)
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(f"SELECT 1 FROM {TABLE} WHERE appointment_id=?", (draft["id"],)).fetchone():
                return RedirectResponse("/tci/appointments", status_code=303)
            when, reason, doctor = validate(draft["form"], now)
            at = when.strftime(STAMP)
            if conn.execute(f"""SELECT 1 FROM {TABLE} WHERE appointment_at=? AND status IN ('Pending','Confirmed')
                                AND (user_id=? OR doctor_id=?)""", (at, user, doctor["staff_id"])).fetchone():
                raise HTTPException(409, "Mẹ hoặc bác sĩ đã có lịch vào giờ này.")
            reminder_at = None
            enabled = form.get("reminder_enabled") == "on"
            if enabled:
                try:
                    reminder = datetime.strptime(f"{form.get('reminder_day')} {form.get('reminder_time')}", STAMP)
                except ValueError:
                    raise HTTPException(422, "Chọn ngày và giờ nhắc hợp lệ.")
                if not now <= reminder < when:
                    raise HTTPException(422, "Giờ nhắc phải từ hiện tại đến trước lịch khám.")
                reminder_at = reminder.strftime(STAMP)
            conn.execute(f"""INSERT INTO {TABLE} (appointment_id,user_id,facility,doctor_id,specialty,reason,
                             appointment_at,status,estimated_fee,reminder_at,reminder_enabled,created_at)
                             VALUES (?,?,?,?,?,?,?,'Confirmed',?,?,?,?)""",
                         (draft["id"], user, FACILITY, doctor["staff_id"], SPECIALTY, reason, at,
                          FEE, reminder_at, enabled, now.strftime(STAMP)))
        return RedirectResponse("/tci/appointments", status_code=303)

    @app.post("/tci/appointments/{appointment_id}/cancel")
    def cancel(request: Request, appointment_id: str):
        user = owner(request)["user_id"]
        now = clock.now().strftime(STAMP)
        with conn:
            exists = conn.execute("SELECT 1 FROM sqlite_master WHERE name=? AND type='table'", (TABLE,)).fetchone()
            if not exists or not conn.execute(f"SELECT 1 FROM {TABLE} WHERE appointment_id=? AND user_id=?",
                                              (appointment_id, user)).fetchone():
                raise HTTPException(404, "Không tìm thấy lịch hẹn.")
            changed = conn.execute(f"""UPDATE {TABLE} SET status='Cancelled',cancelled_at=?
                                    WHERE appointment_id=? AND user_id=? AND visit_id IS NULL
                                    AND status IN ('Pending','Confirmed') AND appointment_at>?""",
                                   (now, appointment_id, user, now))
            if not changed.rowcount:
                raise HTTPException(409, "Chỉ hủy được lịch tương lai chưa khám.")
        return RedirectResponse("/tci/appointments?tab=history", status_code=303)

    return account, remember
