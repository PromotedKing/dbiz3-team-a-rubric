# UI conventions and label reference: Mother & Baby 360

Shared UI conventions of the wireframes and the mapping from the English labels used in every document to the Vietnamese text drawn on the wireframes. This is the only file with Vietnamese UI text.

## UI conventions

Text version of the UI-conventions page `00-QUY-UOC` of the wireframe (the page has no Screen ID, so its image is not in `screens/img/`). Source decision: **D-27**. Applies to every screen.

### 1. Type (4 levels)

| Level | Size | Style |
|---|---|---|
| Page title | 18 | bold |
| Section title | 15 | bold |
| Body | 13 | regular |
| Caption | 11 | grey |

### 2. Buttons

| Type | Look |
|---|---|
| Primary | filled |
| Secondary | outline |
| Small | "Small – primary" (filled) and "Small – secondary" (outline) |
| Text link | underlined, with `›` (e.g. "Text link ›") |

### 3. Fixed CTAs

Each action always uses the same label:

| Action | Button label |
|---|---|
| Enter Group 1 metrics | **Save metrics** |
| Report a Group 2 metric / symptoms | **Submit report** |
| Open S-026 | **View status** |
| Open a report from a list | **View report** |
| Open the history screen | **View metric history** |

### 4. Threshold labels

Only 3 labels: **Normal** · **Above threshold** · **Not assessed** (D-17).

When colour is used: Normal = green · Above threshold = orange · Not assessed = grey. Red only if the team decides to add a critical level.

### 5. Data source labels

Three labels: **From visit** · **Self-entered** · **Doctor-assigned** (D-10).

"Doctor-assigned" = a value the mother reports for a metric that is in the Doctor's instructions. The mother can report only such metrics (D-11 revised), so every Group 2 value she reports is "Doctor-assigned"; "Self-entered" is used for Group 1 metrics and the weight declared on S-007 (D-33 revised).

### 6. Report status (same for the mother and clinical staff)

**Not viewed → Viewed → Escalated to doctor → Resolved** (D-18). Status only moves forward; "Escalated to doctor" may be skipped (D-43).

Only reports that clinical staff need to see have a status. A Normal report with no symptoms has no status.

### 7. Formats

| Type | Example |
|---|---|
| Date | 26/09/2026 |
| Time | 20:15 |
| Date + time | 26/09/2026 · 20:15 |
| Blood pressure | 150/95 mmHg |
| Fetal heart rate / heart rate | 145 bpm |
| Weight | 56.5 kg |
| Temperature | 36.8 °C |

### 8. Terms

| Term in documents | Label on screen |
|---|---|
| Watch-flag | **Doctor's instructions** |
| Report | **Report** |
| Alert (S-028 only) | **Alert** |
| Routine tracking | **Self-tracked metrics** |

The word "Alert" is used only for an above-threshold report on S-028 (D-22).

### 9. Header and navigation

- **Header:** ← · left-aligned title · action · ✕. Only Home and the first-time setup screen have no ←.
- **Bottom bar, 5 tabs:** Home (S-008, S-048, S-051, S-083) · Health (S-023 → S-029 "My reports", metric history) · Appointments (opens the TCI app's booking flow directly, `spec-APT.md` BR-003) · Chatbot (S-031 → S-034) · Profile (S-103).
- ✕ in the header always opens S-083 (close the sub-app, D-01). S-043 has no ←, ✕ or tab bar (D-50).

### 10. Shared states

| State | Look |
|---|---|
| **Empty** | Dashed frame: round icon, one sentence describing the state, CTA if needed |
| **Loading** | Grey placeholders in place of content, layout unchanged |
| **Load error** | Dashed frame "⚠ Could not load data." + "Retry" link |
| **Input error** | Field border + "⚠ Value outside the valid range" directly under the field |

Valid ranges per metric are not set yet (**D-16, Pending SME**).

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
| Symptom (D-73) | Absence of fetal movement | Không thấy thai máy |
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
| Term | Pregnancy timeline | Dòng thời gian thai kỳ |
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
| Screen title | Health chatbot | Chatbot sức khỏe |
| Screen title | Pregnancy timeline | Dòng thời gian thai kỳ |
| Screen title | Add diary entry | Thêm nhật ký |
| Screen title | Cases to handle | Ca cần xử lý |
| Screen title | Mother quick profile | Hồ sơ nhanh của mẹ |
| Screen title | Close Mother & Baby 360? | Đóng Mother & Baby 360? |
| Screen title | Profile | Cá nhân |
| Screen title | Session expired | Phiên làm việc hết hạn |
| Screen title (S-104, D-74) | Onboarding guide | Hướng dẫn sử dụng |
| Screen title (S-105, D-75) | My journey | Hành trình của mẹ |
| Screen text (S-007 / S-046, D-72) | Date of first antenatal check-up (optional) | Ngày khám thai đầu tiên (không bắt buộc) |
| Screen text (S-048, D-75) | Indicators this week / No indicators this week. | Chỉ số trong tuần / Tuần này chưa có chỉ số. |
| CTA (S-105, D-75) | Export PDF album | Xuất album PDF |
| CTA (S-104, D-74) | Skip / Next / Get started | Bỏ qua / Tiếp / Bắt đầu |
| Tab | Home / Health / Appointments / Chatbot / Profile | Trang chủ / Sức khỏe / Lịch hẹn / Chatbot / Cá nhân |
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
| Message | You have not submitted any reports. | Bạn chưa gửi báo cáo nào. |
| Message | You have no notifications. | Bạn chưa có thông báo nào. |
| Message | No cases to handle. | Không có ca nào cần xử lý. |
| Message | Your doctor has not given you any instructions yet. | Bác sĩ chưa có chỉ dẫn nào cho bạn. |
