# HTTP routes: ACC profile

| Method | Path | Screen | Result |
|---|---|---|---|
| GET | `/m/{user_id}/profile?saved=1` | S-103 | Read-only profile |
| GET | `/m/{user_id}/profile/edit` | S-011 | Form |
| POST | `/m/{user_id}/profile/edit` | S-011 | 303 to S-103 `?saved=1`; 422 with field errors, nothing saved |
| GET | `/m/{user_id}/settings/notifications` | S-010 | 4 types less the hidden appointment switch |
| POST | `/m/{user_id}/settings/notifications` | S-010 | `key`, `value`; 303 back; 422 for a locked or unknown key |
| GET | `/m/{user_id}/notices?type=` | S-009 | List, unread count; `type`: Report, Visit result, Appointment, Instruction reminder, Unread |
| GET | `/m/{user_id}/notices/{id}` | S-009 | Marks read; 303 to the target (research R3); 404 if not hers |
| POST | `/m/{user_id}/notices/read-all` | S-009 | Marks all read; 303 to the list |
