-- Schema: Mother & Baby 360 (MODULE-ID MB360 = modules ACC, HLT, ALR, TML, BOT, APT, CLI)
-- DBMS: SQLite 3 (3.38 or later: json_valid). Generated from data/data-model-MB360.md §6 and §9 — do not edit by hand.
-- Logical names follow spec §6; the mother's key is `user_id` in every table (DM-31).
-- Tables are created in foreign-key order, the same order as the seed files (data/seed/NN_{TABLE}.csv).
-- Foreign keys use the default NO ACTION: nothing is deleted in the MVP (DM-13, DM-26).

PRAGMA foreign_keys = ON;

CREATE TABLE STAFF (
    staff_id TEXT NOT NULL CHECK (length(staff_id) = 36),  -- UUID
    full_name VARCHAR(100) NOT NULL CHECK (length(full_name) <= 100),  -- VARCHAR(100)
    role TEXT NOT NULL CHECK (role IN ('Nurse', 'Doctor')),  -- ENUM (Nurse / Doctor)
    login_account VARCHAR(100) NOT NULL CHECK (length(login_account) <= 100),  -- VARCHAR(100) — provisional (CLI §10 Q11)
    PRIMARY KEY (staff_id),
    UNIQUE (login_account)
);

CREATE TABLE THRESHOLD_RULE (
    rule_id TEXT NOT NULL CHECK (length(rule_id) = 36),  -- UUID
    metric TEXT NOT NULL CHECK (metric IN ('Blood pressure', 'Blood glucose', 'Urine protein', 'Fetal heart rate')),  -- ENUM (Blood pressure / Blood glucose / Urine protein / Fetal heart rate)
    glucose_context TEXT CHECK (glucose_context IN ('fasting', 'post_1h', 'post_2h')),  -- ENUM (fasting / post_1h / post_2h)
    component TEXT CHECK (component IN ('systolic', 'diastolic')),  -- ENUM (systolic / diastolic)
    combine TEXT CHECK (combine IN ('any', 'all')),  -- ENUM (any / all)
    operator TEXT NOT NULL CHECK (operator IN ('≥', 'outside range')),  -- ENUM (≥ / outside range)
    threshold_values VARCHAR(20) NOT NULL CHECK (length(threshold_values) <= 20),  -- VARCHAR(20)
    unit VARCHAR(10) NOT NULL CHECK (length(unit) <= 10),  -- VARCHAR(10)
    purpose TEXT NOT NULL CHECK (purpose IN ('Report check', 'Display only')),  -- ENUM (Report check / Display only)
    source VARCHAR(100) NOT NULL CHECK (length(source) <= 100),  -- VARCHAR(100)
    confirmation_status TEXT NOT NULL CHECK (confirmation_status IN ('Confirmed', 'Pending SME')),  -- ENUM (Confirmed / Pending SME)
    effective_from TEXT NOT NULL CHECK (effective_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    PRIMARY KEY (rule_id)
);

CREATE TABLE USER_ACCOUNT (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    tci_account_ref VARCHAR(64) NOT NULL CHECK (length(tci_account_ref) <= 64),  -- VARCHAR(64)
    full_name VARCHAR(100) NOT NULL CHECK (length(full_name) <= 100),  -- VARCHAR(100)
    phone VARCHAR(20) NOT NULL CHECK (length(phone) <= 20),  -- VARCHAR(20)
    record_code VARCHAR(20) CHECK (length(record_code) <= 20),  -- VARCHAR(20)
    role TEXT NOT NULL CHECK (role IN ('Mother')),  -- ENUM (Mother)
    PRIMARY KEY (user_id),
    UNIQUE (tci_account_ref),
    UNIQUE (record_code)
);

CREATE TABLE CONSENT_RECORD (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    accepted_at TEXT NOT NULL CHECK (accepted_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    accepted INTEGER NOT NULL CHECK (accepted IN (0, 1)),  -- BOOLEAN
    terms_version VARCHAR(20) CHECK (length(terms_version) <= 20),  -- VARCHAR(20) — provisional (ACC §10 Q17)
    tci_data_permission INTEGER NOT NULL CHECK (tci_data_permission IN (0, 1)),  -- BOOLEAN
    PRIMARY KEY (user_id, accepted_at),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    CONSTRAINT ck_consent_accepted CHECK (accepted = 1)  -- ACC §5.2 BR-004; DM-08
);

CREATE TABLE CONVERSATION (
    conversation_id TEXT NOT NULL CHECK (length(conversation_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    current_session_data TEXT CHECK (json_valid(current_session_data)),  -- JSON
    PRIMARY KEY (conversation_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE DIARY_ENTRY (
    diary_id TEXT NOT NULL CHECK (length(diary_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    text TEXT NOT NULL,  -- TEXT — maximum length open (TML §10 Q9)
    mood TEXT CHECK (mood IN ('Happy', 'Calm', 'Nervous', 'Tired', 'Worried')),  -- ENUM (Happy / Calm / Nervous / Tired / Worried)
    gestational_week INTEGER NOT NULL CHECK (gestational_week BETWEEN 0 AND 42),  -- INTEGER 0–42
    entry_date TEXT NOT NULL CHECK (entry_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    PRIMARY KEY (diary_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE EMR_LINKAGE_REQUEST (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    record_code VARCHAR(20) NOT NULL CHECK (length(record_code) <= 20),  -- VARCHAR(20)
    facility VARCHAR(100) NOT NULL CHECK (length(facility) <= 100),  -- VARCHAR(100)
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Linked')),  -- ENUM (Pending / Linked)
    requested_at TEXT NOT NULL CHECK (requested_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    linked_at TEXT CHECK (linked_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (user_id, requested_at),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    CONSTRAINT ck_emr_linked_at CHECK ((status = 'Linked') = (linked_at IS NOT NULL))  -- ACC §6 EMR Linkage Request ("empty while Pending")
);

CREATE TABLE FAMILY_MESSAGE (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    week INTEGER NOT NULL CHECK (week BETWEEN 0 AND 42),  -- INTEGER 0–42
    author TEXT NOT NULL CHECK (author IN ('Mother', 'Father')),  -- ENUM (Mother / Father)
    text VARCHAR(200) NOT NULL CHECK (length(text) <= 200),  -- VARCHAR(200)
    created_at TEXT NOT NULL CHECK (created_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE GUIDANCE_TEMPLATE (
    template_id TEXT NOT NULL CHECK (length(template_id) = 36),  -- UUID
    title VARCHAR(100) NOT NULL CHECK (length(title) <= 100),  -- VARCHAR(100)
    content TEXT NOT NULL CHECK (length(content) <= 1000),  -- TEXT, ≤ 1000 characters
    is_default INTEGER NOT NULL CHECK (is_default IN (0, 1)),  -- BOOLEAN
    metric TEXT CHECK (metric IN ('Blood pressure', 'Blood glucose', 'Urine protein')),  -- ENUM (Blood pressure / Blood glucose / Urine protein)
    created_by TEXT CHECK (length(created_by) = 36),  -- UUID
    PRIMARY KEY (template_id),
    FOREIGN KEY (created_by) REFERENCES STAFF (staff_id)
);

CREATE TABLE NOTIFICATION_PREFERENCE (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    report_response INTEGER NOT NULL CHECK (report_response IN (0, 1)),  -- BOOLEAN
    new_visit_result INTEGER NOT NULL CHECK (new_visit_result IN (0, 1)),  -- BOOLEAN
    appointment_reminder INTEGER NOT NULL CHECK (appointment_reminder IN (0, 1)),  -- BOOLEAN
    watch_flag_reminder INTEGER NOT NULL CHECK (watch_flag_reminder IN (0, 1)),  -- BOOLEAN
    updated_at TEXT NOT NULL CHECK (updated_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE PATIENT_ASSIGNMENT (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    doctor_id TEXT NOT NULL CHECK (length(doctor_id) = 36),  -- UUID
    valid_from TEXT NOT NULL CHECK (valid_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    valid_to TEXT CHECK (valid_to GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    PRIMARY KEY (user_id, valid_from),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (doctor_id) REFERENCES STAFF (staff_id),
    CONSTRAINT ck_assignment_period CHECK (valid_to IS NULL OR valid_to >= valid_from)  -- CLI §6 Patient Assignment
);

CREATE TABLE PATIENT_CLINICAL_PROFILE (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    obstetric_history VARCHAR(10) CHECK (length(obstetric_history) <= 10),  -- VARCHAR(10) (PARA, e.g. "1001")
    blood_type TEXT CHECK (blood_type IN ('A+', 'A−', 'B+', 'B−', 'AB+', 'AB−', 'O+', 'O−')),  -- ENUM (A+ / A− / B+ / B− / AB+ / AB− / O+ / O−)
    allergies TEXT,  -- TEXT
    updated_at TEXT NOT NULL CHECK (updated_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE PREGNANCY_PROFILE (
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    edd TEXT NOT NULL CHECK (edd GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    lmp TEXT CHECK (lmp GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    edd_source TEXT NOT NULL CHECK (edd_source IN ('Self-entered', 'Hospital record')),  -- ENUM (Self-entered / Hospital record)
    height_cm NUMERIC,  -- DECIMAL(4,1)
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE SESSION (
    session_token VARCHAR(255) NOT NULL CHECK (length(session_token) <= 255),  -- VARCHAR(255)
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    role TEXT NOT NULL CHECK (role IN ('Mother')),  -- ENUM (Mother)
    created_at TEXT NOT NULL CHECK (created_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    expires_at TEXT NOT NULL CHECK (expires_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME — lifetime open (ACC §10 Q9)
    PRIMARY KEY (session_token),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    CONSTRAINT ck_session_period CHECK (expires_at > created_at)  -- ACC §6 Session
);

CREATE TABLE VISIT (
    visit_id TEXT NOT NULL CHECK (length(visit_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    visit_date TEXT NOT NULL CHECK (visit_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    facility VARCHAR(100) NOT NULL CHECK (length(facility) <= 100),  -- VARCHAR(100)
    visit_type VARCHAR(100) NOT NULL CHECK (length(visit_type) <= 100),  -- VARCHAR(100)
    conclusion TEXT,  -- TEXT
    doctor_note TEXT,  -- TEXT
    ultrasound_image VARCHAR(255) CHECK (length(ultrasound_image) <= 255),  -- VARCHAR(255) (file path)
    fetal_length NUMERIC,  -- DECIMAL(5,1) (cm)
    estimated_fetal_weight NUMERIC,  -- DECIMAL(6,1) (gram)
    ultrasound_report_date TEXT CHECK (ultrasound_report_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    gestational_week INTEGER NOT NULL CHECK (gestational_week BETWEEN 0 AND 42),  -- INTEGER 0–42
    PRIMARY KEY (visit_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id)
);

CREATE TABLE AI_RESPONSE_LOG (
    log_id TEXT NOT NULL CHECK (length(log_id) = 36),  -- UUID
    conversation_id TEXT NOT NULL CHECK (length(conversation_id) = 36),  -- UUID
    ai_response_data TEXT NOT NULL,  -- TEXT
    audit_log_entry TEXT CHECK (json_valid(audit_log_entry)),  -- JSON
    PRIMARY KEY (log_id),
    FOREIGN KEY (conversation_id) REFERENCES CONVERSATION (conversation_id)
);

CREATE TABLE CHAT_MESSAGE (
    message_id TEXT NOT NULL CHECK (length(message_id) = 36),  -- UUID
    conversation_id TEXT NOT NULL CHECK (length(conversation_id) = 36),  -- UUID
    sender TEXT NOT NULL CHECK (sender IN ('Mother', 'Chatbot')),  -- ENUM (Mother / Chatbot)
    text TEXT NOT NULL CHECK (length(text) <= 500),  -- TEXT (the mother's question ≤ 500 characters — D-46)
    parsed_intent TEXT CHECK (json_valid(parsed_intent)),  -- JSON
    is_risk INTEGER NOT NULL CHECK (is_risk IN (0, 1)),  -- BOOLEAN, default false
    handoff_choice TEXT CHECK (handoff_choice IN ('Connect to nurse', 'No thanks')),  -- ENUM (Connect to nurse / No thanks)
    sent_at TEXT NOT NULL CHECK (sent_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (message_id),
    FOREIGN KEY (conversation_id) REFERENCES CONVERSATION (conversation_id),
    CONSTRAINT ck_chat_question_length CHECK (sender <> 'Mother' OR length(text) <= 500),  -- BOT §6; D-46; DM-36
    CONSTRAINT ck_chat_answer_fields CHECK (sender = 'Mother' OR (parsed_intent IS NULL AND handoff_choice IS NULL AND is_risk = 0)),  -- BOT §6 ("the mother's questions only")
    CONSTRAINT ck_chat_handoff_risk CHECK (handoff_choice IS NULL OR is_risk = 1)  -- BOT §5 FR-007 – FR-009
);

CREATE TABLE DIARY_IMAGE (
    image_id TEXT NOT NULL CHECK (length(image_id) = 36),  -- UUID
    diary_id TEXT NOT NULL CHECK (length(diary_id) = 36),  -- UUID
    file VARCHAR(255) NOT NULL CHECK (length(file) <= 255),  -- VARCHAR(255) (path of a JPG / PNG ≤ 10 MB)
    sort_order INTEGER NOT NULL CHECK (sort_order BETWEEN 1 AND 5),  -- INTEGER 1–5
    PRIMARY KEY (image_id),
    CONSTRAINT uq_diary_image_order UNIQUE (diary_id, sort_order),  -- TML §6 Diary Image (1–5)
    FOREIGN KEY (diary_id) REFERENCES DIARY_ENTRY (diary_id)
);

CREATE TABLE HEALTH_METRIC_RECORD (
    record_id TEXT NOT NULL CHECK (length(record_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    metric TEXT NOT NULL CHECK (metric IN ('Weight', 'Temperature', 'Heart rate', 'Sleep', 'Blood pressure', 'Blood glucose', 'Urine protein', 'Fetal heart rate')),  -- ENUM (Weight / Temperature / Heart rate / Sleep / Blood pressure / Blood glucose / Urine protein / Fetal heart rate)
    metric_group TEXT NOT NULL CHECK (metric_group IN ('Group 1', 'Group 2', 'Visit')),  -- ENUM (Group 1 / Group 2 / Visit)
    value VARCHAR(20) NOT NULL CHECK (length(value) <= 20),  -- VARCHAR(20) (DM-22: one formatted string)
    unit VARCHAR(10) CHECK (length(unit) <= 10),  -- VARCHAR(10)
    glucose_context TEXT CHECK (glucose_context IN ('fasting', 'post_1h', 'post_2h')),  -- ENUM (fasting / post_1h / post_2h)
    measured_at TEXT NOT NULL CHECK (measured_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    source TEXT NOT NULL CHECK (source IN ('From visit', 'Self-entered', 'Doctor-assigned')),  -- ENUM (From visit / Self-entered / Doctor-assigned)
    visit_id TEXT CHECK (length(visit_id) = 36),  -- UUID
    gestational_week INTEGER NOT NULL CHECK (gestational_week BETWEEN 0 AND 42),  -- INTEGER 0–42
    created_at TEXT NOT NULL CHECK (created_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (record_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (visit_id) REFERENCES VISIT (visit_id),
    CONSTRAINT ck_hmr_visit_source CHECK ((source = 'From visit') = (visit_id IS NOT NULL)),  -- HLT §6 (`visit_id` Required when source = From visit)
    CONSTRAINT ck_hmr_glucose_context CHECK ((metric = 'Blood glucose') = (glucose_context IS NOT NULL)),  -- HLT §6; ALR §5.1 FR-013
    CONSTRAINT ck_hmr_fetal_hr_visit CHECK (metric <> 'Fetal heart rate' OR source = 'From visit'),  -- HLT §5.2 BR-005
    CONSTRAINT ck_hmr_group1_no_doctor CHECK (metric_group <> 'Group 1' OR source <> 'Doctor-assigned'),  -- HLT §5.2 BR-003
    CONSTRAINT ck_hmr_measured_before_created CHECK (measured_at <= created_at),  -- HLT §6
    CONSTRAINT ck_hmr_metric_group CHECK ((metric IN ('Weight', 'Temperature', 'Heart rate', 'Sleep') AND metric_group = 'Group 1') OR (metric IN ('Blood pressure', 'Blood glucose', 'Urine protein') AND metric_group = 'Group 2') OR (metric = 'Fetal heart rate' AND metric_group = 'Visit'))  -- HLT §6 `metric_group`; D-11, D-51; DM-39
);

CREATE TABLE WATCH_FLAG (
    flag_id TEXT NOT NULL CHECK (length(flag_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    visit_id TEXT CHECK (length(visit_id) = 36),  -- UUID
    metric TEXT NOT NULL CHECK (metric IN ('Blood pressure', 'Blood glucose', 'Urine protein')),  -- ENUM (Blood pressure / Blood glucose / Urine protein)
    flagged_by TEXT NOT NULL CHECK (length(flagged_by) = 36),  -- UUID
    flagged_at TEXT NOT NULL CHECK (flagged_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),  -- DATE
    note TEXT,  -- TEXT — maximum length open (S-064 #9)
    template_id TEXT CHECK (length(template_id) = 36),  -- UUID
    custom_text TEXT CHECK (length(custom_text) <= 1000),  -- TEXT, ≤ 1000 characters
    active INTEGER NOT NULL CHECK (active IN (0, 1)),  -- BOOLEAN
    PRIMARY KEY (flag_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (visit_id) REFERENCES VISIT (visit_id),
    FOREIGN KEY (flagged_by) REFERENCES STAFF (staff_id),
    FOREIGN KEY (template_id) REFERENCES GUIDANCE_TEMPLATE (template_id)
);

CREATE TABLE METRIC_REPORT (
    report_id TEXT NOT NULL CHECK (length(report_id) = 36),  -- UUID
    report_code VARCHAR(20) NOT NULL CHECK (length(report_code) <= 20),  -- VARCHAR(20) — provisional (ALR §10 Q16)
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    metric TEXT NOT NULL CHECK (metric IN ('Blood pressure', 'Blood glucose', 'Urine protein', 'Symptom')),  -- ENUM (Blood pressure / Blood glucose / Urine protein / Symptom)
    health_metric_record_id TEXT CHECK (length(health_metric_record_id) = 36),  -- UUID
    other_symptom_text VARCHAR(100) CHECK (length(other_symptom_text) <= 100),  -- VARCHAR(100)
    note TEXT,  -- TEXT — maximum length open (ALR §10 Q14)
    submitted_at TEXT NOT NULL CHECK (submitted_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    watch_flag_id TEXT CHECK (length(watch_flag_id) = 36),  -- UUID
    PRIMARY KEY (report_id),
    UNIQUE (report_code),
    UNIQUE (health_metric_record_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (health_metric_record_id) REFERENCES HEALTH_METRIC_RECORD (record_id),
    FOREIGN KEY (watch_flag_id) REFERENCES WATCH_FLAG (flag_id),
    CONSTRAINT ck_report_record CHECK ((metric = 'Symptom') = (health_metric_record_id IS NULL)),  -- ALR §6 Metric Report; D-41
    CONSTRAINT ck_report_symptom_no_flag CHECK (metric <> 'Symptom' OR watch_flag_id IS NULL)  -- ALR §6 Metric Report (`watch_flag_id` empty for a symptom report)
);

CREATE TABLE CARE_CASE (
    case_id TEXT NOT NULL CHECK (length(case_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    case_source TEXT NOT NULL CHECK (case_source IN ('Metric report', 'Symptom', 'Chatbot')),  -- ENUM (Metric report / Symptom / Chatbot)
    status TEXT NOT NULL CHECK (status IN ('Not viewed', 'Viewed', 'Escalated to doctor', 'Resolved')),  -- ENUM (Not viewed / Viewed / Escalated to doctor / Resolved)
    metric_report_id TEXT CHECK (length(metric_report_id) = 36),  -- UUID
    chat_message_id TEXT CHECK (length(chat_message_id) = 36),  -- UUID
    assigned_doctor_id TEXT CHECK (length(assigned_doctor_id) = 36),  -- UUID
    created_at TEXT NOT NULL CHECK (created_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    closed_at TEXT CHECK (closed_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    closed_by TEXT CHECK (length(closed_by) = 36),  -- UUID
    PRIMARY KEY (case_id),
    UNIQUE (metric_report_id),
    UNIQUE (chat_message_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (metric_report_id) REFERENCES METRIC_REPORT (report_id),
    FOREIGN KEY (chat_message_id) REFERENCES CHAT_MESSAGE (message_id),
    FOREIGN KEY (assigned_doctor_id) REFERENCES STAFF (staff_id),
    FOREIGN KEY (closed_by) REFERENCES STAFF (staff_id),
    CONSTRAINT ck_case_one_origin CHECK ((metric_report_id IS NULL) <> (chat_message_id IS NULL)),  -- ALR §6 Case
    CONSTRAINT ck_case_chatbot_origin CHECK ((case_source = 'Chatbot') = (chat_message_id IS NOT NULL)),  -- ALR §6 Case; D-41
    CONSTRAINT ck_case_closed CHECK ((status = 'Resolved') = (closed_at IS NOT NULL) AND (closed_at IS NULL) = (closed_by IS NULL)),  -- ALR §6 Case; DM-28
    CONSTRAINT ck_case_escalated_doctor CHECK (status NOT IN ('Not viewed', 'Viewed') OR assigned_doctor_id IS NULL)  -- ALR §6 Case (`assigned_doctor_id` set when Escalated to doctor); D-68
);

CREATE TABLE REPORT_SYMPTOM (
    report_id TEXT NOT NULL CHECK (length(report_id) = 36),  -- UUID
    symptom TEXT NOT NULL CHECK (symptom IN ('No symptoms', 'Headache', 'Dizziness', 'Palpitations', 'Abdominal pain', 'Bleeding', 'Other')),  -- ENUM (No symptoms / Headache / Dizziness / Palpitations / Abdominal pain / Bleeding / Other)
    PRIMARY KEY (report_id, symptom),
    FOREIGN KEY (report_id) REFERENCES METRIC_REPORT (report_id)
);

CREATE TABLE CASE_STATUS_HISTORY (
    case_id TEXT NOT NULL CHECK (length(case_id) = 36),  -- UUID
    status TEXT NOT NULL CHECK (status IN ('Not viewed', 'Viewed', 'Escalated to doctor', 'Resolved')),  -- ENUM (Not viewed / Viewed / Escalated to doctor / Resolved)
    changed_at TEXT NOT NULL CHECK (changed_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    changed_by TEXT CHECK (length(changed_by) = 36),  -- UUID
    role TEXT NOT NULL CHECK (role IN ('System', 'Nurse', 'Doctor')),  -- ENUM (System / Nurse / Doctor)
    PRIMARY KEY (case_id, status),
    FOREIGN KEY (case_id) REFERENCES CARE_CASE (case_id),
    FOREIGN KEY (changed_by) REFERENCES STAFF (staff_id),
    CONSTRAINT ck_history_system_row CHECK ((role = 'System') = (changed_by IS NULL)),  -- CLI §6 Case Status History
    CONSTRAINT ck_history_system_first CHECK (role <> 'System' OR status = 'Not viewed')  -- ALR §5.1 FR-021
);

CREATE TABLE NOTIFICATION (
    notification_id TEXT NOT NULL CHECK (length(notification_id) = 36),  -- UUID
    user_id TEXT NOT NULL CHECK (length(user_id) = 36),  -- UUID
    type TEXT NOT NULL CHECK (type IN ('Report', 'Visit result', 'Appointment', 'Instruction reminder')),  -- ENUM (Report / Visit result / Appointment / Instruction reminder)
    title VARCHAR(100) NOT NULL CHECK (length(title) <= 100),  -- VARCHAR(100)
    subtitle VARCHAR(200) CHECK (length(subtitle) <= 200),  -- VARCHAR(200)
    created_at TEXT NOT NULL CHECK (created_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    read_at TEXT CHECK (read_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    case_id TEXT CHECK (length(case_id) = 36),  -- UUID
    visit_id TEXT CHECK (length(visit_id) = 36),  -- UUID
    watch_flag_id TEXT CHECK (length(watch_flag_id) = 36),  -- UUID
    appointment_ref VARCHAR(64) CHECK (length(appointment_ref) <= 64),  -- VARCHAR(64)
    PRIMARY KEY (notification_id),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id),
    FOREIGN KEY (case_id) REFERENCES CARE_CASE (case_id),
    FOREIGN KEY (visit_id) REFERENCES VISIT (visit_id),
    FOREIGN KEY (watch_flag_id) REFERENCES WATCH_FLAG (flag_id),
    CONSTRAINT ck_notification_one_target CHECK ((case_id IS NOT NULL) + (visit_id IS NOT NULL) + (watch_flag_id IS NOT NULL) + (appointment_ref IS NOT NULL) <= 1),  -- ACC §6 Notification (target)
    CONSTRAINT ck_notification_read_after CHECK (read_at IS NULL OR read_at >= created_at)  -- ACC §5.1 FR-026
);

CREATE TABLE STAFF_RESPONSE (
    response_id TEXT NOT NULL CHECK (length(response_id) = 36),  -- UUID
    case_id TEXT NOT NULL CHECK (length(case_id) = 36),  -- UUID
    responder_id TEXT NOT NULL CHECK (length(responder_id) = 36),  -- UUID
    responder_role TEXT NOT NULL CHECK (responder_role IN ('Nurse', 'Doctor')),  -- ENUM (Nurse / Doctor)
    template_id TEXT CHECK (length(template_id) = 36),  -- UUID
    custom_text TEXT CHECK (length(custom_text) <= 1000),  -- TEXT, ≤ 1000 characters
    sent_at TEXT NOT NULL CHECK (sent_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),  -- DATETIME
    PRIMARY KEY (response_id),
    FOREIGN KEY (case_id) REFERENCES CARE_CASE (case_id),
    FOREIGN KEY (responder_id) REFERENCES STAFF (staff_id),
    FOREIGN KEY (template_id) REFERENCES GUIDANCE_TEMPLATE (template_id),
    CONSTRAINT ck_response_content CHECK (template_id IS NOT NULL OR custom_text IS NOT NULL)  -- ALR §6 Staff Response
);

-- Indexes
CREATE UNIQUE INDEX ux_assignment_one_active ON PATIENT_ASSIGNMENT (user_id) WHERE valid_to IS NULL;  -- CLI §6 ("at most 1 active responsible doctor")
CREATE UNIQUE INDEX ux_watch_flag_one_active ON WATCH_FLAG (user_id, metric) WHERE active = 1;  -- DM-21 (default)
CREATE UNIQUE INDEX ux_template_one_default ON GUIDANCE_TEMPLATE (is_default) WHERE is_default = 1;  -- ALR §5.2 BR-013 ("the hospital's default template")
CREATE INDEX ix_case_queue ON CARE_CASE (status, created_at);  -- S-061 queue (CLI FR-002, FR-020)
CREATE INDEX ix_case_doctor ON CARE_CASE (assigned_doctor_id, status);  -- S-061 doctor view, S-059 (D-68, DM-32)
CREATE INDEX ix_case_mother ON CARE_CASE (user_id, created_at);  -- S-029 My reports (ALR FR-002)
CREATE INDEX ix_report_mother ON METRIC_REPORT (user_id, submitted_at);  -- S-029 (ALR FR-002, FR-003)
CREATE INDEX ix_hmr_history ON HEALTH_METRIC_RECORD (user_id, metric, measured_at);  -- S-025, S-064 metric history (HLT FR-009, CLI FR-008)
CREATE INDEX ix_notification_list ON NOTIFICATION (user_id, created_at);  -- S-009 (ACC FR-025)
CREATE INDEX ix_chat_conversation ON CHAT_MESSAGE (conversation_id, sent_at);  -- S-034 (BOT FR-002)
CREATE INDEX ix_diary_week ON DIARY_ENTRY (user_id, gestational_week);  -- S-048 week view (TML FR-003)
