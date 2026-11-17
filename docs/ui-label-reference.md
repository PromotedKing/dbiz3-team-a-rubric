# UI conventions and label reference: Mother & Baby 360

Shared UI conventions of the wireframes and the mapping from the English labels used in every document to the Vietnamese text drawn on the wireframes. This is the only file with Vietnamese UI text; the app reads its on-screen text from the tables below (`app/mb360/ui.py`, D-79).

## UI conventions

Text version of the UI-conventions page `00-QUY-UOC` of the wireframe (the page has no Screen ID, so its image is not in `screens/img/`), **revised by D-79 (28/10/2026) to match the existing Thu Cuc patient app (TCI app)** from screenshots of its Home and Profile screens, **and by D-80 (02/11/2026) to follow the UI package** in `screens/ui-final/`. Source decisions: **D-27**, **D-79**, **D-80**. Applies to every screen. Implemented in `app/mb360/static/tci.css` (tokens and components of the package; `staff.css` for the clinical web) and `app/mb360/templates/base.html` (header, tab bar, S-083).

Markers: **[measured]** = colour sampled from the TCI screenshots (±2–3 units, JPG compression); **[estimated]** = inferred from the screenshots, to confirm with TCI's own design file if one exists; **[added]** = the TCI app has no such element, derived from the TCI palette for this product.

### 1. Type (5 levels)

Font family: **Roboto** (fallback: -apple-system, "SF Pro Text", sans-serif) **[estimated]**. Sizes converted from the screenshots, assuming a 390 pt wide screen **[estimated]**. Only weights 400 (regular) and 700 (bold); no italics.

| Level | Size | Weight | Line height | Colour | Reference in the TCI app |
|---|---|---|---|---|---|
| Display (highlighted figure) | 22 | 700 | 28 | `color-primary` | "Member", "250" |
| Page title | 18 | 700 | 24 | `color-text-primary` | the member's name; "Thu Cuc Health System – TCI" (in `color-primary`) |
| Section title | 18 | 700 | 24 | `color-text-primary` | "Customer guide", "Profile", "Account & security" |
| Body | 15 | 400 | 20 | `color-text-primary` | menu rows, article card titles |
| Caption | 12 | 400 | 16 | `color-text-secondary` | tab-bar labels, "Member tier", "Available points" |

The tagline under the logo ("Lifelong health care for you!") is Body 15/400 in `color-primary`; it is used only for brand subtitles.

### 2. Colours

**2.1 Brand and background**

| Token | Value | Used for | Source |
|---|---|---|---|
| `color-primary` | `#00A651` | primary button, active tab, menu icons, highlighted figures, emphasised titles | [measured] |
| `color-primary-light` | `#48D07C` | light end of the gradient of the round middle tab button | [measured] |
| `color-primary-pressed` | `#008C44` | pressed state of the primary button | [added] ~15 % darker |
| `color-primary-soft` | `#CCF6D2` | round background under feature icons | [measured] |
| `color-hero-gradient` | `#D3EDD2` → `#C3EAD5` | hero card (member card at the top of Profile; gestational-week card) | [measured] |
| `color-accent` | `#F66A0B` | floating call / hotline button and urgent CTAs only — never for general use | [measured] |
| `color-avatar` | `#009788` | initials avatar background | [measured] |
| `color-bg` | `#F5F5F5` | screen background behind cards | [measured] |
| `color-surface` | `#FFFFFF` | cards, header, tab bar | [measured] |

**2.2 Text and lines**

| Token | Value | Used for |
|---|---|---|
| `color-text-primary` | `#212121` | page title, section title, body |
| `color-text-secondary` | `#6F6F6F` | caption, secondary text, chevron › |
| `color-text-disabled` | `#B4B4B4` | inactive tab label / icon, disabled button |
| `color-border` | `#E0E0E0` | card border, divider between menu rows |

**2.3 Business states [added]** — the TCI screenshots have no threshold labels or warnings; derived from the TCI palette:

| Token | Background / text | Used for |
|---|---|---|
| `color-status-normal` | `#E6F6EC` / `#00873F` | threshold label "Normal" |
| `color-status-alert` | `#FEEDE1` / `#C4520A` | threshold label "Above threshold"; the Alert on S-028 (same family as `color-accent`) |
| `color-status-unrated` | `#EEEEEE` / `#6F6F6F` | threshold label "Not assessed" |
| `color-error` | `#D64545` | network error, input error |
| `color-info` | `#3B7DD8` | neutral information |

Do not use `color-accent` as a solid background for "Above threshold", so that it is not confused with the hotline / promotion buttons. Colour only supplements the text of a label, never replaces it.

### 3. Spacing and shape

| Token | Value | Source |
|---|---|---|
| `space-unit` | 4 px (multiples 8, 12, 16, 24) | unchanged |
| `space-screen-x` | 16 px left / right screen margin | [estimated] |
| `radius-card` | 16 px | [estimated] |
| `radius-banner` | 12 px | [estimated] |
| `radius-button` | 12 px | [added] |
| `radius-tag` | 999 px (pill) | unchanged |
| `border-width` | 1 px, `color-border` | [measured] |
| `shadow-card` | `0 2px 8px rgba(0,0,0,0.06)` | [estimated] |

Two card styles: **floating card** (white, `shadow-card`, no border) on a `color-bg` screen; **bordered card** (white, 1 px `color-border`, no shadow) on a white screen.

### 4. Buttons

| Type | Background | Text | Height | Corners |
|---|---|---|---|---|
| Primary (filled) | `color-primary` | white, 15/700 | 48 px | `radius-button` |
| Secondary (outline) | transparent, `color-primary` border | `color-primary`, 15/700 | 48 px | `radius-button` |
| Small – primary | `color-primary` | white, 13/700 | 36 px | `radius-button` |
| Small – secondary | transparent, `color-border` border | `color-text-primary`, 13/400 | 36 px | `radius-button` |
| Disabled (any type) | `#EEEEEE` | `color-text-disabled` | as above | as above |
| Text link | none | `color-primary`, not underlined, with `›` | — | — |

**Fixed CTAs** — each action always uses the same label:

| Action | Button label |
|---|---|
| Enter Group 1 metrics | **Save metrics** |
| Report a Group 2 metric / symptoms | **Submit report** |
| Open S-026 | **View status** |
| Open a report from a list | **View report** |
| Open the history screen | **View metric history** |

### 5. Icons

| Context | Style | Size | Colour |
|---|---|---|---|
| Menu rows, shortcuts | outline, ~1.5 – 2 px stroke | 24 px | `color-primary` |
| Tab bar | filled | 24 px | active `color-primary` / inactive `color-text-disabled` |
| Feature grid (TCI Home) | multi-colour illustration on a `color-primary-soft` circle | ~64 px | per illustration |
| Chevron › at the end of a row | outline | 20 px | `color-text-secondary` |

### 6. Threshold labels

Only 3 labels: **Normal** · **Above threshold** · **Not assessed** (D-17), Caption 12/700, `radius-tag`, colours of §2.3. Red only if the team decides to add a critical level.

### 7. Data source labels

Three labels: **From visit** · **Self-entered** · **Doctor-assigned** (D-10).

"Doctor-assigned" = a value the mother reports for a metric that is in the Doctor's instructions. The mother can report only such metrics (D-11 revised), so every Group 2 value she reports is "Doctor-assigned"; "Self-entered" is used for Group 1 metrics and the weight declared on S-007 (D-33 revised).

### 8. Report status (same for the mother and clinical staff)

**Not viewed → Viewed → Escalated to doctor → Resolved** (D-18). Status only moves forward; "Escalated to doctor" may be skipped (D-43), and the system records "Viewed" when it is skipped.

Only reports that clinical staff need to see have a status. A Normal report with no symptoms has no status.

### 9. Formats

| Type | Example |
|---|---|
| Date | 26/09/2026 |
| Time | 20:15 |
| Date + time | 26/09/2026 · 20:15 |
| Blood pressure | 150/95 mmHg |
| Fetal heart rate / heart rate | 145 bpm |
| Weight | 56.5 kg |
| Temperature | 36.8 °C |

### 10. Terms

| Term in documents | Label on screen |
|---|---|
| Watch-flag | **Doctor's instructions** |
| Report | **Report** |
| Alert (S-028 only) | **Alert** |
| Routine tracking | **Self-tracked metrics** |

The word "Alert" (on screen: "Cảnh báo") is used only for an above-threshold report on S-028 (D-22).

### 11. Header and navigation

- **Header (child screens):** 56 px, `color-surface`, 1 px `color-border` bottom line, no shadow; ← 24 px · left-aligned page title · action icons · ✕ 24 px. Only Home and the first-time setup screen have no ←. Home uses the brand header: logo + "Mother & Baby 360" + tagline in `color-primary`.
- **Bottom bar, 5 tabs** (64 px, `color-surface`; D-80): Home (S-008) · Timeline (S-048) · Chatbot (S-031 → S-034) · From doctor (S-009, with the unread badge in `color-accent`) · Profile (S-103). Active tab `color-primary`, inactive `color-text-disabled`, labels Caption 12/400. Only these 5 root screens have the bar; other screens have ←. The round floating button (~56 px, gradient) exists only on the "Book" tab of the TCI app.
- ✕ is on Home and first-time setup and opens S-083 (close the sub-app, D-01) as a centred dialog. S-043 has no ←, ✕ or tab bar (D-50).

### 12. Shared states

| State | Look |
|---|---|
| **Empty** | Dashed frame: round icon, one sentence describing the state, CTA if needed |
| **Loading** | Grey `#EEEEEE` placeholders in place of content, layout unchanged |
| **Load error** | "⚠ Could not load data." + "Retry" |
| **Input error** | Field border in `color-error` + "⚠ Value outside the valid range" directly under the field, in `color-error` |

Valid ranges per metric are not set yet (**D-16, Pending SME**).

### Changes made by D-79

| Item | Before (D-27) | Now (D-79) |
|---|---|---|
| Font | not set (wireframe: Inter) | Roboto [estimated] |
| Type scale | 18 / 15 / 13 / 11 (4 levels) | 22 / 18 / 18 / 15 / 12 (5 levels) |
| Primary colour | moss green `#2F6F5E` (wireframe) | TCI green `#00A651` |
| Screen background | `#F7F8FA` | `#F5F5F5` |
| Text primary / secondary / disabled | `#1A1D1F` / `#6B7280` / `#B0B5BB` | `#212121` / `#6F6F6F` / `#B4B4B4` |
| Border | `#E2E5E9` | `#E0E0E0` |
| New tokens | — | `color-primary-light`, `color-primary-soft`, `color-hero-gradient`, `color-accent`, `color-avatar` |
| Removed | `color-surface-alt` `#F1F5F3` | replaced by `color-primary-soft` / `color-bg` |
| Icons | one outline style | 3 styles by context |
| Cards | one style | floating / bordered |
| Text link | underlined | not underlined, `color-primary` |
| Appointments tab | ordinary tab | round floating middle button; **removed by D-80** |

