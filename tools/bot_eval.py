"""Live check of the chatbot model with the question set (spec-BOT §10 Q16). Run by hand, not in CI:

    uv run tools/bot_eval.py                 # needs GROQ_API_KEY or GEMINI_API_KEY in the environment or in .env
    uv run tools/bot_eval.py --out report.md

Only the questions the app classifies as "general" are sent, exactly as the app would send them: the question and a
gestational week, nothing from any record (BR-001). The questions are invented (tests/unit/bot_eval_set.json). For each
answer it prints the output-check result and the time taken. Read the answers yourself: the check catches doses,
diagnoses and watch-list foods, not every wrong statement. Exit code 1 when no key is set or a call fails."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from mb360.bot import classify, guard, llm  # noqa: E402

SET_FILE = ROOT / "tests" / "unit" / "bot_eval_set.json"
WEEK = 24          # an example week, the same for every question
PAUSE = 2.0        # seconds between calls, to stay inside the free plans' rate limits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", help="also write the report to this Markdown file")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    client = llm.get_client()
    if not isinstance(client, (llm.GroqLLM, llm.GeminiLLM)):
        print("No GROQ_API_KEY or GEMINI_API_KEY is set: nothing to check against a real model.")
        return 1
    questions = [q["text"] for q in json.loads(SET_FILE.read_text(encoding="utf-8"))["questions"]
                 if classify.classify(q["text"])["category"] == "general"]
    lines = [f"# Chatbot live check — {llm.describe()}", "",
             f"{len(questions)} general questions, week {WEEK}. Held = the output check replaces the answer with the fallback.", "",
             "| # | Question | Answer | Output check | Seconds |", "|---|---|---|---|---|"]
    held = failed = 0
    for i, q in enumerate(questions, 1):
        start = time.monotonic()
        try:
            answer = client.answer(q, {"gestational_week": WEEK, "earlier": []})
        except Exception as e:                       # a refused or failed call is reported, never the key
            failed += 1
            lines.append(f"| {i} | {q} | *call failed: {llm.describe_error(e)}* | — | — |")
            continue
        reasons = guard.check(answer)
        held += bool(reasons)
        cell = answer.replace("|", "/").replace("\n", " ")
        lines.append(f"| {i} | {q} | {cell} | {'held: ' + ', '.join(reasons) if reasons else 'passed'} | {time.monotonic() - start:.1f} |")
        time.sleep(PAUSE)
    lines += ["", f"Held back: {held}. Failed calls: {failed}."]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
