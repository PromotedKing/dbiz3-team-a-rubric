#!/usr/bin/env python3
"""Seed generator for Mother & Baby 360 — writes data/seed/NN_{TABLE}.csv and data/seed/seed-report.md.

Deterministic: no random numbers, fixed clock (NOW = 2026-09-27 10:00); a re-run writes the same bytes, so
`git status` stays clean (Session 6 test T2).

Run from the repository root (Windows: python instead of python3; `uv run` works the same way):
    python3 data/seed/generate_seed.py            # run every check, then (re)write the seed files
    python3 data/seed/generate_seed.py --check    # run every check, write nothing, confirm the files equal a fresh run
    python3 data/seed/generate_seed.py --db FILE  # also write a loaded SQLite database to FILE (keep it outside the repo)

Reads data/schema/schema-MB360.sql (column order, keys, CHECK constraints). Before writing it
  1. checks the business rules used as data constraints (ALR BR-004, BR-008, BR-016, BR-017; ACC BR-004;
     BOT BR-002 / D-34; D-37 and the CLI permission table; D-46; D-68; DM-08, DM-21, DM-28, DM-39, DM-41), and
  2. creates the schema in an in-memory SQLite database and loads every file in filename order with
     foreign keys on — the same test as gate G3. Any failure stops the script and nothing is written.
Clinical thresholds come only from ALR §5.2 BR-004 (D-14; D-15 = Pending SME). Standard library only.
"""
import csv, io, os, re, sys, uuid, sqlite3
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))               # data/seed/
ROOT = os.path.dirname(os.path.dirname(HERE))                    # repository root
SCHEMA = os.path.join(ROOT, 'data', 'schema', 'schema-MB360.sql')
OUT = HERE
REPORT = os.path.join(HERE, 'seed-report.md')
ARGS = sys.argv[1:]
CHECK_ONLY = '--check' in ARGS
DB_OUT = ARGS[ARGS.index('--db') + 1] if '--db' in ARGS else None
with open(SCHEMA, encoding='utf-8') as _f:
    SCHEMA_SQL = _f.read()
NOW = datetime(2026, 9, 27, 10, 0)
NS = uuid.UUID('6f1c2d3e-0000-4000-8000-000000000364')
LABEL = {}                     # uuid -> readable label (seed report only)


def uid(label):
    """Deterministic UUID derived from a readable label (every id column is UUID in §6)."""
    v = str(uuid.uuid5(NS, label))
    LABEL[v] = label
    return v


