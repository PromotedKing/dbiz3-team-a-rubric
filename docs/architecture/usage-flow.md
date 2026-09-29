# Usage Flow

## MVP — sub-app entry flow

Same flow as `spec-ACC.md` §4.1 (from the wireframe annotations of S-001, S-007, S-008 — not a DBIZ2 diagram; `[PENDING CLIENT: D-01]`). It replaces the DBIZ2 "Login / Register → User Logged In? → Register Account / Login → Land Home Page" part of every MOM flow below. Updated 29/09/2026: the "no valid TCI identity → S-043" branch is added (D-50); the same S-043 also appears if the identity expires mid-session.

```mermaid
flowchart TD
    S(["Start: TCI app home screen"]) --> T["Tap the 'Mother & Baby 360' tile (S-001 state 1)"]
    T --> ID{"Valid TCI identity received?"}
    ID -- No --> SE["Session expired (S-043): explanation + 'Back to TCI app' (D-50)"] --> X
    ID -- Yes --> FO{"First opening / not yet agreed?"}
    FO -- Yes --> C["Connect to TCI account + agree to terms (S-001 state 2)"]
    C -- "Later" --> X(["Close sub-app, return to TCI app"])
    C -- "Agree & continue" --> EDD{"Due date already known?"}
    FO -- No --> H["Home (S-008)"]
    EDD -- No --> P["Pregnancy setup (S-007 + S-046): due date or first day of last period; height, weight optional"] --> H
    EDD -- Yes --> H
    H --> E(["End"])
```

---

## MOM

### Chat box

**DBIZ2 original** (Figure 3, `Schematic2`) — reference only.

```mermaid
flowchart TD
    S(["Start"]) --> LR["Login / Register"]
    LR --> LI{"User Logged In?"}
    LI -- No --> RA["Register Account"] --> LR
    LI -- Yes --> LG["Login"] --> LH["Land Home Page"] --> OC["Open Chatbot"] --> SQ["Send question"]
    SQ --> KB{"Is question in Knowledge Base?"}
    KB -- Yes --> KL["Knowledge Library"] -->|"Related articles"| KAL["Knowledge Article List"] --> KAD["Knowledge Article Detail"]
    KB -- No --> RCR["Receive chatbot reply"] --> RR["Rate Response"] --> E(["End"])
```

