# System Configuration Diagram

## 1. MVP configuration

Drawn by the team from the decisions in this package (sources in the table below) — **not a DBIZ2 diagram**. Use this one when building. Modules are named by their spec; no endpoint or payload names are given.

```mermaid
flowchart TB
    subgraph A["A. Users & Devices"]
        MOM_U["Pregnant mother"]
        NUR_U["Nurse"]
        DOC_U["Doctor"]
        MOBILE["Mobile phone"]
        DESKTOP["Desktop / Tablet"]
    end

    subgraph B["B. Frontend"]
        subgraph TCIAPP["TCI app (host)"]
            SUB["Mother & Baby 360 sub-app<br/>Home · Health metrics · Report · My reports · Notifications ·<br/>Timeline & Diary · Chatbot · Profile"]
        end
        CWEB["Clinician web<br/>Cases to handle · Mother quick profile ·<br/>Doctor's instructions form · in-web notifications"]
    end

    subgraph C["C. Backend modules"]
        direction LR
        subgraph C1[" "]
            ONB["Onboarding, consent & profile (ACC)"]
            NOTI["Notifications & settings (ACC, ALR)"]
            HLTM["Health metrics, visits &<br/>Doctor's instructions (HLT)"]
            RPT["Report storage, threshold check, case &<br/>notifications to the mother (ALR)"]
            TMLM["Timeline & diary with photos (TML)<br/>· Messages to Baby (pending Client — D-03)"]
            BOTM["Chatbot service — Python (BOT)"]
            APTM["Appointment redirect (APT)<br/>button / tab hand-off · read-only upcoming card · reminders"]
        end
        subgraph C2[" "]
            CLIM["Case handling, escalation &<br/>Doctor's instructions (CLI)"]
        end
    end

    subgraph D["D. Data"]
        DB[("Mother & Baby 360 database<br/>incl. visit and record-link seed data, threshold rules")]
        FILES[("File storage<br/>diary photos, ultrasound images")]
    end

    subgraph E["E. External"]
        TCIID["TCI app identity & notification delivery"]
        TCIBOOK["TCI app booking flow"]
        LLM["LLM API: Google AI Studio (Gemini) — D-76"]
        AUTHS["Authentication service (clinician web)"]
    end

    MOM_U --> MOBILE --> SUB
    NUR_U --> DESKTOP
    DOC_U --> DESKTOP
    DESKTOP --> CWEB
    SUB <--> C1
    CWEB <--> C2
    C <--> DB
    C <--> FILES
    C <-->|"identity in (ACC), notifications out (ACC, ALR, APT), booking hand-off + upcoming appointments read (APT), questions (BOT), staff sign-in (CLI)"| E
```

