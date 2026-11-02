# UI package: Mother & Baby 360, 25 mother-side screens

The team's latest UI design, as delivered in `MotherBaby360_UI_hoan-chinh` (received 02/11/2026). **It is a design input, not yet the source of truth:** where it differs from `docs/prd.md`, `specs/` or `screens/screen-spec-*.md`, the difference below stays open until a person decides it (AGENTS.md rule 1). The running app does not follow this package yet.

| Path | Content |
|---|---|
| `prototype/index.html` | Map of the screens; open it in a browser, then "Chạy prototype từ app TCI". Clickable, static, invented sample data |
| `prototype/tci.css` | Design tokens and components of the prototype |
| `png/` | One image per screen (25) |
| `Mother-Baby-360_Tong-hop-man-hinh.pdf` | Printed overview (8 pages) |
| `README.txt` | The package's own list of screens (Vietnamese) |
| `UX_UI_finallllize.txt` | UI conventions. One person's name quoted from a TCI app screenshot is replaced by `[tên thành viên]` (rule 3); otherwise unchanged. English version: `docs/ui-label-reference.md` on PR #15 |

Left out of the delivered package: `.DS_Store`. As an exception to the note in `docs/ui-label-reference.md`, the files of this folder contain Vietnamese UI text. All people in the prototype are sample names.

## Screen map

"App" = state of `main` plus the open PR #15 (D-79).

