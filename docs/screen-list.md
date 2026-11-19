# Screen List (Group A)

ID scheme `S-{DBIZ2 ID}`; `S-025A` (D-38), `S-104` (D-74) and `S-105` (D-75) are existing non-DBIZ2 IDs; S-106 is proposed. Actor and Priority of in-scope screens are team inferences (DBIZ2 has neither column for screens).

## In-scope screens (63 DBIZ2 IDs + S-025A, S-104, S-105, proposed S-106)

| Actor | Function name | Screen ID | Screen name | Screen overview | Priority |
|---|---|---|---|---|---|
| Mom | ACC — Onboarding & Session | S-001 | Sub-app Entry & TCI Account Consent | 2 states: (1) "Mother & Baby 360" tile on the TCI app home; (2) first launch: permission to use TCI account info + accept terms. No phone/password login. No valid TCI identity (opened outside the TCI app, expired, invalid) → S-043; there is no login screen (D-50). Permission list also names the date of birth; a non-female TCI account sees a notice and returns to the TCI app (D-71, not drawn); after agreeing → S-104 (D-74) *(Wireframe title: Mother & Baby 360; DBIZ2 mockup: Yes; drawn: Yes — to redraw.)* | Must |
| Mom | ACC — Onboarding & Session | S-104 | Onboarding Guide | **New ID (D-74)** — not a DBIZ2 row. Shown once after the first agreement on S-001, before pregnancy setup; pages + "Skip" / "Next" (ACC FR-028). Screen spec file: `screen-spec-S-104.md` *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | ACC — Onboarding & Session | S-007 | Pregnancy Setup | Enter due date **or** first day of last period → system computes gestational week; height, weight and the first antenatal check-up date optional (D-72). Screen spec file: `screen-spec-S-007.md` (covers S-046) *(Wireframe title: Pregnancy setup; DBIZ2 mockup: No; drawn: Yes (shared with S-046).)* | Must |
| Mom | ACC — Onboarding & Session | S-008 | Home | Gestational week + due date (→ S-048); new visit-result notice; "My reports" card (replaces "Risk assessment" — ALR-01); "Doctor's instructions" card; 4 self-tracked metric cards with measured time; read-only next-appointment card; proposed D-108 adds the host handoff only when no upcoming appointment exists. Root bar: Home · Timeline · Chatbot · From doctor · Profile (D-80 / D-86). No "Normal" banner. "Notifications" button → S-009 (D-39) *(Wireframe title: Home; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | SHARED — cross-cutting | S-009 | Notification Center | Opened from the "Notifications" button on S-008 (D-39). Filter chips All / Report / Visit result / Appointment / Instruction reminder (new — ACC-02); unread dot; report → S-026, new visit result → S-023, appointment → TCI app flow, instruction reminder → S-027 (proposed). Does not use the word "Alert" (reserved for S-028). FR: `spec-ACC.md` FR-025 / FR-026, `spec-ALR.md` FR-018, FR-019, FR-022 (D-48; Must — D-56) *(Wireframe title: Notifications; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | ACC — Onboarding & Session | S-010 | Notification Settings | Opened from S-103 (D-39). 4 toggles: Report responses (locked on — **team proposal**, not a Client requirement `[NEEDS CLARIFICATION]`), New visit results, Appointment reminders (Could — D-77), Doctor's-instruction reminders *(Wireframe title: Notification settings; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | ACC — Onboarding & Session | S-011 | Edit Profile | Opened from S-103 "Edit profile" (D-39). Name and phone locked (from TCI account); due date locked once the hospital record is linked; height editable; Cancel / Save changes. Height valid range pending D-16 *(Wireframe title: Edit profile; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | APT — Appointment (redirect to host app) | S-012 | Appointment Home Screen | **Handled by Host App (Redirect only).** DBIZ2 full-booking mockup exists but APT redirects to the TCI host app instead — see `spec-APT.md`. Entry point belongs to the TCI host app, not a sub-app Home CTA or tab (APT BR-003; D-80 / D-86). Not built in the sub-app (APT-03) *(Wireframe title: —; DBIZ2 mockup: Yes; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-013 | Visit Reason Screen | **Handled by Host App (Redirect only).** Select reason for medical visit *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-014 | Clinic & Date Selection Screen | **Handled by Host App (Redirect only).** Same note as S-012 *(Wireframe title: —; DBIZ2 mockup: Yes; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-015 | Time Slot Selection Screen | **Handled by Host App (Redirect only).** Same note as S-012 *(Wireframe title: —; DBIZ2 mockup: Yes; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-016 | Slot Unavailable Screen | **Handled by Host App (Redirect only).** Notification when selected slot is unavailable *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-017 | Appointment Review Screen | **Handled by Host App (Redirect only).** Same note as S-012 *(Wireframe title: —; DBIZ2 mockup: Yes; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-018 | Appointment Success Screen | **Handled by Host App (Redirect only).** Same note as S-012 *(Wireframe title: —; DBIZ2 mockup: Yes; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-019 | Appointment Detail Screen | **Handled by Host App (Redirect only).** Appointment details with QR code for check-in *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-020 | Appointment List Screen | **Handled by Host App (Redirect only).** List of user's appointments *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-021 | Appointment Cancellation Screen | **Handled by Host App (Redirect only).** Appointment cancellation confirmation dialog *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | APT — Appointment (redirect to host app) | S-022 | Cancellation Success Screen | **Handled by Host App (Redirect only).** Appointment cancellation success confirmation *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | HLT — Health Visibility | S-023 | Health Metrics (hub) | 3 zones: latest visit results (fetal heart rate with its 110–160 bpm reference range, no label — D-12) / cards S-027 "Doctor's instructions" (names of flagged metrics) + S-029 "My reports" (highlighted; replaces "Risk assessment") / self-tracked metrics. Refresh button; "View metric history" → **S-025**. No height, BMI or "Overall" *(Wireframe title: Health metrics; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | HLT — Health Visibility | S-024 | Self-tracking Metric Entry (group 1) | Group-1 metrics (weight, temperature, heart rate, sleep), measured time per metric; no height; CTA "Save metrics"; **no threshold check** *(Wireframe title: Enter self-tracked metrics; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | HLT — Health Visibility | S-025 | Metric History | DBIZ2 ID "Health History" (D-38). Choose metric, filter from date – to date, chart (threshold line for group-2 metrics; 110–160 bpm reference lines for fetal heart rate, no label; none for group 1), average / min / max, list of measurements with source label. Opened from "View metric history" (S-023, S-027). HLT FR-009 – FR-012 *(Wireframe title: Metric history; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | ALR — Risk Feedback & Health Alerts | S-025A | Report Metric / Symptom (shared) | **Suffixed ID (D-38)** — not a DBIZ2 row. One shared screen for blood pressure, blood glucose, urine protein and symptoms; blood pressure threshold systolic ≥ 140 or diastolic ≥ 90 mmHg (D-14); symptoms multi-select dropdown: the PRD alarm symptoms (Vaginal bleeding, Severe abdominal pain, Waters breaking / fluid leakage, Severe headache / dizziness / blurred vision, Absence of fetal movement), Palpitations, Other (free text ≤100 chars) — D-73, image to redraw; CTA "Submit report". Blood glucose requires measurement time (Fasting / 1 h after meal / 2 h after meal); thresholds blood glucose ≥5.3 / ≥7.8 / ≥6.7 mmol/L, urine protein ≥1+ (D-15, team-set, needs Thu Cuc doctor confirmation). Routing after submit (D-19) applies to all 3 group-2 metrics: above threshold → S-028 regardless of symptoms; not above threshold + symptoms → S-026 (Not viewed); not above threshold + no symptoms → back to S-027, no case created *(Wireframe title: Report a metric; DBIZ2 mockup: Supplied (non-DBIZ2); drawn: Yes.)* | Must |
| Mom | ALR — Risk Feedback & Health Alerts | S-026 | Report Status | **ID reused — not DBIZ2's original S-026.** 4 statuses: Not viewed → Viewed → Escalated to doctor → Resolved; label "Above threshold"; shows selected symptoms; skipped step shows "No doctor escalation needed"; "Safety note" only while there is no response; ← button (D-53) *(Wireframe title: Report status; DBIZ2 mockup: Supplied (non-DBIZ2); drawn: Yes.)* | Must |
| Mom | HLT — Health Visibility | S-027 | Doctor's Instructions | **ID reused — not DBIZ2's original S-027.** Group-2 metrics only; each card shows doctor name, date prescribed, label "Doctor-assigned", "+ Report metric" (→ S-025A), "View metric history" (→ S-025); plus "+ Report symptoms". ("+ Report another metric" removed — ALR-02.) No temperature card. Back → S-023 *(Wireframe title: Doctor's instructions; DBIZ2 mockup: Supplied (non-DBIZ2); drawn: Yes.)* | Must |
| Mom | ALR — Risk Feedback & Health Alerts | S-028 | Metric Alert | Popup over S-025A. Example is blood pressure, with measured time and threshold; "sent to clinical staff"; doctor's guidance (template or custom); buttons View status (→ S-026), Call hotline / nurse, Close. Only screen that uses the word "Alert" *(Wireframe title: Metric alert; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | ALR — Risk Feedback & Health Alerts | S-029 | My Reports | **One list, no tabs** (revised 29/09/2026 — ALR-01, D-06 revised). The mother's reports and chatbot cases (D-34) with their status; filters by status and by type (metric / Symptom / Chatbot). The former tab 1 "Risk assessment" is removed (not in the MVP Scope). *(Wireframe title: My reports; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | BOT — AI Chatbot L1 Support | S-031 | Chatbot Home Screen | Disclaimer line "reference information, does not replace your doctor's advice"; 4 suggested questions; CTA "Send" *(Wireframe title: Chatbot; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |
| Mom | BOT — AI Chatbot L1 Support | S-032 | Chatbot Input Screen | Drawn as one conversation frame with S-033/S-034. Screen spec file: `screen-spec-S-034.md` (covers S-032/S-033). Own full spec `screen-spec-S-032.md` (own full spec — D-55) + `img/S-032.png` (copy of the shared image) *(Wireframe title: Chatbot conversation; DBIZ2 mockup: No; drawn: Yes (shared S-032–S-034).)* | Must |
| Mom | BOT — AI Chatbot L1 Support | S-033 | Chatbot Processing Screen | "•••" typing state in the shared conversation frame. Own full spec `screen-spec-S-033.md` (own full spec — D-55) + `img/S-033.png` (copy of the shared image) *(Wireframe title: Chatbot conversation; DBIZ2 mockup: No; drawn: Yes (shared S-032–S-034).)* | Must |
| Mom | BOT — AI Chatbot L1 Support | S-034 | Chatbot Response Screen | Chat bubbles, hand-off to nurse (Connect to nurse / No, thanks) — BOT FR-006 – FR-009, BR-002. No answer rating (BOT-02). A case is created only when the mother taps "Connect to nurse"; "No, thanks" → no case, hotline shown; reply tracked in S-029 "My reports" → S-026 (D-34) *(Wireframe title: Chatbot conversation; DBIZ2 mockup: No; drawn: Yes (shared S-032–S-034).)* | Must |
| Mom | BOT — AI Chatbot L1 Support | S-037 | Response Rating | Modal allowing users to rate AI response. **Not built in the MVP (BOT-02):** not in the MVP Scope; no FR or entity stores a rating; the inline "Yes / No" in S-034 is removed *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Could |
| Any (cross-cutting) | SHARED — cross-cutting | S-038 | Network Error | Displayed when internet connection is lost. Uses the shared empty / loading / error template (`docs/ui-label-reference.md`, section "UI conventions") *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Any (cross-cutting) | SHARED — cross-cutting | S-039 | Maintenance | System maintenance notification *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Any (cross-cutting) | SHARED — cross-cutting | S-040 | Page Not Found | 404 page not found screen *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Any (cross-cutting) | SHARED — cross-cutting | S-041 | Global Loading | Generic loading overlay. See the shared template (`docs/ui-label-reference.md`, section "UI conventions") *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Any (cross-cutting) | SHARED — cross-cutting | S-042 | Permission Denied | Displayed when required permissions are denied *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Any (cross-cutting) | SHARED — cross-cutting | S-043 | Session Expired | Used when the TCI identity has expired or is invalid, or the sub-app is opened outside the TCI app: explanatory sentence + "Back to TCI app" button (D-50). Screen spec: `screen-spec-S-043.md` *(Wireframe title: Session expired; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-044 | Pregnancy Timeline Entry | Entry point to Pregnancy Timeline. The gestational-week card on S-008 opens S-048 *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-045 | Due Date Check Screen | System check for existing due date (non-UI logic) *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-046 | Due Date Input Screen | Drawn in the same frame as S-007; see S-007. Own full spec `screen-spec-S-046.md` (own full spec — D-55) + `img/S-046.png` (copy of the shared image) *(Wireframe title: Pregnancy setup; DBIZ2 mockup: No; drawn: Yes (shared with S-007).)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-047 | Due Date Confirmation Screen | Confirmation that due date is saved *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-048 | Pregnancy Timeline (weekly) | Week selection with arrows; content tied to **real visits** (ultrasound image, measurements from the visit form, doctor's note); no Tips or "Size of" content (**scope change, pending Client approval** — D-02; TML FR-001/FR-007); "Messages to Baby" (mom & dad; TML FR-011, **Must item, pending Client approval** — D-03, D-65); week diary + "+ Add diary entry" (→ S-051). **D-75:** indicators of the week listed by day + visit card on top, diary and messages below; "My journey" → S-105 *(Wireframe title: Pregnancy timeline; DBIZ2 mockup: Yes; drawn: Yes — to redraw.)* | Must |
| Mom | APT | S-106 | Lịch khám | Proposed D-88 read-only current and historical host appointments, reached from S-008 and S-009 | Could |
| Mom | TML — Pregnancy Timeline & Diary | S-105 | My Journey & Album | **New ID (D-75)** — not a DBIZ2 row. Journey review by stage (trimesters, boundaries Pending SME) and PDF keepsake album export (TML FR-013, FR-014). Screen spec file: `screen-spec-S-105.md` *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-049 | Pregnancy Week Scroll Screen | Scroll through pregnancy weeks *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-050 | Pregnancy Week Detail Screen | Detailed view of a selected pregnancy week *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-051 | Add Diary Entry | Popup form: auto date, content, mood, photo. Screen spec file: `screen-spec-S-051.md` (covers S-052) *(Wireframe title: Add diary entry; DBIZ2 mockup: No; drawn: Yes (shared with S-052).)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-052 | Pregnancy Memory Upload Screen | Photo upload is part of the S-051 popup. Own full spec `screen-spec-S-052.md` (own full spec — D-55) + `img/S-052.png` (copy of the shared image) *(Wireframe title: Add diary entry; DBIZ2 mockup: No; drawn: Yes (shared with S-051).)* | Must |
| Mom | TML — Pregnancy Timeline & Diary | S-053 | Pregnancy Memory Save Success Screen | Confirmation that diary is saved *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Must |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-054 | Nurse Login | Login screen for nurses *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-055 | Nurse Home Screen | Main nurse dashboard *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-056 | Alert Management Screen | Entry screen for alert management *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-057 | Alert List Screen | List of pending alerts *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-058 | Alert Detail Screen | Detailed view of a selected alert *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-059 | Doctor Notification Screen | Notify doctor about escalated alerts — inside the clinical web, behind the "Notifications" button on S-061; no push / SMS (ALR-03) *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-060 | Doctor Login Screen | Login screen for doctors *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse / Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-061 | Cases to Handle (web) | One table of cases: case source, threshold label, status; filter by the 4 statuses; no Search, Schedule, Messages or START CALL. Header shows the logged-in role ("Nurse: Trần Thị B" / "Dr. Nguyễn Văn A"; drawn as Nurse); nurse "Escalate to doctor" → status "Escalated to doctor" + high-priority notification to the assigned doctor inside the clinical web (ALR FR-009, ALR-03). Doctor: default filter "Escalated to doctor" (CLI-02). No Quick notes panel (CLI-03). Urine protein label "Above threshold" per D-15; nurse may close only non-escalated cases (D-37). Spec: `specs/spec-CLI.md` *(Wireframe title: Cases to handle; DBIZ2 mockup: Yes; drawn: Yes.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-062 | Patient List Screen | List of assigned patients *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-063 | Patient Selection Screen | Select a patient from the list *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse / Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-064 | Mother Quick Profile (web) | Case actions (Mark as viewed, Escalate to doctor, Send guidance, Close case); "Doctor's instructions" + add/edit form with "Above-threshold guidance"; chart ("From visit" / "Doctor-assigned" only — no self-tracked card, CLI-01); source labels; chatbot-case variant of the Report block (question instead of value — not drawn). No SpO2, Bluetooth, Call/Message or documents. **Permissions (D-37, D-43, D-44):** Nurse — view, mark as viewed, escalate to doctor, send guidance, close case **only if not yet escalated** ("Close case" hidden/locked for the nurse once "Escalated to doctor"). Doctor — view; on escalated cases only: send guidance, close case = clear red flag (D-44); add/edit instructions; no "Mark as viewed" (D-43 revised, CLI-02). "Send guidance" does not change status; "Close case" → Resolved. Instruction form labelled "Doctor only". Spec: `specs/spec-CLI.md` *(Wireframe title: Mother quick profile; DBIZ2 mockup: Yes; drawn: Yes.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-065 | Risk Alert Review Screen | Review patient risk alerts *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-066 | Smart Messaging Screen | Secure communication hub *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-067 | Clinical Decision Screen | Clinical intervention decision screen *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-068 | Patient Status Update Screen | Update patient status after intervention *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Nurse/Doctor | CLI — Clinical Escalation (Nurse + Doctor) | S-069 | Care Note Screen | Create care notes or recommendations *(Wireframe title: —; DBIZ2 mockup: No; drawn: No.)* | Should |
| Mom | ACC — Onboarding & Session | S-083 | Close Sub-app Confirmation | Buttons Stay / Close app (in place of logout). Screen spec file: `screen-spec-S-083.md` *(Wireframe title: Close Mother & Baby 360?; DBIZ2 mockup: No; drawn: Yes.)* | Must |
| Mom | ACC — Onboarding & Session | S-103 | Personal | FTU-Hub pattern: avatar, name, record ID; Edit profile, Pregnancy information, Hospital record link, Notification settings, Support. No logout, change password or delete account. **2 states in `img/S-103.png` (D-39):** (1) menu; (2) bottom sheet "Hospital record link" (no new ID) — link status "Linked" / "Pending link" set by seed data; no link error / Retry (ACC-01, D-61). Edit profile → S-011; Notification settings → S-010; Support → hand-off to the TCI app's support page (no screen in the sub-app) *(Wireframe title: Profile; DBIZ2 mockup: Yes; drawn: Yes.)* | Must |

### Not a screen

`00-QUY-UOC` in the wireframe is the UI-conventions page (terms, statuses, formats, CTAs, tab per screen, shared empty / loading / error templates). It has no Screen ID; its content is in `docs/ui-label-reference.md`, section "UI conventions" (D-27); the image stays in the team's wireframe set.

### DBIZ2 IDs `S-025`–`S-027`

DBIZ2's `ST` sheet assigns `S-025`–`S-027` to "Health History", "Sync Loading" and "Sync Success Screen" — three `HLT` screens without a DBIZ2 mockup.

**Decision D-57: the reuse of `S-026` and `S-027` is kept.** DBIZ2 "Sync Loading" and "Sync Success Screen" belong to the manual-sync flow, which is not built (Hardware Device Auto-Sync = Won't; no sync screen is drawn), so the two IDs carry no DBIZ2 mockup or content that could be lost. Renumbering "Report status" and "Doctor's instructions" now would change IDs already used in the specs, the screen specs, the images and the data model. The DBIZ2 meaning of both IDs stays recorded in this table. See `docs/decisions.md` decision log, D-57.

| DBIZ2 ID | DBIZ2 name | DBIZ2 module | Use in this package |
|---|---|---|---|
| S-025 | Health History | HLT | ID holds "Metric history" (D-38). The supplied report screen uses **S-025A** |
| S-026 | Sync Loading | HLT | ID holds "Report status" (supplied, non-DBIZ2) — **kept, D-57** |
| S-027 | Sync Success Screen | HLT | ID holds "Doctor's instructions" (supplied, non-DBIZ2) — **kept, D-57**. Post-submit routing: see the S-025A row |

## Removed (6)

Listed for traceability. Screen spec files for these are marked **Removed**, not deleted.

| Actor | Function name | Screen ID | Screen name | Screen overview | Priority |
|---|---|---|---|---|---|
| Mom | ACC — Onboarding & Session | S-002 | Account registration Screen | **Removed.** Sub-app uses the TCI account; no registration. Basis: D-01. **Pending Client confirmation** | Removed |
| Mom | ACC — Onboarding & Session | S-003 | OTP Verification Screen | **Removed.** Same as S-002. Basis: Same | Removed |
| Mom | ACC — Onboarding & Session | S-004 | Success Verification Screen | **Removed.** Same as S-002. Basis: Same | Removed |
| Mom | ACC — Onboarding & Session | S-005 | Forgot Password Screen | **Removed.** Same as S-002. Basis: Same | Removed |
| Mom | ACC — Onboarding & Session | S-006 | Password Reset Success Screen | **Removed.** Same as S-002. Basis: Same | Removed |
| Mom | ALR — Risk Feedback & Health Alerts | S-030 | Risk Recommendation Screen | **Removed.** Recommendations shown in S-028 and S-026 instead. Basis: D-05 | Removed |

## Screens outside MVP scope (Won't) (34)

| Actor | Function name | Screen ID | Screen name | Screen overview | Priority |
|---|---|---|---|---|---|
| Mom | — (outside the 7 modules) | S-035 | Knowledge Article List Screen | Knowledge Base range — the MVP Scope §5 lists it as Could-tier, but the Session 4 assignment document excludes `F-145`-`F-148`/this screen range from the 7 specced modules; this package follows the narrower reading — see `docs/decisions.md`, "Module scope and key corrections". Has a DBIZ2 mockup that goes unused | Won't (this package) |
| Mom | — (outside the 7 modules) | S-036 | Knowledge Article Detail Screen | Same note as `S-035`. Has a DBIZ2 mockup that goes unused | Won't (this package) |
| Doctor + Nurse | — (outside the 7 modules) | S-070 | Doctor Appointment List Screen | Full native appointment/doctor-schedule ecosystem — see `spec-APT.md` §1 | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-071 | Doctor Appointment Detail Screen | Full native appointment/doctor-schedule ecosystem | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-072 | Schedule Confirmation Screen | Full native appointment/doctor-schedule ecosystem | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-073 | Appointment Rescheduling Screen | Full native appointment/doctor-schedule ecosystem | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-074 | Personal Schedule Screen | Doctor/nurse self-management of their own schedule — out of MVP function scope per the Session 4 assignment document | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-075 | Schedule Change Request Screen | Doctor/nurse schedule self-management | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-076 | Schedule Submission Screen | Doctor/nurse schedule self-management | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-077 | Medication Module Screen | Medication/e-prescription — not named in the MVP Scope; see `spec-CLI.md` §10 Q1 | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-078 | Medication List Screen | Medication/e-prescription | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-079 | Medication Prescription Screen | Medication/e-prescription | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-080 | Prescription Confirmation Screen | Medication/e-prescription | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-081 | Message List Screen | Dedicated messaging module beyond the "Smart Messaging" hub (S-066) | Won't |
| Doctor + Nurse | — (outside the 7 modules) | S-082 | Conversation Detail Screen | Dedicated messaging module | Won't |
| Admin | — (outside the 7 modules) | S-084 | Admin Login Screen | Full administrative management ecosystem; the MVP Scope has no Admin actor (§3) | Won't |
| Admin | — (outside the 7 modules) | S-085 | Admin 2FA Verification Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-086 | Admin Dashboard Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-087 | Medical CMS Home Screen | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-088 | Pregnancy Timeline List Screen (CMS) | Content-management back office (editing timeline content, distinct from the mother-facing TML screens) | Won't |
| Admin | — (outside the 7 modules) | S-089 | Pregnancy Week Editor Screen | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-090 | Knowledge Base Screen (CMS) | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-091 | Article List Screen (CMS) | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-092 | Article Detail Screen (CMS) | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-093 | New article Screen | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-094 | Confirmation Screen (CMS) | Content-management back office | Won't |
| Admin | — (outside the 7 modules) | S-095 | User Management Home Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-096 | User Search Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-097 | User Detail Screen (Admin) | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-098 | User Action Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-099 | Schedule Management Screen (Admin) | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-100 | User Schedule Screen (Admin) | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-101 | User detail schedule Screen | Full administrative management ecosystem | Won't |
| Admin | — (outside the 7 modules) | S-102 | Schedule editor Screen | Full administrative management ecosystem | Won't |

## Build scope

Classification of the 67 in-scope IDs including proposed S-106 by how each one is delivered. It is derived only from the columns above (drawn / module / notes); it does not add or remove any screen.

| Build scope | Count | Screen IDs | What exists in this package |
|---|---|---|---|
| **A. Build — drawn, own screen spec + image** | 27 | S-001, S-007, S-008, S-009, S-010, S-011, S-023, S-024, S-025, S-025A, S-026, S-027, S-028, S-029, S-031, S-032, S-033, S-034, S-043, S-046, S-048, S-051, S-052, S-061, S-064, S-083, S-103 | `screens/screen-spec-{ID}.md` + `screens/img/{ID}.png`. Images to redraw after the PRD alignment (14/10/2026): S-001, S-007 / S-046, S-008, S-025A, S-034, S-048, S-064 (chatbot variant) |
| **A2. Build — specified, not drawn yet (new IDs)** | 3 | S-104 (D-74), S-105 (D-75), S-106 (proposed D-88) | `screens/screen-spec-{ID}.md` only; image to be drawn |
| **B. Handled by Host App (Redirect only)** | 11 | S-012 – S-022 | No screen in the sub-app; booking controls belong to the TCI host app; no sub-app Home booking CTA or Appointments tab (`spec-APT.md` §1, BR-003; D-80 / D-86). Listed for traceability only |
| **C. Covered inside another screen or a shared template — no own spec** | 6 | S-037 (Could — not built in the MVP, BOT-02), S-038 and S-041 (shared error / loading templates, `docs/ui-label-reference.md` "UI conventions"), S-044 (the gestational-week card on S-008 opens S-048), S-045 (non-UI check), S-053 (toast "Diary entry saved" after S-051) | Described in the screen spec named in brackets |
| **D. In scope, not drawn — delivery not decided** | 20 | S-039, S-040, S-042, S-047, S-049, S-050, S-054 – S-060, S-062, S-063, S-065 – S-069 | Listed for traceability only. `[NEEDS CLARIFICATION: for each ID — build it, merge it into a drawn screen, or drop it?]` Known links: S-047 ↔ `screen-spec-S-046.md` §9 Q5; S-049 / S-050 ↔ week arrows on S-048; S-054 / S-060 ↔ staff sign-in (`spec-CLI.md` §10 Q11); S-059 ↔ `screen-spec-S-061.md` §9 Q4 |

## Reconciliation

- **103 DBIZ2 screen IDs** = 63 in scope (56 module rows + 7 `SHARED`) + 6 Removed + 34 Won't.
- **+3 IDs outside the 103:** `S-025A` (supplied report screen, D-38), `S-104` (onboarding guide, D-74) and `S-105` (journey review & album, D-75). S-106 is proposed under D-88.
- **Screens drawn:** 27 IDs in 23 drawings — S-001, S-007/S-046, S-008, S-009, S-010, S-011, S-023, S-024, S-025, S-025A, S-026, S-027, S-028, S-029, S-031, S-032/S-033/S-034, S-043, S-048, S-051/S-052, S-061, S-064, S-083, S-103 — plus the UI-conventions page (text in `docs/ui-label-reference.md`). S-043 is drawn in the same style but is not part of the wireframe file. **27 image files** (the 4 shared IDs S-046, S-032, S-033, S-052 have image copies — D-55).

## Open items that affect this list

1. **Sub-app model** needs Client confirmation. If rejected, S-002 – S-006 return to scope and S-001 / S-083 / S-103 revert (D-01). S-043 also depends on D-01.
2. **S-048 scope changes** (no Tips; "Messages to Baby" added) need Client approval (D-02, D-03). In the latest MVP Scope "Messages to Baby" is in the Must item, pending Client approval (D-65).
3. Thresholds for blood glucose / urine protein (D-15) are team-set and need Thu Cuc doctor confirmation; valid input ranges (D-16) still open.
