"""Install the journal of a fictional mother into a newly built demo."""
import uuid
from datetime import date, timedelta

MOODS = ("Happy", "Calm", "Nervous", "Tired", "Worried")
PHOTOS = ("bump-1", "bump-2", "bump-3", "hands", "park", "clothes", "flowers")
NOTES = (
    ("Sáng nay mình dành thêm chút thời gian để ăn sáng.", "Mình kể cho bố nghe chuyện hôm nay. Hai đứa ngồi nói đến tối.",
     "Hôm nay mình muốn nghỉ sớm, để mai có sức đi làm.", "Mình mở lại cuốn sổ và ghi vài điều muốn hỏi lần tới.",
     "Buổi tối yên ắng, mình ngồi đọc vài trang sách."),
    ("Mình đi một vòng công viên rồi về ăn tối cùng cả nhà.", "Bố bảo cứ để bố chọn nhạc, cuối cùng cả hai nghe lại bài cũ.",
     "Mình gấp mấy bộ đồ nhỏ và cất riêng vào ngăn tủ.", "Hôm nay mình thử chụp lại chiếc bụng từ góc cửa sổ.",
     "Mình ghi lại một ngày bình thường để sau này có chuyện kể cho con."),
    ("Mình để túi đồ ngay cạnh cửa cho dễ tìm.", "Hai đứa bàn xem ai sẽ kể chuyện cho con trước.",
     "Chiều nay mình ngồi cạnh cửa sổ lâu hơn mọi ngày.", "Mình gấp lại chăn nhỏ rồi nhắn bà là cả nhà đang mong con.",
     "Tối nay bố nấu cơm, mình ngồi chọn bài hát muốn nghe cùng con."),
)
DETAILS = ("Trời mát nên mình mở cửa sổ một lúc.", "Mình muốn nhớ cả những chuyện nhỏ như thế này.",
           "Lúc ghi lại, mình vẫn thấy vui.", "Mình nhắn cho bố đọc cùng.", "Giờ thì mình cất điện thoại đi nghỉ.")


def install(conn, user, lmp, today, counts, photo_phase):
    visits = {date.fromisoformat(row[0]): row[1] for row in conn.execute(
        "SELECT visit_date, ultrasound_image FROM VISIT WHERE user_id=?", (user,))}
    if not counts:
        return
    first = min(visits)
    first_week = (first - lmp).days // 7
    conn.execute("DELETE FROM DIARY_IMAGE WHERE diary_id IN (SELECT diary_id FROM DIARY_ENTRY WHERE user_id=?)", (user,))
    conn.execute("DELETE FROM DIARY_ENTRY WHERE user_id=?", (user,))
    ordinal = image_count = 0
    for elapsed, count in enumerate(counts):
        week = first_week + elapsed
        start = lmp + timedelta(weeks=week)
        offsets = (0, 2, 3) if elapsed == len(counts) - 1 and count == 3 else range(count)
        for offset in offsets:
            day = start + timedelta(days=offset)
            if not first <= day < today:
                raise ValueError("Demo diary date outside recorded pregnancy history")
            stage = 0 if week < 14 else 1 if week < 28 else 2
            note = NOTES[stage][ordinal % len(NOTES[stage])]
            detail = DETAILS[(ordinal // len(NOTES[stage]) + week) % len(DETAILS)]
            if day in visits:
                note = f"Hôm nay mình đi khám thai tuần {week}."
                detail = ("Mình cất lại hình siêu âm để sau này xem cùng con." if visits[day]
                          else "Về nhà mình ghi lại vài điều muốn nhớ sau buổi khám.")
            diary = uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-demo-diary/{user}/{week}/{offset}")
            conn.execute("INSERT INTO DIARY_ENTRY VALUES (?,?,?,?,?,?)",
                         (str(diary), user, f"{note} {detail}", MOODS[ordinal % len(MOODS)], week, day.isoformat()))
            if ordinal % 3 == photo_phase:
                photo = PHOTOS[image_count % len(PHOTOS)]
                conn.execute("INSERT INTO DIARY_IMAGE VALUES (?,?,?,1)",
                             (str(uuid.uuid5(diary, "photo")), str(diary), f"demo/{photo}.svg"))
                image_count += 1
            ordinal += 1

    # Existing messages retain their author, text and time of day.
    messages = conn.execute("SELECT author,text,created_at FROM FAMILY_MESSAGE WHERE user_id=? ORDER BY created_at",
                            (user,)).fetchall()
    conn.execute("DELETE FROM FAMILY_MESSAGE WHERE user_id=?", (user,))
    for author, text, stamp in messages:
        day = today - timedelta(days=1)
        week = (day - lmp).days // 7
        conn.execute("INSERT INTO FAMILY_MESSAGE VALUES (?,?,?,?,?)", (user, week, author, text, f"{day} {stamp[11:]}"))