| # | Prototype | Package title | Screen ID | App today |
|---|---|---|---|---|
| 1 | `TciHome` | App TCI – màn chủ | TCI host, S-001 state 1 | Built, different layout |
| 2 | `Consent` | Kết nối tài khoản TCI | S-001 state 2 | Built |
| 13 | `Onboarding` | Hướng dẫn sử dụng | S-104 | Built, 4 pages |
| 3 | `Setup` | Khai báo thai kỳ | S-007 / S-046 | Built |
| 14 | `Expired` | Phiên làm việc hết hạn | S-043 | Not built |
| 15 | `CloseConfirm` | Đóng Mother & Baby 360? | S-083 | Built as a bottom sheet (PR #15) |
| 4 | `Main` | Trang chủ | S-008 | Built, different content |
| 5 | `Report` | Báo cáo chỉ số / triệu chứng | S-025A | Built |
| 16 | `Alert` | Cảnh báo chỉ số | S-028 | Built as a page; the spec and this package use a popup |
| 17 | `SelfTrack` | Nhập chỉ số tự theo dõi | S-024 | Built |
| 18 | `History` | Lịch sử chỉ số | S-025 | Not built |
| 6 | `Timeline` | Timeline thai kỳ | S-048 | Built, no day strip |
| 7 | `Day` | Chi tiết ngày | **No ID** | Not built |
| 8 | `Diary` | Viết nhật ký | S-051 / S-052 | Built |
| 19 | `Saved` | Timeline – đã lưu nhật ký | S-048, success state | Built, different look |
| 20 | `Journey` | Hành trình & album kỷ niệm | S-105 | Not built |
| 9 | `Notices` | Thông báo từ bác sĩ | S-009 (narrowed) | Not built |
| 10 | `NoticeDetail` | Chi tiết thông báo | **No ID** | Not built |
| 21 | `MyReports` | Báo cáo của tôi | S-029 | Built |
| 11 | `Chat` | Chatbot | S-031, S-032, S-034 | Built |
| 22 | `ChatHandoff` | Chatbot – đã chuyển y tá | S-034, state | Built, different content |
| 12 | `Profile` | Hồ sơ | S-103 | Placeholder (PR #15) |
| 23 | `Instructions` | Chỉ dẫn của bác sĩ | S-027 | Built, with report buttons |
| 24 | `EditProfile` | Chỉnh sửa hồ sơ | S-011 | Not built |
| 25 | `NotifSettings` | Cài đặt thông báo | S-010 | Not built |

No design in this package: S-023 Health metrics, S-026 Report status, S-033 typing state, and the clinical web (S-061, S-064).

## Differences to decide

| # | The package shows | The repository says | Who decides |
|---|---|---|---|
| U1 | Tabs: Trang chủ · Timeline · Chatbot · Từ bác sĩ (badge) · Hồ sơ. The round button exists only in the TCI host app | Home · Health · Appointments · Chatbot · Profile (D-27, S-008 SR-005). The Appointments tab opens TCI booking (APT BR-003). PR #15 D-79 makes it a round middle button | Team; changes D-27, D-79, APT BR-003, every screen spec's tab row |
| U2 | No way to book a visit from the sub-app. Home shows "Lịch khám kế tiếp" | "Book a visit ↗" and the tab (APT FR-001, BR-001). The appointment card is Could, read from TCI (D-77); no appointment data exists in the seed | Team / Client |
| U3 | No Health hub (S-023). Home shows the metric tiles | S-023 is Must (HLT FR-001): latest visit results with threshold labels, reference range | Owner of HLT (Ánh) |
| U4 | No Report status (S-026). "Xem trạng thái" opens My reports; "Xem báo cáo" opens the notice detail | S-026 carries the handling progress, responses and Safety note (ALR FR-005, FR-007, BR-011, BR-012) | Owner of ALR (Tâm) |
| U5 | "Báo cáo sẽ được chuyển ngay cho bác sĩ"; "Bác sĩ xem và trả lời" | A report goes to the **nurse** queue first; escalation to a doctor is a nurse's action and may be skipped (ALR BR-007, D-18, D-43). **The wording misleads the mother about who sees her report** | Owners of ALR, CLI |
| U6 | Chatbot warning: hotline and "Kết nối y tá" only; no "Không, cảm ơn"; no version for a personal question without a danger sign | Connect to nurse / No, thanks (BOT FR-011, D-76). Hotline number is still open (BOT Q8) | Owner of BOT (Sang) |
| U7 | "Y tá trực sẽ gọi lại cho mẹ trong ít phút" | No call-back or response time exists in any document. **A promise to a mother with bleeding must not ship without the hospital's confirmation** | Client / SME |
| U8 | Clinical sentences as fixed text: "Nằm nghỉ nghiêng trái 15 phút…", "Mẹ cần được kiểm tra ngay", "Báo cáo ngay nếu từ 140/90", the chatbot's nutrition answer | Guidance comes from GUIDANCE_TEMPLATE and is supplied by the hospital (D-25, BR-013); thresholds only from THRESHOLD_RULE; few-shot clinical answers not adopted (D-76). Treated here as sample data | SME |
| U9 | Notice detail: "Bác sĩ nhận xét", numbered "Mẹ cần làm", "Bác sĩ hẹn khám sớm", specialty, "Mẹ đã hiểu" | STAFF_RESPONSE has one template and one free text; no appointment, no acknowledgement, no specialty (schema; APT stores no appointment, DM-04) | Team; needs spec → data model → seed |
| U10 | Notices list only what doctors and nurses send | S-009 lists four types, including visit results and reminders; opened from the header on Home | Owner of ACC (Chi) |
| U11 | Week strip with one screen per day; week 24 = 26/10 – 01/11 (Monday start) | Weekly view with a daily listing (D-04, D-75). With this prototype's last period of 10/05/2026, week 24 starts on Sunday 25/10 | Owner of TML (Tâm) |
| U12 | Trimesters: weeks 1 – 13, 14 – 27, 28 – 40 | 0 – 13, 14 – 27, 28 – 42, boundaries Pending SME (D-75) | SME |
| U13 | "Messages to Baby" does not appear | Shown on S-048; writing them is pending Client (D-03) | Client |
| U14 | ✕ only on Home, setup and consent. S-083 is a centred dialog with new text | ✕ on every screen, S-083 a bottom sheet (ui-label-reference, S-083 §1, #5) | Owner of `screens/` |
| U15 | Doctor's instructions are read-only, opened from Profile; reporting starts from Home | S-027 has "+ Report metric" / "+ Report symptoms" and belongs to the Health tab | Owner of HLT |
| U16 | Report tabs show all three metrics | Only metrics in the mother's active instructions (D-11). In the prototype itself Profile lists three and Instructions two | Implementation: follow D-11 |
| U17 | Onboarding has 3 pages with new text | 4 proposed pages; number and text open (ACC Q20) | Owner of ACC |
| U18 | Heart rate 8 bpm rejected as out of range | Valid ranges are not set (D-16, Pending SME); no range may be invented | SME |

Not contradicted: tokens, type, buttons, cards and labels match `UX_UI_finallllize.txt`; "Cảnh báo" appears only on the Alert screen; the chatbot notice uses "Dấu hiệu cần chú ý y tế"; "Phản hồi báo cáo" locked on matches the team proposal in S-010 SR-001.
