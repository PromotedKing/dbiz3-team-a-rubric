# PRD: Mother & Baby 360°

| Field | Value |
|---|---|
| Product | Mother & Baby 360° — maternity remote-monitoring sub-app for Thu Cuc Hospital (TCI app) |
| Team | Group A — DBIZ3 |
| Source | MVP Requirements & Scope Specification, Version 8 (29/09/2026), updated with the architectural and product scope refinement of 14/10/2026; sections 7 and 8 are added for traceability |
| Next document in the chain | Spec Documents `specs/spec-{MODULE-ID}.md` (Must items → modules in section 7) |

## 1. Problem statement

Expectant mothers experience constant anxiety due to a lack of immediate professional support and visibility into their health status between scheduled hospital visits. They need a trusted, convenient way to review the health information captured during hospital visits, understand what it means, receive timely guidance when something needs attention, and stay connected to appropriate care - without depending on unverified online sources or overloaded hospital hotlines.

## 2. Product context and integration scope

- **Sub-app / Mini-app inside TCI host app**: Mother & Baby 360° is not a standalone application. It operates strictly as an embedded sub-app / mini-app session inside the main Thu Cuc Hospital patient application (TCI app). It has no registration, sign-in or password of its own (D-01).
- **Session & Identity Connection**: The sub-app reuses the existing patient account from the TCI host app. No new registration or password is created; the sub-app keeps only a copy of the TCI identity it needs to attach its data to the right mother (D-71). Upon first opening, the mother completes a single session link: agreeing to terms of service & data sharing consent. Basic patient profile information (Full Name, Date of Birth / Age, Phone Number, Patient ID / Medical Record Number) is directly fetched from the host TCI database. The sub-app is for expectant mothers: only a female TCI account can open it, and the pregnancy setup confirms the pregnancy (D-71). An intuitive onboarding guide introduces key features before landing on the dashboard (D-74).
- **Pregnancy Baseline Setup**: Specific maternity context not present in the general TCI account (estimated due date [EDD], first day of last menstrual period [LMP], and the date of the first antenatal check-up) is captured during first-time pregnancy setup / onboarding and associated with the active session (D-72). Later visits come from the hospital records (D-59).
- **Clinical Data Visibility vs. Daily Measurement**: Health information shown to the mother is sourced primarily from hospital visit records (clinical/EMR records) already in the TCI system. Daily routine self-measurement is not required. Mothers only report specific indicators flagged by the doctor (watch-flags) or observed alarming symptoms, which trigger the alert & triage mechanism described in Section 5. Optional self-tracked metrics (weight, temperature, heart rate, sleep) are recorded for mom's own reference without threshold evaluations or alerts.

## 3. Target user (MVP)

- **Primary MVP User**: Expectant Pregnant Mothers (using the Mobile Application).
  *Justification: The MVP is designed around the mother's daily companion experience. She goes through the initial onboarding guide, reviews clinical findings, documents her pregnancy journey through timeline and diary, queries the pregnancy AI chatbot, and reports abnormal indicators or symptoms when needed.*
- **Supporting Clinical Users**: Triage Nurses and Attending Doctors (using the Clinician Web Dashboard). Secondary operational actors who handle triage queues when cases are created by clinical threshold breaches, alarming symptoms, or chatbot escalation.

## 4. Link to the Product Design Package (DBIZ2)

### Related system objectives

- **MVP Primary Objective - Mom-Centered Continuous Care**: Give expectant mothers an easy way to understand their health status between hospital visits, build an emotional connection to their pregnancy journey, and know when and how to seek help - through a simple daily mobile experience for health visibility, risk awareness, pregnancy guidance, and access to appropriate support.
- **Instant Triage (AI & Nurse)**: Proactive risk detection combining AI triage guardrails with structured indicator thresholds and critical symptom triggers, routing cases seamlessly to clinical staff.
- **Seamless Handover**: When a mother's reported condition or chatbot conversation requires clinical attention, relevant medical context and chat transcripts move to the nurse/doctor queue to eliminate repeated manual explanations (D-78).
- **Daily Habit Formation**: Engage the mother through a unified Pregnancy Timeline & Memory Diary (displaying gestational week progress on Home Dashboard; tap to view daily indicators & ultrasound photos, with integrated daily diary entries below and full journey review with PDF album export — D-75).

