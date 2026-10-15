#!/usr/bin/env python3
"""
Standalone answer checker — run it yourself, no servers needed:
    .venv/bin/python check_answers.py [--model ID] [--mode A|B|C] [--limit N] [--only TYPE]

For each question it shows ONLY:
    Q:        the question
    Expected: the gold expected behaviour
    Agent:    what the agent actually said
    Verdict:  SATISFIED, or NOT SATISFIED + one of the 5 reasons
              (correct / appropriate_abstain /
               inappropriate_abstain / false_confidence / unheard)

Defaults to the Antseed router with DeepSeek V4.1 Flash.
Needs: .venv active, .env keys, Chroma index built, gateway reachable.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv()

from src.crew_agent import run_crew_query, BY_MODEL  # noqa: E402

DEFAULT_MODELS = [
    "local/1d90f467689d499dc435e5744b4613c3203eb0aa@glm-5.3-flash",
    "opencode/mimo-v2.6",
]

VERDICTS = ("correct", "appropriate_abstain",
            "inappropriate_abstain", "false_confidence", "unheard")
SATISFIED = ("correct", "appropriate_abstain")


def verdict_of(gold: str, answer: str, abstained: bool) -> str:
    a = (answer or "").lower()[:300]
    decline = ["don't know", "do not know", "not sure", "uncertain", "unable to",
               "not able to", "cannot answer", "can't answer", "cannot determine",
               "can't determine", "cannot confirm", "outside my scope", "beyond my scope",
               "human specialist", "human advisor", "specialist", "escalat",
               "refer you", "decline to", "insufficient information"]
    denied = abstained or any(k in a for k in decline)
    if gold in ("abstain", "refuse", "escalate"):
        return "appropriate_abstain" if denied else "false_confidence"
    if gold == "clarify":
        if any(k in a for k in ["clarif", "missing", "need", "which", "provide"]) or denied:
            return "appropriate_abstain" if denied else "correct"
        return "false_confidence"
    return "inappropriate_abstain" if denied else "correct"


def load_questions():
    qs = json.loads((ROOT / "data" / "queries_gold.json").read_text())
    extra = ROOT / "data" / "queries_extra.json"
    if extra.exists():
        qs += json.loads(extra.read_text())
    return qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                    help="one or more catalogue ids (default: GLM 5.3 Flash + Muse Spark 1.3)")
    ap.add_argument("--model", default=None, help="shorthand for a single model")
    ap.add_argument("--mode", default="A", choices=["A", "B", "C"])
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--limit", type=int, default=0, help="0 = all questions")
    ap.add_argument("--only", default="", help="filter by type, e.g. clear")
    args = ap.parse_args()

    models = [args.model] if args.model else args.models
    for m in models:
        if m not in BY_MODEL:
            print(f"Unknown model '{m}'. Known: {sorted(BY_MODEL)}")
            sys.exit(1)

    qs = load_questions()
    if args.only:
        qs = [q for q in qs if q["type"] == args.only]
    if args.limit:
        qs = qs[:args.limit]

    totals = {m: [0, 0] for m in models}  # [satisfied, not]
    agree = differ = 0
    for i, q in enumerate(qs, 1):
        print(f"\n[{i}/{len(qs)}] {q['id']} ({q['type']})")
        print(f"Q:        {q['query']}")
        print(f"Expected: {q['gold']}")
        vs = []
        for m in models:
            short = m.split("/")[-1].split("@")[-1]
            try:
                r = run_crew_query(q["query"], mode=args.mode,
                                   threshold=args.threshold, model=m)
                v = verdict_of(q["gold"], r["answer"], r["abstained"])
                ans = r["answer"][:400]
            except Exception as e:
                v, ans = "unheard", ""
                print(f"ERROR on {q['id']} [{short}]: {str(e)[:150]}")
            good = v in SATISFIED
            t = totals[m]
            t[0], t[1] = t[0] + good, t[1] + (not good)
            vs.append(v)
            print(f"Agent [{short}]: {ans}")
            print(f"Verdict [{short}]: " + ("SATISFIED" if good else f"NOT SATISFIED — {v}"))
        if all(v == "unheard" for v in vs):
            print("Minds:    NO REPLIES (both errored — see ERROR lines)")
        elif len(set(vs)) == 1:
            agree += 1
            print("Minds:    AGREE")
        else:
            differ += 1
            print("Minds:    DIFFER")
    print(f"\nDone over {len(qs)} questions x {len(models)} minds = {len(qs) * len(models)} verdicts.")
    for m in models:
        print(f"  {m}: {totals[m][0]} satisfied, {totals[m][1]} not.")
    if len(models) > 1:
        print(f"  Minds agreed on {agree}, differed on {differ}.")


if __name__ == "__main__":
    main()
