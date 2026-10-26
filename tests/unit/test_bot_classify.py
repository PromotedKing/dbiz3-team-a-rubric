"""T004 — BOT FR-006, FR-010, FR-011, BR-002, BR-005 (classification, provisional keyword lists — Q2, Q12, Q14)."""
import json

import pytest

from mb360.bot import classify


@pytest.mark.parametrize("text, category, danger", [
    ("How can I eat beef safely during pregnancy?", "general", False),
    ("I have had a little bleeding since this morning, is that okay?", "needs_nurse", True),
    ("Tôi bị chảy máu từ sáng", "needs_nurse", True),
    ("Hôm nay em không thấy thai máy", "needs_nurse", True),
    ("I feel tired, is that normal?", "needs_nurse", False),
    ("How do I change a car tyre?", "out_of_scope", False),
])
def test_categories(text, category, danger):
    assert classify.classify(text) == {"category": category, "danger": danger}


def test_keyword_file_drives_the_result(tmp_path, monkeypatch):
    data = json.loads(classify.KEYWORDS_FILE.read_text(encoding="utf-8"))
    data["danger_phrases"].append("itchy palms")
    f = tmp_path / "keywords.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(classify, "KEYWORDS_FILE", f)
    assert classify.classify("Pregnancy question: itchy palms at night?")["danger"] is True