| Element | Why it is here / what changed from DBIZ2 | Source |
|---|---|---|
| Sub-app inside the TCI app | Replaces the DBIZ2 "Patient Mobile App": the mother uses the signed-in TCI account, no own login | D-01 `[PENDING CLIENT: D-01]` |
| Clinician web | Nurse and doctor screens S-061, S-064 (incl. the doctor's "Add / edit instruction" form); the escalation notification is shown here; "Messaging" of DBIZ2 and Quick notes are not built | `spec-CLI.md`; D-29; ALR-03, CLI-03 |
| Backend modules | One per module spec. Removed from DBIZ2: Knowledge Library, Medications Management, Schedule Management, native appointment booking, messaging hub | `docs/decisions.md` "Module scope and key corrections"; MVP v8 §5 (Won't) |
| Report, threshold check & case | Merges DBIZ2 "Risk alert" and "Risk Assessment": stores the mother's report (FR-020), checks it against the threshold rules and opens the case (FR-021, also for chatbot cases); creates the mother's notifications (FR-018, FR-019, FR-022). No risk-summary screen for the mother (ALR-01) | `spec-ALR.md` BR-004, BR-008; D-52, D-64 |
| Chatbot service | Python backend; calls the LLM API with the question and light context only | `spec-BOT.md` BR-001, BR-003 |
| One database | Replaces the 8 DBIZ2 hospital databases; visit data and the hospital record link are seed data | D-59, D-61; MVP v8 §5 (Won't: Deep Two-Way HIS/EMR Integration) |
| File storage (team addition, not DBIZ2) | Holds diary photos (JPG/PNG ≤ 10 MB, up to 5 per entry — D-46, TML-01 pending) and the ultrasound images of the seed visits; the database keeps only the file path | `spec-TML.md` FR-009, §6 Diary Image; `spec-HLT.md` §6 Visit |
| TCI app identity & notification delivery | Provides the signed-in identity; notifications are sent via the TCI app | D-01; S-010 SR-004 |
| TCI app booking flow | "Book a visit ↗" and the "Appointments" tab open the host app's booking flow directly; the sub-app only reads the upcoming appointments for the Home card | `spec-APT.md` §1, BR-001 – BR-003; D-62 |
| Authentication service | Kept only for clinician web sign-in | `spec-CLI.md` §10 Q11 `[NEEDS CLARIFICATION]` |
| **Hospital EMR — removed from the MVP diagram** | The record-number link is simulated with seed data (no EMR call); an EMR connection is for a later version | `spec-ACC.md` FR-001, FR-002 (ACC-01); D-61; DM-23 |
| **Removed:** Maps API, Messaging Gateway, Push Notification Gateway | No feature uses them; notifications go through the TCI app | S-010 SR-004 |
| Doctor notification channel | The high-priority notification is shown inside the clinical web (S-061 "Notifications" / S-059); no push, no SMS | `spec-ALR.md` FR-009, §10 Q13 resolved (ALR-03) |

## 2. DBIZ2 original (reference only — not the MVP)

Source: `DBIZ2_GROUPA_FinalReport.xlsx`, sheet `Schematic1`, section 1.3b ("System Overall Configuration"), Figure 2. Transcribed unchanged.

```mermaid
flowchart TB
    subgraph A["A. Users & Devices"]
        MOM_U["Pregnant Mothers"]
        NUR_U["Nurses"]
        DOC_U["Doctors"]
        MOBILE["Mobile Devices"]
        DESKTOP["Desktop / Tablet"]
    end

    subgraph B["B. Frontend Applications"]
        PWA["Patient Mobile App<br/>Timeline · Health Metrics · Chatbot"]
        CDASH["Clinician Dashboard<br/>Patient List · Alerts · Messaging"]
    end

    subgraph C["C. Backend APIs & Core Logic"]
        subgraph C1[" "]
            HM["Health Metrics<br/>/submit_health_metrics, /get_health_metrics"]
            RA["Risk alert<br/>/evaluate_risk_level, /get_risk_alerts, /configure_alert_rules"]
            PP["Patient Profile<br/>/get_patient_profile, /update_patient_profile"]
            PT["Patient Timeline<br/>/get_patient_timeline, /add_timeline_event"]
            APT["Appointment<br/>/check_appointment_availability, /create_appointment, /get_appointment_detail, /get_my_appointments, /cancel_appointment"]
            KL["Knowledge Library<br/>/get_medical_contents, /get_medical_content_detail"]
        end
        subgraph C2[" "]
            CA["Clinician access<br/>/login_clinician, /logout_clinician, /get_clinician_profile"]
            MM["Medications Management<br/>/get_patient_medications, /update_medication_plan, /prescribe_medication"]
            CC["Care Coordination<br/>/open_smart_messaging_hub, /notify_care_team, /record_clinical_decision, /update_patient_status"]
            PL["Patient List<br/>/get_patient_list, /get_patient_snapshot"]
            RAS["Risk Assessment<br/>/check_patient_risk, /get_risk_alerts, /evaluate_patient_condition"]
            SM["Schedule Management<br/>/get_work_schedule, /request_schedule_adjustment, /submit_schedule_change"]
        end
    end

    subgraph D["D. Thu Cuc Hospital Databases"]
        DB1[("Clinical Records Database")]
        DB2[("Laboratory Results Database")]
        DB3[("Diagnostic Imaging Database")]
        DB4[("Prescription & Medication Database")]
        DB5[("Medical Staff Database")]
        DB6[("Patient Master Database")]
        DB7[("Appointment & Scheduling Database")]
        DB8[("Medical Content Database")]
    end

    subgraph E["E. External Interfaces"]
        AUTHS["Authentication Service"]
        PNG["Push Notification Gateway"]
        MSGW["Messaging Gateway"]
        MAPS["Maps API"]
    end

    MOM_U --> MOBILE
    NUR_U --> DESKTOP
    DOC_U --> DESKTOP
    MOBILE --> PWA
    DESKTOP --> CDASH
    PWA <--> C1
    CDASH <--> C2
    E <--> C
    C <--> D
```
