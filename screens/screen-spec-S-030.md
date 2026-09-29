# Screen Spec: S-030 Risk Recommendation Screen

| Field | Value |
|---|---|
| Screen ID | `S-030` |
| Screen name | Risk Recommendation Screen |
| Actor | Mother |
| Priority | **Removed (D-05)** |
| Belongs to module | `spec-ALR.md` |
| Mockup image | — (a DBIZ2 mockup exists in sheet `SL`; no image is included in this package because the screen is removed — D-05) |
| Status | **Removed (D-05)** |

> **This screen is removed (D-05).** Do not build it. No screen navigates to `S-030` (there is no "See recommendations" button on `S-029` — D-06).

## Where recommendations are shown

| Shown on | Content | Basis |
|---|---|---|
| `S-028` Metric alert | "Doctor's guidance" box: the Above-threshold guidance written by the doctor when creating a Doctor's instructions entry on `S-064` (choose a template and/or write custom text); if there is none, the hospital's default template is used | D-05, D-24 |
| `S-026` Report status | "Response" box from the nurse / doctor (guidance chosen from a template or custom-written, sent from `S-064`); while there is no response, the "Safety note" is shown | D-05, D-24, D-25 |

`spec-ALR.md` FR-007 remains in scope (Must); only the display surface is different.

---

## Completion checklist

- [x] The screen is marked Removed with its decision ID (D-05).
- [x] The replacement display surfaces for FR-007 are stated (S-028, S-026).
- [x] No screen navigates to S-030 (S-029 has no "See recommendations" button).
