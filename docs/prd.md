# PRD: Mother & Baby 360°

| Field | Value |
|---|---|
| Product | Mother & Baby 360° — maternity remote-monitoring sub-app for Thu Cuc Hospital (TCI app) |
| Team | Group A — DBIZ3 |
| Source | MVP Requirements & Scope Specification, Version 8 (29/09/2026), converted to Markdown without changing its content; sections 7 and 8 are added for traceability |
| Next document in the chain | Spec Documents `specs/spec-{MODULE-ID}.md` (Must items → modules in section 7) |

## 1. Problem statement

Expectant mothers experience constant anxiety due to a lack of immediate professional support and visibility into their health status between scheduled hospital visits. They need a trusted, convenient way to review the health information captured during hospital visits, understand what it means, receive timely guidance when something needs attention, and stay connected to appropriate care - without depending on unverified online sources or overloaded hospital hotlines.

## 2. Product context and integration scope

- Mother & Baby 360° is not a standalone application. It is designed as a sub-app / module embedded within Thu Cuc Hospital's existing patient application, reusing the host app's existing patient identity where feasible.

- The MVP avoids duplicating capabilities that already exist in the host app (e.g., full appointment booking) and instead focuses on the gap the host app does not fill: visibility into health status between visits, and an emotionally engaging pregnancy memory experience.

- Health information shown to the mother is sourced primarily from data captured during hospital visits (clinical/EMR records), not from routine daily self-measurement. This reflects the confirmed assumption that most expectant mothers do not routinely self-measure clinical metrics at home. Mothers may occasionally report a specific indicator the doctor flagged for follow-up, or a symptom they notice, and this report is what feeds the alert-checking flow described in Section 5. Mothers may also optionally log a small set of self-tracked metrics (weight, temperature, heart rate, sleep) for their own reference; these are never checked against thresholds and never raise an alert.

## 3. Target user (MVP)

- Primary MVP User: Expectant Pregnant Mothers (using the Mobile Application).

*Justification: The MVP is deliberately designed around the mother's end-to-end experience. The mother is the primary user who creates the pregnancy profile, reviews health information captured during visits, documents her pregnancy journey, reports symptoms when relevant, and uses the application as a daily companion. Clinical users remain supporting actors only where their involvement is necessary to verify a mother-reported concern and complete a safe escalation and follow-up process.*

- Supporting Clinical Users: Triage Nurses and Attending Doctors (using the Clinician Web Dashboard). They are secondary operational actors who support the mother's journey when a risk alert requires human verification, triage, escalation, or clinical follow-up.

## 4. Link to the Product Design Package (DBIZ2)

### Related system objectives

- MVP Primary Objective - Mom-Centered Continuous Care: Give expectant mothers an easy way to understand their health status between hospital visits, build an emotional connection to their pregnancy journey, and know when and how to seek help - through a simple daily mobile experience for health visibility, risk awareness, pregnancy guidance, and access to appropriate support.

- Instant Triage (AI & Nurse): Provide mothers with proactive risk awareness based on health information already captured during hospital visits and symptoms mothers choose to report, reducing uncertainty between scheduled visits without requiring daily self-measurement.

- Seamless Handover: When a mother's reported condition requires clinical attention, ensure relevant patient and remote-monitoring context can move to the appropriate nurse and doctor so that the mother does not have to repeat the entire situation manually.

- Daily Habit Formation: Build the application into a trusted daily pregnancy companion through the Pregnancy Timeline & Baby Memory Journal, health visibility, and diary-based engagement.

### Function scope