## UI label reference

The wireframe images show on-screen text in Vietnamese. This table maps the English labels used in every document to the text drawn on the wireframes. It is the only place in the package with Vietnamese text.

| Group | English (used in documents) | On-screen text (wireframe) |
|---|---|---|
| Status (case / report) | Not viewed | Chưa xem |
| Status (case / report) | Viewed | Đã xem |
| Status (case / report) | Escalated to doctor | Đã chuyển bác sĩ |
| Status (case / report) | Resolved | Đã xử lý |
| Status (case / report) | No action needed | Không cần xử lý |
| Status (case / report) | No doctor escalation needed | Không cần chuyển bác sĩ |
| Threshold label | Normal | Bình thường |
| Threshold label | Above threshold | Vượt ngưỡng |
| Threshold label | Not assessed | Chưa đánh giá |
| Data source label | From visit | Từ lần khám |
| Data source label | Self-entered | Mẹ tự nhập |
| Data source label | Doctor-assigned | Bác sĩ chỉ định |
| Case source | Metric report | Báo cáo chỉ số |
| Case source | Symptom | Triệu chứng |
| Case source | Chatbot | Chatbot |
| Metric group | Group 1 | Nhóm 1 |
| Metric group | Group 2 | Nhóm 2 |
| Metric group | Visit | Lần khám |
| Metric | Weight | Cân nặng |
| Metric | Temperature | Nhiệt độ |
| Metric | Heart rate | Nhịp tim |
| Metric | Sleep | Giấc ngủ |
| Metric | Blood pressure | Huyết áp |
| Metric | Blood glucose | Đường huyết |
| Metric | Urine protein | Protein niệu |
| Metric | Fetal heart rate | Tim thai |
| Urine protein level | Negative / Trace / 1+ / 2+ / 3+ | Âm tính / Vết / 1+ / 2+ / 3+ |
| Glucose context (code) | fasting / post_1h / post_2h (UI: Fasting / 1 h after meal / 2 h after meal) | Lúc đói / Sau ăn 1 giờ / Sau ăn 2 giờ |
| Symptom | No symptoms | Không có triệu chứng |
| Symptom (D-73) | Vaginal bleeding | Ra máu âm đạo |
| Symptom (D-73) | Severe abdominal pain | Đau bụng dữ dội |
| Symptom (D-73) | Waters breaking or fluid leakage (UI: Waters breaking / fluid leakage) | Vỡ ối / rỉ ối |
| Symptom (D-73) | Severe headache, dizziness or blurred vision (UI: Severe headache / dizziness / blurred vision) | Đau đầu dữ dội / chóng mặt / hoa mắt |
| Symptom (D-73) | Absence of fetal movement | Không cảm nhận được cử động thai |
| Symptom | Palpitations | Hồi hộp |
| Symptom | Other | Khác |
| Diary mood | Happy / Calm / Nervous / Tired / Worried | Vui / Bình yên / Hồi hộp / Mệt / Lo lắng |
| Message author | Mother / Father | Mẹ / Bố |
| Role | Mother / Nurse / Doctor | Mẹ / Y tá / Bác sĩ |
| Notification type | Report / Visit result / Appointment / Instruction reminder | Báo cáo / Kết quả khám / Lịch hẹn / Nhắc theo chỉ dẫn |
| Notification setting | Report responses | Phản hồi báo cáo |
| Notification setting | New visit results | Kết quả khám mới |
| Notification setting | Appointment reminders | Nhắc lịch hẹn |
| Notification setting | Doctor's-instruction reminders | Nhắc theo Chỉ dẫn của bác sĩ |
| Hospital record link | Pending link / Linked | Chờ liên kết / Đã liên kết |
| Due-date source | Self-entered / Hospital record | Mẹ tự nhập / Hồ sơ bệnh viện |
| Chatbot hand-off | Connect to nurse / No, thanks | Kết nối y tá / Không, cảm ơn |
| Chatbot notice (D-76; never "Alert") | Signs that need medical attention | Dấu hiệu cần chú ý y tế |
| Sex (D-71) | Female | Nữ |
| Journey stage (D-75) | First trimester / Second trimester / Third trimester / Full journey | Tam cá nguyệt 1 / Tam cá nguyệt 2 / Tam cá nguyệt 3 / Cả hành trình |
| Answer rating (not built — BOT-02) | Was this answer helpful? Yes / No | Câu trả lời có hữu ích? Có / Không |
| Term | Doctor's instructions (entity: Watch-Flag) | Chỉ dẫn của bác sĩ |
| Term | Self-tracked metrics | Chỉ số tự theo dõi |
| Term | Alert (used only on S-028) | Cảnh báo |
| Term | Report | Báo cáo |
| Term | case | ca |
| Term | mother / nurse / doctor / clinical staff | mẹ / y tá / bác sĩ / nhân viên y tế |
| Term | Red flag | Cờ đỏ |
| Term | TCI app (Thu Cuc app) / TCI account / TCI identity | app TCI / tài khoản TCI / danh tính TCI |
| Term | Mother & Baby 360 sub-app | sub-app Mẹ & Bé 360 |
| Term | gestational week | tuần thai |
| Term | due date (EDD) / first day of last menstrual period (LMP) | ngày dự sinh / ngày đầu kỳ kinh cuối |
| Term | visit | lần khám |
| Term | medical record number | mã hồ sơ khám |
| Term | Above-threshold guidance | Hướng dẫn khi vượt ngưỡng |
| Term | Guidance template | Mẫu hướng dẫn |
| Term | Safety note | Lưu ý an toàn |
| Term | Messages to Baby | Lời nhắn gửi con |
| Term | diary | nhật ký |
| Screen text (S-029) | Type: All ▾ | Loại: Tất cả ▾ |
| Screen text (S-023) | (reference range 110–160 bpm) | (tham chiếu 110–160 bpm) |
| Screen text (S-028) | Track progress in My reports. | Theo dõi xử lý trong Báo cáo của tôi. |
| Screen text (S-008, S-023) | 2 reports being handled | 2 báo cáo đang xử lý |
| Screen text (S-009) | Reminder: measure and report Blood pressure | Nhắc đo và báo cáo Huyết áp |
| Screen text (S-009) | Doctor's instructions · Dr. … | Chỉ dẫn của bác sĩ · BS. … |
| Term | Pregnancy timeline | Thai kỳ theo tuần |
| Screen title | Mother & Baby 360 | Mẹ & Bé 360 (tile) |
| Screen title | Pregnancy setup | Khai báo thai kỳ |
| Screen title | Home | Trang chủ |
| Screen title | Notifications | Thông báo |
| Screen title | Notification settings | Cài đặt thông báo |
| Screen title | Edit profile | Chỉnh sửa hồ sơ |
| Screen title | Health metrics | Chỉ số sức khỏe |
| Screen title | Enter self-tracked metrics | Nhập chỉ số tự theo dõi |
| Screen title | Metric history | Lịch sử chỉ số |
| Screen title | Report a metric | Báo cáo chỉ số |
| Screen title | Report status | Trạng thái báo cáo |
| Screen title | Metric alert | Cảnh báo chỉ số |
| Screen title | My reports (S-029; the former tab "Risk assessment" is removed) | Báo cáo của tôi |
| Screen title | Health chatbot | Trợ lý thai sản |
| Screen title | Pregnancy timeline | Thai kỳ theo tuần |
| Screen title | Add diary entry | Thêm nhật ký |
| Screen title | Cases to handle | Ca cần xử lý |
| Screen title | Mother quick profile | Hồ sơ nhanh của mẹ |
| Screen title | Close Mother & Baby 360? | Đóng Mẹ & Bé 360? |
| Screen title | Profile | Hồ sơ |
| Screen title | Session expired | Phiên làm việc hết hạn |
| Screen title (S-104, D-74) | Onboarding guide | Hướng dẫn sử dụng |
| Screen title (S-105, D-75) | My journey | Hành trình của mẹ |
| Screen text (S-007 / S-046, D-72) | Date of first antenatal check-up (optional) | Ngày khám thai đầu tiên (không bắt buộc) |
| Screen text (S-048, D-75) | Indicators this week / No indicators this week. | Chỉ số trong tuần / Tuần này chưa có chỉ số. |
| CTA (S-105, D-75) | Export PDF album | Xuất album PDF |
| CTA (S-104, D-74) | Skip / Next / Get started | Bỏ qua / Tiếp / Bắt đầu |
| Tab | Home / Timeline / Chatbot / From doctor / Profile | Trang chủ / Thai kỳ / Chatbot / Thông báo / Hồ sơ |
| CTA | Save metrics | Lưu chỉ số |
| CTA | Submit report | Gửi báo cáo |
| CTA | View status | Xem trạng thái |
| CTA | View report | Xem báo cáo |
| CTA | View metric history | Xem lịch sử chỉ số |
| CTA | + Report metric / + Report symptoms ("+ Report another metric" removed — D-11 revised) | + Báo cáo chỉ số / + Báo cáo triệu chứng |
| CTA | + Enter self-tracked metrics | + Nhập chỉ số tự theo dõi |
| CTA | + Add diary entry | + Thêm nhật ký |
| CTA | + Message from Mom / + Message from Dad | + Mẹ nhắn con / + Bố nhắn con |
| CTA | Save diary entry | Lưu nhật ký |
| CTA | Save changes | Lưu thay đổi |
| CTA | Save instruction | Lưu chỉ dẫn |
| CTA | Agree & continue / Later | Đồng ý & tiếp tục / Để sau |
| CTA | Confirm / Cancel / Close / Edit / Send | Xác nhận / Hủy / Đóng / Sửa / Gửi |
| CTA | Stay / Close app | Ở lại / Đóng app |
| CTA | Back to TCI app | Quay lại app TCI |
| Error screen (15/11/2026) | Could not complete this | Chưa thực hiện được |
| Error screen (15/11/2026) | Some of the information sent is not valid. Go back and try again. | Một số thông tin gửi đi chưa hợp lệ. Mẹ hãy quay lại và thử lại. |
| Error screen (15/11/2026) | This is not available for this account. | Nội dung này không dành cho tài khoản đang dùng. |
| Error screen (15/11/2026) | This page or item is no longer available. | Trang hoặc nội dung này không còn nữa. |
| Error screen (15/11/2026) | This was already changed, maybe on another screen. Open it again to see the latest state. | Việc này đã được thực hiện, có thể trên một máy khác. Hãy mở lại để xem trạng thái mới nhất. |
| Error screen (15/11/2026) | Something went wrong. Please try again. | Đã có lỗi xảy ra. Vui lòng thử lại. |
| Error screen (15/11/2026) | Go to Home | Về Trang chủ |
| Error screen (15/11/2026) | Go to the case list | Về danh sách ca |
| Error screen (15/11/2026) | This case was already updated, maybe on another screen. Its current status is shown below. | Ca này vừa được cập nhật, có thể trên một màn hình khác. Trạng thái hiện tại hiển thị bên dưới. |
| CTA | Retry / Refresh | Thử lại / Làm mới |
| CTA | Mark all as read | Đánh dấu đã đọc tất cả |
| CTA | Mark as viewed | Đánh dấu Đã xem |
| CTA | Escalate to doctor | Chuyển bác sĩ |
| CTA | Close case | Đóng ca |
| CTA | Send guidance | Gửi hướng dẫn |
| CTA | Emergency call / Call hotline / nurse | Gọi khẩn cấp / Gọi tổng đài / y tá |
| CTA | Book a visit ↗ | Đặt lịch khám ↗ |
| CTA | I know my due date / I know the first day of my last period | Tôi biết ngày dự sinh / Tôi biết ngày đầu kỳ kinh cuối |
| Message | Calculated by the system | Hệ thống tính được |
| Message | Report submitted / Metrics saved / Diary entry saved / Changes saved | Đã gửi báo cáo / Đã lưu chỉ số / Đã lưu nhật ký / Đã lưu thay đổi |
| Message | Sent to a nurse | Đã chuyển cho y tá |
| Message | This needs a proper consultation. | Vấn đề này cần được tư vấn kỹ. |
| Message | ⚠ Could not load data. | ⚠ Không tải được dữ liệu. |
| Message | ⚠ Value outside the valid range | ⚠ Giá trị ngoài khoảng hợp lệ |
| Message | No visit this week. | Tuần này chưa có lần khám. |
| Message | You have not submitted any reports. | Mẹ chưa gửi báo cáo nào. |
| Message | You have no notifications. | Mẹ chưa có thông báo nào. |
| Message | No cases to handle. | Không có ca nào cần xử lý. |
| Message | Your doctor has not given you any instructions yet. | Bác sĩ chưa có chỉ dẫn nào cho mẹ. |

