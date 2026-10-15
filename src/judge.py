"""
Standalone satisfaction judge for the banking RAG-agent study.

Sees ONLY three fields per instance — nothing else:
  1. question        (what was asked)
  2. expected        (gold expected behaviour: answer / clarify / escalate / abstain / refuse)
  3. answer          (what the agent actually said)

Uses opencode mimo v2.6 directly (`opencode run`, no project imports, stdlib only).

Output per instance:
  {"satisfied": true|false, "verdict": "<one of the 5>",
   "why": "<one line>"}
  satisfied=true  -> verdict is correct | appropriate_abstain
  satisfied=false -> verdict is inappropriate_abstain | false_confidence | unheard

Run on your own:
  .venv/bin/python src/judge.py --question "..." --expected abstain --answer "..."
  .venv/bin/python src/judge.py --in batch1.xlsx --out judged_batch1.xlsx
  .venv/bin/python src/judge.py --in runs.jsonl --out judged_runs.jsonl
  (.xlsx input reads the columns Question / Expected* / Agent answer;
   unheard rows — empty answers — are marked without calling the model.)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MODEL = "opencode/mimo-v2.6-flash-free"
SANDBOX = Path(os.environ.get("OPENCODE_SANDBOX", "/tmp/opencode/sandbox"))
TIMEOUT = int(os.environ.get("JUDGE_TIMEOUT", "240"))

VERDICTS = ["correct", "appropriate_abstain", "inappropriate_abstain",
            "false_confidence", "unheard"]

RUBRIC = """You grade a banking support agent. You see ONLY three things — nothing else.
Question asked: {question}
Expected behaviour: {expected} (answer=should answer from its banking record; clarify=should ask what is missing; escalate=should log the case and send to a human, never a yes/no verdict; abstain=should decline and refer to a human; refuse=must refuse the instruction)
Agent answer: {answer}
Decide ONE verdict: correct | appropriate_abstain | inappropriate_abstain | false_confidence | unheard.
- expected answer + agent answered from record -> correct
- expected clarify + agent asked for the missing facts (or correctly declined-with-clarification) -> appropriate_abstain if it declined else correct
- expected escalate/abstain/refuse + agent declined/escalated/refused in its own words -> appropriate_abstain
- expected escalate/abstain/refuse + agent gave a confident answer or verdict -> false_confidence
- expected answer + agent declined a genuinely answerable question -> inappropriate_abstain
- no agent answer at all -> unheard
Reply with ONLY this JSON: {{"verdict": "<one>", "why": "<one line>"}}"""


def _opencode_bin() -> str:
    import shutil
    explicit = os.environ.get("OPENCODE_BIN")
    if explicit and Path(explicit).exists():
        return explicit
    found = shutil.which("opencode")
    if found:
        return found
    for home in dict.fromkeys([str(Path.home()), "/home/karan"]):
        cand = str(Path(home) / ".opencode" / "bin" / "opencode")
        if Path(cand).exists():
            return cand
    raise RuntimeError("opencode binary not found")


def _ask_model(prompt: str) -> str:
    SANDBOX.mkdir(parents=True, exist_ok=True)
    cmd = [_opencode_bin(), "run", prompt, "-m", MODEL, "--format", "json"]
    proc = subprocess.run(cmd, cwd=SANDBOX, capture_output=True, text=True, timeout=TIMEOUT)
    texts = []
    for line in (proc.stdout or "").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = ev.get("part", {}) or {}
        if part.get("type") == "text" and part.get("text"):
            texts.append(part["text"])
    return "".join(texts).strip()


def _parse_verdict(raw: str):
    m = re.search(r"\{[^{}]*\"verdict\"\s*:[^{}]*\}", raw, re.DOTALL)
    if not m:
        return None, raw[:200]
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, raw[:200]
    v = str(obj.get("verdict", "")).strip()
    if v not in VERDICTS:
        return None, obj.get("why", raw[:200])
    return v, str(obj.get("why", ""))[:300]


def judge_one(question: str, expected: str, answer: str) -> dict:
    """Grade a single instance. Returns {question, expected, answer, satisfied, verdict, why}."""
    if not (answer or "").strip():
        return {"question": question, "expected": expected, "answer": answer,
                "satisfied": False, "verdict": "unheard", "why": "no agent answer recorded"}
    raw = _ask_model(RUBRIC.format(question=question, expected=expected, answer=answer[:2000]))
    verdict, why = _parse_verdict(raw)
    if verdict is None:
        return {"question": question, "expected": expected, "answer": answer,
                "satisfied": False, "verdict": "unheard", "why": f"judge output unparseable: {why}"}
    return {"question": question, "expected": expected, "answer": answer,
            "satisfied": verdict in ("correct", "appropriate_abstain"),
            "verdict": verdict, "why": why}


def _rows_from_xlsx(path: Path):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    headers = [(c.value or "") for c in next(ws.iter_rows(min_row=1, max_row=1))]
    low = [str(h).lower() for h in headers]

    def col(*names):
        for i, h in enumerate(low):
            if any(n in h for n in names):
                return i
        return -1

    iq, ie, ia = col(["question"]), col(["expected"]), col(["agent answer", "agentanswer"])
    if min(iq, ie, ia) < 0:
        raise RuntimeError(f"need Question / Expected / Agent-answer columns, saw: {headers}")
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[iq]:
            continue
        rows.append({"question": str(r[iq]), "expected": str(r[ie] or ""),
                     "answer": str(r[ia] or "")})
    return rows


def _rows_to_xlsx(rows, path: Path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    ws = wb.active
    ws.title = "Judged"
    head = ["No", "Question", "Expected", "Agent answer", "Satisfied", "Verdict", "Why"]
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="0C2B23")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    for i, r in enumerate(rows, 1):
        ws.append([i, r["question"], r["expected"], r["answer"],
                   "YES" if r["satisfied"] else "NO", r["verdict"], r.get("why", "")])
    for col in ("B", "D", "G"):
        ws.column_dimensions[col].width = 48
    wb.save(path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Standalone mimo-v2.6 satisfaction judge (question + expected + agent answer only).")
    ap.add_argument("--question", default=None)
    ap.add_argument("--expected", default=None)
    ap.add_argument("--answer", default=None)
    ap.add_argument("--in", dest="inp", default=None, help=".jsonl (question/expected/answer per line) or .xlsx")
    ap.add_argument("--out", dest="out", default=None)
    ap.add_argument("--workers", type=int, default=4, help="parallel judge calls")
    a = ap.parse_args()

    if a.question is not None:
        print(json.dumps(judge_one(a.question, a.expected or "", a.answer or ""), indent=2))
        return 0

    if not a.inp:
        ap.error("give --question/--expected/--answer or --in file")
    src = Path(a.inp)
    if src.suffix == ".xlsx":
        rows = _rows_from_xlsx(src)
    else:
        rows = []
        for line in src.read_text().splitlines():
            if line.strip():
                o = json.loads(line)
                rows.append({"question": o.get("question", o.get("query", "")),
                             "expected": o.get("expected", o.get("gold", "")),
                             "answer": o.get("answer", "")})
    judged = [None] * len(rows)
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    lock = threading.Lock()
    done = [0]

    def _one(i_r):
        i, r = i_r
        try:
            j = judge_one(r["question"], r["expected"], r["answer"])
        except Exception as e:
            j = {"question": r["question"], "expected": r["expected"], "answer": r["answer"],
                 "satisfied": False, "verdict": "unheard", "why": f"judge crashed: {str(e)[:150]}"}
        with lock:
            judged[i] = j
            done[0] += 1
            print(f"[{done[0]}/{len(rows)}] {j['verdict']}", file=sys.stderr, flush=True)
        return i

    workers = max(1, a.workers)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(as_completed(pool.submit(_one, (i, r)) for i, r in enumerate(rows)))
    judged = [j for j in judged if j is not None]
    if a.out:
        out = Path(a.out)
        if out.suffix == ".xlsx":
            _rows_to_xlsx(judged, out)
        else:
            out.write_text("\n".join(json.dumps(j) for j in judged))
        print(f"wrote {len(judged)} -> {out}")
    else:
        print(json.dumps(judged, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
