"""Fixes from the v1.0.0 review (Tâm, Ánh, Chi, 06/11/2026)."""
import pytest

from mb360 import numbers
from mb360.acc import notices
from mb360.bot import classify, llm

DANGER, NURSE, DECLINE, GENERAL = ("needs_nurse", True), ("needs_nurse", False), ("out_of_scope", False), ("general", False)


@pytest.mark.parametrize("text, expected", [
    ("dau bung du doi va ra mau", DANGER),            # typed without accents
    ("Em bi ra mau", DANGER),
    ("Bé không đạp từ hôm qua", DANGER),
    ("Em bị co giật", DANGER),
    ("Em sốt cao 39 độ", NURSE),
    ("Đau bụng", NURSE),
    ("Em uống thuốc hạ huyết áp liều bao nhiêu?", NURSE),
    ("What's the weather today?", DECLINE),            # "eat" inside "weather"
    ("Mua khăn tắm ở đâu rẻ?", DECLINE),                # "ăn" inside "khăn"
    ("Hôm nay trời có mưa không?", DECLINE),
    ("tôi nên mua kem rạn nào vì nhiều loại quá", GENERAL),
    ("Mất ngủ khi mang thai", GENERAL),
    ("Có nên tập thể dục?", GENERAL),
    ("thai không máy", DANGER), ("vỡ ối", DANGER), ("mờ mắt chóng mặt", DANGER), ("đau bụng dữ dội", DANGER),
    ("đau đầu nhiều có sao không", NURSE), ("phù chân", NURSE),
    ("How can I eat beef safely during pregnancy?", GENERAL),
])
def test_classification_from_the_review(text, expected):
    got = classify.classify(text)
    assert (got["category"], got["danger"]) == expected


def test_local_answers_match_whole_words():
    assert "rạn" in llm.LocalAnswers().answer("tôi nên mua kem rạn nào", {})
    assert llm.LocalAnswers().answer("an toàn khi đi xe", {}).startswith(llm.LocalAnswers.GENERAL)


@pytest.mark.parametrize("text, value, error", [
    ("58,5", "58.5", None), ("58.5", "58.5", None), ("", None, None),
    ("-5", None, numbers.NOT_POSITIVE), ("0", None, numbers.NOT_POSITIVE),
    ("nan", None, numbers.NOT_A_NUMBER), ("inf", None, numbers.NOT_A_NUMBER), ("abc", None, numbers.NOT_A_NUMBER),
])
def test_numbers_read(text, value, error):
    assert numbers.read(text) == (value, error)


@pytest.mark.parametrize("text, todo, follow_up", [
    ("A\n* B\n• C\n-D", ["B", "C", "D"], None),
    ("A\nHẹn khám : 10/11/2026 · 08:00", [], "10/11/2026 · 08:00"),
    ("A\nhẹn khám: 10/11", [], "10/11"),
])
def test_parse_response_accepts_other_bullets(text, todo, follow_up):
    parsed = notices.parse_response(text)
    assert parsed["comment"] == "A" and parsed["todo"] == todo and parsed["follow_up"] == follow_up