**MVP flow** — `spec-BOT.md` FR-006 – FR-009; D-34. The Knowledge Library branch is not built (Knowledge Base = Won't). "Rate Response" is not built (BOT-02).

```mermaid
flowchart TD
    S(["Start"]) --> H["Home (S-008)"] -->|"Chatbot tab"| OC["Chatbot (S-031)"] --> SQ["Send a question (S-032)"] --> W["Waiting for the answer: '•••' (S-033)"]
    W --> PQ{"Personal health question or risk keyword? (BOT FR-006, BR-002)"}
    PQ -- No --> ANS["Answer + disclaimer (S-034)"] --> E(["End"])
    PQ -- Yes --> OFF["'This needs a proper consultation' + 'Connect to nurse' / 'No, thanks' + hotline (S-034, BOT FR-007)"]
    OFF -- "Connect to nurse" --> CASE["Case created: source Chatbot, status Not viewed (BOT FR-008 → ALR FR-021)"] --> FOL["Mother follows it: S-029 'My reports' → S-026"] --> E
    OFF -- "No, thanks" --> HOT["No case; the hotline number is shown (BOT FR-009)"] --> E
```

### Pregnancy timeline

**DBIZ2 original** (Figure 3) — reference only. Two sub-flows: browsing the weekly dashboard, and adding a diary entry.

```mermaid
flowchart TD
    S1(["Start"]) --> TPT1["Tap Pregnancy Timeline"] --> DD1{"Is Due Date Set?"}
    DD1 -- No --> IDD1["Input Due Date, Tap Confirm"] --> WD1["Weekly Dashboard: View fetal image, size, tips"]
    DD1 -- Yes --> WD1
    WD1 --> SPW["Scroll Previous or Future Weeks"] --> VWI["View Week Info"] --> LB["Loop back to Dashboard"] --> E1(["End"])
```

```mermaid
flowchart TD
    S2(["Start"]) --> TPT2["Tap Pregnancy Timeline"] --> DD2{"Is Due Date Set?"}
    DD2 -- No --> IDD2["Input Due Date, Tap Confirm"] --> WD2["Weekly Dashboard: View fetal image, size, tips"]
    DD2 -- Yes --> WD2
    WD2 --> ATD["Add to diary"] --> UPN["Upload Photo or Save Note"] --> SYS2["System saves and returns to Dashboard"] --> E2(["End"])
```

**MVP flows** — `spec-TML.md`. The week shows the real visit of that week, not generic "fetal image, size, tips" (D-02, D-04 `[PENDING CLIENT: D-02]`); the due date is set in the entry flow, so there is no "Input Due Date" step here.

Browse by week:

```mermaid
flowchart TD
    S(["Start"]) --> H["Home (S-008)"] -->|"Pregnancy timeline ›"| W["Week view (S-048): the week's visit (ultrasound image, measurements, doctor's note — seed data) or 'No visit this week.', diary entries + Messages to Baby (pending Client — D-03)"]
    W --> NAV{"Another week?"}
    NAV -- "‹ / ›" --> W
    NAV -- No --> E(["End"])
```

Add a diary entry:

```mermaid
flowchart TD
    S(["Start"]) --> W["Week view (S-048)"] -->|"+ Add diary entry"| F["Add diary entry (S-051): content (required), mood (optional), photo(s) (optional, up to 5 — S-052; number pending team lead, TML-01)"]
    F -- "Cancel" --> W
    F -- "Save diary entry" --> V{"Valid?"}
    V -- No --> ERR["Field error; the entry is not saved"] --> F
    V -- Yes --> OK["Toast 'Diary entry saved' (S-053); back to S-048; the entry is read-only (D-60)"] --> E(["End"])
```

Messages to Baby — Must item in the latest MVP Scope, **pending Client approval** `[PENDING CLIENT: D-03]` (the input form is not drawn — `spec-TML.md` §10 Q12):

```mermaid
flowchart TD
    S(["Start"]) --> W["Week view (S-048)"] -->|"+ Message from Mom / + Message from Dad"| M["Write a message (≤ 200 characters; the father writes on the mother's device)"]
    M --> SV["Save"] --> SH["Message shown in the week's 'Messages to Baby' card"] --> E(["End"])
```

### Health metric

**DBIZ2 original** (Figure 3) — reference only.

```mermaid
flowchart TD
    S(["Start"]) --> LR["Login / Register"] --> LI{"User Logged In?"}
    LI -- No --> RA["Register Account"] --> LR
    LI -- Yes --> LG["Login"] --> LH["Land Home Page"] --> OD["Open health dashboard"] --> CL["Choose log in health metrics"]
    CL --> HH{"Health history?"}
    HH -- no --> MS["Manual sync"] --> MSS["Manual Sync Success"] --> VC["View health charts, flagged values, risk assessment"]
    HH -- yes --> VC
    VC --> RR["Receive Risk Recommendation"] --> E(["End"])
```

**MVP flows** — `spec-HLT.md`, `spec-ALR.md`. There is no manual or device sync (Hardware Device Auto-Sync = Won't); guidance is shown on S-028 / S-026 instead of a "Risk Recommendation" screen (D-05).

View health metrics and log self-tracked metrics:

```mermaid
flowchart TD
    S(["Start"]) --> H["Home (S-008)"] -->|"Health tab / Health metrics ›"| HM["Health metrics (S-023): latest visit results (fetal heart rate with 110–160 bpm reference range, no label), Doctor's instructions (flagged metrics), My reports card, self-tracked metrics"]
    HM --> CH{"What does the mother open?"}
    CH -- "+ Enter self-tracked metrics" --> ST["Weight / temperature / heart rate / sleep (S-024)"] --> SV["Save metrics: labelled 'Self-entered', no threshold check (D-07)"] --> HM
    CH -- "View metric history" --> HIS["Metric history (S-025)"] --> E(["End"])
    CH -- "Doctor's instructions" --> DI["Doctor's instructions (S-027)"] --> E
    CH -- "My reports" --> MR["My reports (S-029): the mother's reports and chatbot cases with status"] --> E
```

Report a metric or symptoms and follow the report (same as `spec-ALR.md` §4.1(b); the mother reports only a flagged indicator — a metric in her Doctor's instructions — or symptoms, ALR-02; thresholds per ALR BR-004 — D-14 decided, D-15 Pending SME):

```mermaid
flowchart TD
    S27["S-027 Doctor's instructions"] -->|"+ Report metric / + Report symptoms"| S25["S-025A Report a metric (choose: a metric in the Doctor's instructions, or symptoms)"]
    S25 -->|"Submit report — stored (ALR FR-020)"| CK{"Threshold check (Group 2) and symptoms"}
    CK -->|"Above threshold (with or without symptoms) — case created (ALR FR-021)"| S28["S-028 Metric alert (status: Not viewed)"]
    CK -->|"Not above threshold, with symptoms — case created (ALR FR-021)"| S26["S-026 Report status (Not viewed)"]
    CK -->|"Not above threshold, no symptoms"| BACK["Report submitted → back to S-027 (no case, no status)"]
    S28 -->|"View status"| S26
    S29["S-029 My reports"] -->|"View report"| S26
```

### Appointment

**DBIZ2 original** (Figure 3) — reference only. Two sub-flows: booking a new appointment, and viewing / cancelling one.

```mermaid
flowchart TD
    S1(["Start"]) --> LR1["Login / Register"] --> LI1{"User Logged In?"}
    LI1 -- No --> RA1["Register Account"] --> LR1
    LI1 -- Yes --> LG1["Login"] --> LH1["Land Home Page"] --> OAS["Open appointment section"] --> CR["Choose reason for visit"] --> SCDT["Select clinic, Date & Time"]
    SCDT --> SAC{"Slot Availability Checking"}
    SAC -- No --> SCDT
    SAC -- yes --> SSA["Select Slot Available"] --> ARV["Appointment Review (dates, time, doctor assigned, price)"]
    ARV -- Confirm --> ASU["Appointment Success"] --> E1(["End"])
```

```mermaid
flowchart TD
    S2(["Start"]) --> LR2["Login / Register"] --> LI2{"User Logged In?"}
    LI2 -- No --> RA2["Register Account"] --> LR2
    LI2 -- Yes --> LG2["Login"] --> LH2["Land Home Page"] --> OAS2["Open appointment section"] --> MAL["My Appointments List"] --> AD["Appointment Detail"] --> CA["Cancel Appointment"] --> E2(["End"])
```

**MVP flow** — `spec-APT.md` §1: booking, the appointment list and cancelling happen in the TCI app; the sub-app has no intermediate screen.

```mermaid
flowchart TD
    S(["Start"]) --> H["Home (S-008): 'Upcoming appointments' card"] -->|"Book a visit ↗ / Appointments tab"| TCI["TCI app booking flow (outside the sub-app)"] --> E(["End"])
```

### Notifications and profile (MVP only — no DBIZ2 flow)

Notifications — `spec-ACC.md` FR-025 – FR-027; D-48:

```mermaid
flowchart TD
    S(["Start"]) --> H["Home (S-008)"] -->|"Notifications"| N["Notifications (S-009): filter All / Report / Visit result / Appointment / Instruction reminder; unread count"]
    N -->|"Mark all as read"| N
    N -->|"Tap a notification"| R["Marked as read"] --> TY{"Type"}
    TY -- "Report" --> S26["Report status (S-026)"] --> E(["End"])
    TY -- "Visit result" --> S23["Health metrics (S-023)"] --> E
    TY -- "Appointment" --> TCI["TCI app appointment flow"] --> E
    TY -- "Instruction reminder" --> S27["Doctor's instructions (S-027) — proposed target"] --> E
```

New visit result (system side) — `spec-ALR.md` FR-019; D-59:

```mermaid
flowchart TD
    V(["Visit record inserted (seed data in the demo — D-59)"]) --> ON{"'New visit results' switched on? (S-010)"}
    ON -- Yes --> NT["Visit result notification (ALR FR-019)"] --> SEE["Mother sees it on S-009 and on the Home card (S-008)"] --> E(["End"])
    ON -- No --> NN["No notification; the visit still shows on S-023 and S-048"] --> E
```

Doctor's-instruction reminder (system side) — `spec-ALR.md` FR-022; trigger / frequency open (ALR Q20):

```mermaid
flowchart TD
    W(["Reminder due for a metric in the mother's active Doctor's instructions (trigger: ALR Q20)"]) --> ON{"'Doctor's-instruction reminders' switched on? (S-010)"}
    ON -- Yes --> NT["Instruction reminder notification (ALR FR-022), delivered via the TCI app"] --> SEE["Mother sees it on S-009 → S-027"] --> E(["End"])
    ON -- No --> NN["No notification"] --> E
```

Profile — `spec-ACC.md` US-3:

```mermaid
flowchart TD
    S(["Start"]) --> P["Profile tab (S-103)"]
    P -->|"Edit profile / Pregnancy information"| PI["Edit profile (S-011): Save changes → back to S-103"] --> E(["End"])
    P -->|"Hospital record link"| HL["Link status: Linked / Pending link (seed data — no Retry, D-61); Close → back to S-103"] --> E
    P -->|"Notification settings"| NS["Notification settings (S-010): switch types on / off, saved at once; 'Report responses' locked on — proposal"] --> E
    P -->|"Support"| SUP["TCI app support page"] --> E
```

---

## NURSE

**DBIZ2 original** (Figure 3) — "Manage alert" only; the Schedule (view) and Schedule (update) sub-flows are out of MVP scope and not transcribed.

```mermaid
flowchart TD
    S(["Start"]) --> OMA["Open Manage Alert"] --> VAL["View Alert List"] --> SA["Select Alert"] --> TAA["Take Action or Acknowledge"] --> E(["End"])
```

**MVP flow** — `spec-CLI.md` §4.1(b). The responsible doctor is the doctor the hospital assigned to the mother (D-68; seed data in the MVP); how staff sign in on the web is open (`spec-CLI.md` §10 Q11).

```mermaid
flowchart TD
    S(["Start"]) --> SI["Sign in on the clinical web (S-054, not drawn; method open — CLI Q11)"] --> Q["Cases to handle (S-061): cases from metric reports, symptoms and chatbot; filter by status"] -->|"View report ›"| P["Mother quick profile + report (S-064)"]
    P --> MV["Mark as viewed (recorded automatically if the nurse escalates first — D-43)"] --> G["Send guidance to the mother (optional; status unchanged)"] --> D{"Doctor needed?"}
    D -- Yes --> ESC["Escalate to doctor: status Escalated to doctor + high-priority notification to the responsible doctor, inside the clinical web (ALR-03)"] --> E(["End"])
    D -- No --> CL["Close case: Resolved (D-37)"] --> E
```

---

## DOCTOR

**DBIZ2 original** (Figure 3) — patient monitoring & escalation only; the Appointment, Schedule, Medications and Messages sub-flows are out of MVP scope and not transcribed.

```mermaid
flowchart TD
    S(["Start"]) --> LH["Land homepage"] --> VPL["View Patient List"] --> ARA{"Any Risk or Alert?"}
    ARA -- no --> VPL
    ARA -- yes --> SP["Select Patient"] --> VPS["View Patient Snapshot Panel"] --> RRA["Review Risk Alerts"]
    RRA --> SEV{"Is patients' conditions severe?"}
    SEV -- no --> CCN["Create Care Note or Recommendation"] --> E(["End"])
    SEV -- yes --> OSM["Open Smart Messaging Hub"] --> NCT["Notify Care Team, Doctors and Nurses"] --> DCI["Decide Clinical Intervention"] --> UPS["Update Patient Status"] --> E
```

**MVP flow** — `spec-CLI.md` §4.1(b). No messaging hub or care-team notification: the doctor answers the mother in writing. The doctor handles only cases "Escalated to doctor" (CLI-02).

Review an escalated case (MVP: Review Escalated Cases, Provide Consultation, Update Patient Status):

```mermaid
flowchart TD
    S(["Start"]) --> SI["Sign in on the clinical web (S-060, not drawn; method open — CLI Q11)"] --> N["In-web notification or Cases to handle (S-061), default filter 'Escalated to doctor'"] -->|"View report ›"| P["Mother quick profile + report + metric history (S-064)"]
    P --> G["Send guidance ('Provide Consultation' — D-58)"] --> CL["Close case: Resolved, red flag cleared ('Update Patient Status' — D-37, D-44)"] --> E(["End"])
```

Add / edit Doctor's instructions (watch-flag) after a visit — `spec-CLI.md` FR-025, US-3:

```mermaid
flowchart TD
    S(["Start"]) --> P["Mother quick profile (S-064), signed in as Doctor"] --> F["'Add / edit instruction' form: metric to monitor (Group 2), note for the mother (how to measure, frequency), above-threshold guidance (template and / or custom text)"]
    F --> SV["Save instruction (Watch-Flag)"] --> M["Mother sees it on S-023 / S-027; S-025A lists the metric; S-028 uses the guidance"] --> E(["End"])
    F -- "Cancel" --> P
```

---

## ADMIN

Not transcribed: Admin is not an MVP actor (D-49). DBIZ2 sub-flows: Manage accounts, Manage Medical Content, Manage Schedule, View statistics.
