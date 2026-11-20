# S-106 — Lịch khám

**Proposed D-88** · APT FR-011–014 · GET /m/{user_id}/appointments

| Element | Behavior |
|---|---|
| Back | S-008. No root tab bar. |
| Lịch hiện tại / Lịch sử đặt | The signed-in mother's host records. Each row shows time, doctor, specialty, facility and status. Current same-day rows show Hôm nay. |
| Empty current / history | Mẹ chưa có lịch hẹn nào / Mẹ chưa có lần khám nào. Current offers a TCI booking handoff. |
| Đặt lịch khám ↗ | TCI booking. The server binds the return path to the verified mother and session. |
| Xem kết quả › | Timeline day for a completed appointment linked to the same mother's visit on that date. |
| Past without visit | History shows Đã qua giờ hẹn, chưa ghi nhận lần khám. |

S-106 is read-only. Entry points are S-008 and S-009. Other mothers' lists are denied. Booking and cancellation stay in TCI.

**Exception pending team review:** Quản lý lịch ở TCI ↗ opens the signed-in mother’s TCI list for cancellation or rebooking.

Booking and cancellation notices open the corresponding host card under proposed FR-015.


## Proposed D-108 — consistent empty states

Current empty text is “Chưa có lịch khám sắp tới”. History empty text is “Mẹ chưa có lần khám nào. Lịch và lịch sử khám sẽ hiện ở đây.”. The existing top booking link uses the same full-width green outline component and accessible label as Home. Empty bodies do not repeat the booking button.