### Labels added for the app (D-79) — proposed, to be reviewed by the owners of `screens/` (Chi, Ánh)

Text the screens need that the wireframes do not show (form labels, messages, demo pages). Same columns as above; `{name}` marks a value filled in by the app.

| Group | English (used in documents) | On-screen text (wireframe) |
|---|---|---|
| App shell (D-79) | Back | Quay lại |
| App shell (D-79) | Mother & Baby 360 is for expectant mothers. | Mẹ & Bé 360 dành cho mẹ bầu. |
| App shell (D-79) | TCI app (simulated host) | App TCI (mô phỏng) |
| App shell (D-79) | Thu Cuc Health System – TCI | Hệ Thống Y Tế Thu Cúc – TCI |
| App shell (D-79) | Lifelong health care for you! | Chăm sóc sức khoẻ trọn đời cho bạn! |
| App shell (D-79) | Stand-in for the Thu Cuc patient app: how the real app passes the identity is not decided yet. Every identity here is invented. | Mô phỏng app bệnh nhân Thu Cúc: cách app thật chuyển danh tính chưa được quyết định. Mọi danh tính ở đây đều là giả. |
| App shell (D-79) | Open Mother & Baby 360 as | Mở Mẹ & Bé 360 với tài khoản |
| App shell (D-79) | Simulate another TCI account | Mô phỏng tài khoản TCI khác |
| App shell (D-79) | TCI app booking flow | Luồng đặt lịch của app TCI |
| App shell (D-79) | Booking happens in the TCI app. This page stands in for it; no appointment is stored in Mother & Baby 360. | Việc đặt lịch diễn ra trong app TCI. Trang này chỉ đứng thay cho nó; Mẹ & Bé 360 không lưu lịch hẹn nào. |
| App shell (D-79) | Back to Mother & Baby 360 | Quay lại Mẹ & Bé 360 |
| App shell (D-79) | Demo start page | Trang bắt đầu demo |
| App shell (D-79) | Mother side — open from the TCI app | Phía mẹ — mở từ app TCI |
| App shell (D-79) | Consent, guide and pregnancy setup the first time, then Home. | Lần đầu: đồng ý, hướng dẫn và khai báo thai kỳ; các lần sau vào thẳng Trang chủ. |
| App shell (D-79) | Clinical web | Web nhân viên y tế |
| App shell (D-79) | Nurses and doctors handle the mothers' reports. | Y tá và bác sĩ xử lý báo cáo của mẹ. |
| App shell (D-79) | Go straight to a mother's Home (demo) | Vào thẳng Trang chủ của một mẹ (demo) |
| App shell (D-79) | You can come back at any time from the TCI app. | Mẹ sẽ quay lại app TCI. Dữ liệu đã lưu vẫn được giữ, lần sau mở lại không cần đăng nhập. |
| App shell (D-79) | Record no. {code} | Mã hồ sơ {code} |
| App shell (D-79) | Week {n} | Tuần {n} |
| App shell (D-79) | ‹ Week {n} | ‹ Tuần {n} |
| App shell (D-79) | Week {n} › | Tuần {n} › |
| App shell (D-79) | All | Tất cả |
| App shell (D-79) | Male | Nam |
| App shell (D-79) | Full name | Họ tên |
| App shell (D-79) | Date of birth | Ngày sinh |
| App shell (D-79) | Sex | Giới tính |
| App shell (D-79) | Phone number | Số điện thoại |
| App shell (D-79) | Medical record number | Mã hồ sơ khám |
| App shell (D-79) | Medical record number (optional) | Mã hồ sơ khám (không bắt buộc) |
| ACC screens (D-79) | Connect to your TCI account | Kết nối với tài khoản TCI của mẹ |
| ACC screens (D-79) | Mother & Baby 360 will use the following information from the TCI app: | Mẹ & Bé 360 sẽ dùng các thông tin sau từ app TCI, không cần đăng nhập lại: |
| ACC screens (D-79) | Full name, date of birth, phone number | Họ tên, ngày sinh, số điện thoại |
| ACC screens (D-79) | Medical record number at Thu Cuc | Mã hồ sơ khám tại Thu Cúc |
| ACC screens (D-79) | Results of your prenatal visits | Kết quả các lần khám thai |
| ACC screens (D-79) | I agree to the Terms and the Privacy Policy | Tôi đồng ý với Điều khoản và Chính sách quyền riêng tư |
| ACC screens (D-79) | Page {n} of {total} | Trang {n}/{total} |
| ACC screens (D-79) | Health dashboard | Bảng sức khỏe |
| ACC screens (D-79) | See the results of your visits and the metrics your doctor asked you to watch. | Xem kết quả các lần khám và các chỉ số bác sĩ dặn mẹ theo dõi. |
| ACC screens (D-79) | Report a metric or symptom | Báo cáo chỉ số hoặc triệu chứng |
| ACC screens (D-79) | Tell the care team when a watched metric or a symptom worries you. | Báo cho đội ngũ chăm sóc khi một chỉ số cần theo dõi hoặc một triệu chứng khiến mẹ lo lắng. |
| ACC screens (D-79) | Pregnancy timeline & diary | Dòng thời gian & nhật ký thai kỳ |
| ACC screens (D-79) | Follow your pregnancy week by week and keep your memories. | Theo dõi thai kỳ từng tuần và lưu giữ kỷ niệm. |
| ACC screens (D-79) | Ask general questions about pregnancy and baby care. | Hỏi các câu hỏi chung về thai kỳ và chăm sóc bé. |
| ACC screens (D-79) | Pregnancy information | Thông tin thai kỳ |
| ACC screens (D-79) | So the app knows which gestational week you are in. | Để app biết mẹ đang ở tuần thai thứ mấy. |
| ACC screens (D-79) | Due date | Ngày dự sinh |
| ACC screens (D-79) | Due date * | Ngày dự sinh * |
| ACC screens (D-79) | First day of last period * | Ngày đầu kỳ kinh cuối * |
| ACC screens (D-79) | The due date your doctor set after an ultrasound (if any). | Ngày dự sinh bác sĩ đã xác định sau siêu âm (nếu có). |
| ACC screens (D-79) | Week {n} · day {d} | Tuần {n} · ngày {d} |
| ACC screens (D-79) | Today {today} · Due {edd} | Hôm nay {today} · Dự sinh {edd} |
| ACC screens (D-79) | Height (optional) | Chiều cao (không bắt buộc) |
| ACC screens (D-79) | Current weight (optional) | Cân nặng hiện tại (không bắt buộc) |
| ACC screens (D-79) | Hello, {name}! | Xin chào, Mẹ {name}! |
| ACC screens (D-79) | Due date: {date} | Ngày dự sinh: {date} |
| ACC screens (D-79) | {n} reports being handled | {n} báo cáo đang xử lý |
| ACC messages (D-79) | Please tick the box to agree to the Terms and the Privacy Policy. | Mẹ hãy tích vào ô để đồng ý với Điều khoản và Chính sách quyền riêng tư. |
| ACC messages (D-79) | Choose: I know my due date, or I know the first day of my last period. | Hãy chọn: Tôi biết ngày dự sinh, hoặc Tôi biết ngày đầu kỳ kinh cuối. |
| ACC messages (D-79) | Enter the date. | Hãy nhập ngày. |
| ACC messages (D-79) | Value outside the valid range: the due date cannot be in the past and the week must be 0 – 42. | Giá trị ngoài khoảng hợp lệ: ngày dự sinh không được ở quá khứ và tuần thai phải trong khoảng 0 – 42. |
| ACC messages (D-79) | Enter a number. | Hãy nhập một số. |
| ACC messages (D-79) | The first check-up date must be within this pregnancy and not in the future. | Ngày khám thai đầu tiên phải nằm trong thai kỳ này và không ở tương lai. |
| HLT screens (D-79) | Data updated. | Đã cập nhật dữ liệu. |
| HLT screens (D-79) | Latest visit results | Kết quả lần khám gần nhất |
| HLT screens (D-79) | Visit date {date} · not editable | Ngày khám {date} · không chỉnh sửa được |
| HLT screens (D-79) | (reference range {range}) | (tham chiếu {range}) |
| HLT screens (D-79) | No visit results yet. | Chưa có kết quả khám. |
| HLT screens (D-79) | {n} metrics: {names} | {n} chỉ số: {names} |
| HLT screens (D-79) | No self-tracked metrics yet. | Chưa có chỉ số tự theo dõi. |
| HLT screens (D-79) | Optional. Enter the metrics you want to track; you can leave fields you don't need blank. | Không bắt buộc. Mẹ nhập các chỉ số muốn theo dõi; có thể bỏ trống các ô không cần. |
| HLT screens (D-79) | Enter value | Nhập giá trị |
| HLT screens (D-79) | Measured at | Thời điểm đo |
| HLT screens (D-79) | Bedtime | Giờ đi ngủ |
| HLT screens (D-79) | Wake-up time | Giờ thức dậy |
| HLT screens (D-79) | No threshold check, no report created. | Không so ngưỡng, không tạo báo cáo. |
| HLT messages (D-79) | Value outside the valid range | Giá trị ngoài khoảng hợp lệ |
| HLT messages (D-79) | Enter the measured time. | Hãy nhập thời điểm đo. |
| HLT messages (D-79) | The measured time cannot be later than now. | Thời điểm đo không được muộn hơn hiện tại. |
| HLT messages (D-79) | Enter the bedtime. | Hãy nhập giờ đi ngủ. |
| HLT messages (D-79) | Enter the wake-up time. | Hãy nhập giờ thức dậy. |
| HLT messages (D-79) | The wake-up time must be after the bedtime (within 24 hours). | Giờ thức dậy phải sau giờ đi ngủ (trong vòng 24 giờ). |
| HLT messages (D-79) | The wake-up time cannot be later than now. | Giờ thức dậy không được muộn hơn hiện tại. |
| HLT messages (D-79) | Enter at least one metric. | Hãy nhập ít nhất một chỉ số. |
| HLT messages (D-79) | Set up the pregnancy first. | Hãy khai báo thai kỳ trước. |
| ALR screens (D-79) | Report symptoms | Báo cáo triệu chứng |
| ALR screens (D-79) | Change metric ▾ | Đổi chỉ số ▾ |
| ALR screens (D-79) | Symptoms only | Chỉ báo cáo triệu chứng |
| ALR screens (D-79) | Systolic (mmHg) | Tâm thu (mmHg) |
| ALR screens (D-79) | Diastolic (mmHg) | Tâm trương (mmHg) |
| ALR screens (D-79) | Measurement time | Thời điểm đo trong ngày |
| ALR screens (D-79) | Choose… | Chọn… |
| ALR screens (D-79) | Blood glucose (mmol/L) | Đường huyết (mmol/L) |
| ALR screens (D-79) | Choose the measurement time to see the threshold. | Chọn thời điểm đo để xem ngưỡng. |
| ALR screens (D-79) | Above threshold when ≥ {value} | Vượt ngưỡng khi ≥ {value} |
| ALR screens (D-79) | Accompanying symptoms (select multiple) | Triệu chứng kèm theo (chọn nhiều) |
| ALR screens (D-79) | Describe other symptom (max 100 characters) | Mô tả triệu chứng khác (tối đa 100 ký tự) |
| ALR screens (D-79) | Note | Ghi chú |
| ALR screens (D-79) | Your report has been sent to clinical staff. | Đã gửi báo cáo tới nhân viên y tế. |
| ALR screens (D-79) | Doctor's guidance | Hướng dẫn của bác sĩ |
| ALR screens (D-79) | Hotline number pending | Số tổng đài đang chờ xác nhận |
| ALR screens (D-79) | Call hotline / nurse | Gọi tổng đài / y tá |
| ALR screens (D-79) | Your question: | Câu hỏi của mẹ: |
| ALR screens (D-79) | Sent | Gửi lúc |
| ALR screens (D-79) | Report code {code} | Mã báo cáo {code} |
| ALR screens (D-79) | Measured | Đo lúc |
| ALR screens (D-79) | Submitted | Gửi lúc |
| ALR screens (D-79) | Symptom report | Báo cáo triệu chứng |
| ALR screens (D-79) | Symptoms: | Triệu chứng: |
| ALR screens (D-79) | Mother's note: | Ghi chú của mẹ: |
| ALR screens (D-79) | Handling progress | Tiến trình xử lý |
| ALR screens (D-79) | Dr. {name} | BS. {name} |
| ALR screens (D-79) | Nurse {name} | Y tá {name} |
| ALR screens (D-79) | Response from Dr. {name} | Phản hồi từ BS. {name} |
| ALR screens (D-79) | Response from Nurse {name} | Phản hồi từ y tá {name} |
| ALR messages (D-79) | Choose a metric from your Doctor's instructions, or report symptoms. | Hãy chọn một chỉ số trong Chỉ dẫn của bác sĩ, hoặc báo cáo triệu chứng. |
| ALR messages (D-79) | Please select your symptoms | Mẹ hãy chọn triệu chứng |
| ALR messages (D-79) | Choose symptoms from the list. | Hãy chọn triệu chứng trong danh sách. |
| ALR messages (D-79) | "No symptoms" cannot be combined with other symptoms. | "Không có triệu chứng" không chọn cùng triệu chứng khác được. |
| ALR messages (D-79) | Describe the other symptom. | Hãy mô tả triệu chứng khác. |
| ALR messages (D-79) | Only when "Other" is selected. | Chỉ nhập khi đã chọn "Khác". |
| ALR messages (D-79) | At most {n} characters. | Tối đa {n} ký tự. |
| ALR messages (D-79) | Enter a whole number (mmHg). | Hãy nhập số nguyên (mmHg). |
| ALR messages (D-79) | Enter a number (mmol/L). | Hãy nhập một số (mmol/L). |
| ALR messages (D-79) | Choose the measurement time. | Hãy chọn thời điểm đo trong ngày. |
| ALR messages (D-79) | Choose a level. | Hãy chọn mức. |
| TML screens (D-79) | Visit {date} | Lần khám {date} |
| TML screens (D-79) | Ultrasound image, {date} | Ảnh siêu âm, {date} |
| TML screens (D-79) | Fetal length | Chiều dài thai |
| TML screens (D-79) | Estimated weight | Cân nặng ước tính |
| TML screens (D-79) | Measurements per ultrasound report dated {date} | Số đo theo phiếu siêu âm ngày {date} |
| TML screens (D-79) | Doctor's note | Ghi chú của bác sĩ |
| TML screens (D-79) | Family | Gia đình |
| TML screens (D-79) | From Mom | Mẹ nhắn |
| TML screens (D-79) | From Dad | Bố nhắn |
| TML screens (D-79) | Diary | Nhật ký |
| TML screens (D-79) | Diary photo, {date} | Ảnh nhật ký, {date} |
| TML screens (D-79) | No diary entry this week. | Tuần này chưa có nhật ký. |
| TML screens (D-79) | Week {n} – current week | Tuần {n} – tuần hiện tại |
| TML screens (D-79) | Date {date} (automatic) | Ngày {date} (tự động) |
| TML screens (D-79) | Content * | Nội dung * |
| TML screens (D-79) | Mood (optional) | Tâm trạng (không bắt buộc) |
| TML screens (D-79) | Photos (optional) — Take photo / Library, JPG or PNG, up to 5, 10 MB each | Ảnh (không bắt buộc) — Chụp ảnh / Thư viện, JPG hoặc PNG, tối đa 5 ảnh, mỗi ảnh 10 MB |
| TML screens (D-79) | The diary entry is linked to the current week. | Nhật ký được gắn với tuần thai hiện tại. |
| TML messages (D-79) | Please write something about today. | Mẹ hãy viết vài dòng về hôm nay. |
| TML messages (D-79) | Choose one of the moods. | Hãy chọn một tâm trạng. |
| TML messages (D-79) | At most {n} photos. | Tối đa {n} ảnh. |
| TML messages (D-79) | Photos must be JPG or PNG. | Ảnh phải là JPG hoặc PNG. |
| TML messages (D-79) | Each photo must be 10 MB or smaller. | Mỗi ảnh tối đa 10 MB. |
| BOT screens (D-79) | The chatbot provides general reference information only and does not replace your doctor's advice. | Chatbot chỉ cung cấp thông tin tham khảo chung, không thay thế lời khuyên của bác sĩ. |
| BOT screens (D-79) | Hello, Mom! | Xin chào mẹ! |
| BOT screens (D-79) | I can answer general questions about pregnancy and baby care. | Mình có thể trả lời các câu hỏi chung về thai kỳ và chăm sóc bé. |
| BOT screens (D-79) | Suggested questions | Câu hỏi gợi ý |
| BOT screens (D-79) | How can I eat beef safely during pregnancy? | Ăn thịt bò thế nào cho an toàn khi mang thai? |
| BOT screens (D-79) | How can I produce more breast milk? | Làm sao để có nhiều sữa mẹ hơn? |
| BOT screens (D-79) | What should I look for when choosing formula for my baby? | Nên chú ý gì khi chọn sữa công thức cho bé? |
| BOT screens (D-79) | How should Dad read to the baby during pregnancy? | Bố nên đọc truyện cho bé trong bụng mẹ thế nào? |
| BOT screens (D-79) | For reference only; does not replace your doctor's advice. | Chỉ để tham khảo; không thay thế lời khuyên của bác sĩ. |
| BOT screens (D-79) | Your question relates to your own health, so the chatbot does not answer it directly. If you agree, your question will be sent to a nurse. | Câu hỏi liên quan đến sức khỏe của chính mẹ nên chatbot không trả lời trực tiếp. Nếu mẹ đồng ý, câu hỏi sẽ được chuyển cho y tá. |
| BOT screens (D-79) | If you have any emergency signs, call {hotline}. | Nếu có dấu hiệu khẩn cấp, mẹ hãy gọi {hotline}. |
| BOT screens (D-79) | Type your question… | Nhập câu hỏi của mẹ… |
| BOT messages (D-79) | I can only help with pregnancy, prenatal care, nutrition and postpartum wellness. Could you ask me a pregnancy question? | Mình chỉ hỗ trợ các chủ đề thai kỳ, chăm sóc trước sinh, dinh dưỡng và sức khỏe sau sinh. Mẹ hãy hỏi một câu về thai kỳ nhé? |
| BOT messages (D-79) | [Sample chatbot answer] | [Câu trả lời mẫu của chatbot] |
| BOT messages (D-79) | Type your question. | Mẹ hãy nhập câu hỏi. |
| BOT messages (D-79) | ⚠ Could not get an answer. Retry | ⚠ Chưa nhận được câu trả lời. Thử lại |
| BOT messages (D-79) | I can't give a safe answer to this question here. Please ask your doctor or a nurse. | Câu này mình chưa thể trả lời an toàn ở đây. Mẹ hãy hỏi bác sĩ hoặc y tá nhé. |
| BOT data lookup (D-89) | The chatbot only repeats your data from the app and does not assess it. If you are worried, ask a nurse. | Chatbot chỉ nhắc lại dữ liệu của mẹ trong app, không đánh giá. Nếu lo lắng, mẹ hãy hỏi y tá. |
| BOT data lookup (D-89) | View in the app | Xem trong app |
| BOT data lookup (D-89) | You have no upcoming appointment in the TCI app. | Mẹ chưa có lịch hẹn sắp tới trong app TCI. |
| BOT data lookup (D-89) | Your next appointment: {day}, {at}, {place}. | Lịch hẹn tới của mẹ: {day}, {at}, tại {place}. |
| BOT data lookup (D-89) | That is today. | Tức là hôm nay. |
| BOT data lookup (D-89) | That is tomorrow. | Tức là ngày mai. |
| BOT data lookup (D-89) | That is in {days} days. | Tức là còn {days} ngày nữa. |
| BOT data lookup (D-89) | There is no visit in the app yet. | Trong app chưa có lần khám nào. |
| BOT data lookup (D-89) | {days} days ago | {days} ngày trước |
| BOT data lookup (D-89) | Your latest visit: {date} ({ago}). | Lần khám gần nhất của mẹ: ngày {date} ({ago}). |
| BOT data lookup (D-89) | Recorded at that visit: {items}. | Ghi nhận ở lần khám đó: {items}. |
| BOT data lookup (D-89) | There is no {metric} value in the app yet. | Trong app chưa có giá trị {metric} nào. |
| BOT data lookup (D-89) | Latest {metric}: {value}, {date} ({source}). | Chỉ số {metric} gần nhất: {value}, {date} ({source}). |
| BOT data lookup (D-89) | This is the only {metric} value in the app. | Đây là giá trị {metric} duy nhất trong app. |
| BOT data lookup (D-89) | The one before: {value}, {date}. | Lần trước đó: {value}, {date}. |
| BOT data lookup (D-89) | Change: {change}. | Chênh lệch: {change}. |
| BOT data lookup (D-89) | systolic {s}, diastolic {d} mmHg | tâm thu {s}, tâm trương {d} mmHg |
| BOT data lookup (D-89) | Your pregnancy profile is not set up yet. | Mẹ chưa khai báo thông tin thai kỳ. |
| BOT data lookup (D-89) | You are in week {week} of your pregnancy. | Mẹ đang ở tuần thai thứ {week}. |
| BOT data lookup (D-89) | Due date: {edd}, in {days} days. | Ngày dự sinh: {edd}, còn {days} ngày. |
| BOT data lookup (D-89) | You have no unread notices. | Mẹ không có thông báo nào chưa đọc. |
| BOT data lookup (D-89) | You have {n} unread notices. | Mẹ có {n} thông báo chưa đọc. |
| BOT data lookup (D-89) | Latest: {title}, {at}. | Mới nhất: {title}, {at}. |
| BOT data lookup (D-89) | None of your reports is being handled now. | Hiện không có báo cáo nào của mẹ đang được xử lý. |
| BOT data lookup (D-89) | Reports being handled: {n}. The latest is {status}. | Báo cáo đang được xử lý: {n}. Báo cáo mới nhất: {status}. |
| BOT data lookup (D-89) | Your doctor has no tracking instruction for you now. | Hiện bác sĩ không có chỉ dẫn theo dõi nào cho mẹ. |
| BOT data lookup (D-89) | Your doctor asked you to track: {metrics}. | Bác sĩ dặn mẹ theo dõi: {metrics}. |
| BOT data lookup (D-93) | There is no fetal measurement in the app yet. | Trong app chưa có số đo thai nhi nào. |
| BOT data lookup (D-93) | Latest fetal measurements ({date}): {items}. | Số đo thai nhi gần nhất ({date}): {items}. |
| BOT data lookup (D-93) | estimated weight {w} g | cân nặng ước tính {w} g |
| BOT data lookup (D-93) | length {l} cm | chiều dài {l} cm |
| BOT data lookup (D-93) | The chatbot cannot do this for you. You can do it yourself in the app. | Chatbot chưa làm thay mẹ việc này được. Mẹ tự làm trong app ở đây nhé. |
| BOT data lookup (D-93) | Booking, changing or cancelling an appointment is done in the TCI app. Your appointments are here. | Đặt, đổi hoặc huỷ lịch khám làm trong app TCI. Lịch hẹn của mẹ ở đây. |
| BOT data lookup (D-94) | Medical record number: {code}. | Mã hồ sơ khám: {code}. |
| BOT data lookup (D-94) | Hospital record link: {status}. | Liên kết hồ sơ bệnh viện: {status}. |
| BOT data lookup (D-94) | Height: {h} cm. | Chiều cao: {h} cm. |
| BOT data lookup (D-94) | Blood type, history and allergies are not shown in the app: please ask your doctor at your next visit. | Nhóm máu, tiền sử và dị ứng không có trong app: mẹ hỏi bác sĩ ở lần khám tới nhé. |
| BOT data lookup (D-94) | Doctor's note: “{note}” | Ghi chú của bác sĩ: “{note}” |
| BOT data lookup (D-94) | The doctor left no note at this visit. | Lần khám này bác sĩ không để lại ghi chú. |
| BOT data lookup (D-94) | Ultrasound: {items}. | Siêu âm: {items}. |
| BOT data lookup (D-94) | the last {n} days | {n} ngày qua |
| BOT data lookup (D-94) | the whole pregnancy | cả thai kỳ |
| BOT data lookup (D-94) | No {metric} value in {span}. | Không có giá trị {metric} nào trong {span}. |
| BOT data lookup (D-94) | {metric} in {span}: {n} readings, the latest {value} ({date}). | {metric} trong {span}: {n} lần đo, gần nhất {value} ({date}). |
| BOT data lookup (D-94) | Average {avg}, lowest {low}, highest {high} {unit}. | Trung bình {avg}, thấp nhất {low}, cao nhất {high} {unit}. |
| BOT data lookup (D-94) | Change from the first to the latest reading: {change}. | Chênh lệch từ lần đo đầu đến lần gần nhất: {change}. |
| BOT data lookup (D-94) | You have no diary entry yet. | Mẹ chưa viết nhật ký nào. |
| BOT data lookup (D-94) | You have written {n} diary entries; the latest on {date}. | Mẹ đã viết {n} trang nhật ký; trang gần nhất ngày {date}. |
| BOT data lookup (D-94) | No diary entry on {date}. | Ngày {date} mẹ không viết nhật ký. |
| BOT data lookup (D-94) | No diary entry in the last 7 days. | 7 ngày qua mẹ chưa viết nhật ký. |
| BOT data lookup (D-94) | {date} ({mood}): “{entry}” | {date} ({mood}): “{entry}” |
| BOT data lookup (D-94) | There is no message to the baby yet. | Chưa có lời nhắn nào gửi bé. |
| BOT data lookup (D-94) | Message from {author} (week {week}): “{message}” | Lời nhắn của {author} (tuần {week}): “{message}” |
| BOT data lookup (D-94) | No nurse or doctor has replied to you yet. | Chưa có y tá hay bác sĩ nào phản hồi mẹ. |
| BOT data lookup (D-94) | Latest reply from {role} {name} ({date}): | Phản hồi gần nhất của {role} {name} ({date}): |
| BOT data lookup (D-94) | To do: {items}. | Việc cần làm: {items}. |
| BOT data lookup (D-94) | Follow-up visit: {when}. | Hẹn khám: {when}. |
| BOT data lookup (D-94) | You have sent {n} reports; {k} are being handled now. | Mẹ đã gửi {n} báo cáo; {k} báo cáo đang được xử lý. |
| BOT chat (D-95) | Your latest {metric} readings: {items}. | Các lần đo {metric} gần nhất của mẹ: {items}. |
| BOT chat (D-95) | Hello, Mom! I can answer general questions about pregnancy and read your data in this app. What would you like to ask? | Chào mẹ! Mình trả lời được các câu hỏi chung về thai kỳ và đọc dữ liệu của mẹ trong app. Mẹ muốn hỏi gì ạ? |
| BOT chat (D-95) | You're welcome, Mom! Ask me anytime. | Không có gì ạ! Mẹ cần gì cứ hỏi mình nhé. |
| BOT chat (D-95) | I am the pregnancy assistant of Mother & Baby 360. I answer general questions about pregnancy and read your data in this app; I do not diagnose and do not replace your doctor. | Mình là trợ lý thai sản của Mẹ & Bé 360. Mình trả lời câu hỏi chung về thai kỳ và đọc dữ liệu của mẹ trong app; mình không chẩn đoán và không thay thế bác sĩ. |
| BOT chat (D-95) | Goodbye, Mom! Take care of yourself and the baby. | Tạm biệt mẹ! Mẹ giữ gìn sức khỏe cho mình và bé nhé. |
| BOT chat (D-95) | Could you ask the whole question again, Mom? For example: “What was my last blood pressure?” | Mẹ hỏi lại đầy đủ giúp mình nhé? Ví dụ: “Huyết áp lần trước của em là bao nhiêu?” |
| BOT chat (D-95) | For prices, packages, insurance, addresses and opening hours of Thu Cuc Hospital, please see the TCI app or call {hotline}. | Giá khám, gói dịch vụ, bảo hiểm, địa chỉ và giờ làm việc của Bệnh viện Thu Cúc: mẹ xem trong app TCI hoặc gọi {hotline} nhé. |
| CLI screens (D-79) | Nurse: {name} | Y tá: {name} |
| CLI screens (D-79) | change | đổi |
| CLI screens (D-79) | Choose a staff member (demo) | Chọn nhân viên y tế (demo) |
| CLI screens (D-79) | Staff come from the sample data; there is no staff sign-in yet. | Nhân viên lấy từ dữ liệu mẫu; chưa có đăng nhập cho nhân viên. |
| CLI screens (D-79) | Sort: Newest | Sắp xếp: Mới nhất |
| CLI screens (D-79) | Gestational age | Tuổi thai |
| CLI screens (D-79) | Case source | Nguồn ca |
| CLI screens (D-79) | Content | Nội dung |
| CLI screens (D-79) | Value | Giá trị |
| CLI screens (D-79) | Submitted at | Thời điểm gửi |
| CLI screens (D-79) | Status | Trạng thái |
| CLI screens (D-79) | Last visit | Lần khám gần nhất |
| CLI screens (D-79) | Medical history | Tiền sử |
| CLI screens (D-79) | Obstetric history (PARA) | Tiền sử sản khoa (PARA) |
| CLI screens (D-79) | Blood type | Nhóm máu |
| CLI screens (D-79) | Allergies | Dị ứng |
| CLI screens (D-79) | None | Không có |
| CLI screens (D-79) | Assigned {date} · Dr. {name} | Chỉ định {date} · BS. {name} |
| CLI screens (D-79) | No instructions. | Chưa có chỉ dẫn. |
| CLI screens (D-79) | Add / edit instruction | Thêm / sửa chỉ dẫn |
| CLI screens (D-79) | Doctor only | Chỉ bác sĩ |
| CLI screens (D-79) | Metric to monitor | Chỉ số cần theo dõi |
| CLI screens (D-79) | Note for the mother (how to measure, frequency) | Ghi chú cho mẹ (cách đo, tần suất) |
| CLI screens (D-79) | Enter a note… | Nhập ghi chú… |
| CLI screens (D-79) | Above-threshold guidance (shown on S-028 when a report is above threshold) | Hướng dẫn khi vượt ngưỡng (hiện trên S-028 khi báo cáo vượt ngưỡng) |
| CLI screens (D-79) | Choose a guidance template ▾ | Chọn mẫu hướng dẫn ▾ |
| CLI screens (D-79) | Add custom text for this mother (optional)… | Thêm nội dung riêng cho mẹ này (không bắt buộc)… |
| CLI screens (D-79) | You can choose only a template, only custom text, or both. If there is nothing, S-028 uses the hospital's default template. | Có thể chọn chỉ mẫu, chỉ nội dung riêng, hoặc cả hai. Nếu không có gì, S-028 dùng mẫu mặc định của bệnh viện. |
| CLI screens (D-79) | Report {code} | Báo cáo {code} |
| CLI screens (D-79) | Source | Nguồn |
| CLI screens (D-79) | Chatbot question | Câu hỏi chatbot |
| CLI screens (D-79) | Source: Chatbot · whole conversation | Nguồn: Chatbot · toàn bộ hội thoại |
| CLI screens (D-79) | Responses sent | Phản hồi đã gửi |
| CLI screens (D-79) | Send guidance to the mother | Gửi hướng dẫn cho mẹ |
| CLI screens (D-79) | Or write / edit the text… | Hoặc viết / sửa nội dung… |
| CLI screens (D-79) | The mother sees the guidance on S-026. Sending guidance does not change the status. | Mẹ xem hướng dẫn trên S-026. Gửi hướng dẫn không làm đổi trạng thái. |
| CLI screens (D-79) | Metric history — {metric} | Lịch sử chỉ số — {metric} |
| CLI screens (D-79) | Latest visit | Lần khám gần nhất |
| CLI screens (D-79) | Visit history | Lịch sử khám |
| CLI screens (D-79) | Conclusion: | Kết luận: |
| CLI screens (D-79) | No visit yet. | Chưa có lần khám. |
| Visit type (seed, D-79) | Routine antenatal check-up | Khám thai định kỳ |
| Visit type (seed, D-79) | Anomaly scan | Siêu âm hình thái |
| UI package (D-80) | App name | Mẹ & Bé 360 |
| UI package (D-80) | With you through pregnancy | Đồng hành suốt thai kỳ |
| UI package (D-80) | Timeline | Thai kỳ |
| UI package (D-80) | From doctor | Thông báo |
| UI package (D-80) | Notices from your doctor | Thông báo |
| UI package (D-80) | See the status of each report | Xem trạng thái từng báo cáo |
| UI package (D-80) | days to go | ngày nữa |
| UI package (D-80) | Week {n} + {d} days | Tuần {n} + {d} ngày |
| UI package (D-80) | Report metric / symptom | Báo cáo chỉ số / triệu chứng |
| UI package (D-80) | You have {n} new notices | Mẹ có {n} thông báo mới |
| UI package (D-80) | My metrics | Chỉ số của mẹ |
| UI package (D-80) | No diary entry today yet | Hôm nay chưa có nhật ký |
| UI package (D-80) | Note a feeling or a photo of your bump | Ghi lại cảm xúc hay một tấm ảnh bụng bầu |
| UI package (D-80) | Write | Viết |
| UI package (D-80) | Fill in what you have, not all 4 are needed. These metrics are not checked against a threshold. | Nhập chỉ số nào có thì điền, không cần đủ cả 4. Các chỉ số này không xét ngưỡng. |
| UI package (D-80) | The metrics your doctor asked you to measure at home. | Các chỉ số bác sĩ dặn mẹ đo tại nhà. |
| UI package (D-80) | Systolic | Tâm thu |
| UI package (D-80) | Diastolic | Tâm trương |
| UI package (D-80) | Accompanying symptoms | Triệu chứng kèm theo |
| UI package (D-80) | (select multiple) | (chọn nhiều) |
| UI package (D-80) | (optional) | (không bắt buộc) |
| UI package (D-80) | What else should clinical staff know? | Mẹ muốn nhân viên y tế biết thêm điều gì? |
| UI package (D-80) | Clinical staff view and respond under | Nhân viên y tế xem và phản hồi ở mục |
| UI package (D-80) | Your visits and diary, week by week. | Ngày khám và nhật ký của mẹ, theo từng tuần. |
| UI package (D-80) | Visit day | Ngày khám |
| UI package (D-80) | Has diary | Có nhật ký |
| UI package (D-80) | Today | Hôm nay |
| UI package (D-80) | No diary yet | Chưa có nhật ký |
| UI package (D-80) | This week | Trong tuần này |
| UI package (D-80) | {n} indicators | {n} chỉ số |
| UI package (D-80) | Indicators | Chỉ số |
| UI package (D-80) | Your diary | Nhật ký của mẹ |
| UI package (D-80) | No diary entry this day. | Ngày này chưa có nhật ký. |
| UI package (D-80) | Mon | T2 |
| UI package (D-80) | Tue | T3 |
| UI package (D-80) | Wed | T4 |
| UI package (D-80) | Thu | T5 |
| UI package (D-80) | Fri | T6 |
| UI package (D-80) | Sat | T7 |
| UI package (D-80) | Sun | CN |
| UI package (D-80) | Monday | Thứ Hai |
| UI package (D-80) | Tuesday | Thứ Ba |
| UI package (D-80) | Wednesday | Thứ Tư |
| UI package (D-80) | Thursday | Thứ Năm |
| UI package (D-80) | Friday | Thứ Sáu |
| UI package (D-80) | Saturday | Thứ Bảy |
| UI package (D-80) | Sunday | Chủ Nhật |
| UI package (D-80) | How do you feel today? | Hôm nay mẹ cảm thấy thế nào? |
| UI package (D-80) | When the baby kicked, something tasty, or a note for your baby… | Con đạp lúc nào, mẹ ăn gì ngon, hay một lời nhắn gửi con… |
| UI package (D-80) | Photos | Ảnh |
| UI package (D-80) | JPG or PNG, up to 5 photos, 10 MB each. | JPG hoặc PNG, tối đa 5 ảnh, mỗi ảnh 10 MB. |
| UI package (D-80) | Full name, phone number | Họ tên, số điện thoại |
| UI package (D-80) | Date of birth, sex | Ngày sinh, giới tính |
| UI package (D-80) | Height | Chiều cao |
| UI package (D-80) | Your TCI account could not be verified. Go back to the TCI app and open Mother & Baby 360 again from its home screen. | Không xác thực được tài khoản TCI. Mẹ hãy quay lại app TCI và mở lại Mẹ & Bé 360 từ màn chủ. |
| UI package (D-80) | Shown when the TCI identity cannot be verified (demo link). | Hiện khi không xác thực được danh tính TCI (link demo). |
| UI package (D-80) | Offers | Ưu đãi |
| UI package (D-80) | Book | Đặt lịch |
| TCI host app tab bar, not the sub-app (D-80; the sub-app tab is "Hồ sơ") | Personal tab | Cá nhân |
| UI package (D-80) | [TCI app banner] | [Banner của app TCI] |
| UI package (D-80) | Medical records | Hồ sơ khám |
| UI package (D-80) | Voucher | Voucher |
| UI package (D-80) | Services | Dịch vụ |
| UI package (D-80) | New | Mới |
| UI package (D-80) | Open | Mở |
| UI package (D-80) | Symptom | Triệu chứng |
| ACC screens (specs/009, D-80) | Pregnancy | THAI KỲ |
| ACC screens (specs/009, D-80) | Last menstrual period | Kỳ kinh cuối |
| ACC screens (specs/009, D-80) | Gestational age now | Tuổi thai hiện tại |
| ACC screens (specs/009, D-80) | {w} weeks {d} days | {w} tuần {d} ngày |
| ACC screens (specs/009, D-80) | Monitor at home, as your doctor asked | BÁC SĨ DẶN THEO DÕI TẠI NHÀ |
| ACC screens (specs/009, D-80) | See the instructions | Xem chỉ dẫn |
| ACC screens (specs/009, D-80) | None yet | Chưa có |
| ACC screens (specs/009, D-80) | Data & privacy | DỮ LIỆU & QUYỀN RIÊNG TƯ |
| ACC screens (specs/009, D-80) | Data sharing consent | Đồng ý chia sẻ dữ liệu |
| ACC screens (specs/009, D-80) | Agreed | Đã đồng ý |
| ACC screens (specs/009, D-80) | Not agreed | Chưa đồng ý |
| ACC screens (specs/009, D-80) | On | Bật |
| ACC screens (specs/009, D-80) | Off | Tắt |
| ACC screens (specs/009, D-80) | Hospital record link | Liên kết hồ sơ bệnh viện |
| ACC screens (specs/009, D-80) | Linked on | Liên kết ngày |
| ACC screens (specs/009, D-80) | Requested on | Yêu cầu ngày |
| ACC screens (specs/009, D-80) | Facility | Cơ sở |
| ACC screens (specs/009, D-80) | Link request awaiting hospital confirmation | Yêu cầu liên kết đang chờ bệnh viện xác nhận |
| ACC screens (specs/009, D-80) | Data used in Mother & Baby 360: results of prenatal visits, due date set by the hospital. | Dữ liệu dùng trong Mẹ & Bé 360: kết quả các lần khám thai, ngày dự sinh do bệnh viện xác định. |
| ACC screens (specs/009, D-80) | Support — TCI app ↗ | Hỗ trợ — App TCI ↗ |
| ACC screens (specs/009, D-80) | Edit › | Sửa › |
| ACC screens (specs/009, D-80) | Record no. {code} • TCI account | Tài khoản TCI · Mã hồ sơ {code} |
| ACC screens (specs/009, D-80) | From your TCI account – edit in the TCI app | Lấy từ tài khoản TCI, không sửa được ở đây |
| ACC screens (specs/009, D-80) | Locked because the hospital record is linked | Đã khoá vì hồ sơ bệnh viện đã liên kết |
| ACC screens (specs/009, D-80) | Hospital record | Hồ sơ bệnh viện |
| ACC screens (specs/009, D-80) | When clinical staff view or respond to your report | Luôn bật để mẹ không bỏ lỡ phản hồi của nhân viên y tế |
| ACC screens (specs/009, D-80) | When results from a new visit are available | Khi bệnh viện cập nhật kết quả lần khám |
| ACC screens (specs/009, D-80) | Reminders to report the metrics your doctor assigned | Nhắc đo và báo cáo chỉ số bác sĩ dặn |
| ACC screens (specs/009, D-80) | Notifications are sent via the TCI app. | Thông báo được gửi qua app TCI. |
| ACC screens (specs/009, D-80) | This setting cannot be changed. | Không đổi được cài đặt này. |
| ACC screens (specs/009, D-80) | {n} unread notifications | {n} thông báo chưa đọc |
| ACC screens (specs/009, D-80) | Read | Đã đọc |
| ACC screens (specs/009, D-80) | New notice | Mới |
| ACC screens (specs/009, D-80) | Unread | Chưa đọc |
| ACC screens (specs/009, D-80) | Doctors and nurses send these after a visit or after viewing your report. | Bác sĩ, y tá gửi sau khi khám hoặc xem báo cáo của mẹ. |
| ACC screens (specs/009, D-80) | You only receive information here. To report a metric or symptom, go to | Mẹ chỉ nhận thông tin ở đây. Cần báo chỉ số hay triệu chứng, mẹ vào |
| ACC screens (specs/009, D-80) | Home › Report | Trang chủ › Báo cáo |
| ACC screens (specs/009, D-80) | New visit results available | Có kết quả khám mới |
| ACC screens (specs/009, D-80) | Appointment reminder | Nhắc lịch hẹn |
| ACC screens (specs/009, D-80) | Reminder: measure and report {metric} | Nhắc đo và báo cáo {metric} |
| ACC screens (specs/009, D-80) | Your question has been sent to a nurse | Câu hỏi của mẹ đã được chuyển cho y tá |
| ACC screens (specs/009, D-80) | Your {what} has been sent to clinical staff | {what} của mẹ đã được gửi tới nhân viên y tế |
| ACC screens (specs/009, D-80) | {actor} responded to your {what} | {actor} đã phản hồi {what} của mẹ |
| ACC screens (specs/009, D-80) | Your {what} is {status} | {what} của mẹ: {status} |
| ACC screens (specs/009, D-80) | {metric} report | Báo cáo {metric} |
| ACC screens (specs/009, D-80) | question | câu hỏi |
| ACC screens (specs/009, D-80) | Report {code} resolved | Báo cáo {code} đã xử lý |
| ACC screens (specs/009, D-80) | Report {code} escalated to a doctor | Báo cáo {code} đã chuyển bác sĩ |
| ACC screens (specs/009, D-80) | Your report has been received | Đã nhận báo cáo của mẹ |
| ACC screens (specs/009, D-80) | Your report has been viewed | Báo cáo của mẹ đã được xem |
| ACC screens (specs/009, D-80) | Routine antenatal check-up {date} | Khám thai định kỳ {date} |
| HLT screens (specs/010, D-80) | Metric | Chỉ số |
| HLT screens (specs/010, D-80) | From date | Từ ngày |
| HLT screens (specs/010, D-80) | To date | Đến ngày |
| HLT screens (specs/010, D-80) | Average | Trung bình |
| HLT screens (specs/010, D-80) | Lowest | Thấp nhất |
| HLT screens (review of PR #18, Ánh) | Lowest and highest are taken for systolic and diastolic separately, so they can come from two different readings. | Thấp nhất và cao nhất tính riêng cho tâm thu và tâm trương, nên có thể lấy từ hai lần đo khác nhau. |
| HLT screens (specs/010, D-80) | Highest | Cao nhất |
| HLT screens (specs/010, D-80) | Threshold {value} | Ngưỡng {value} |
| HLT screens (specs/010, D-80) | Reference range {value} | Tham chiếu {value} |
| HLT screens (specs/010, D-80) | No data for this period. | Không có dữ liệu trong khoảng này. |
| HLT screens (specs/010, D-80) | The start date must not be after the end date. | Từ ngày không được sau Đến ngày. |
| HLT screens (specs/010, D-80) | Latest | Lần gần nhất |
| HLT screens (specs/010, D-80) | Assigned {date} | chỉ định {date} |
| TML screens (specs/011, D-80) | Weeks {a} – {b} | Tuần {a} – tuần {b} |
| TML screens (specs/011, D-80) | weeks {a} – {b} | tuần {a} – {b} |
| TML screens (specs/011, D-80) | You are in week {n} | mẹ đang ở tuần {n} |
| TML screens (specs/011, D-80) | visits | lần khám |
| TML screens (specs/011, D-80) | diary entries | nhật ký |
| TML screens (specs/011, D-80) | photos | ảnh |
| TML screens (specs/011, D-80) | {n} visits | {n} lần khám |
| TML screens (specs/011, D-80) | Not reached yet | Chưa đến giai đoạn này |
| TML screens (specs/011, D-80) | Nothing to show for this stage yet. | Giai đoạn này chưa có gì để hiển thị. |
| TML screens (specs/011, D-80) | Nothing to export yet. | Chưa có gì để xuất. |
| TML screens (specs/011, D-80) | Past | Đã qua |
| TML screens (specs/011, D-80) | Current | Hiện tại |
| TML screens (specs/011, D-80) | To come | Sắp tới |
| TML screens (specs/011, D-80) | The print sheet opens: choose Save as PDF. Nothing is stored. | Trang in sẽ mở ra: mẹ chọn Lưu thành PDF. Hệ thống không lưu gì. |
| TML screens (specs/011, D-80) | Export keepsake album (PDF) | Xuất album kỷ niệm (PDF) |
| Mother app v1.0.0 (D-81) | + Enter metrics | + Nhập chỉ số |
| Mother app v1.0.0 (D-81) | Antenatal check-up process | Quy trình khám thai |
| Mother app v1.0.0 (D-81) | Call the emergency hotline | Gọi khẩn cấp |
| Mother app v1.0.0 (D-81) | Call the hospital | Gọi bệnh viện |
| Mother app v1.0.0 (D-81) | Clinical staff will view your report. If your symptoms get worse, go to the nearest hospital. | Nhân viên y tế sẽ xem báo cáo của mẹ. Nếu triệu chứng nặng hơn, mẹ đến bệnh viện gần nhất nhé. |
| Mother app v1.0.0 (D-81) | Clinical web (doctor, nurse) | Web nhân viên y tế (bác sĩ, y tá) |
| Mother app v1.0.0 (D-81) | Complete antenatal care at Thu Cuc | Khám thai trọn gói tại Thu Cúc |
| Mother app v1.0.0 (D-81) | Customer guide | Hướng dẫn khách hàng |
| Mother app v1.0.0 (D-81) | DOCTOR'S COMMENT | BÁC SĨ NHẬN XÉT |
| Mother app v1.0.0 (D-81) | NURSE'S COMMENT | Y TÁ NHẬN XÉT |
| Mother app v1.0.0 (D-81) | Date of first antenatal check-up | Ngày khám thai đầu tiên |
| Mother app v1.0.0 (D-81) | Getting ready for birth | Chuẩn bị đi sinh |
| Mother app v1.0.0 (D-81) | Highlights | Kỷ niệm nổi bật |
| Mother app v1.0.0 (D-81) | Week by week | Xem theo từng tuần |
| Mother app v1.0.0 (D-81) | Mother & Baby 360 will use the following information from the TCI app, with no need to sign in again: | Mẹ & Bé 360 sẽ dùng các thông tin sau từ app TCI, không cần đăng nhập lại: |
| Mother app v1.0.0 (D-81) | Next appointment | Lịch khám kế tiếp |
| Proposed S-106 | Appointment schedule | Lịch khám |
| Mother app v1.0.0 (D-81) | Open as another TCI account | Mở bằng tài khoản TCI khác |
| Mother app v1.0.0 (D-81) | Sample data: everyone here is invented, and the medical wording is waiting for hospital review. | Dữ liệu mẫu: mọi tên người đều là giả, nội dung y khoa đang chờ bệnh viện duyệt. |
| Mother app v1.0.0 (D-81) | See the timeline | Xem dòng thời gian |
| Mother app v1.0.0 (D-81) | Start again from the first opening | Chạy lại từ lần mở đầu tiên |
| Mother app v1.0.0 (D-81) | Take / choose photo | Chụp / chọn ảnh |
| Mother app v1.0.0 (D-81) | Tell Mother & Baby 360 your pregnancy date so it can work out your week. | Cho Mẹ & Bé 360 biết mốc thai kỳ để tính tuần thai cho mẹ. |
| Mother app v1.0.0 (D-81) | The hospital will confirm this number before launch: {hotline}. | Số tổng đài chờ bệnh viện xác nhận trước khi phát hành: {hotline}. |
| Mother app v1.0.0 (D-81) | The mother's app, embedded in the TCI app. Open this address on a phone for the full-screen version. | App dành cho mẹ, nhúng trong app TCI. Mở địa chỉ này trên điện thoại để dùng toàn màn hình. |
| Mother app v1.0.0 (D-81) | The nurse will view your question and respond under From doctor. If it gets worse, call the emergency hotline, do not wait. | Y tá sẽ xem câu hỏi và phản hồi ở mục Thông báo. Nếu nặng hơn, mẹ gọi cấp cứu ngay, đừng chờ. |
| Mother app v1.0.0 (D-81) | This needs a medical assessment. Please do not wait. | Dấu hiệu này cần nhân viên y tế đánh giá. Mẹ đừng chờ đợi. |
| Mother app v1.0.0 (D-81) | Ultrasound image sent by the hospital · tap to enlarge | Ảnh siêu âm do bệnh viện gửi · chạm để phóng to |
| Mother app v1.0.0 (D-81) | Ultrasound images are attached to the visit day by the hospital. | Ảnh siêu âm do bệnh viện tự gắn vào ngày khám. |
| Mother app v1.0.0 (D-81) | Understood | Mẹ đã hiểu |
| Mother app v1.0.0 (D-81) | WHAT YOU NEED TO DO | MẸ CẦN LÀM |
| Mother app v1.0.0 (D-81) | WHAT YOU REPORTED | MẸ ĐÃ BÁO |
| Mother app v1.0.0 (D-81) | With: | Kèm: |
| Mother app v1.0.0 (D-81) | You chose: {choice} | Mẹ đã chọn: {choice} |
| Mother app v1.0.0 (D-81) | You need to be checked right away | Mẹ cần được kiểm tra ngay |
| Mother app v1.0.0 (D-81) | You will return to the TCI app. Your data stays saved, and you do not need to sign in next time. | Mẹ sẽ quay lại app TCI. Dữ liệu đã lưu vẫn được giữ, lần sau mở lại không cần đăng nhập. |
| Mother app v1.0.0 (D-81) | Your doctor sent {n} notice | Bác sĩ vừa gửi {n} thông báo |
| Mother app v1.0.0 (D-81) | Your doctor booked an earlier visit | Bác sĩ hẹn khám sớm |
| Mother app v1.0.0 (D-81) | Your report will be sent to clinical staff. | Báo cáo sẽ được gửi tới nhân viên y tế. |
| Mother app v1.0.0 (D-81) | has diary | có nhật ký |
| Mother app v1.0.0 (D-81) | today | hôm nay |
| Mother app v1.0.0 (D-81) | with this chat | kèm đoạn chat |
| Mother app v1.0.0 (D-81) | {n} days left | Còn {n} ngày |
| Mother app v1.0.0 (D-81) | Appointment reminders | Nhắc lịch hẹn |
| Mother app v1.0.0 (D-81) | One day before your visit | Trước buổi khám 1 ngày |
| Mother app v1.0.0 (D-81) | Follow your pregnancy with Thu Cuc doctors | Theo dõi thai kỳ cùng bác sĩ Thu Cúc |
| Mother app v1.0.0 (D-81) | Visit results update on their own. Report a metric or symptom and clinical staff will view and respond. | Kết quả mỗi lần khám tự cập nhật về app. Mẹ báo chỉ số hoặc triệu chứng, nhân viên y tế sẽ xem và phản hồi. |
| Mother app v1.0.0 (D-81) | Keep every moment of your pregnancy | Lưu lại từng khoảnh khắc thai kỳ |
| Mother app v1.0.0 (D-81) | Your visits, ultrasound images and diary, week by week, ready to keep as an album. | Lần khám, ảnh siêu âm và nhật ký theo từng tuần, sẵn sàng giữ lại thành album. |
| Mother app v1.0.0 (D-81) | Answers whenever you need them | Có câu trả lời khi mẹ cần |
| Mother app v1.0.0 (D-81) | Ask the chatbot general questions about pregnancy. For anything about your own health, it passes you to a nurse. | Mẹ hỏi chatbot những điều chung về thai kỳ. Điều gì liên quan đến sức khỏe của riêng mẹ, chatbot sẽ chuyển cho y tá. |
| Mother app v1.0.0 (D-81) | Trouble sleeping during pregnancy | Mất ngủ khi mang thai |
| Mother app v1.0.0 (D-81) | Should I exercise? | Có nên tập thể dục? |
| Mother app v1.0.0 (D-81) | Leg cramps | Chuột rút chân |
| Mother app v1.0.0 (D-81) | Visits this week | Lần khám trong tuần |
| Review fixes 06/11/2026 (D-81) | Enter a number greater than 0. | Hãy nhập một số lớn hơn 0. |
| Review fixes 06/11/2026 (D-81) | The first day of the last period cannot be in the future, and the week must be 0 – 42. | Ngày đầu kỳ kinh cuối không được ở tương lai, và tuần thai phải trong khoảng 0 – 42. |
| Review fixes 06/11/2026 (D-81) | e.g. {value} | VD: {value} |
| Review fixes 06/11/2026 (D-81) | Doctor asked to monitor | Bác sĩ dặn theo dõi |
| Review fixes 06/11/2026 (D-81) | {h} h {m} min | {h} giờ {m} phút |
| Review fixes 06/11/2026 (D-81) | {h} h | {h} giờ |
| Review fixes 06/11/2026 (D-81) | In the mother's app, lines starting with - become her to-do list, and a line “Hẹn khám: dd/mm/yyyy · HH:mm” shows as the follow-up visit. | Trên app của mẹ, dòng bắt đầu bằng - thành việc mẹ cần làm, còn dòng “Hẹn khám: dd/mm/yyyy · HH:mm” hiện thành lịch khám lại. |
| Review fixes 06/11/2026 (D-81) | Appointments | Lịch hẹn |
| Review fixes 06/11/2026 (D-81) | Chatbot: {engine} | Chatbot: {engine} |
| Clinical dashboard (D-85) | Overview | Tổng quan |
| Clinical dashboard (D-85) | Case board | Bảng xử lý |
| Clinical dashboard (D-85) | Case list | Danh sách ca |
| Clinical dashboard (D-85) | All sources | Mọi nguồn |
| Clinical dashboard (D-85) | Received from | Nhận từ ngày |
| Clinical dashboard (D-85) | to | đến |
| Clinical dashboard (D-85) | Apply | Áp dụng |
| Clinical dashboard (D-85) | Reset | Đặt lại |
| Clinical dashboard (D-85) | Cases sent by mothers and how far each one has been handled. | Các ca mẹ gửi và tiến độ xử lý từng ca. |
| Clinical dashboard (D-85) | Updated {time} | Cập nhật {time} |
| Clinical dashboard (D-85) | Refresh | Làm mới |
| Clinical dashboard (D-85) | {n} cases in this view | {n} ca trong phạm vi đang xem |
| Clinical dashboard (D-85) | Open cases | Ca đang mở |
| Clinical dashboard (D-85) | From sent to resolved | Từ lúc gửi đến khi xử lý xong |
| Clinical dashboard (D-85) | Waiting longest: {d}d {h}h | Chờ lâu nhất: {d} ngày {h} giờ |
| Clinical dashboard (D-85) | Waiting longest: {h}h {m}m | Chờ lâu nhất: {h} giờ {m} phút |
| Clinical dashboard (D-85) | Nothing waiting | Không có ca nào đang chờ |
| Clinical dashboard (D-85) | Above threshold, open | Vượt ngưỡng, đang mở |
| Clinical dashboard (D-85) | Thresholds from THRESHOLD_RULE | Ngưỡng theo bảng THRESHOLD_RULE |
| Clinical dashboard (D-85) | {n} assigned to me | {n} ca giao cho tôi |
| Clinical dashboard (D-85) | Waiting for a doctor's decision | Đang chờ bác sĩ quyết định |
| Clinical dashboard (D-85) | Where cases stand | Tình trạng xử lý |
| Clinical dashboard (D-85) | Current status · same columns as the case board | Trạng thái hiện tại · cùng các cột của Bảng xử lý |
| Clinical dashboard (D-85) | Needs attention | Cần chú ý |
| Clinical dashboard (D-85) | Open the board | Mở bảng xử lý |
| Clinical dashboard (D-85) | {n} open cases flagged · a case can be in more than one group | {n} ca đang mở cần chú ý · một ca có thể thuộc nhiều nhóm |
| Clinical dashboard (D-85) | Above threshold, not viewed | Vượt ngưỡng, chưa xem |
| Clinical dashboard (D-85) | Alarm symptoms | Có triệu chứng báo động |
| Clinical dashboard (D-85) | No response sent yet | Chưa gửi phản hồi |
| Clinical dashboard (D-85) | Escalated, waiting for the doctor | Đã chuyển, chờ bác sĩ trả lời |
| Clinical dashboard (D-85) | From the chatbot | Từ chatbot |
| Clinical dashboard (D-85) | Handle next | Cần xử lý tiếp |
| Clinical dashboard (D-85) | See all cases | Xem tất cả ca |
| Clinical dashboard (D-85) | Not viewed first, above threshold first, then the oldest | Ưu tiên chưa xem, vượt ngưỡng, rồi ca chờ lâu nhất |
| Clinical dashboard (D-85) | No open cases. | Không có ca đang mở. |
| Clinical dashboard (D-85) | By source | Theo nguồn |
| Clinical dashboard (D-85) | Open cases: oldest on top. Tap a card to open the case. | Ca đang mở: ca chờ lâu nhất ở trên cùng. Bấm vào thẻ để mở ca. |
| Clinical dashboard (D-85) | CASE STATUS | TRẠNG THÁI CA |
| Clinical dashboard (D-85) | A nurse checks the report first | Y tá xem báo cáo trước |
| Clinical dashboard (D-85) | A nurse is handling it | Y tá đang xử lý |
| Clinical dashboard (D-85) | Waiting for the doctor | Chờ bác sĩ |
| Clinical dashboard (D-85) | Closed by a nurse or a doctor | Y tá hoặc bác sĩ đã đóng ca |
| Clinical dashboard (D-85) | No cases. | Không có ca nào. |
| Clinical dashboard (D-85) | {n} more | Còn {n} ca |
| Clinical dashboard (D-85) | Nurse handling | Y tá xử lý |
| Clinical dashboard (D-85) | waiting {d}d {h}h | chờ {d} ngày {h} giờ |
| Clinical dashboard (D-85) | waiting {h}h {m}m | chờ {h} giờ {m} phút |
| Clinical dashboard (D-85) | Showing: {group} | Đang lọc: {group} |
| Clinical dashboard (D-85) | Show all | Bỏ lọc |
| Notification wording (review 10/11/2026; stored demo title) | Về báo cáo thai máy giảm | Về báo cáo cử động thai giảm |
| Notification filter dropdown (10/11/2026) | Notification type | Loại thông báo |
| Notification filter dropdown (10/11/2026) | Filter | Lọc |
| Notification dropdown review (11/11/2026) | All notifications | Tất cả thông báo |
| Report response link (11/11/2026) | Detailed instructions from your doctor | Chỉ dẫn cụ thể của bác sĩ |
| Clinical notifications (D-107) | Cases waiting for a first look. | Ca đang chờ xem lần đầu. |
| Clinical notifications (D-107) | Cases a nurse escalated to you. | Ca y tá đã chuyển cho bạn. |
| Clinical notifications (D-107) | {n} waiting | {n} ca đang chờ |
| Clinical notifications (D-107) | Shown while the case is open · nothing is marked as read | Hiện khi ca còn mở · không có trạng thái đã đọc |
| Clinical notifications (D-107) | Escalated by Nurse {name} · {time} | Y tá {name} chuyển · {time} |
| Clinical notifications (D-107) | Escalated {time} | Đã chuyển {time} |
| Clinical notifications (D-107) | Sent {time} | Mẹ gửi {time} |
| Clinical notifications (D-107) | No notifications. | Không có thông báo nào. |
| Nurse permissions (D-98, D-99) | Only a doctor can close this case: the value is above threshold. Escalate it to the doctor. | Chỉ bác sĩ mới được đóng ca này: chỉ số vượt ngưỡng. Hãy chuyển ca cho bác sĩ. |
| Nurse permissions (D-98, D-99) | Only a doctor can close this case: the chatbot marked this question as a danger sign. Escalate it to the doctor. | Chỉ bác sĩ mới được đóng ca này: chatbot đã đánh dấu câu hỏi là dấu hiệu nguy hiểm. Hãy chuyển ca cho bác sĩ. |
| Case routing (D-96, D-97) | Will be sent to: Dr. {name} | Sẽ gửi tới: BS. {name} |
| Case routing (D-96, D-97) | Will be sent to the doctor on duty · Responsible doctor: Dr. {name} (Away) | Sẽ gửi tới bác sĩ đang trực · Bác sĩ phụ trách: BS. {name} (Vắng) |
| Case routing (D-96, D-97) | Will be sent to: Dr. {name} · Doctor availability unknown | Sẽ gửi tới: BS. {name} · Chưa rõ bác sĩ có mặt hay không |
| Case routing (D-96, D-97) | No doctor available: the case is visible to all doctors | Không có bác sĩ nào nhận: ca này hiện với tất cả bác sĩ |
| Case routing (D-96, D-97) | This mother is not in your care (spec-CLI BR-010) | Mẹ này không thuộc danh sách bạn phụ trách |


## Proposed S-106 labels

**Lịch khám**, **Lịch hiện tại**, **Lịch sử đặt**, **Đặt lịch khám ↗**, **Xem kết quả ›**, **Mẹ chưa có lịch hẹn nào**, **Mẹ chưa có lần khám nào**.
