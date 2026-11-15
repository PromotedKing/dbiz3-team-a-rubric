"""BOT FR-006, FR-010, FR-011, BR-002, BR-005 and the output check (§10 Q16): the Vietnamese question set and the sample
answers in bot_eval_set.json, checked offline. A live run against the real model is `uv run tools/bot_eval.py`."""
import json
import sys
from pathlib import Path

import pytest

from mb360.bot import classify, guard

SET = json.loads(Path(__file__).with_name("bot_eval_set.json").read_text(encoding="utf-8"))


def label(text: str) -> str:
    kind = classify.classify(text)
    return "danger" if kind["danger"] else kind["category"]


@pytest.mark.parametrize("case", [pytest.param(c, marks=pytest.mark.xfail(reason=c["known_gap"], strict=True)) if c.get("known_gap") else c
                                  for c in SET["questions"]], ids=lambda c: c["text"][:40])
def test_question_is_routed_as_expected(case):
    assert label(case["text"]) == case["expect"], case.get("note", "")


@pytest.mark.parametrize("case", SET["answers"], ids=lambda c: c["text"][:40])
def test_answer_check(case):
    assert guard.check(case["text"]) == case["held"]


def test_the_set_covers_every_route():
    assert {c["expect"] for c in SET["questions"]} == {"general", "needs_nurse", "danger", "lookup", "out_of_scope"}
    assert len(SET["questions"]) >= 40


def test_the_local_sample_answers_pass_the_check():
    """The answers shown without a Groq or Gemini key (LocalAnswers) are never held back by the output check."""
    from mb360.bot.llm import LocalAnswers
    for text in [a for _, a in LocalAnswers.TOPICS] + [LocalAnswers.GENERAL]:
        assert guard.check(text + LocalAnswers.CLOSING) == [], text


def test_live_tool_sends_only_general_questions(monkeypatch, tmp_path, capsys):
    """tools/bot_eval.py with a stand-in Groq client: no network call; one row per general question, the check applied."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bot_eval", Path(__file__).resolve().parents[2] / "tools" / "bot_eval.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    sent = []

    class StandIn(tool.llm.GroqLLM):
        def answer(self, question, context):
            sent.append((question, context))
            return "Mẹ uống viên sắt 60 mg mỗi ngày." if "sắt" in question else "Mẹ ăn chín uống sôi."

    monkeypatch.setattr(tool.llm, "get_client", lambda: StandIn("test-key-not-real", "test-model"))
    monkeypatch.setattr(tool.llm, "describe", lambda: "Groq · test-model")
    monkeypatch.setattr(tool, "PAUSE", 0)
    monkeypatch.setattr(sys, "argv", ["bot_eval.py", "--out", str(tmp_path / "r.md")])
    assert tool.main() == 0
    general = [c["text"] for c in SET["questions"] if classify.classify(c["text"])["category"] == "general"]
    assert [q for q, _ in sent] == general and all(c == {"gestational_week": 24, "earlier": []} for _, c in sent)
    report = (tmp_path / "r.md").read_text(encoding="utf-8")
    assert "held: dose" in report and "Held back: 1. Failed calls: 0." in report