### Function scope

- **Mother Functions - MVP focus**:
  - Open sub-app via TCI host session (first-time consent & account link, onboarding walkthrough guide).
  - Pregnancy baseline setup (EDD, LMP, first check-up date).
  - View Health Dashboard (sourced from hospital records with doctor's watch-flags).
  - Log Optional Self-Tracked Metrics (weight, temperature, heart rate, sleep - no threshold checks).
  - Report Flagged Indicator or Symptom (with clear threshold criteria and critical symptom triggers).
  - View Report Status & Care Team Response.
  - View Pregnancy Timeline on Home Dashboard (gestational week indicator); tap into dedicated view to inspect daily health indicators, baby's ultrasound images, write integrated daily diary entries below, review full journey across trimesters/stages, and export commemorative album (PDF format).
  - Consult Maternity AI Chatbot (powered by Google AI Studio API with strict pregnancy-only prompt context and risk escalation notices).
  - Notifications & Notification Settings.
- **Supporting Nurse Functions**: Process Medical Alerts, Triage Patient Cases (from over-threshold reports, alarming symptoms, or chatbot handoffs), and Access Patient Dashboard.
- **Supporting Doctor Functions**: Access Patient Dashboard, Review Escalated Cases, Provide Clinical Guidance, and Update Patient / Instruction Status.

## 5. MVP scope priority — MoSCoW

Each item has an ID so that it can be followed into the specs (section 7).

| ID | Priority | Feature / item | Function mapping | Spec module | Notes / justification |
|---|---|---|---|---|---|
| M1 | Must | Patient Onboarding & Pregnancy Setup | Open sub-app via TCI session + first-time consent & account linking, pregnancy setup (EDD / LMP / first visit date), onboarding guide | ACC (Onboarding & Session) | Foundation of the mother's journey. Replaces the legacy separate account concept (registration, OTP, password — D-01). Reuses the authenticated TCI session; the sub-app keeps only a copy of the TCI identity (D-71). On first access, the mother accepts terms & authorizes data linking. Core identity (name, date of birth / age, phone, patient code) is retrieved from TCI; only a female TCI account opens the sub-app. A brief onboarding guide introduces the app (D-74), followed by entering pregnancy parameters (EDD or LMP, first visit date) to personalize gestational weeks. |
| M2 | Must | Health Visibility (Clinical Data Review) | View Health Dashboard (sourced from hospital visit records, incl. doctor's watch-flags), Log Optional Self-Tracked Metrics | HLT | Sourced primarily from hospital visit records (vitals, lab results, ultrasound findings) and watch-flags placed by the doctor. Optional self-tracked metrics (weight, temp, HR, sleep) are labeled "Self-entered", kept separate, and never threshold-checked. Fetal heart rate is read-only from hospital visits (110–160 bpm reference range, display only). Live EMR is Won't; simulated via clinician seed data. |
| M3 | Must | Risk Feedback & Health Alerts | Report Flagged Indicator or Self-Observed Symptom, View Report Status & Care Team Response | ALR | Clear two-pronged alert flow: (1) **Indicator reporting**: Doctor flags Group 2 metrics (blood pressure, blood glucose, urine protein). When mom reports a value, the system evaluates it against the clinical thresholds stored in the threshold rules: Systolic BP ≥140 mmHg or Diastolic BP ≥90 mmHg; Blood glucose ≥5.3 (fasting), ≥7.8 (1h post-meal), or ≥6.7 mmol/L (2h post-meal); Urine protein ≥1+ (glucose and urine protein pending SME, D-15). Exceeding a threshold triggers an immediate "Metric Alert" popup (S-028), creates a "Not viewed" Case, and alerts the Nurse queue. `[NEEDS CLARIFICATION: the source also calls this case "high-priority"; there is no priority field (D-17) — spec-ALR.md Q22]` Normal values with no symptoms return "No action needed". (2) **Symptom checklist**: Mom can tick symptoms. The key alarm checkboxes are Vaginal bleeding, Severe abdominal pain, Waters breaking / fluid leakage, Severe headache / dizziness / blurred vision and Absence of fetal movement (list pending SME, D-73); the list also keeps Palpitations and Other. Any ticked symptom routes the report to the Nurse queue as a case even if vitals are within normal range (ALR BR-007). Status tracking (Not viewed → Viewed → Escalated to doctor → Resolved) allows mom to follow clinical responses. |
| M4 | Must | Pregnancy Timeline & Baby Memory Journal (Integrated Journey) | View Timeline on Dashboard, tap to view daily indicators & ultrasound photos, write daily diary, review journey, export PDF album | TML | Unified Must item serving the core emotional & memory journey. On the Home Dashboard, a prominent Timeline widget shows the current gestational week. Tapping it opens a dedicated detailed screen displaying clinical indicators by day and the baby's ultrasound images (weekly view with a daily listing — D-75). Directly beneath this, the mother can write daily diary entries (notes, mood tags, baby bump/personal photos) and weekly Messages to Baby (pending Client approval, D-03). At the end of each pregnancy stage or the full journey, mom can review her entire journey and compile it into a commemorative keepsake album exported directly to her device (PDF format). Stage boundaries (trimesters) pending SME. |
| M5 | Must | AI Chatbot L1 Support (Google AI Studio) | Consult AI Chatbot | BOT | First-line maternal assistant powered by Google AI Studio API (Gemini models via AI Studio), called from a Python backend (D-76). Employs a strict system prompt context restriction: queries must revolve strictly around pregnancy, prenatal care, nutrition, and postpartum wellness; out-of-domain queries are politely declined. Medical disclaimer is always visible. The medical record is never sent to the chatbot. Includes strict risk detection: recognizing danger phrases (e.g., "chảy máu", "đau bụng quằn quại", "không thấy thai máy", "vỡ ối", "hoa mắt chóng mặt"; list pending SME, D-47) to immediately halt automated general advice, issue an urgent advisory notice ("Dấu hiệu cần chú ý y tế" — "Signs that need medical attention"), and offer instant handover to the Nurse triage queue ("Connect to nurse") or display the emergency hospital hotline (real number pending Client). |
| S1 | Should | Nurse Triage & Alert Verification | Process Medical Alerts, Triage Patient | CLI (+ ALR) | Supporting workflow: Nurse receives cases triggered by over-threshold metrics, ticked alarm symptoms, or chatbot escalations (with the chat transcript, D-78). Nurse reviews context, assesses severity, provides written home care guidance, or escalates to the Doctor. |
| S2 | Should | Doctor Escalation & Follow-up | Review Escalated Cases, Provide Consultation, Update Patient Status | CLI | Completes clinical escalation for high-risk red-flag cases routed by the Nurse. |
| C1 | Could | Basic Appointment Booking (Host App WebView) | Read-only upcoming appointment / visit reminders; booking in host | APT | Booking belongs to the TCI host app and its existing antenatal portal. **Current release alignment (D-80 / D-86):** no Home booking CTA, no Appointments tab, and no booking-session API in MB360; the root bar uses Timeline. Shows the upcoming-appointment card (data read from TCI) and sends appointment reminder notifications (D-77). |
| W1 | Won't | Knowledge Base Search & Filtering | Access Knowledge Library | — | Out of scope for MVP; curated content embedded in core experiences and AI chatbot is sufficient. |
| W2 | Won't | In-App Payment Processing | N/A | — | Excluded due to conflicts with hospital HIS payment workflows. |
| W3 | Won't | Hardware Device Auto-Sync | N/A | — | Excluded to eliminate hardware driver compatibility overhead. |
| W4 | Won't | Deep Two-Way HIS/EMR Integration | N/A | — (seed data instead, D-59) | Excluded; simulated visit and clinical data are loaded via clinician seed records. |

## 6. Rough sprint backlog — Phase 1

| # | Item | Description and requirements | Spec module |
|---|---|---|---|
| 1 | Patient Onboarding & Session Linking | Implement sub-app session entry within TCI app, terms agreement & data authorization, auto-fetching TCI basic profile (name, date of birth / age, sex, phone, patient ID), onboarding tutorial, and pregnancy baseline capture (EDD, LMP, first visit date). | ACC |
| 2 | Health Visibility (Clinical Data Review) | Implement Health Dashboard displaying visit records (vitals, ultrasound, labs), doctor's watch-flags, and optional self-tracked metrics (weight, temp, HR, sleep) without threshold logic. | HLT |
| 3 | Risk Feedback & Health Alerts | Implement Group 2 metric reporting with clinical threshold validation (BP, glucose, protein), alarming symptom checklist creating Nurse cases, "Metric Alert" popup, and status tracking (Not viewed → Viewed → Escalated to doctor → Resolved). | ALR |
| 4 | Pregnancy Timeline & Baby Memory Journal (Dashboard & Detail) | Build Timeline widget on Home Dashboard (gestational week progress); tap opens detail screen with daily clinical indicators and baby's ultrasound images, integrated daily diary entry section below, full journey review across stages, and PDF commemorative album export. | TML |
| 5 | AI Chatbot L1 Support (Google AI Studio) | Integrate Google AI Studio API with strict maternity prompt context guardrails, out-of-domain decline, danger phrase detection (notice to mom), and "Connect to nurse" triage handoff. | BOT |
| 6 | Clinical Escalation Support (Nurse Triage + Doctor Follow-up) | Implement Nurse queue for escalated cases (metrics, symptoms, chatbot with its transcript) and doctor review workflow. | CLI |
| 7 | Basic Appointment Booking (WebView) | Implement the Could-tier read-only appointment card and reminder touchpoints. Booking stays in TCI; no sub-app booking launcher (D-80 / D-86). | APT |

## 7. Must items → spec modules

| ID | Must item | Spec document | Main FRs | Screens |
|---|---|---|---|---|
| M1 | Patient Onboarding & Pregnancy Setup | `specs/spec-ACC.md` | FR-001 – FR-005, FR-011, FR-015 – FR-028 | S-001, S-104, S-007 / S-046, S-008, S-009, S-010, S-011, S-043, S-083, S-103 |
| M2 | Health Visibility (Clinical Data Review) | `specs/spec-HLT.md` | HLT FR-001 – FR-005, FR-007 – FR-012 | S-023, S-024, S-025, S-027 |
| M3 | Risk Feedback & Health Alerts | `specs/spec-ALR.md` | FR-001 – FR-003, FR-005 – FR-008, FR-010 – FR-016, FR-018 – FR-022 | S-025A, S-026, S-028, S-029, S-009 |
| M4 | Pregnancy Timeline & Baby Memory Journal | `specs/spec-TML.md` | FR-002 – FR-006, FR-008 – FR-014 (FR-011 pending Client, D-03) | S-008 (week widget), S-048, S-051, S-052, S-105 |
| M5 | AI Chatbot L1 Support | `specs/spec-BOT.md` | FR-001 – FR-011 | S-031, S-032, S-033, S-034 |

Should items: S1 Nurse Triage & Alert Verification and S2 Doctor Escalation & Follow-up → `specs/spec-CLI.md` (with `spec-ALR.md` FR-004, FR-008, FR-009). Could item: C1 Basic Appointment Booking → `specs/spec-APT.md` (FR-005, FR-009; FR-001 host-only under D-80 / D-86); its card on S-008 and its switch on S-010 are Could elements inside Must screens. Won't items are kept as Won't rows in `docs/function-list.md`.

## 8. Scope changes and their reasons

The decisions below changed or sharpened the scope while the specs were written; the full text and status of each is in `docs/decisions.md`.

`[NEEDS CLARIFICATION: which of these changes came after the scope confirmed with the Client in Session 3, and which were already part of it — owner Product/PM]`

| Decision | Change | Reason | Status |
|---|---|---|---|
| D-01 | Identity from the TCI app; no registration, OTP or password in the sub-app | PRD §2: the sub-app reuses the host app's identity | Pending Client |
| D-02 | Weekly tips / reference content removed from the timeline | Content is linked to real visits instead (PRD §5, M4) | Pending Client |
| D-03, D-65 | "Messages to Baby" added to the Timeline Must item | Emotional engagement; no FR in DBIZ2 | Pending Client |
| D-11 | Metrics split into Group 1 (self-tracked, no threshold) and Group 2 (doctor-assigned, threshold); the mother reports only flagged Group 2 metrics or symptoms | PRD §2 and §5: mothers do not self-measure daily | Decided |
| D-12 | Fetal heart rate only from visits; 110 – 160 bpm shown for reference, never an alert | PRD §5 M2, confirmed 29/09/2026 | Decided |
| D-34 | Chatbot case created only when the mother taps "Connect to nurse" | PRD §5 M5: hand-off is offered, not forced | Decided |
| D-49 | No Admin actor | PRD §3 names no Admin | Decided |
| D-59 | Visit data is seed data; no visit entry screen, no EMR integration | PRD §5: Deep HIS/EMR integration is Won't; demo data is simulated | Decided |
| D-62 | Appointments: no booking screen in the sub-app; the TCI booking flow is opened | PRD §5 C1: booking exists in the host app | Decided (priority revised by D-77) |
| D-67 | Chatbot context also keeps the earlier questions / answers of the conversation | Dialogue continuity; the medical record is never sent | Decided (team) — to confirm with the Client |
| D-71 | User Account copies the date of birth and sex from TCI; only a female TCI account opens the sub-app | PRD §2 lists date of birth / age; the sub-app is for expectant mothers | Decided (team, 14/10/2026) |
| D-72 | Date of the first antenatal check-up captured at setup | PRD §2 "past antenatal check-up history", M1 "visit info"; later visits are hospital data | Decided (team, 14/10/2026) |
| D-73 | Symptom list = PRD alarm symptoms + Palpitations + Other; every symptom still creates a case | PRD M3 symptom checklist; ALR BR-007 kept | Pending SME |
| D-74 | ACC shown as "Onboarding & Session"; onboarding guide S-104 | PRD §2, M1 | Decided (team, 14/10/2026) |
| D-75 | Timeline: daily indicators + ultrasound on S-048 above the diary; journey review by stage and PDF album (S-105) | PRD §4, M4 | Decided (team); trimester boundaries Pending SME |
| D-76 | Chatbot on Google AI Studio; pregnancy-only scope with polite decline; danger-phrase notice | PRD M5 | Decided (team, 14/10/2026) |
| D-77 | Appointments become Could; WebView of the TCI booking portal; upcoming card read from TCI | PRD C1 | Decided (team, 14/10/2026) |
| D-78 | Chatbot case shows the whole conversation to the nurse / doctor | PRD §4 "Seamless Handover" | Decided (team, 14/10/2026) |

### Navigation alignment confirmed 11/11/2026

Hải Anh confirms the current release follows D-80 (recorded as D-86): Home · Timeline · Chatbot · From doctor · Profile, with no Appointments tab or booking CTA on Home. This removes the old sub-app launcher from C1; the read-only next-appointment card, Appointment notices and S-010 switch remain (D-77 / D-81). D-77 / DM-04 still prohibit MB360 appointment storage. The proposed booking-session Part B is cancelled; no API contract is adopted. Host-integration and Client/SME markers remain open.