- Mother Functions - MVP focus: Open the sub-app with the TCI account (first-time consent), Set up pregnancy information (due date or last menstrual period), Manage profile, View Health Dashboard (sourced from hospital visit records, including watch-flags the doctor has placed on specific indicators), Log Optional Self-Tracked Metrics (weight, temperature, heart rate, sleep - no threshold check), Report a Flagged Indicator or Self-Observed Symptom, View Report Status & Care Team Response, View Notifications & Notification Settings, View & Build Pregnancy Timeline (visit-linked photos/milestones + personal memories), Manage Pregnancy Diary, Consult AI Chatbot, and Basic Appointment Booking (view/redirect to the host app's existing booking flow). These are prioritized according to their contribution to the mother's daily experience and core care journey..

- Supporting Nurse Functions: Process Medical Alerts, Triage Patient, and Access Patient Dashboard. Only the functions necessary to triage alerts raised from a mother's report - whether tied to a doctor-flagged indicator or a self-observed symptom - are considered supporting MVP capabilities.

- Supporting Doctor Functions: Access Patient Dashboard, Review Escalated Cases, Provide Consultation, and Update Patient Status. These functions are retained only to complete the clinical escalation loop initiated by the mother.

## 5. MVP scope priority — MoSCoW

Each item has an ID so that it can be followed into the specs (section 7).

| ID | Priority | Feature / item | Function mapping | Spec module | Notes / justification |
|---|---|---|---|---|---|
| M1 | Must | Patient Onboarding & Pregnancy Profile | Open sub-app with TCI identity + first-time consent, Set up pregnancy information, Manage profile | ACC | Foundation of the mother's journey. Establishes identity and pregnancy/gestational context so the rest of the mobile experience can be personalized and linked to the correct patient. Identity is reused from the TCI host app (Section 2); registration, OTP and password functions are not built in the sub-app. |
| M2 | Must | Health Visibility (Clinical Data Review) | View Health Dashboard (sourced from hospital visit records, incl. doctor's watch-flags), Log Optional Self-Tracked Metrics, Report a Flagged Indicator or Self-Observed Symptom | HLT (+ ALR for reporting) | The dashboard displays health data recorded during hospital visits (vitals, lab results, ultrasound findings), including any indicator the doctor flags for the mother to watch. Mothers are not required to self-measure or log vitals daily. Optionally, a mother may log weight, temperature, heart rate and sleep; these values are labelled "Self-entered", kept separate from visit data, and are never checked against thresholds. Fetal heart rate is taken only from hospital visits; its 110-160 bpm range is shown for reference and does not raise an alert. Data flow: Visit → doctor enters the record → system stores it → Dashboard displays it. Since live EMR integration is out of scope (see Won't), demo data for this feature is manually entered/simulated by the clinician role rather than pulled from a real hospital system. |
| M3 | Must | Risk Feedback & Health Alerts | Report a Flagged Indicator or Self-Observed Symptom, View Report Status & Care Team Response | ALR | Direction of the alert is mother → clinical team, not the reverse. Flow: (1) After a visit, the doctor may attach a watch-flag to a specific indicator for the mother to pay attention to at home - this is an informational note, not an alert; (2) the mother sees this note on her Dashboard; (3) if she later observes that flagged indicator, or a symptom, to be abnormal, she reports it (a measurable value where possible, or a description); (4) the system checks the report against predefined clinical thresholds (e.g., blood pressure ≥140/90 mmHg, abnormal proteinuria/glucose; fetal heart rate is not reported by the mother - it comes only from hospital visits and its 110-160 bpm range is for display only); (5) if it exceeds the threshold, the system raises an Alert and routes it to the Nurse for triage (see the Should-tier "Nurse Triage & Alert Verification" item below), escalating to the Doctor when needed; if no value exceeds the threshold but the mother reports a symptom, the report is still routed to the Nurse as a case (without an Alert); if no value exceeds the threshold and she reports no symptom, no case is created. Separately, the app also sends a routine Update Notification whenever a new visit record is added, distinct from a Risk Alert. The mother sees all her notifications (report responses, new visit results, appointment reminders) in a notification list, can mark them as read, and can switch notification types on or off in notification settings (new visit results, appointment reminders, doctor's-instruction reminders); report responses may stay always on so that she does not miss a reply from the care team - this is a team proposal pending confirmation. Note: this Must-tier item completes its loop together with Nurse Triage & Alert Verification (Should). |
| M4 | Must | Pregnancy Timeline & Baby Memory Journal | View/Build Pregnancy Timeline, Upload Ultrasound & Media, Manage Pregnancy Diary, Messages to Baby (pending Client approval) | TML | The feature has two parts: (1) Visit-linked milestones - ultrasound images and the doctor's notes, tied to each actual hospital visit; (2) Free-form diary - the mother can record how she's feeling or a memorable moment at any time, independent of visit dates. Each diary entry includes: entry date (automatic), free-text note, mood tag (optional), and attached photo (optional). Pending Client approval: (a) the weekly view shows content tied to the mother's actual visits instead of generic weekly tips / baby-size content (team decision D-02); (b) Messages to Baby - the mother and the father write short weekly messages (max 200 characters) on the mother's device; the father has no account of his own (team decision D-03). |
| M5 | Must | AI Chatbot L1 Support | Consult AI Chatbot | BOT | The chatbot directly answers simple, common maternity questions, helping mothers rely less on unverified sources. Technical direction: Python backend calling the OpenAI or Gemini API (n8n was ruled out, as it cannot support the custom question-classification and escalation logic needed). Input: the mother's question text plus light profile context (e.g., gestational week); the full medical record is not sent. A system prompt restricts the chatbot to general maternity knowledge and blocks personal diagnosis. Questions tied to a personal health condition, or matching risk keywords, are not answered directly - instead the chatbot offers to pass the question to a nurse and, only if the mother agrees ("Connect to nurse"), opens a case in the same Nurse/Doctor queue used for record-based alerts (Process Medical Alerts / Triage Patient), so escalation reuses one mechanism rather than a separate path. If she declines, no case is opened and the hospital hotline number is shown. |
| S1 | Should | Basic Appointment Booking | Connects the mother's digital journey to hospital care when an in-person consultation is appropriate | APT | Equivalent booking functionality already exists in the hospital's current app; the MVP will only surface/redirect to the existing flow rather than rebuilding it in full. |
| S2 | Should | Nurse Triage & Alert Verification | Process Medical Alerts, Triage Patient | CLI (+ ALR FR-004, FR-008, FR-009) | A supporting capability rather than the primary user experience. Triggered whenever a mother's report of a doctor-flagged indicator crosses the defined alert threshold, whenever her report includes a symptom (even if no value crosses the threshold), or when she agrees to pass a chatbot question to a nurse (see Must-tier "Risk Feedback & Health Alerts" and "AI Chatbot L1 Support"). The nurse verifies the report, judges severity, and either closes it with guidance or escalates it to the Doctor. |
| S3 | Should | Doctor Escalation & Follow-up | Review Escalated Cases, Update Patient Status | CLI | Completes the safety loop for higher-risk cases initiated by the mother. |
| W1 | Won't | Knowledge Base Search & Filtering | Access Knowledge Library | — (not specified) | Excluded from this MVP: the Session 4 assignment removes the Knowledge Base range (DBIZ2 functions F-145 - F-148, screens S-035 - S-036) from the specified modules. It would enhance the educational experience, but curated content within the core experience is already sufficient to meet basic needs. |
| W2 | Won't | In-App Payment Processing | N/A | — (not specified) | Excluded from scope due to conflicts with the hospital's current HIS workflow and financial integration risks. |
| W3 | Won't | Hardware Device Auto-Sync | N/A | — (not specified) | Excluded from scope to avoid hardware compatibility issues, keeping focus on visit-record-based health data and mother-reported symptoms. |
| W4 | Won't | Deep Two-Way HIS/EMR Integration | N/A | — (seed data instead, D-59) | Out of scope for the MVP to ensure rapid deployment and reduce dependency on external systems. The MVP demo uses simulated hospital visit data rather than a live, bidirectional EMR integration. |

## 6. Rough sprint backlog — Phase 1

| # | Item | Description and requirements | Spec module |
|---|---|---|---|
| 1 | Patient Onboarding & Pregnancy Profile | Define the sub-app entry from the TCI app (reuse TCI identity, first-time consent), profile fields, pregnancy setup (due date or last menstrual period), and the minimum information needed to personalize the mobile experience. | ACC |
| 2 | Health Visibility (Clinical Data Review) | Define the experience for viewing health data from hospital visit records (dashboard), the optional self-tracked metrics (weight, temperature, heart rate, sleep - no threshold check), plus the flow for reporting a flagged indicator or a self-observed symptom. | HLT |
| 3 | Risk Feedback & Health Alerts | Define the doctor's watch-flag on a visit record, the mother's report flow for that indicator or a self-observed symptom, the threshold check that raises an Alert to the Nurse (escalating to the Doctor when needed), the routing of symptom reports that do not cross a threshold, how the mother sees her report's status, and the mother's notification list and notification settings. | ALR |
| 4 | Pregnancy Timeline & Baby Memory Journal | Define the experience for storing ultrasound images tied to each visit, milestones based on actual visit dates, and the free-form diary flow with fields: date (auto), content, mood (optional), photo (optional); plus Messages to Baby (pending Client approval). | TML |
| 5 | AI Chatbot L1 Support | Define the scope of questions the chatbot answers directly (Python backend, OpenAI/Gemini API), the prompt guardrails, the hand-off flow into the Nurse/Doctor triage queue for personal-health-related questions (only after the mother agrees), and how answers are presented to the mother. | BOT |
| 6 | Basic Appointment Booking | Define the mother-facing entry point into appointment booking - the "Book a visit" button on Home and the Appointments tab open the host app's existing booking flow directly; there is no intermediate screen in the sub-app. Lightweight scope - surfaces/redirects to the host app's existing booking function rather than rebuilding slot selection, booking, or an appointments list. | APT |
| 7 | Clinical Escalation Support for Mom-Generated Alerts (Nurse Triage + Doctor Follow-up) | Define the minimum nurse verification and doctor follow-up workflow when a symptom or abnormal value requires clinical attention, including relevant patient context. | CLI |

## 7. Must items → spec modules

| ID | Must item | Spec document | Main FRs | Screens |
|---|---|---|---|---|
| M1 | Patient Onboarding & Pregnancy Profile | `specs/spec-ACC.md` | FR-001 – FR-005, FR-011, FR-015 – FR-027 | S-001, S-007 / S-046, S-008, S-009, S-010, S-011, S-083, S-103 |
| M2 | Health Visibility (Clinical Data Review) | `specs/spec-HLT.md`; reporting in `specs/spec-ALR.md` | HLT FR-001 – FR-005, FR-007 – FR-012; ALR FR-010 – FR-015, FR-020 | S-023, S-024, S-025, S-027, S-025A |
| M3 | Risk Feedback & Health Alerts | `specs/spec-ALR.md` | FR-001 – FR-003, FR-005 – FR-008, FR-016, FR-018 – FR-022 | S-025A, S-026, S-028, S-029, S-009 |
| M4 | Pregnancy Timeline & Baby Memory Journal | `specs/spec-TML.md` | FR-002 – FR-006, FR-008 – FR-011 (FR-011 pending Client, D-03) | S-048, S-051, S-052 |
| M5 | AI Chatbot L1 Support | `specs/spec-BOT.md` | FR-001 – FR-009 | S-031, S-032, S-033, S-034 |

Should items: S1 Basic Appointment Booking → `specs/spec-APT.md` (FR-001, FR-005, FR-009); S2 Nurse Triage & Alert Verification and S3 Doctor Escalation & Follow-up → `specs/spec-CLI.md` (with `spec-ALR.md` FR-004, FR-008, FR-009). Won't items are kept as Won't rows in `docs/function-list.md`.

## 8. Scope changes and their reasons

The decisions below changed or sharpened the scope while the specs were written; the full text and status of each is in `docs/decisions.md`.

`[NEEDS CLARIFICATION: which of these changes came after the scope confirmed with the Client in Session 3, and which were already part of it — owner Product/PM]`

| Decision | Change | Reason | Status |
|---|---|---|---|
| D-01 | Identity from the TCI app; no registration, OTP or password in the sub-app | MVP §2: the sub-app reuses the host app's identity | Pending Client |
| D-02 | Weekly tips / reference content removed from the timeline | Content is linked to real visits instead (MVP §5, Timeline row) | Pending Client |
| D-03, D-65 | "Messages to Baby" added to the Timeline Must item | Emotional engagement; no FR in DBIZ2 | Pending Client |
| D-11 | Metrics split into Group 1 (self-tracked, no threshold) and Group 2 (doctor-assigned, threshold); the mother reports only flagged Group 2 metrics or symptoms | MVP §2 and §5: mothers do not self-measure daily | Decided |
| D-12 | Fetal heart rate only from visits; 110 – 160 bpm shown for reference, never an alert | MVP §5, confirmed 29/09/2026 | Decided |
| D-34 | Chatbot case created only when the mother taps "Connect to nurse" | MVP §5 chatbot row: hand-off only after the mother agrees | Decided |
| D-49 | No Admin actor | MVP §3 names no Admin | Decided |
| D-59 | Visit data is seed data; no visit entry screen, no EMR integration | MVP §5: Deep HIS/EMR integration is Won't; demo data is simulated | Decided |
| APT-01 | Appointments: a redirect to the TCI app booking flow, no booking screen in the sub-app | MVP §5: equivalent booking exists in the host app | Decided |
| D-67 | Chatbot context also keeps the earlier questions / answers of the conversation | Dialogue continuity; the medical record is never sent | Decided (team) — to confirm with the Client |
