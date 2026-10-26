"""T002 — BOT facts of the seed (checked with queries before writing)."""
import json

from mb360 import db as dbmod


def test_counts_and_session_data():
    conn = dbmod.build()
    assert [conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("CONVERSATION", "CHAT_MESSAGE", "AI_RESPONSE_LOG")] == [9, 16, 8]
    rows = [r[0] for r in conn.execute("SELECT current_session_data FROM CONVERSATION")]
    assert rows.count(None) == 1                                    # optional column: one edge-case conversation without it
    for data in filter(None, rows):
        assert {"gestational_week", "earlier_turns"} <= set(json.loads(data))


def test_chatbot_cases_point_to_risk_questions():
    conn = dbmod.build()
    rows = conn.execute("""SELECT m.is_risk, m.handoff_choice FROM CARE_CASE c JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
                           WHERE c.case_source = 'Chatbot'""").fetchall()
    assert [tuple(r) for r in rows] == [(1, "Connect to nurse"), (1, "Connect to nurse")]


def test_u09_has_no_conversation():
    conn = dbmod.build()
    assert conn.execute("""SELECT COUNT(*) FROM CONVERSATION v JOIN USER_ACCOUNT u ON u.user_id = v.user_id
                           WHERE u.tci_account_ref = 'tci-000131'""").fetchone()[0] == 0