def dt(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M')


def iso(x):
    if x is None:
        return ''
    if isinstance(x, bool):
        return '1' if x else '0'
    if isinstance(x, datetime):
        return x.strftime('%Y-%m-%d %H:%M')
    if isinstance(x, date):
        return x.isoformat()
    return str(x)


def week_at(edd, when):
    """Completed gestational weeks at `when` (week 40 = due date). Seed assumption: 280-day pregnancy."""
    d = when.date() if isinstance(when, datetime) else when
    return (280 - (edd - d).days) // 7


def text_of_len(prefix, n):
    s = prefix
    while len(s) < n:
        s += ' sample text'
    return s[:n]


T = defaultdict(list)
KIND = defaultdict(list)


def add(table, _kind, _note='', **row):
    T[table].append(row)
    KIND[table].append((row, _kind, _note))


# ---- STAFF (S01 / S02 keep the placeholder names drawn in the wireframes)
S = {k: uid('staff-' + k) for k in ['S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07']}
for k, kind, note, name, role, login in [
    ('S01', 'ordinary', 'nurse drawn on S-061 / S-026 (wireframe placeholder name)', 'Trần Thị B', 'Nurse', 'nurse.tranthib'),
    ('S02', 'ordinary', 'doctor drawn on S-064 / S-009 (wireframe placeholder name)', 'Nguyễn Văn A', 'Doctor', 'dr.nguyenvana'),
    ('S03', 'ordinary', '', 'Lê Thị Hạnh', 'Nurse', 'nurse.lethihanh'),
    ('S04', 'ordinary', '', 'Phạm Quốc Dũng', 'Doctor', 'dr.phamquocdung'),
    ('S05', 'ordinary', '', 'Hoàng Thị Yến', 'Nurse', 'nurse.hoangthiyen'),
    ('S06', 'boundary', 'full_name and login_account exactly 100 characters (VARCHAR(100))', text_of_len('Nguyễn Thị Minh Châu', 100), 'Nurse', text_of_len('nurse.long', 100)),
    ('S07', 'exceptional', 'doctor with no assigned mother: no case is escalated to him (CLI §10 Q10)', 'Vũ Minh Hải', 'Doctor', 'dr.vuminhhai'),
]:
    add('STAFF', kind, note, staff_id=S[k], full_name=name, role=role, login_account=login)
STAFF_ROLE = {r['staff_id']: r['role'] for r in T['STAFF']}

# ---- USER_ACCOUNT (mothers only — DM-02 default)
U = {k: uid('user-' + k) for k in ['U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07', 'U08', 'U09', 'U10']}
# date of birth and sex are copies of the TCI account (D-71); only female accounts open the sub-app (ACC BR-007)
DOB = {'U01': date(1996, 4, 12), 'U02': date(1993, 8, 3), 'U03': date(1998, 11, 20), 'U04': date(1990, 2, 14), 'U05': date(1995, 6, 30), 'U06': date(1986, 1, 9), 'U07': date(2001, 10, 5), 'U08': date(1999, 3, 22), 'U09': date(1992, 12, 1), 'U10': date(1997, 7, 18)}
for k, kind, note, ref, name, phone, code in [
    ('U01', 'ordinary', 'Ms. Lan — wireframe data on S-103 / S-064 / S-029', 'tci-000123', 'Nguyễn Thị Lan', '0900000101', 'TC-00123'),
    ('U02', 'ordinary', '', 'tci-000124', 'Trần Thu Hà', '0900000102', 'TC-00124'),
    ('U03', 'ordinary', '', 'tci-000125', 'Lê Minh Anh', '0900000103', 'TC-00125'),
    ('U04', 'ordinary', '', 'tci-000126', 'Phạm Ngọc Mai', '0900000104', 'TC-00126'),
    ('U05', 'ordinary', '', 'tci-000127', 'Vũ Thị Hoa', '0900000105', 'TC-00127'),
    ('U06', 'boundary', 'phone exactly 20 characters (VARCHAR(20)); gestational week 42', 'tci-000128', 'Đỗ Thị Hương', '+84 (0)900 000 1060', 'TC-00128'),
    ('U07', 'empty', 'new mother: consented, no pregnancy set up, no record code', 'tci-000129', 'Hoàng Thu Trang', '0900000107', None),
    ('U08', 'exceptional', 'tapped "Later" first (nothing saved — ACC BR-004), agreed on 25/09/2026; session expired (S-043)', 'tci-000130', 'Bùi Thị Ngọc', '0900000108', 'TC-00130'),
    ('U09', 'ordinary', 'blood pressure report of exactly 140/90', 'tci-000131', 'Ngô Thị Thảo', '0900000109', 'TC-00131'),
    ('U10', 'ordinary', '', 'tci-000132', 'Đặng Thu Phương', '0900000110', 'TC-00132'),
]:
    add('USER_ACCOUNT', kind, note, user_id=U[k], tci_account_ref=ref, full_name=name, phone=phone,
        date_of_birth=DOB[k], sex='Female', record_code=code, role='Mother')
NAME = {r['user_id']: r['full_name'] for r in T['USER_ACCOUNT']}

# ---- SESSION (role is always Mother — ACC §6)
CONSENT = {}
for k, kind, note, when, acc, perm, ver in [
    ('U01', 'ordinary', '', dt('2026-06-10 19:00'), True, True, 'v1.0'),
    ('U02', 'ordinary', '', dt('2026-05-02 08:10'), True, True, 'v1.0'),
    ('U03', 'ordinary', '', dt('2026-07-01 21:05'), True, True, 'v1.0'),
    ('U04', 'ordinary', '', dt('2026-05-20 10:00'), True, True, 'v1.0'),
    ('U05', 'ordinary', '', dt('2026-06-01 07:45'), True, True, 'v1.0'),
    ('U06', 'boundary', 'consent in the same minute as the first session; terms_version exactly 20 characters', dt('2026-02-01 09:00'), True, True, text_of_len('v1.0-2026-02', 20)),
    ('U07', 'ordinary', 'new mother — S-001 state 2', dt('2026-09-27 09:30'), True, True, 'v1.0'),
    ('U08', 'ordinary', 'first consent; the earlier "Later" on 20/09/2026 saved nothing (ACC BR-004)', dt('2026-09-25 08:00'), True, True, 'v1.0'),
    ('U02', 'exceptional', 'second consent row for the same mother, after a new terms version — only if terms versions are managed (ACC §10 Q17)', dt('2026-09-01 07:00'), True, True, 'v1.1'),
    ('U09', 'ordinary', '', dt('2026-08-01 20:00'), True, True, 'v1.0'),
    ('U10', 'empty', 'terms_version empty (ACC §10 Q17)', dt('2026-03-01 06:30'), True, True, None),
]:
    add('CONSENT_RECORD', kind, note, user_id=U[k], accepted_at=when, accepted=acc, terms_version=ver, tci_data_permission=perm)
    if acc:
        CONSENT.setdefault(k, when)

for k, kind, note, created, exp in [
    ('U01', 'ordinary', '', dt('2026-09-27 08:00'), dt('2026-09-27 20:00')),
    ('U02', 'ordinary', '', dt('2026-09-27 09:00'), dt('2026-09-27 21:00')),
    ('U03', 'ordinary', '', dt('2026-09-27 08:30'), dt('2026-09-27 20:30')),
    ('U04', 'ordinary', '', dt('2026-09-26 18:00'), dt('2026-09-27 06:00')),
    ('U05', 'ordinary', '', dt('2026-09-26 07:20'), dt('2026-09-26 19:20')),
    ('U06', 'boundary', 'expires_at = NOW', dt('2026-02-01 09:00'), NOW),
    ('U07', 'empty', 'no optional column in SESSION; shortest possible lifetime not decided (ACC §10 Q9) — 1 minute used', dt('2026-09-27 09:31'), dt('2026-09-27 09:32')),
    ('U08', 'exceptional', 'session expired → S-043; closing the sub-app sets expires_at (DM-19)', dt('2026-09-25 08:01'), dt('2026-09-25 08:40')),
    ('U09', 'ordinary', '', dt('2026-09-26 21:00'), dt('2026-09-27 09:00')),
    ('U10', 'ordinary', '', dt('2026-09-26 12:00'), dt('2026-09-27 00:00')),
]:
    add('SESSION', kind, note, session_token='sess-' + k.lower() + '-' + created.strftime('%m%d%H%M'), user_id=U[k], role='Mother',
        created_at=created, expires_at=exp)

# ---- EDD / PREGNANCY_PROFILE
EDD = {'U01': date(2026, 12, 20), 'U02': date(2026, 11, 15), 'U03': date(2027, 1, 10), 'U04': date(2026, 11, 29),
       'U05': date(2026, 12, 5), 'U06': date(2026, 9, 13), 'U08': date(2027, 3, 1), 'U09': date(2027, 2, 14),
       'U10': date(2026, 10, 25)}
# first antenatal check-up entered at setup (D-72); later visits stay hospital seed data (D-59)
FIRST_VISIT = {'U01': date(2026, 5, 10), 'U02': date(2026, 3, 28), 'U03': date(2026, 5, 30), 'U04': None, 'U05': date(2026, 4, 5), 'U06': date(2026, 1, 20), 'U08': None, 'U09': date(2026, 7, 15), 'U10': date(2026, 3, 10)}
for k, kind, note, lmp, src, h in [
    ('U01', 'exceptional', 'edd_source = Hospital record, set only in seed (ACC BR-003, DM-23)', date(2026, 3, 15), 'Hospital record', 158.0),
    ('U02', 'ordinary', '', None, 'Self-entered', 162.0),
    ('U03', 'ordinary', '', date(2026, 4, 5), 'Self-entered', 155.0),
    ('U04', 'ordinary', '', None, 'Self-entered', 160.0),
    ('U05', 'ordinary', '', None, 'Self-entered', 165.5),
    ('U06', 'boundary', 'gestational week 42 at NOW — upper bound of 0–42', date(2025, 12, 7), 'Self-entered', 150.0),
    ('U08', 'empty', 'no LMP, no height, no first visit date', None, 'Self-entered', None),
    ('U09', 'ordinary', '', None, 'Self-entered', 157.0),
    ('U10', 'ordinary', '', None, 'Self-entered', 163.0),
]:
    add('PREGNANCY_PROFILE', kind, note, user_id=U[k], edd=EDD[k], lmp=lmp, edd_source=src,
        height_cm=None if h is None else f'{h:.1f}', first_visit_date=FIRST_VISIT[k])

# ---- EMR_LINKAGE_REQUEST (every row is seed data — DM-23)
for k, kind, note, req, status, linked in [
    ('U01', 'ordinary', 'S-103: Linked', dt('2026-09-19 10:00'), 'Linked', dt('2026-09-20 09:00')),
    ('U02', 'ordinary', '', dt('2026-05-02 08:20'), 'Linked', dt('2026-05-03 09:00')),
    ('U03', 'ordinary', '', dt('2026-07-01 21:10'), 'Linked', dt('2026-07-02 08:00')),
    ('U04', 'ordinary', '', dt('2026-05-20 10:05'), 'Linked', dt('2026-05-21 14:00')),
    ('U05', 'ordinary', '', dt('2026-06-01 07:50'), 'Linked', dt('2026-06-02 10:30')),
    ('U06', 'boundary', 'linked_at = requested_at', dt('2026-02-01 09:05'), 'Linked', dt('2026-02-01 09:05')),
    ('U08', 'exceptional', 'two requests for one mother; the older one stays Pending (no error state — ACC §6)', dt('2026-09-10 11:00'), 'Pending', None),
    ('U08', 'ordinary', 'second request', dt('2026-09-25 08:05'), 'Linked', dt('2026-09-25 09:00')),
    ('U09', 'empty', 'Pending link: linked_at empty', dt('2026-09-24 20:00'), 'Pending', None),
    ('U10', 'ordinary', '', dt('2026-03-01 06:40'), 'Linked', dt('2026-03-02 08:00')),
]:
    code = next(r['record_code'] for r in T['USER_ACCOUNT'] if r['user_id'] == U[k])
    add('EMR_LINKAGE_REQUEST', kind, note, user_id=U[k], record_code=code, facility='Thu Cuc Hospital', status=status,
        requested_at=req, linked_at=linked)

# ---- PATIENT_ASSIGNMENT
for k, doc, kind, note, f, t in [
    ('U01', 'S02', 'ordinary', '', date(2026, 6, 10), None),
    ('U02', 'S02', 'ordinary', '', date(2026, 5, 3), None),
    ('U03', 'S04', 'ordinary', '', date(2026, 7, 2), None),
    ('U04', 'S02', 'ordinary', '', date(2026, 5, 21), None),
    ('U05', 'S02', 'exceptional', 'change of responsible doctor: old row ended', date(2026, 6, 2), date(2026, 8, 31)),
    ('U05', 'S04', 'ordinary', 'change of responsible doctor: new row', date(2026, 9, 1), None),
    ('U06', 'S04', 'boundary', 'valid_to = today', date(2026, 2, 1), date(2026, 9, 27)),
    ('U09', 'S04', 'ordinary', '', date(2026, 8, 1), None),
    ('U10', 'S02', 'empty', 'valid_to empty = still active', date(2026, 3, 2), None),
]:
    add('PATIENT_ASSIGNMENT', kind, note, user_id=U[k], doctor_id=S[doc], valid_from=f, valid_to=t)

# ---- GUIDANCE_TEMPLATE (content is a placeholder; the hospital supplies the real text — D-24)
G = {k: uid('tpl-' + k) for k in ['G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08']}
for k, kind, note, title, metric, dflt, by in [
    ('G01', 'ordinary', 'hospital default template (BR-013), loaded from seed', 'Default above-threshold guidance', None, True, None),
    ('G02', 'ordinary', '', 'Blood pressure guidance', 'Blood pressure', False, 'S02'),
    ('G03', 'ordinary', '', 'Blood glucose guidance', 'Blood glucose', False, 'S02'),
    ('G04', 'ordinary', '', 'Urine protein guidance', 'Urine protein', False, 'S04'),
    ('G05', 'ordinary', '', 'Follow-up visit', None, False, 'S04'),
    ('G08', 'exceptional', 'written by a nurse — who may write templates is not stated (DM-10)', 'Rest and measure again', 'Blood pressure', False, 'S03'),
    ('G06', 'empty', 'no metric, no author', 'Contact the hospital', None, False, None),
    ('G07', 'boundary', 'content exactly 1000 characters (D-46); title exactly 100', text_of_len('Please submit the report again', 100), None, False, 'S04'),
]:
    content = text_of_len('[Placeholder — to be supplied by the hospital]', 1000) if kind == 'boundary' else f'[Placeholder — to be supplied by the hospital] {title}'
    add('GUIDANCE_TEMPLATE', kind, note, template_id=G[k], title=title, content=content, is_default=dflt, metric=metric,
        created_by=S[by] if by else None)

# ---- THRESHOLD_RULE (only ALR §5.2 BR-004)
for k, kind, note, metric, ctx, comp, comb, op, val, unit, purpose, src, conf in [
    ('TR-01', 'ordinary', 'D-14 systolic row', 'Blood pressure', None, 'systolic', 'any', '≥', '140', 'mmHg', 'Report check', 'MVP v8', 'Confirmed'),
    ('TR-02', 'ordinary', 'D-14 diastolic row', 'Blood pressure', None, 'diastolic', 'any', '≥', '90', 'mmHg', 'Report check', 'MVP v8', 'Confirmed'),
    ('TR-03', 'ordinary', 'D-15 Pending SME', 'Blood glucose', 'fasting', None, None, '≥', '5.3', 'mmol/L', 'Report check', 'ADA – Ministry of Health', 'Pending SME'),
    ('TR-04', 'ordinary', 'D-15 Pending SME', 'Blood glucose', 'post_1h', None, None, '≥', '7.8', 'mmol/L', 'Report check', 'ADA – Ministry of Health', 'Pending SME'),
    ('TR-05', 'ordinary', 'D-15 Pending SME', 'Blood glucose', 'post_2h', None, None, '≥', '6.7', 'mmol/L', 'Report check', 'ADA – Ministry of Health', 'Pending SME'),
    ('TR-06', 'empty', 'D-15 Pending SME; glucose_context, component, combine empty (single row, not glucose)', 'Urine protein', None, None, None, '≥', '1+', '—', 'Report check', 'ADA – Ministry of Health', 'Pending SME'),
    ('TR-07', 'exceptional', 'fetal heart rate: display-only reference range, never checked (D-12, HLT BR-005)', 'Fetal heart rate', None, None, None, 'outside range', '110–160', 'bpm', 'Display only', 'MVP v8', 'Confirmed'),
]:
    add('THRESHOLD_RULE', kind, note, rule_id=uid('rule-' + k), metric=metric, glucose_context=ctx, component=comp, combine=comb,
        operator=op, threshold_values=val, unit=unit, purpose=purpose, source=src, confirmation_status=conf, effective_from=date(2026, 9, 1))

PROTEIN = ['Negative', 'Trace', '1+', '2+', '3+']


def over_threshold(metric, value, ctx):
    """ALR BR-004 evaluated from THRESHOLD_RULE rows with purpose = Report check."""
    rows = [r for r in T['THRESHOLD_RULE'] if r['metric'] == metric and r['purpose'] == 'Report check'
            and (r['glucose_context'] or None) == (ctx or None)]
    assert rows, f'no threshold rule for {metric} {ctx}'
    if metric == 'Blood pressure':
        parts = dict(zip(('systolic', 'diastolic'), map(int, value.split('/'))))
        assert {x['combine'] for x in rows} == {'any'} and len(rows) == 2
        return any(parts[x['component']] >= int(x['threshold_values']) for x in rows)
    r = rows[0]
    if metric == 'Blood glucose':
        return float(value) >= float(r['threshold_values'])
    return PROTEIN.index(value) >= PROTEIN.index(r['threshold_values'])


# ---- VISIT (seed data — D-59)
V, VD = {}, {}
for k, u, kind, note, d, vtype, concl, dnote, img, fl, efw, usd in [
    ('VIS-001', 'U01', 'ordinary', 'latest visit 15/09/2026 (S-064, S-023)', dt('2026-09-15 09:00'), 'Routine antenatal check-up', 'Fetal growth consistent with gestational age', 'Sample doctor note', None, None, None, None),
    ('VIS-002', 'U01', 'ordinary', 'anomaly scan with ultrasound results (S-048)', dt('2026-08-18 14:00'), 'Anomaly scan', 'Fetal anatomy within normal limits', 'Sample doctor note', 'us/VIS-002.jpg', '27.0', '480.0', date(2026, 8, 18)),
    ('VIS-003', 'U02', 'ordinary', '', dt('2026-09-10 08:30'), 'Routine antenatal check-up', 'Fetal growth consistent with gestational age', 'Sample doctor note', None, None, None, None),
    ('VIS-004', 'U03', 'ordinary', '', dt('2026-09-05 10:00'), 'Routine antenatal check-up', 'Fetal growth consistent with gestational age', 'Sample doctor note', None, None, None, None),
    ('VIS-005', 'U04', 'exceptional', 'fetal heart rate 172 bpm outside 110–160: display only, no case (D-12)', dt('2026-09-12 15:00'), 'Routine antenatal check-up', 'Further monitoring', 'Sample doctor note', None, None, None, None),
    ('VIS-006', 'U05', 'ordinary', '', dt('2026-09-08 09:30'), 'Routine antenatal check-up', 'Fetal growth consistent with gestational age', 'Sample doctor note', None, None, None, None),
    ('VIS-007', 'U06', 'boundary', 'visit at week 42 (upper bound of INTEGER 0–42); fetal length 9999.9 = largest DECIMAL(5,1)', dt('2026-09-27 08:00'), 'Routine antenatal check-up', 'As prescribed by the doctor', 'Sample doctor note', 'us/VIS-007.jpg', '9999.9', '3400.0', date(2026, 9, 27)),
    ('VIS-008', 'U10', 'empty', 'all optional columns empty', dt('2026-09-20 09:00'), 'Routine antenatal check-up', None, None, None, None, None, None),
]:
    V[k] = uid('visit-' + k)
    VD[V[k]] = (U[u], d)
    add('VISIT', kind, note, visit_id=V[k], user_id=U[u], visit_date=d.date(), facility='Thu Cuc Hospital', visit_type=vtype,
        conclusion=concl, doctor_note=dnote, ultrasound_image=img, fetal_length=fl, estimated_fetal_weight=efw,
        ultrasound_report_date=usd, gestational_week=week_at(EDD[u], d))

# ---- PATIENT_CLINICAL_PROFILE (seed data — D-59)
LATEST_VISIT = {'U01': 'VIS-001', 'U02': 'VIS-003', 'U03': 'VIS-004', 'U04': 'VIS-005', 'U05': 'VIS-006', 'U06': 'VIS-007', 'U10': 'VIS-008'}
for u, kind, note, para, blood, allergy in [
    ('U01', 'ordinary', 'S-064: PARA 1001, O+', '1001', 'O+', 'None known'),
    ('U02', 'ordinary', '', '0000', 'A+', 'None known'),
    ('U03', 'ordinary', '', '1001', 'B+', 'None known'),
    ('U04', 'ordinary', '', '2002', 'O+', 'Penicillin'),
    ('U05', 'ordinary', '', '0010', 'AB+', 'None known'),
    ('U06', 'boundary', 'obstetric_history exactly 10 characters (VARCHAR(10))', '2002-00-01', 'A−', 'None known'),
    ('U09', 'exceptional', 'rare blood type with the non-ASCII sign declared in §6 (DM-40); no visit yet', '0000', 'O−', 'Seafood'),
    ('U10', 'empty', 'blood type and allergies empty', '1001', None, None),
    ('U07', 'ordinary', 'blood type B− (enum coverage); no visit yet', '0000', 'B−', 'None known'),
    ('U08', 'ordinary', 'blood type AB− (enum coverage); no visit yet', '0000', 'AB−', 'None known'),
]:
    upd = VD[V[LATEST_VISIT[u]]][1] if u in LATEST_VISIT else dt('2026-08-01 09:00')
    add('PATIENT_CLINICAL_PROFILE', kind, note, user_id=U[u], obstetric_history=para, blood_type=blood, allergies=allergy, updated_at=upd)

# ---- WATCH_FLAG ("Doctor's instructions")
W = {k: uid('flag-' + k) for k in ['W01', 'W02', 'W03', 'W04', 'W05', 'W06', 'W07', 'W08', 'W09']}
LONG1000 = text_of_len('Guidance for this mother:', 1000)
for k, u, kind, note, visit, metric, by, at, n, tpl, custom, active in [
    ('W01', 'U01', 'ordinary', 'S-064 / S-027: Blood pressure, placed after the 15/09/2026 visit by Dr. Nguyễn Văn A', 'VIS-001', 'Blood pressure', 'S02', date(2026, 9, 15), 'Measure twice a day, morning and evening', 'G02', None, True),
    ('W02', 'U01', 'ordinary', 'S-008 #9: Blood glucose', 'VIS-001', 'Blood glucose', 'S02', date(2026, 9, 15), 'Measure fasting every morning', 'G03', 'State the measurement time', True),
    ('W03', 'U05', 'ordinary', '', 'VIS-006', 'Urine protein', 'S04', date(2026, 9, 8), 'Dipstick test every morning', 'G04', None, True),
    ('W04', 'U03', 'ordinary', '', 'VIS-004', 'Blood glucose', 'S04', date(2026, 9, 5), 'Measure after meals', 'G03', None, True),
    ('W05', 'U10', 'ordinary', '', 'VIS-008', 'Blood glucose', 'S02', date(2026, 9, 20), 'Measure 2 h after meals', None, 'Record the meal', True),
    ('W06', 'U02', 'boundary', 'custom_text exactly 1000 characters (D-46)', 'VIS-003', 'Blood pressure', 'S02', date(2026, 9, 10), 'Measure every evening', None, LONG1000, True),
    ('W07', 'U04', 'empty', 'no visit, no note, no template, no custom text → S-028 uses the default template (BR-013)', None, 'Blood pressure', 'S02', date(2026, 9, 12), None, None, None, True),
    ('W08', 'U05', 'exceptional', 'active = false: an earlier instruction the doctor switched off (DM-21)', None, 'Blood pressure', 'S04', date(2026, 9, 1), 'Measure every morning', 'G02', None, False),
    ('W09', 'U09', 'ordinary', 'blood-pressure instruction behind RPT-006 (ALR BR-006: only a flagged metric can be reported); no visit yet, placed by the responsible doctor', None, 'Blood pressure', 'S04', date(2026, 9, 20), 'Measure every evening', None, None, True),
]:
    add('WATCH_FLAG', kind, note, flag_id=W[k], user_id=U[u], visit_id=V[visit] if visit else None, metric=metric,
        flagged_by=S[by], flagged_at=at, note=n, template_id=G[tpl] if tpl else None, custom_text=custom, active=active)
FLAG_OF = {(r['user_id'], r['metric']): r['flag_id'] for r in T['WATCH_FLAG'] if r['active']}

# ---- HEALTH_METRIC_RECORD
H = {}
UNIT = {'Weight': 'kg', 'Temperature': '°C', 'Heart rate': 'bpm', 'Sleep': None, 'Blood pressure': 'mmHg',
        'Blood glucose': 'mmol/L', 'Urine protein': None, 'Fetal heart rate': 'bpm'}
GROUP = {'Weight': 'Group 1', 'Temperature': 'Group 1', 'Heart rate': 'Group 1', 'Sleep': 'Group 1',
         'Blood pressure': 'Group 2', 'Blood glucose': 'Group 2', 'Urine protein': 'Group 2', 'Fetal heart rate': 'Visit'}


def hmr(k, u, kind, note, metric, value, when, source, visit=None, ctx=None, created=None):
    H[k] = dict(id=uid('hmr-' + k), u=u, metric=metric, value=value, when=when, ctx=ctx)
    add('HEALTH_METRIC_RECORD', kind, note, record_id=H[k]['id'], user_id=U[u], metric=metric, metric_group=GROUP[metric],
        value=value, unit=UNIT[metric], glucose_context=ctx, measured_at=when, source=source,
        visit_id=V[visit] if visit else None, gestational_week=week_at(EDD[u], when), created_at=created or when)


hmr('H01', 'U01', 'ordinary', 'S-023 section 1 (From visit)', 'Blood pressure', '132/84', dt('2026-09-15 09:00'), 'From visit', 'VIS-001')
hmr('H02', 'U01', 'ordinary', 'fetal heart rate with the display-only 110–160 range', 'Fetal heart rate', '145', dt('2026-09-15 09:00'), 'From visit', 'VIS-001')
hmr('H03', 'U01', 'ordinary', '', 'Weight', '56.5', dt('2026-09-15 09:00'), 'From visit', 'VIS-001')
hmr('H04', 'U01', 'ordinary', '', 'Urine protein', 'Negative', dt('2026-09-15 09:00'), 'From visit', 'VIS-001')
hmr('H05', 'U04', 'exceptional', 'fetal heart rate 172 outside 110–160: display only, no case (D-12)', 'Fetal heart rate', '172', dt('2026-09-12 15:00'), 'From visit', 'VIS-005')
hmr('H06', 'U01', 'ordinary', 'weight entered on S-007, stored by ACC FR-005 (D-42)', 'Weight', '52.0', dt('2026-06-10 19:05'), 'Self-entered')
hmr('H07', 'U01', 'ordinary', 'S-008 #13', 'Temperature', '36.8', dt('2026-09-27 07:30'), 'Self-entered')
hmr('H08', 'U01', 'ordinary', 'sleep stored as one string (DM-22); unit empty', 'Sleep', '22:30-06:00', dt('2026-09-27 06:00'), 'Self-entered')
hmr('H09', 'U06', 'empty', 'glucose_context and visit_id empty', 'Heart rate', '88', dt('2026-09-26 20:00'), 'Self-entered')
hmr('H10', 'U01', 'ordinary', 'report value, Normal', 'Blood pressure', '128/82', dt('2026-09-25 07:10'), 'Doctor-assigned', created=dt('2026-09-25 07:12'))
hmr('H11', 'U01', 'ordinary', 'S-026 / S-064: 150/95 Above threshold', 'Blood pressure', '150/95', dt('2026-09-26 20:15'), 'Doctor-assigned', created=dt('2026-09-26 20:17'))
hmr('H12', 'U04', 'ordinary', '', 'Blood pressure', '145/92', dt('2026-09-26 18:02'), 'Doctor-assigned', created=dt('2026-09-26 18:05'))
hmr('H13', 'U05', 'ordinary', '', 'Urine protein', '2+', dt('2026-09-26 07:30'), 'Doctor-assigned', created=dt('2026-09-26 07:32'))
hmr('H14', 'U09', 'boundary', 'exactly 140/90 → Above threshold (≥, D-14); reported under instruction W09 → source Doctor-assigned', 'Blood pressure', '140/90', dt('2026-09-27 07:00'), 'Doctor-assigned', created=dt('2026-09-27 07:02'))
hmr('H15', 'U03', 'ordinary', '', 'Blood glucose', '4.9', dt('2026-09-26 06:45'), 'Doctor-assigned', ctx='fasting', created=dt('2026-09-26 06:47'))
hmr('H16', 'U10', 'boundary', 'exactly 6.7 two hours after a meal → Above threshold (D-15, Pending SME)', 'Blood glucose', '6.7', dt('2026-09-26 13:00'), 'Doctor-assigned', ctx='post_2h', created=dt('2026-09-26 13:05'))
hmr('H17', 'U01', 'ordinary', 'S-008 #12', 'Weight', '57.0', dt('2026-09-27 07:30'), 'Self-entered')
hmr('H18', 'U01', 'ordinary', 'S-008 #14', 'Heart rate', '82', dt('2026-09-27 07:30'), 'Self-entered')
hmr('H19', 'U03', 'ordinary', 'glucose 1 h after a meal, 7.2 < 7.8 → Normal (enum coverage: post_1h)', 'Blood glucose', '7.2', dt('2026-09-27 08:10'), 'Doctor-assigned', ctx='post_1h', created=dt('2026-09-27 08:12'))

# ---- METRIC_REPORT + REPORT_SYMPTOM
R = {}
LONG100 = text_of_len('Other:', 100)


def report(k, code, u, kind, note, rec, symptoms, submitted, other=None, mnote=None):
    R[k] = uid('report-' + k)
    metric = H[rec]['metric'] if rec else 'Symptom'
    flag = FLAG_OF.get((U[u], metric)) if rec else None
    add('METRIC_REPORT', kind, note, report_id=R[k], report_code=code, user_id=U[u], metric=metric,
        health_metric_record_id=H[rec]['id'] if rec else None, other_symptom_text=other, note=mnote,
        submitted_at=submitted, watch_flag_id=flag)
    for i, s in enumerate(symptoms):
        add('REPORT_SYMPTOM', 'ordinary', '', report_id=R[k], symptom=s)


report('RPT-001', 'BC-0925-008', 'U01', 'ordinary', 'Normal, no symptoms → "No action needed", no case (BR-008 branch 3, BR-009)', 'H10', ['No symptoms'], dt('2026-09-25 07:12'))
report('RPT-002', 'BC-0926-015', 'U01', 'ordinary', 'S-026 / S-064 / S-061 row 1', 'H11', ['Severe headache, dizziness or blurred vision', 'Other'], dt('2026-09-26 20:17'), other='Back ache worse in the afternoon', mnote='Measured a second time, still high')
report('RPT-003', 'BC-0927-021', 'U02', 'ordinary', 'symptom report, no health metric record (D-41) — S-061 row 2', None, ['Severe headache, dizziness or blurred vision', 'Palpitations'], dt('2026-09-27 09:05'))
report('RPT-004', 'BC-0926-011', 'U04', 'ordinary', 'S-061 row 4', 'H12', ['No symptoms'], dt('2026-09-26 18:05'))
report('RPT-005', 'BC-0926-004', 'U05', 'ordinary', 'S-061 row 5', 'H13', ['No symptoms'], dt('2026-09-26 07:32'))
report('RPT-006', 'BC-0927-020', 'U09', 'boundary', 'exactly 140/90; other_symptom_text exactly 100 characters', 'H14', ['Other'], dt('2026-09-27 07:02'), other=LONG100)
report('RPT-007', 'BC-0926-009', 'U03', 'empty', 'optional columns empty; Normal → no case', 'H15', ['No symptoms'], dt('2026-09-26 06:47'))
report('RPT-008', 'BC-0926-012', 'U10', 'exceptional', 'above threshold + 2 symptoms; the case skips a manual "Viewed" (recorded automatically — BR-016)', 'H16', ['Severe abdominal pain', 'Waters breaking or fluid leakage'], dt('2026-09-26 13:05'), mnote='Abdominal pain since noon')
report('RPT-009', 'BC-0927-003', 'U06', 'ordinary', 'symptom report at week 42', None, ['Vaginal bleeding', 'Absence of fetal movement'], dt('2026-09-27 06:30'))
report('RPT-011', 'BC-0927-023', 'U03', 'ordinary', 'Normal glucose 1 h after a meal, no symptoms → no case', 'H19', ['No symptoms'], dt('2026-09-27 08:12'))
report('RPT-010', 'BC-0927-022', 'U01', 'ordinary', 'S-029: Lan\'s symptom report 27/09/2026 09:05, "Not viewed"', None, ['Severe headache, dizziness or blurred vision'], dt('2026-09-27 09:05'))

# ---- CONVERSATION / CHAT_MESSAGE / AI_RESPONSE_LOG
CV = {}
for k, u, kind, note, week in [
    ('CV-001', 'U01', 'ordinary', '', 28), ('CV-002', 'U03', 'ordinary', 'risk question → Connect to nurse (S-061 row 3)', 25),
    ('CV-003', 'U02', 'ordinary', '', 33), ('CV-004', 'U04', 'ordinary', '', 31), ('CV-005', 'U05', 'ordinary', '', 30),
    ('CV-006', 'U06', 'boundary', 'question of exactly 500 characters', 42), ('CV-007', 'U07', 'empty', 'chatbot opened, no question sent; context empty', None),
    ('CV-008', 'U02', 'exceptional', 'risk question but the mother chose "No thanks"', 33),
    ('CV-009', 'U01', 'ordinary', 'S-029: Lan\'s chatbot case 27/09/2026 09:12, "Not viewed"', 28)]:
    CV[k] = uid('conv-' + k)
    ctx = None if week is None else '{"gestational_week": %d, "earlier_turns": 0}' % week
    add('CONVERSATION', kind, note, conversation_id=CV[k], user_id=U[u], current_session_data=ctx)
BOT_ANSWER = '[Sample chatbot answer] For reference only; does not replace your doctor\'s advice.'
HANDOFF = 'This needs a proper consultation. It will be sent to a nurse if you agree'  # BOT BR-002 verbatim
MSG = {}
for k, cv, kind, note, sender, text, intent, risk, handoff, at in [
    ('MSG-001', 'CV-001', 'ordinary', '', 'Mother', 'What should I eat at week 28?', '{"intent": "nutrition"}', False, None, dt('2026-09-27 08:10')),
    ('MSG-002', 'CV-001', 'ordinary', '', 'Chatbot', BOT_ANSWER, None, False, None, dt('2026-09-27 08:10')),
    ('MSG-003', 'CV-002', 'ordinary', 'opens a Chatbot case', 'Mother', 'I have had a headache since this morning, is that okay?', '{"intent": "personal_health"}', True, 'Connect to nurse', dt('2026-09-27 08:38')),
    ('MSG-004', 'CV-002', 'ordinary', 'hand-off offer instead of an answer (BOT BR-002)', 'Chatbot', HANDOFF, None, False, None, dt('2026-09-27 08:38')),
    ('MSG-005', 'CV-003', 'ordinary', '', 'Mother', 'How often should I have check-ups at week 33?', '{"intent": "visits"}', False, None, dt('2026-09-26 21:00')),
    ('MSG-006', 'CV-003', 'empty', 'parsed_intent and handoff_choice empty', 'Chatbot', BOT_ANSWER, None, False, None, dt('2026-09-26 21:00')),
    ('MSG-007', 'CV-006', 'boundary', 'exactly 500 characters (D-46)', 'Mother', text_of_len('I would like to ask:', 500), '{"intent": "other"}', False, None, dt('2026-09-26 22:00')),
    ('MSG-008', 'CV-008', 'exceptional', 'is_risk but handoff = No thanks → no case (BOT FR-009)', 'Mother', 'I noticed a little bleeding, do I need to see a doctor?', '{"intent": "personal_health"}', True, 'No thanks', dt('2026-09-27 09:20')),
    ('MSG-009', 'CV-004', 'ordinary', '', 'Mother', 'When should I measure my blood pressure?', '{"intent": "measuring"}', False, None, dt('2026-09-26 17:00')),
    ('MSG-010', 'CV-005', 'ordinary', '', 'Mother', 'How do I use a urine protein dipstick?', '{"intent": "measuring"}', False, None, dt('2026-09-26 06:00')),
    ('MSG-011', 'CV-008', 'ordinary', 'hand-off offer; the mother then chose "No thanks" on MSG-008', 'Chatbot', HANDOFF, None, False, None, dt('2026-09-27 09:20')),
    ('MSG-012', 'CV-004', 'ordinary', '', 'Chatbot', BOT_ANSWER, None, False, None, dt('2026-09-26 17:00')),
    ('MSG-013', 'CV-005', 'ordinary', '', 'Chatbot', BOT_ANSWER, None, False, None, dt('2026-09-26 06:00')),
    ('MSG-014', 'CV-006', 'ordinary', 'answer to the 500-character question', 'Chatbot', BOT_ANSWER, None, False, None, dt('2026-09-26 22:00')),
    ('MSG-015', 'CV-009', 'ordinary', 'S-029 chatbot card: "I have had a little bleeding since this morning…"', 'Mother', 'I have had a little bleeding since this morning, is that normal?', '{"intent": "personal_health"}', True, 'Connect to nurse', dt('2026-09-27 09:12')),
    ('MSG-016', 'CV-009', 'ordinary', 'hand-off offer', 'Chatbot', HANDOFF, None, False, None, dt('2026-09-27 09:12')),
]:
    MSG[k] = uid('msg-' + k)
    add('CHAT_MESSAGE', kind, note, message_id=MSG[k], conversation_id=CV[cv], sender=sender, text=text, parsed_intent=intent,
        is_risk=risk, handoff_choice=handoff, sent_at=at)
for k, cv, kind, note in [('LOG-001', 'CV-001', 'ordinary', ''), ('LOG-002', 'CV-002', 'ordinary', ''), ('LOG-003', 'CV-003', 'ordinary', ''),
                          ('LOG-004', 'CV-004', 'ordinary', ''), ('LOG-005', 'CV-005', 'ordinary', ''),
                          ('LOG-006', 'CV-006', 'boundary', 'answer to the 500-character question'),
                          ('LOG-007', 'CV-008', 'empty', 'audit_log_entry empty (no schema — DM-06)'),
                          ('LOG-008', 'CV-009', 'exceptional', 'log of a hand-off offer that became a case; no link to the message (DM-37)')]:
    add('AI_RESPONSE_LOG', kind, note, log_id=uid('log-' + k), conversation_id=CV[cv],
        ai_response_data=HANDOFF if cv in ('CV-002', 'CV-008', 'CV-009') else BOT_ANSWER,
        audit_log_entry=None if kind == 'empty' else '{"call": "' + k + '"}')

# ---- CARE_CASE + CASE_STATUS_HISTORY
C = {}


def care_case(k, u, kind, note, source, rpt, msg, history, doctor=None):
    C[k] = uid('case-' + k)
    created = history[0][1]
    last_status, last_at, last_by = history[-1]
    closed = last_status == 'Resolved'
    add('CARE_CASE', kind, note, case_id=C[k], user_id=U[u], case_source=source, status=last_status,
        metric_report_id=R[rpt] if rpt else None, chat_message_id=MSG[msg] if msg else None,
        assigned_doctor_id=S[doctor] if doctor else None, created_at=created,
        closed_at=last_at if closed else None, closed_by=S[last_by] if closed else None)
    for i, (st, at, by) in enumerate(history):
        add('CASE_STATUS_HISTORY', 'ordinary', '', case_id=C[k], status=st, changed_at=at,
            changed_by=S[by] if by else None, role=STAFF_ROLE[S[by]] if by else 'System')


care_case('C1', 'U01', 'ordinary', 'S-026 / S-061: Viewed 20:25 by Nurse Trần Thị B, escalation skipped, Resolved 20:40 (S-064 is the snapshot at 20:18, before handling)', 'Metric report', 'RPT-002', None,
          [('Not viewed', dt('2026-09-26 20:17'), None), ('Viewed', dt('2026-09-26 20:25'), 'S01'), ('Resolved', dt('2026-09-26 20:40'), 'S01')])
care_case('C2', 'U02', 'empty', 'Not viewed; optional columns empty (S-061 row 2)', 'Symptom', 'RPT-003', None, [('Not viewed', dt('2026-09-27 09:05'), None)])
care_case('C3', 'U03', 'ordinary', 'Chatbot case (D-34), Viewed (S-061 row 3)', 'Chatbot', None, 'MSG-003',
          [('Not viewed', dt('2026-09-27 08:40'), None), ('Viewed', dt('2026-09-27 09:10'), 'S03')])
care_case('C4', 'U04', 'ordinary', 'escalated to the responsible doctor (ALR FR-009; S-061 row 4)', 'Metric report', 'RPT-004', None,
          [('Not viewed', dt('2026-09-26 18:05'), None), ('Viewed', dt('2026-09-26 18:20'), 'S01'), ('Escalated to doctor', dt('2026-09-26 18:22'), 'S01')], doctor='S02')
care_case('C5', 'U05', 'ordinary', 'S-061 row 5', 'Metric report', 'RPT-005', None,
          [('Not viewed', dt('2026-09-26 07:32'), None), ('Viewed', dt('2026-09-26 07:50'), 'S03'), ('Resolved', dt('2026-09-26 08:30'), 'S03')])
care_case('C6', 'U09', 'boundary', 'opened by exactly 140/90', 'Metric report', 'RPT-006', None, [('Not viewed', dt('2026-09-27 07:02'), None)])
care_case('C7', 'U10', 'exceptional', 'nurse taps "Escalate to doctor" while Not viewed → Viewed recorded automatically, same person and time (BR-016); doctor closes (D-37)', 'Metric report', 'RPT-008', None,
          [('Not viewed', dt('2026-09-26 13:05'), None), ('Viewed', dt('2026-09-26 13:15'), 'S05'), ('Escalated to doctor', dt('2026-09-26 13:15'), 'S05'), ('Resolved', dt('2026-09-26 15:00'), 'S02')], doctor='S02')
care_case('C8', 'U06', 'ordinary', 'symptom case at week 42, handled and closed by a nurse', 'Symptom', 'RPT-009', None,
          [('Not viewed', dt('2026-09-27 06:30'), None), ('Viewed', dt('2026-09-27 06:45'), 'S05'), ('Resolved', dt('2026-09-27 07:30'), 'S05')])
care_case('C9', 'U01', 'ordinary', 'S-029: Lan\'s symptom report, "Not viewed"', 'Symptom', 'RPT-010', None, [('Not viewed', dt('2026-09-27 09:05'), None)])
care_case('C10', 'U01', 'ordinary', 'S-029: Lan\'s chatbot case, "Not viewed"', 'Chatbot', None, 'MSG-015', [('Not viewed', dt('2026-09-27 09:13'), None)])



def mark(table, kind, note, **match):
    """Give a child row its own kind (child rows do not inherit the parent's kind)."""
    hits = [i for i, (r, _, _) in enumerate(KIND[table]) if all(r[c] == v for c, v in match.items())]
    assert len(hits) == 1, (table, match)
    r = KIND[table][hits[0]][0]
    KIND[table][hits[0]] = (r, kind, note)


mark('REPORT_SYMPTOM', 'boundary', 'largest symptom set in the seed: 2 items including "Other" (RPT-002; the D-73 list merges headache and dizziness)', report_id=R['RPT-002'], symptom='Other')
mark('REPORT_SYMPTOM', 'exceptional', '"No symptoms" on an above-threshold report — the case is still opened (BR-008 branch 1, RPT-004)', report_id=R['RPT-004'], symptom='No symptoms')
mark('CASE_STATUS_HISTORY', 'empty', 'first row: written by the System, changed_by empty (ALR FR-021)', case_id=C['C2'], status='Not viewed')
mark('CASE_STATUS_HISTORY', 'boundary', '"Viewed" and "Escalated to doctor" in the same minute — Viewed recorded automatically (BR-016, C7)', case_id=C['C7'], status='Escalated to doctor')
mark('CASE_STATUS_HISTORY', 'exceptional', 'Resolved straight after Viewed: the optional "Escalated to doctor" step is skipped (BR-012; C1)', case_id=C['C1'], status='Resolved')

# ---- STAFF_RESPONSE
for k, case, kind, note, by, tpl, custom, at in [
    ('SR1', 'C1', 'ordinary', 'S-026 "Response from Nurse Trần Thị B"', 'S01', 'G02', None, dt('2026-09-26 20:38')),
    ('SR2', 'C5', 'ordinary', '', 'S03', None, 'Please send the dipstick result again tomorrow morning', dt('2026-09-26 08:25')),
    ('SR3', 'C4', 'ordinary', 'doctor sends guidance; status unchanged (BR-015)', 'S02', 'G05', None, dt('2026-09-26 19:00')),
    ('SR4', 'C7', 'ordinary', '', 'S02', 'G03', None, dt('2026-09-26 14:50')),
    ('SR5', 'C8', 'ordinary', '', 'S05', 'G05', None, dt('2026-09-27 07:25')),
    ('SR6', 'C3', 'boundary', 'custom_text exactly 1000 characters (D-46)', 'S03', None, LONG1000, dt('2026-09-27 09:15')),
    ('SR7', 'C5', 'empty', 'template only, custom_text empty', 'S03', 'G04', None, dt('2026-09-26 08:28')),
    ('SR8', 'C7', 'exceptional', 'default template plus custom text, sent by the nurse after escalation', 'S05', 'G01', 'Please rest and wait for the doctor to call you', dt('2026-09-26 13:20')),
]:
    add('STAFF_RESPONSE', kind, note, response_id=uid('resp-' + k), case_id=C[case], responder_id=S[by], responder_role=STAFF_ROLE[S[by]],
        template_id=G[tpl] if tpl else None, custom_text=custom, sent_at=at)

# ---- NOTIFICATION_PREFERENCE
for u, kind, note, a, b, c, d, upd in [
    ('U01', 'ordinary', 'every type on (S-009 shows an Instruction reminder)', True, True, True, True, dt('2026-09-15 10:00')),
    ('U02', 'ordinary', '', True, True, True, False, dt('2026-09-01 08:00')),
    ('U03', 'ordinary', '', True, True, True, False, dt('2026-09-01 08:00')),
    ('U04', 'ordinary', '', True, True, True, False, dt('2026-09-01 08:00')),
    ('U05', 'ordinary', '', True, True, True, False, dt('2026-09-01 08:00')),
    ('U06', 'boundary', 'every type off except "Report responses" (always on — proposal, ACC §10 Q13)', True, False, False, False, dt('2026-09-01 08:00')),
    ('U09', 'empty', 'no optional column; S-010 never opened — defaults written with the account (DM-41)', True, True, True, False, dt('2026-08-01 20:00')),
    ('U10', 'exceptional', 'appointment reminders off; instruction reminders on', True, True, False, True, dt('2026-09-20 21:00')),
    ('U07', 'ordinary', 'default values written by ACC FR-011 at consent (DM-41)', True, True, True, False, dt('2026-09-27 09:30')),
    ('U08', 'ordinary', 'default values written by ACC FR-011 at consent (DM-41)', True, True, True, False, dt('2026-09-25 08:00')),
]:
    add('NOTIFICATION_PREFERENCE', kind, note, user_id=U[u], report_response=a, new_visit_result=b, appointment_reminder=c,
        watch_flag_reminder=d, updated_at=upd)

# ---- NOTIFICATION (mothers only — DM-32 resolved: the notification to the doctor is not stored)
for k, kind, note, u, typ, title, sub, case, visit, flag, appt, at, read in [
    ('N01', 'ordinary', 'ALR FR-018 after the case is closed (S-009)', 'U01', 'Report', 'Report BC-0926-015 resolved', 'Response from Nurse Trần Thị B', 'C1', None, None, None, dt('2026-09-26 20:40'), dt('2026-09-26 21:00')),
    ('N02', 'ordinary', 'ALR FR-019 (S-009, S-008 #7)', 'U01', 'Visit result', 'New visit results available', 'Routine antenatal check-up 15/09/2026', None, 'VIS-001', None, None, dt('2026-09-15 11:00'), dt('2026-09-15 12:00')),
    ('N03', 'ordinary', 'APT FR-009; appointment reference in the TCI app (DM-04)', 'U01', 'Appointment', 'Appointment reminder', 'Routine antenatal check-up', None, None, None, 'TCI-APT-8841', dt('2026-09-26 09:00'), None),
    ('N04', 'ordinary', '', 'U04', 'Report', 'Report BC-0926-011 escalated to a doctor', None, 'C4', None, None, None, dt('2026-09-26 18:22'), None),
    ('N05', 'ordinary', '', 'U05', 'Report', 'Report BC-0926-004 resolved', None, 'C5', None, None, None, dt('2026-09-26 08:30'), dt('2026-09-26 09:00')),
    ('N06', 'exceptional', 'ALR FR-022 Instruction reminder — Should until ALR §10 Q20; S-009 #11a "Reminder: measure and report Blood pressure"', 'U01', 'Instruction reminder', 'Reminder: measure and report Blood pressure', 'Doctor\'s instructions · Dr. Nguyễn Văn A', None, None, 'W01', None, dt('2026-09-27 07:00'), dt('2026-09-27 07:05')),
    ('N07', 'ordinary', '', 'U03', 'Report', 'Your report has been viewed', 'Chatbot question', 'C3', None, None, None, dt('2026-09-27 09:10'), None),
    ('N08', 'boundary', 'read_at = created_at; title exactly 100 characters', 'U10', 'Report', text_of_len('Report BC-0926-012 resolved', 100), None, 'C7', None, None, None, dt('2026-09-26 15:00'), dt('2026-09-26 15:00')),
    ('N09', 'empty', 'subtitle, read_at and every target empty', 'U09', 'Report', 'Your report has been received', None, None, None, None, None, dt('2026-09-27 07:02'), None),
]:
    add('NOTIFICATION', kind, note, notification_id=uid('notif-' + k), user_id=U[u], type=typ, title=title, subtitle=sub,
        created_at=at, read_at=read, case_id=C[case] if case else None, visit_id=V[visit] if visit else None,
        watch_flag_id=W[flag] if flag else None, appointment_ref=appt)

# ---- DIARY_ENTRY / DIARY_IMAGE
DI = {}
for k, u, kind, note, text, mood, at in [
    ('DIA-001', 'U01', 'ordinary', '', 'The baby kicked a lot today.', 'Happy', dt('2026-09-27 08:00')),
    ('DIA-002', 'U01', 'ordinary', 'week 22 — anomaly scan', 'Anomaly scan today, a little nervous before the results.', 'Nervous', dt('2026-08-18 20:00')),
    ('DIA-003', 'U02', 'ordinary', '', 'Getting the newborn clothes ready.', 'Calm', dt('2026-09-20 21:00')),
    ('DIA-004', 'U03', 'ordinary', '', 'Bought more books for the baby.', 'Happy', dt('2026-09-22 19:30')),
    ('DIA-005', 'U04', 'ordinary', '', 'A bit tired after work.', 'Tired', dt('2026-09-26 22:00')),
    ('DIA-006', 'U06', 'boundary', 'week 42 and the full 5 photos (D-46)', 'We will meet you soon.', 'Worried', dt('2026-09-27 07:00')),
    ('DIA-007', 'U10', 'empty', 'no mood, no photos', 'Writing down an ordinary day.', None, dt('2026-09-24 21:00')),
    ('DIA-008', 'U01', 'exceptional', 'second entry on the same day (entry_date is a DATE)', 'Read a story to the baby this evening.', 'Calm', dt('2026-09-27 09:45')),
]:
    DI[k] = uid('diary-' + k)
    add('DIARY_ENTRY', kind, note, diary_id=DI[k], user_id=U[u], text=text, mood=mood, gestational_week=week_at(EDD[u], at), entry_date=at.date())
n = 0
for d, cnt, ext, kind, note in [('DIA-001', 1, 'jpg', 'ordinary', ''), ('DIA-002', 1, 'jpg', 'ordinary', ''), ('DIA-003', 2, 'jpg', 'ordinary', ''),
                                ('DIA-004', 1, 'jpg', 'ordinary', ''), ('DIA-005', 1, 'jpg', 'ordinary', ''), ('DIA-006', 5, 'jpg', 'boundary', '5 photos — maximum (D-46); sort_order 1–5'),
                                ('DIA-008', 1, 'png', 'exceptional', 'PNG photo (JPG / PNG allowed)')]:
    for i in range(1, cnt + 1):
        n += 1
        add('DIARY_IMAGE', kind if i == 1 else 'ordinary', note if i == 1 else '', image_id=uid(f'img-{n:03d}'), diary_id=DI[d],
            file=f'diary/{d}-{i}.{ext}', sort_order=i)

# ---- FAMILY_MESSAGE (implied user_id — DM-33)
LONG200 = text_of_len('Message:', 200)
for u, kind, note, week, author, text, at in [
    ('U01', 'ordinary', '', 28, 'Mother', 'Mom loves you so much.', dt('2026-09-27 08:05')),
    ('U01', 'ordinary', 'the father writes on the mother\'s device (BR-004)', 28, 'Father', 'Dad is counting the days until you arrive.', dt('2026-09-27 08:06')),
    ('U02', 'ordinary', '', 33, 'Mother', 'Be good, little one.', dt('2026-09-20 21:05')),
    ('U03', 'ordinary', '', 25, 'Father', 'Hello, my love.', dt('2026-09-22 19:35')),
    ('U04', 'ordinary', '', 31, 'Mother', 'Mom has your room ready.', dt('2026-09-26 22:05')),
    ('U06', 'boundary', 'exactly 200 characters (D-03, BR-004)', 42, 'Mother', LONG200, dt('2026-09-27 07:05')),
    ('U10', 'exceptional', 'message for a week other than the current one', 40, 'Father', 'For you, on the day you are born.', dt('2026-09-24 21:10')),
]:
    add('FAMILY_MESSAGE', kind, note, user_id=U[u], week=week, author=author, text=text, created_at=at)


# ============================================================================= checks
# The schema is the source of the column order, keys and CHECK constraints.
DBX = sqlite3.connect(':memory:')
DBX.executescript(SCHEMA_SQL)
LOAD_ORDER = [r[0] for r in DBX.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY rowid")]
COLS = {t: [r[1] for r in DBX.execute(f'PRAGMA table_info({t})')] for t in LOAD_ORDER}
PKS = {t: [r[1] for r in sorted(DBX.execute(f'PRAGMA table_info({t})'), key=lambda r: r[5]) if r[5]] for t in LOAD_ORDER}
FKS = {t: {r[3]: r[2] for r in DBX.execute(f'PRAGMA foreign_key_list({t})')} for t in LOAD_ORDER}
assert set(COLS) == set(T), f'tables differ: {set(COLS) ^ set(T)}'
for t, rows in T.items():
    for r in rows:
        assert list(r) == COLS[t], f'{t}: column order {list(r)} != schema {COLS[t]}'
    keys = [tuple(iso(r[c]) for c in PKS[t]) for r in rows]
    dup = [k for k, n in Counter(keys).items() if n > 1]
    assert not dup, f'{t}: duplicate PK {dup}'
errors = []
for t, rows in T.items():
    for c, parent in FKS[t].items():
        pcol = PKS[parent][0]
        pvals = {iso(r[pcol]) for r in T[parent]}
        for r in rows:
            if r[c] is not None and iso(r[c]) not in pvals:
                errors.append(f'FK {t}.{c}={r[c]} not in {parent}.{pcol}')
assert not errors, '\n'.join(errors)
for t, c, n in [('WATCH_FLAG', 'custom_text', 1000), ('STAFF_RESPONSE', 'custom_text', 1000), ('GUIDANCE_TEMPLATE', 'content', 1000)]:
    for r in T[t]:
        assert len(r[c] or '') <= n, f'D-46 {t}.{c}'
for r in T['CHAT_MESSAGE']:
    if r['sender'] == 'Mother':
        assert len(r['text']) <= 500, 'D-46 question length'
    else:
        assert r['parsed_intent'] is None and r['handoff_choice'] is None and not r['is_risk'], 'BOT §6: intent / hand-off only on the mother\'s questions'
for r in T['DIARY_IMAGE']:
    assert 1 <= r['sort_order'] <= 5 and r['file'].rsplit('.', 1)[1] in ('jpg', 'png')
assert max(Counter(r['diary_id'] for r in T['DIARY_IMAGE']).values()) <= 5, 'D-46'
for r in T['VISIT']:
    assert 0 <= r['gestational_week'] <= 42
for r in T['DIARY_ENTRY']:
    assert 0 <= r['gestational_week'] <= 42, 'gestational_week INTEGER 0–42 (04 type decision)'

# DM-08 / DM-41 / ACC BR-004: every account has >= 1 accepted consent and exactly one preference row
for u in T['USER_ACCOUNT']:
    cons = [c for c in T['CONSENT_RECORD'] if c['user_id'] == u['user_id']]
    assert cons and all(c['accepted'] for c in cons), 'DM-08 / ACC BR-004'
    assert sum(p['user_id'] == u['user_id'] for p in T['NOTIFICATION_PREFERENCE']) == 1, 'DM-41'
    first = min(c['accepted_at'] for c in cons)
    assert all(s['created_at'] >= first for s in T['SESSION'] if s['user_id'] == u['user_id']), 'session after consent'

# D-14 either value: systolic OR diastolic
assert over_threshold('Blood pressure', '132/92', None) and over_threshold('Blood pressure', '141/80', None)
assert not over_threshold('Blood pressure', '139/89', None) and over_threshold('Blood pressure', '140/90', None)

# BR-017 / D-41 / D-23
sym = defaultdict(list)
for r in T['REPORT_SYMPTOM']:
    sym[r['report_id']].append(r['symptom'])
hmr_by_id = {r['record_id']: r for r in T['HEALTH_METRIC_RECORD']}
case_by_report = {r['metric_report_id']: r for r in T['CARE_CASE'] if r['metric_report_id']}
for r in T['METRIC_REPORT']:
    s = sym[r['report_id']]
    assert s and not ('No symptoms' in s and len(s) > 1), 'BR-017'
    assert ('Other' in s) == bool(r['other_symptom_text']), 'Other text only with Other'
    assert (r['metric'] == 'Symptom') == (r['health_metric_record_id'] is None), 'D-41'
    over = False
    if r['health_metric_record_id']:
        h = hmr_by_id[r['health_metric_record_id']]
        assert h['user_id'] == r['user_id'] and h['metric'] == r['metric'] and h['measured_at'] <= r['submitted_at']
        assert h['created_at'] == r['submitted_at'], 'ALR FR-020 stores record and report together'
        over = over_threshold(r['metric'], h['value'], h['glucose_context'])
        assert h['source'] == ('Doctor-assigned' if r['watch_flag_id'] else 'Self-entered'), 'D-33 as revised'
        assert r['watch_flag_id'] == FLAG_OF.get((r['user_id'], r['metric'])) is not None, f'ALR BR-006 {r["report_code"]}: only a metric with an active instruction is reported'
    else:
        assert r['watch_flag_id'] is None, 'ALR §6: no instruction for a symptom report'
    c = case_by_report.get(r['report_id'])
    real_sym = any(x != 'No symptoms' for x in s)
    assert (c is not None) == (over or real_sym), f'BR-008 {r["report_code"]}'
    if c:
        assert c['case_source'] == ('Metric report' if over else 'Symptom')
        assert c['created_at'] == r['submitted_at'] and c['user_id'] == r['user_id'], 'DM-39'

# chatbot (BOT BR-002, D-34)
conv_user = {r['conversation_id']: r['user_id'] for r in T['CONVERSATION']}
for r in T['CHAT_MESSAGE']:
    opened = [c for c in T['CARE_CASE'] if c['chat_message_id'] == r['message_id']]
    assert bool(opened) == (r['handoff_choice'] == 'Connect to nurse'), 'D-34'
    assert r['handoff_choice'] is None or r['is_risk'], 'offer only for a risk question'
    if opened:
        assert opened[0]['created_at'] >= r['sent_at'] and opened[0]['user_id'] == conv_user[r['conversation_id']], 'DM-39'
    if r['sender'] == 'Mother':
        replies = [m for m in T['CHAT_MESSAGE'] if m['conversation_id'] == r['conversation_id'] and m['sender'] == 'Chatbot']
        assert len(replies) == 1 and replies[0]['sent_at'] >= r['sent_at'], 'one reply per question (DM-29 default)'
        assert (replies[0]['text'] == HANDOFF) == bool(r['is_risk']), 'BOT BR-002'
for c in T['CARE_CASE']:
    assert (c['metric_report_id'] is None) != (c['chat_message_id'] is None), 'exactly one origin'
    assert (c['case_source'] == 'Chatbot') == (c['chat_message_id'] is not None)

# BR-016 / D-43 / D-37 / DM-28
ORDER_ST = ['Not viewed', 'Viewed', 'Escalated to doctor', 'Resolved']
hist = defaultdict(list)
for h in T['CASE_STATUS_HISTORY']:
    hist[h['case_id']].append(h)
for c in T['CARE_CASE']:
    hs = hist[c['case_id']]
    idx = [ORDER_ST.index(h['status']) for h in hs]
    assert idx[0] == 0 and all(a < b for a, b in zip(idx, idx[1:])), 'BR-016 forward only, each status once'
    assert len(idx) == 1 or idx[1] == 1, 'BR-016: Viewed is recorded before later steps'
    assert all(a['changed_at'] <= b['changed_at'] for a, b in zip(hs, hs[1:]))
    assert hs[0]['role'] == 'System' and hs[0]['changed_by'] is None, 'ALR FR-021: System writes Not viewed'
    assert all(h['changed_by'] and h['role'] == STAFF_ROLE[h['changed_by']] for h in hs[1:]), 'DM-39'
    assert hs[-1]['status'] == c['status'] and hs[0]['changed_at'] == c['created_at'], 'DM-28'
    esc = [h for h in hs if h['status'] == 'Escalated to doctor']
    if esc:
        assert STAFF_ROLE[esc[0]['changed_by']] == 'Nurse' and c['assigned_doctor_id'], 'escalated by a nurse'
        day = esc[0]['changed_at'].date()
        active = [a for a in T['PATIENT_ASSIGNMENT'] if a['user_id'] == c['user_id'] and a['valid_from'] <= day and (a['valid_to'] is None or a['valid_to'] >= day)]
        assert active and active[0]['doctor_id'] == c['assigned_doctor_id'], 'assigned doctor = responsible doctor'
    else:
        assert c['assigned_doctor_id'] is None
    for h in hs[1:]:  # CLI permission table (D-29, D-37, D-43): nurse views / escalates; closing depends on escalation
        want = ('Doctor' if esc else 'Nurse') if h['status'] == 'Resolved' else 'Nurse'
        assert h['role'] == want, f'CLI BR-004 permission: {h["status"]} by {h["role"]}'
    if c['status'] == 'Resolved':
        assert c['closed_at'] == hs[-1]['changed_at'] and c['closed_by'] == hs[-1]['changed_by'], 'DM-28'
        if esc:
            assert STAFF_ROLE[c['closed_by']] == 'Doctor', 'D-37'
    else:
        assert c['closed_at'] is None and c['closed_by'] is None
case_by_id = {c['case_id']: c for c in T['CARE_CASE']}
for r in T['STAFF_RESPONSE']:
    assert r['template_id'] or r['custom_text'], 'ALR §6: template or text'
    assert r['sent_at'] >= case_by_id[r['case_id']]['created_at'] and r['responder_role'] == STAFF_ROLE[r['responder_id']]
    if r['responder_role'] == 'Doctor':  # CLI permission table: doctor sends guidance on escalated cases only
        esc = [h for h in hist[r['case_id']] if h['status'] == 'Escalated to doctor']
        assert esc and esc[0]['changed_at'] <= r['sent_at'], 'CLI BR-004 doctor guidance'
for r in T['WATCH_FLAG']:
    assert STAFF_ROLE[r['flagged_by']] == 'Doctor', 'D-29'
    if r['visit_id']:
        vu, vd = VD[r['visit_id']]
        assert vu == r['user_id'] and vd.date() <= r['flagged_at']
assert max(Counter((r['user_id'], r['metric']) for r in T['WATCH_FLAG'] if r['active']).values()) == 1, 'DM-21 default'
for r in T['GUIDANCE_TEMPLATE']:
    assert r['created_by'] is None or r['created_by'] in STAFF_ROLE
assert sum(r['is_default'] for r in T['GUIDANCE_TEMPLATE']) == 1, 'one default template (BR-013)'
for u in U.values():
    rows = sorted([a for a in T['PATIENT_ASSIGNMENT'] if a['user_id'] == u], key=lambda a: a['valid_from'])
    for a, b in zip(rows, rows[1:]):
        assert a['valid_to'] is not None and a['valid_to'] < b['valid_from'], 'CLI §6: one active assignment'
    for a in rows:
        assert STAFF_ROLE[a['doctor_id']] == 'Doctor'

# notifications
pref = {p['user_id']: p for p in T['NOTIFICATION_PREFERENCE']}
SWITCH = {'Report': 'report_response', 'Visit result': 'new_visit_result', 'Appointment': 'appointment_reminder', 'Instruction reminder': 'watch_flag_reminder'}
TARGET = {'Report': 'case_id', 'Visit result': 'visit_id', 'Appointment': 'appointment_ref', 'Instruction reminder': 'watch_flag_id'}
flag_by_id = {r['flag_id']: r for r in T['WATCH_FLAG']}
for r in T['NOTIFICATION']:
    targets = [c for c in ('case_id', 'visit_id', 'watch_flag_id', 'appointment_ref') if r[c] is not None]
    assert len(targets) <= 1 and (not targets or targets[0] == TARGET[r['type']]), 'one target matching the type'
    assert r['read_at'] is None or r['read_at'] >= r['created_at']
    p = pref.get(r['user_id'])
    assert p is None or p[SWITCH[r['type']]], 'ALR FR-018 / FR-019 / FR-022, APT FR-009: switch on'
    if r['case_id']:
        assert case_by_id[r['case_id']]['user_id'] == r['user_id']
    if r['watch_flag_id']:
        f = flag_by_id[r['watch_flag_id']]
        assert f['active'] and f['user_id'] == r['user_id'], 'ALR FR-022: active instruction of this mother'
    if r['visit_id']:
        assert VD[r['visit_id']][0] == r['user_id'] and VD[r['visit_id']][1] <= r['created_at']

# timestamps and other rules
for r in T['SESSION']:
    k = [kk for kk, v in U.items() if v == r['user_id']][0]
    assert r['created_at'] < r['expires_at'] and CONSENT[k] <= r['created_at'], 'ACC BR-004: session after consent'
for r in T['EMR_LINKAGE_REQUEST']:
    assert (r['status'] == 'Linked') == (r['linked_at'] is not None) and (r['linked_at'] is None or r['requested_at'] <= r['linked_at'])
for r in T['HEALTH_METRIC_RECORD']:
    assert r['measured_at'] <= r['created_at'] <= NOW and 0 <= r['gestational_week'] <= 42
    assert (r['source'] == 'From visit') == (r['visit_id'] is not None)
    assert r['metric_group'] == GROUP[r['metric']], 'DM-39: metric_group follows the metric'
    assert (r['metric'] == 'Fetal heart rate') <= (r['source'] == 'From visit'), 'HLT BR-005'
    assert (r['metric_group'] == 'Group 1') <= (r['source'] != 'Doctor-assigned'), 'HLT BR-003'
    if r['visit_id']:
        vu, vd = VD[r['visit_id']]
        assert vu == r['user_id'] and vd == r['measured_at']
    assert (r['metric'] == 'Blood glucose') == (r['glucose_context'] is not None)
for r in T['PREGNANCY_PROFILE']:
    assert 0 <= week_at(r['edd'], NOW) <= 42
    if r['first_visit_date']:
        assert r['edd'] - timedelta(days=280) <= r['first_visit_date'] <= NOW.date(), 'D-72: first visit inside the pregnancy, not in the future'
for r in T['USER_ACCOUNT']:
    assert r['sex'] == 'Female', 'ACC BR-007: only a female TCI account opens the sub-app'
    assert r['date_of_birth'] < NOW.date()
for r in T['DIARY_ENTRY']:
    assert r['entry_date'] <= NOW.date()
for r in T['FAMILY_MESSAGE']:
    assert len(r['text']) <= 200 and 0 <= r['week'] <= 42

# row kinds
NA = {
    'REPORT_SYMPTOM': {'empty': 'both columns are part of the primary key; BR-017 needs at least 1 item per report'},
    'DIARY_IMAGE': {'empty': 'every column is required'},
    'FAMILY_MESSAGE': {'empty': 'every column is required (TML §6)'},
    'STAFF': {'empty': 'every column is required (CLI §6)'},
    'THRESHOLD_RULE': {'boundary': 'the configuration holds only the 7 rows of ALR BR-004; boundary values are exercised in HEALTH_METRIC_RECORD (140/90, 6.7)'},
}
summary, gaps = [], []
for t in COLS:
    cnt = Counter(k for _, k, _ in KIND[t])
    for kind in ('ordinary', 'boundary', 'empty', 'exceptional'):
        need = 5 if kind == 'ordinary' else 1
        if cnt[kind] < need and kind not in NA.get(t, {}):
            gaps.append(f'{t}: {kind} rows {cnt[kind]} < {need}')
    summary.append((t, cnt))
assert not gaps, '\n'.join(gaps)


# ============================================================================= write
FILES, FILE_OF = {}, {}
for i, t in enumerate(LOAD_ORDER, 1):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(COLS[t])
    for r in sorted(T[t], key=lambda r: tuple(iso(r[c]) for c in PKS[t])):
        w.writerow([iso(r[c]) for c in COLS[t]])
    name = f'{i:02d}_{t}.csv'
    FILE_OF[t] = name
    FILES[os.path.join(OUT, name)] = buf.getvalue()


def load_into(con):
    """Gate G3: create the schema, then load every seed file in filename order with foreign keys on."""
    con.executescript(SCHEMA_SQL)
    con.execute('PRAGMA foreign_keys = ON')
    for path in sorted(p for p in FILES if p.endswith('.csv')):
        table = re.match(r'\d\d_([A-Z_]+)\.csv$', os.path.basename(path)).group(1)
        rows = list(csv.reader(io.StringIO(FILES[path])))
        head, data = rows[0], rows[1:]
        sql = f'INSERT INTO {table} ({", ".join(head)}) VALUES ({", ".join("?" * len(head))})'
        con.executemany(sql, [[None if v == '' else v for v in row] for row in data])
    con.commit()
    bad = con.execute('PRAGMA foreign_key_check').fetchall()
    assert not bad, f'foreign key errors: {bad[:5]}'
    return {t: con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in LOAD_ORDER}


LOADED = load_into(sqlite3.connect(':memory:'))
assert LOADED == {t: len(T[t]) for t in LOAD_ORDER}, 'row counts after load'


def pk_text(t, r):
    return ' / '.join(LABEL.get(iso(r[c]), iso(r[c]))[:40] for c in PKS[t])


lines = ['# Seed report', '',
         'Generated by `data/seed/generate_seed.py` — do not edit by hand. `python3 data/seed/generate_seed.py --check` confirms that the files on disk equal a fresh run, without writing. All checks, including the load test below, run before any file is written.', '',
         f'Fixed clock: {iso(NOW)}; no random numbers. Dates are ISO (`YYYY-MM-DD`, `YYYY-MM-DD HH:MM`), UTF-8, LF, rows sorted by primary key; an empty cell is NULL; BOOLEAN is `1` / `0`. '
         'Every id column is a UUID derived from a readable label (U01, C1, RPT-002 …) with uuid5; the labels are used below. '
         '**Seed assumption, not a decided rule:** gestational week = whole weeks counted back from the EDD with a 280-day pregnancy (`spec-ACC.md` §10 Q10 is open).', '',
         'S01 and S02 keep the placeholder names drawn in the wireframes ("Trần Thị B", "Nguyễn Văn A"); every other person is invented. Phone numbers follow the fictitious pattern 0900 000 1xx. Guidance templates and chatbot answers are placeholders, not clinical content; the hand-off offer quotes BOT BR-002. Thresholds come only from ALR BR-004 (D-14; D-15 Pending SME).', '',
         'The rows follow the wireframes: Lan (U01) has 2 reports being handled — C9 (symptom) and C10 (chatbot), both "Not viewed" (S-008, S-023, S-029); her 26/09 report C1 is "Resolved" (S-026, S-061); S-064 shows C1 at 20:18, before the nurse handled it.', '',
         '## Load test (gate G3)', '',
         f'The schema `data/schema/schema-MB360.sql` was created in an empty SQLite 3 in-memory database (the version is not written, so the report is the same on every machine) and the {len(LOAD_ORDER)} files were loaded in filename order with `PRAGMA foreign_keys = ON`: no constraint error, `PRAGMA foreign_key_check` empty, {sum(LOADED.values())} rows.', '',
         '| File | Table | Rows |', '|---|---|---|']
lines += [f'| `{FILE_OF[t]}` | {t} | {LOADED[t]} |' for t in LOAD_ORDER]
lines += ['', '## Row kinds per table', '', '| Table | Rows | ordinary | boundary | empty | exceptional | Not applicable (reason) |', '|---|---|---|---|---|---|---|']
for t, cnt in summary:
    na = '; '.join(f'{k}: {v}' for k, v in NA.get(t, {}).items()) or '—'
    lines.append(f'| {t} | {len(T[t])} | {cnt["ordinary"]} | {cnt["boundary"]} | {cnt["empty"]} | {cnt["exceptional"]} | {na} |')
lines.append(f'| **Total** | {sum(len(v) for v in T.values())} | | | | | |')
lines += ['', '## Non-ordinary rows', '', '| Table | Kind | Row (primary key) | Why |', '|---|---|---|---|']
for t in COLS:
    for r, kind, note in KIND[t]:
        if kind != 'ordinary':
            lines.append(f'| {t} | {kind} | {pk_text(t, r)} | {note} |')
# ---- edge-case register (C4): enumerated values, empty states, boundaries, business rules
ENUM_NA = {('THRESHOLD_RULE', 'combine', 'all'): 'no rule in ALR BR-004 combines rows with "all"; a threshold is never invented to fill the value'}
lines += ['', '## Edge-case register', '', '### Every enumerated value', '',
          'One row per value of every ENUM column (parsed from the CHECK constraints of the schema).', '',
          '| Table | Column | Value | First row with it |', '|---|---|---|---|']
for t in LOAD_ORDER:
    ddl = DBX.execute("SELECT sql FROM sqlite_master WHERE name = ?", (t,)).fetchone()[0]
    for col, vals in re.findall(r"\n    (\w+) TEXT[^\n]*?CHECK \(\1 IN \(([^)]*)\)\)", ddl):
        for v in re.findall(r"'((?:[^']|'')*)'", vals):
            v = v.replace("''", "'")
            hit = next((r for r in T[t] if r[col] == v), None)
            if hit is None:
                why = ENUM_NA.get((t, col, v))
                assert why, f'enum value not seeded: {t}.{col} = {v}'
                lines.append(f'| {t} | `{col}` | {v} | not seeded — {why} |')
            else:
                lines.append(f'| {t} | `{col}` | {v} | {pk_text(t, hit)} |')
lines += ['', '### Empty states', '', '| Table | Row (primary key) | Empty state |', '|---|---|---|']
lines += [f'| {t} | {pk_text(t, r)} | {note} |' for t in LOAD_ORDER for r, kind, note in KIND[t] if kind == 'empty']
lines += ['', 'Parents with zero children: U07 has no pregnancy profile, visit, report, case or diary (new mother, S-007 shown next); CV-007 has no message; VIS-008 has no health metric record; DIA-007 has no photo; S07 has no assignment and no case.', '']
BOUNDS = [
    ('Blood pressure threshold ≥ 140 / ≥ 90 (D-14)', 'H14 = 140/90 → Above threshold → C6; control: H10 = 128/82 → Normal'),
    ('Glucose thresholds 5.3 / 7.8 / 6.7 mmol/L (D-15, Pending SME)', 'H16 = 6.7 two hours after a meal → Above threshold → C7; H15 = 4.9 fasting and H19 = 7.2 one hour after a meal → Normal'),
    ('Urine protein ≥ 1+ (D-15)', 'H13 = 2+ → C5; H04 = Negative (visit value, no check)'),
    ('Fetal heart rate 110–160 bpm, display only (D-12, HLT BR-005)', 'H05 = 172 → no report, no case'),
    ('Gestational week 0–42', 'U06 at week 42: VIS-007, DIA-006, FAMILY_MESSAGE week 42'),
    ('D-46 text limits 1000 / 500 / 200', 'W06 and SR6 custom_text = 1000; G07 content = 1000; MSG-007 = 500; FAMILY_MESSAGE of U06 = 200'),
    ('VARCHAR limits', 'U06 phone = 20; S06 full_name and login_account = 100; G07 title = 100; N08 title = 100; RPT-006 other_symptom_text = 100; U06 terms_version = 20; U06 obstetric_history = 10'),
    ('At most 5 photos per diary entry (D-46)', 'DIA-006 with sort_order 1 – 5'),
    ('Equal timestamps allowed', 'U06 consent and first session in the same minute; U06 EMR linked_at = requested_at; N08 read_at = created_at; C7 Viewed and Escalated in the same minute'),
    ('Date ranges', 'U06 assignment valid_to = today; U06 session expires_at = NOW; U05 change of responsible doctor (old row ended 31/08, new row from 01/09)'),
    ('DECIMAL(5,1)', 'VIS-007 fetal_length = 9999.9'),
]
lines += ['### Boundaries (numeric and date rules)', '', '| Rule | Rows |', '|---|---|'] + [f'| {a} | {b} |' for a, b in BOUNDS]
RULES = [
    ('ALR BR-008 branch 1 — above threshold → Metric report case', 'RPT-002 → C1, RPT-004 → C4, RPT-005 → C5, RPT-006 → C6, RPT-008 → C7'),
    ('ALR BR-008 branch 2 / BR-007 — symptoms only → Symptom case', 'RPT-003 → C2, RPT-009 → C8, RPT-010 → C9'),
    ('ALR BR-008 branch 3 / BR-009 — Normal, no symptoms → no case', 'RPT-001, RPT-007, RPT-011'),
    ('ALR BR-017 / D-45 — ≥ 1 symptom, "No symptoms" alone', 'RPT-002 (3 items), RPT-004 ("No symptoms" on an above-threshold report)'),
    ('ALR BR-012 — "Escalated to doctor" is optional', 'C1, C5, C8 (Viewed → Resolved)'),
    ('ALR BR-016 / D-43 — forward only; "Viewed" recorded automatically', 'C7 (Viewed and Escalated at 13:15 by the same nurse)'),
    ('ALR BR-015 / D-37 / CLI BR-001, BR-004 — who may close / send guidance', 'C7 closed by a doctor after escalation; C1, C5, C8 closed by a nurse; SR3, SR4 doctor guidance on escalated cases only'),
    ('ALR FR-021 — first history row written by the System', 'every CASE_STATUS_HISTORY "Not viewed" row (role System, changed_by empty)'),
    ('D-68 — escalated case goes to the active responsible doctor', 'C4 and C7 → S02 = active PATIENT_ASSIGNMENT of U04 / U10'),
    ('ALR BR-013 — default template when the instruction has no guidance', 'W07 (no template, no text) → G01 is_default'),
    ('ALR FR-022 — Instruction reminder only for an active instruction with the switch on', 'N06 → W01 (U01 watch_flag_reminder = 1)'),
    ('ALR FR-018 / FR-019 / APT FR-009 — notifications respect the switches', 'N01 – N09; U06 and U10 with switches off receive none of those types'),
    ('BOT BR-002 / D-34 — case only after "Connect to nurse"', 'MSG-003 → C3, MSG-015 → C10; MSG-008 "No thanks" → no case'),
    ('HLT BR-001 / BR-005 — visit values, fetal heart rate from visits only', 'H01 – H05 (source From visit, visit_id set)'),
    ('HLT BR-003 — Group 1 never checked, no report', 'H07, H08, H09, H17, H18 (no METRIC_REPORT)'),
    ('ACC BR-003 — hospital EDD takes priority', 'U01 edd_source = Hospital record'),
    ('ACC BR-004 / DM-08 — no consent saved on "Later"; account created at consent', 'U08: first CONSENT_RECORD on 25/09 only; every stored consent accepted = 1'),
    ('ACC BR-006 — setup shown when no due date', 'U07 (no PREGNANCY_PROFILE)'),
    ('DM-41 — one preference row per account', 'all 10 accounts, U07 and U08 with default values'),
    ('DM-21 — at most 1 active instruction per metric', 'W08 inactive next to W03 (U05)'),
    ('TML BR-004 / BR-005 / D-60 — messages ≤ 200, diary linked to the current week, read-only', 'FAMILY_MESSAGE of U06; DIA-001 – DIA-008 gestational_week = week at saving'),
]
lines += ['', '### Business rules', '', '| Rule | Rows that exercise it |', '|---|---|'] + [f'| {a} | {b} |' for a, b in RULES]
SCEN = [
    ('ACC US-1', 'First open and consent: U07 (CONSENT_RECORD, SESSION, no PREGNANCY_PROFILE); "Later" first (nothing saved), agreed later: U08', 'Yes'),
    ('ACC US-2', 'Pregnancy set-up; setup weight stored as HEALTH_METRIC_RECORD (D-42): U01 PREGNANCY_PROFILE, H06; week 42: U06', 'Yes'),
    ('ACC US-3', 'Profile and hospital record link (Linked / Pending): EMR_LINKAGE_REQUEST U01, U09, U08 × 2', 'Yes — Linked is seed data (DM-23)'),
    ('ACC FR-025 – FR-027', 'Notification list with 4 types, read / unread, settings: NOTIFICATION N01 – N09; NOTIFICATION_PREFERENCE U06, U10', 'Yes'),
    ('HLT US-1', 'Health metrics screen: latest visit, instructions, self-tracked metrics: U01 VIS-001, H01 – H04, W01 – W02, H07, H08, H17, H18', 'Yes'),
    ('HLT US-2', 'Enter Group 1 metrics: H07, H08, H09, H17, H18', 'Yes'),
    ('HLT US-3 / US-4', 'Doctor\'s instructions and one metric\'s history (U01 blood pressure): W01; H01, H10, H11', 'Yes'),
    ('ALR US-1 branch 3', 'Normal, no symptoms → no case (BR-008): RPT-001, RPT-007', 'Yes'),
    ('ALR US-1 branch 1', 'Above threshold → Metric report case: RPT-002 → C1; RPT-004 → C4; RPT-005 → C5; RPT-008 → C7', 'Yes'),
    ('ALR US-1 branch 2', 'Symptoms only → Symptom case: RPT-003 → C2; RPT-009 → C8; RPT-010 → C9', 'Yes'),
    ('ALR US-1 edge', 'Exactly on the threshold (≥): 140/90 RPT-006 → C6; 6.7 mmol/L RPT-008 → C7', 'Yes — D-15 values are Pending SME'),
    ('ALR US-2', 'Report status with a skipped "Escalated to doctor" and a response: C1 + history + SR1 + N01', 'Yes'),
    ('ALR FR-022', 'Instruction reminder for an active instruction with the switch on: N06 → W01', 'Yes — trigger / frequency open (ALR §10 Q20)'),
    ('BOT US-1', 'General question and answer: CV-001, MSG-001, MSG-002', 'Yes'),
    ('BOT US-2', 'Risk question → hand-off offer → Connect to nurse → Chatbot case: MSG-003 → C3; MSG-015 → C10', 'Yes'),
    ('BOT US-2 edge', 'Risk question, "No thanks" → no case: MSG-008, MSG-011', 'Yes'),
    ('CLI US-1', 'Nurse queue, mark Viewed, send guidance, close: C2, C6, C9, C10 (Not viewed); C3 (Viewed); C1, C5 (Resolved)', 'Yes'),
    ('CLI US-1 edge', 'Escalate while still Not viewed → Viewed recorded automatically (BR-016): C7', 'Yes'),
    ('CLI US-2', 'Doctor handles an escalated case and closes it: C4 (SR3, still escalated); C7 (SR4, closed by S02); a nurse closes a case that was not escalated: C1, C5, C8', 'Yes — the notification to the doctor is not stored by decision (DM-32); the doctor sees C4 / C7 through CARE_CASE.assigned_doctor_id'),
    ('CLI US-3', 'Doctor adds / edits instructions; no guidance → default template: W01 – W08; W07 → G01', 'Yes'),
    ('TML US-1 – US-3', 'Week view, diary with photos (max 5), Messages to Baby: DIA-001 – DIA-008, DIARY_IMAGE, FAMILY_MESSAGE; VIS-002 (week 22)', 'Yes'),
    ('APT', 'Upcoming appointment and reminder: N03 (`appointment_ref` only)', 'Partly — APPOINTMENT_RECORD is external (DM-04)'),
]
lines += ['', '## Scenario coverage', '', '| Scenario | Rows that make it runnable | Covered? |', '|---|---|---|']
lines += [f'| {a} | {b} | {c} |' for a, b, c in SCEN]
FILES[REPORT] = '\n'.join(lines) + '\n'
n_rows = sum(len(v) for v in T.values())


def read(path):
    try:
        with open(path, encoding='utf-8', newline='') as f:
            return f.read()
    except FileNotFoundError:
        return None


TABLE_CSV = re.compile(r'^\d\d_[A-Z][A-Z_]*\.csv$')
os.makedirs(OUT, exist_ok=True)
stale = sorted(f for f in os.listdir(OUT) if TABLE_CSV.match(f) and os.path.join(OUT, f) not in FILES)
if CHECK_ONLY:
    differ = sorted(os.path.relpath(p, ROOT) for p, text in FILES.items() if read(p) != text)
    if differ or stale:
        print('Checks passed, but the files on disk differ from a fresh run:')
        print('\n'.join([f'  differs: {d}' for d in differ] + [f'  not produced by the script: {e}' for e in stale]))
        sys.exit(1)
    print(f'OK — {len(T)} tables, {n_rows} rows; all checks passed; the {len(FILES)} files on disk are identical to a fresh run (nothing written)')
else:
    for old in stale:
        os.remove(os.path.join(OUT, old))
    for p, text in FILES.items():
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    print(f'OK — {len(T)} tables, {n_rows} rows; all checks passed; wrote {len(FILES) - 1} CSV files + seed-report.md')
