# Context Diagram

## 1. MVP context

Drawn by the team from the decisions in this package (sources in the table below) — **not a DBIZ2 diagram**. Use this one when building. On each arrow, **in** = information coming into Mother & Baby 360, **out** = information it sends.

```mermaid
flowchart LR
    MOM["Mother (uses the sub-app inside the TCI app)"]
    TCI["TCI app (host app)"]
    HOS["Thu Cuc Hospital visit data (simulated as seed data prepared by the clinical role — D-59)"]
    SYS["Mother & Baby 360 (sub-app + clinician web)"]
    NUR["Nurse (web)"]
    DOC["Doctor (web)"]
    LLM["LLM provider (OpenAI or Gemini — not chosen)"]
    AUTH["Authentication service (clinician web sign-in)"]

    MOM <-->|"<b>in:</b> consent, pregnancy information, profile, self-tracked metrics,<br/>flagged-metric and symptom reports, diary entries and photos,<br/>Messages to Baby (pending Client — D-03), chatbot questions, notification settings<br/><b>out:</b> visit results, Doctor's instructions, threshold labels, report status,<br/>staff guidance, chatbot answers, upcoming appointments (read only), notifications"| SYS
    TCI <-->|"<b>in:</b> signed-in TCI identity, account information (with consent),<br/>upcoming appointments (read only)<br/><b>out:</b> hand-offs (booking flow — redirect only; support page), notifications to deliver"| SYS
    HOS -->|"visit records, hospital record link, hospital due date (seed)"| SYS
    SYS <-->|"<b>out:</b> cases to handle (metric reports, symptom reports, chatbot hand-offs),<br/>mother's quick profile (no self-tracked metrics)<br/><b>in:</b> case status changes, guidance to the mother"| NUR
    SYS <-->|"<b>out:</b> escalated cases, high-priority notification (in the clinical web),<br/>mother's quick profile<br/><b>in:</b> closure of escalated cases (Update Patient Status), guidance to the mother,<br/>Doctor's instructions"| DOC
    SYS <-->|"<b>out:</b> question text + earlier questions / answers + gestational week<br/>(no medical record)<br/><b>in:</b> answer text"| LLM
    AUTH -->|"staff sign-in"| SYS
```

| Element | Why it is here / why it changed from DBIZ2 | Source |
|---|---|---|
| Mother | Uses the sub-app inside the TCI app; no own account | D-01 `[PENDING CLIENT: D-01]` |
| Nurse, Doctor | The only clinical roles (Role ENUM = Mother / Nurse / Doctor) | D-29, D-49 |
| TCI app (host app) | Provides the signed-in identity (replaces the DBIZ2 "Authentication service" for the mother); receives the appointment-booking and support hand-offs — booking is a **redirect only**, the sub-app keeps no appointment data and only reads the upcoming appointments for the Home card; delivers notifications ("Notifications are sent via the TCI app", S-010) | D-01, D-39, D-62; `spec-APT.md` §1, BR-002, BR-003; S-010 |
| Thu Cuc Hospital visit data | Source of Visit records ("From visit"), the hospital record link status and the hospital's due date; no two-way EMR integration. **In the MVP, simulated as seed data prepared by the clinical role; there is no visit entry screen** (same sentence in `spec-HLT.md` §1 and `spec-TML.md` §1 — HLT-06) | D-42, D-59, D-61; `spec-HLT.md` §10 Q14 |
| Authentication service | Kept only for clinician web sign-in; how staff sign in is open | `spec-CLI.md` §10 Q11 `[NEEDS CLARIFICATION]` |
| LLM provider | Answers general maternity questions for the chatbot; receives only the question text, the earlier questions / answers of the conversation and the gestational week, never the medical record. Provider not chosen | `spec-BOT.md` BR-001, BR-003, FR-003 (D-67); MVP v8 §5 |
| **Admin — removed** | No Admin actor in the MVP | D-49 |
| **Removed 29/09/2026** | Quick notes (nurse / doctor), the mother's self-tracked metrics shown to staff, chatbot answer rating | CLI-01, CLI-03, BOT-02; D-63 |
| **International Research Institute — removed** | Appears in no spec; the Knowledge Base range (`F-145`–`F-148`) that would use its content is outside this package | `docs/decisions.md` "Module scope and key corrections" |

## 2. DBIZ2 original (reference only — not the MVP)

Source: `DBIZ2_GROUPA_FinalReport.xlsx`, sheet `Schematic1`, section 1.3a ("Context Diagram"), Figure 1. Transcribed unchanged.

```mermaid
flowchart LR
    MOM["Pregnant Mother"]
    DOC["Doctor"]
    IRI["International Research Institute"]
    NUR["Nurse"]
    ADM["Admin"]
    AUTH["Authentication service"]
    SYS["Mother & Baby 360° Platform"]

    MOM -->|"Health data, messages, bookings"| SYS
    SYS -->|"Reminders, alerts, guidance"| MOM
    DOC -->|"Clinical decisions, notes"| SYS
    SYS -->|"Patient data, alerts"| DOC
    IRI -->|"Verified medical content"| SYS
    SYS -->|"Alerts, tasks"| NUR
    NUR -->|"Care actions, responses"| SYS
    ADM -->|"Update, operation"| SYS
    SYS -->|"Report statistics"| ADM
    SYS -->|"Customer information"| AUTH
    AUTH -->|"Service"| SYS
```
