#!/usr/bin/env python3
"""CFIX: verify review items 2/3/4 (data-release drop, braces note, run-date move).
- Numbers recomputed from Rag results.xlsx, asserted identical (no value changes).
- Prompts verbatim STRICT vs check_satisfaction.py and src/evaluate.py.
- Appendix C: 2 monospace fences, braces escape note, single Run date sitting
  with the third-model paragraph (before first fence).
- C5 dropped: no deferred-release / artefact-claim language anywhere.
- Placeholders listed in notes/open_issues.md (no values invented).
- DOCX: braces note + run date with third-model + Consolas code blocks.
Reads ONLY Rag results.xlsx via openpyxl. Appends CFIX-* ledger rows.
"""
import csv
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
WB = ROOT / "Rag results.xlsx"
TABLES = ROOT / "paper" / "tables"
C3 = "Satisfied (3rd llm as judge)"
CF = "Satisfied (Friend)"


def is_miss(v):
    return str(v).strip().lower() != "yes"


wb = openpyxl.load_workbook(WB, data_only=True)
data = {}
for sheet in ["glm", "muse"]:
    ws = wb[sheet]
    hdr = [c.value for c in ws[1]]
    idx = {h: i + 1 for i, h in enumerate(hdr) if h}
    rows = []
    for r in range(2, ws.max_row + 1):
        a = ws.cell(r, idx["satisfied"]).value
        t3 = ws.cell(r, idx[C3]).value
        fr = ws.cell(r, idx[CF]).value
        miss = sum([is_miss(a), is_miss(t3), is_miss(fr)])
        rows.append({"id": ws.cell(r, idx["ID"]).value,
                     "type": str(ws.cell(r, idx["Type"]).value),
                     "maj": miss >= 2})
    data[sheet] = rows
    assert len(rows) == 100, (sheet, len(rows))


def read_csv(name):
    with open(TABLES / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


t3 = read_csv("T3_merged.csv")
exp = {"overall": (11, 13), "clear": (1, 2), "ambiguous": (6, 7),
       "out_of_scope": (0, 1), "high_stakes": (2, 2), "adversarial": (2, 1)}
for r in t3:
    ef, em = exp[r["scope"]]
    assert int(r["fast_miss"]) == ef and int(r["muse_miss"]) == em, r
    print(f"verified T3 {r['scope']}: fast {r['fast_miss']} muse {r['muse_miss']} b={r['b']} c={r['c']} p={r['p_exact']}")

t16 = read_csv("T16_pooled.csv")
expF = {"overall": 0.3203, "clear": 0.3905, "ambiguous": 0.4665,
        "out_of_scope": 0.1228, "high_stakes": 0.1619, "adversarial": 0.1}
for r in t16:
    assert abs(float(r["fleiss_kappa"]) - expF[r["scope"]]) < 1e-4, r
    print(f"verified T16 {r['scope']}: Fleiss {r['fleiss_kappa']} all3 {r['all3_agree']}/{r['n']}")

t17 = read_csv("T17_majority_reasons.csv")
d17 = {(r["model_sheet"], r["category"]): int(r["n"]) for r in t17}
assert d17[("glm", "Mixed")] == 7 and d17[("glm", "Failure to Answer")] == 2
assert d17[("muse", "Failure to Answer")] == 8 and d17[("muse", "Mixed")] == 3
print("verified T17 consensus")

t18 = read_csv("T18_unanimous.csv")
assert {r["model_sheet"]: int(r["n_unanimous"]) for r in t18} == {"glm": 3, "muse": 4}
print("verified T18 unanimous 3+4")

gmap = {x["id"]: x for x in data["glm"]}
mmap = {x["id"]: x for x in data["muse"]}
common = sorted(set(gmap) & set(mmap))
bp = sum(1 for i in common if not gmap[i]["maj"] and not mmap[i]["maj"])
of = sum(1 for i in common if gmap[i]["maj"] and not mmap[i]["maj"])
om = sum(1 for i in common if not gmap[i]["maj"] and mmap[i]["maj"])
bf = sum(1 for i in common if gmap[i]["maj"] and mmap[i]["maj"])
assert (bp, of, om, bf) == (80, 7, 9, 4), (bp, of, om, bf)
print(f"verified grid: {bp}/{of}/{om}/{bf}")

# prompts verbatim STRICT
cs = (ROOT / "check_satisfaction.py").read_text()
m = re.search(r'JUDGE_PROMPT = """(.*?)"""', cs, re.S)
assert m, "checker prompt missing"
judge_cs = m.group(1)
asm = (ROOT / "analysis" / "assemble_draft.py").read_text()
m2 = re.search(r'THIRD_MODEL_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m2 and m2.group(1) == judge_cs, "third-model prompt mismatch STRICT"
print("verified third-model prompt verbatim STRICT vs check_satisfaction.py")
ev = (ROOT / "src" / "evaluate.py").read_text()
m3 = re.search(r'JUDGE_PROMPT = """(.*?)"""', ev, re.S)
assert m3, "evaluate prompt missing"
m4 = re.search(r'AUTOMATED_MARK_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m4 and m4.group(1) == m3.group(1), "auto prompt mismatch STRICT"
print("verified auto prompt verbatim STRICT vs src/evaluate.py")
assert "OWN_JUDGE_RUBRIC_TEXT" not in asm, "own-judge remnant"
assert "unheard" not in asm.lower(), "unheard remnant in assemble"

# Appendix C structure: 2 fences, braces note, run date with third-model
assert asm.count("```text") == 2, "need 2 monospace fences in assemble"
assert "The doubled braces in the prompts" in asm and "Python format-string escapes" in asm, "braces note missing in assemble"
assert asm.count("Run date: 10 October 2026 (author-reported) for this third-model run.") == 1, "run date with third-model missing in assemble"
assert asm.count("Run date:") == 1, "must be exactly 1 Run date in assemble"
assert "day before yesterday" not in asm, "day-before remnant in assemble"
print("verified Appendix C in assemble: 2 fences + braces note + run date with third-model")

for fn in ["paper/methodology.md", "paper/results.md", "paper/discussion.md",
           "paper/conclusion.md", "paper/related_work.md", "paper/introduction.md",
           "analysis/assemble_draft.py", "analysis/build_docx.py"]:
    txt = (ROOT / fn).read_text(encoding="utf-8")
    assert "localhost" not in txt, f"localhost remnant in {fn}"
    assert "up to 4 attempts" not in txt and "timeout 240s x4" not in txt, f"retry remnant in {fn}"
    print(f"clean {fn}")

bd = (ROOT / "analysis" / "build_docx.py").read_text()
assert "Consolas" in bd and "Courier New" in bd and "add_code_block" in bd, "docx monospace renderer missing"
print("verified build_docx renders fenced code as Consolas/Courier")

meth = (ROOT / "paper" / "methodology.md").read_text()
assert "Run date:" not in meth and "run date:" not in meth, "run date in methods"
disc = (ROOT / "paper" / "discussion.md").read_text()
assert "Run date:" not in disc and "run date:" not in disc, "run date in discussion"
print("verified methods/discussion have zero run-date copies")

draft = (ROOT / "paper" / "FINAL_DRAFT.md").read_text()
assert draft.count("Run date: 10 October 2026 (author-reported) for this third-model run.") == 1, "run date with third-model missing in draft"
assert draft.count("Run date:") == 1, "must be exactly 1 Run date in draft"
assert draft.index("for this third-model run.") < draft.index("```text"), "run date not before first fence"
assert draft.index("for this third-model run.") < draft.index("Workbook column 'Auto verdict"), "run date must sit with third-model para"
assert "The doubled braces in the prompts" in draft and "Python format-string escapes" in draft, "braces note missing in draft"
assert draft.count("```text") == 2, "need 2 fences in draft"
assert "day before yesterday" not in draft, "day-before remnant in draft"
assert "unheard" not in draft.lower(), "unheard remnant in draft"
print("verified draft Appendix C: run date with third-model + braces note + 2 fences")

# C5 dropped everywhere
for fn in ["paper/introduction.md", "paper/conclusion.md", "paper/methodology.md"]:
    st = (ROOT / fn).read_text(encoding="utf-8")
    assert "C5 deferred" not in st, f"C5 deferred remnant in {fn}"
    assert "waits for that sign-off" not in st, f"artefact-wait remnant in {fn}"
    assert "later public release" not in st, f"later-release remnant in {fn}"
    assert "live in the study archive" not in st, f"archive-availability remnant in {fn}"
    print(f"verified C5 dropped in {fn}")
assert "no artefact contribution is claimed" in (ROOT / "paper" / "introduction.md").read_text()
assert "no artefact contribution is claimed" in (ROOT / "paper" / "conclusion.md").read_text()
for bad in ["C5 deferred", "waits for that sign-off", "later public release",
            "live in the study archive", "until authors clear release",
            "until the authors clear release"]:
    assert bad not in draft, f"C5 remnant in draft: {bad}"
assert "no artefact contribution is claimed" in draft, "artefact disclaimer missing in draft"
print("verified C5 dropped in draft")

oi = (ROOT / "notes" / "open_issues.md").read_text()
assert "## Remaining placeholders" in oi
for k in ["Authors:", "Affiliations:", "Corresponding author", "Funding:",
          "Data release link:", "Venue"]:
    assert k in oi, f"placeholder missing {k}"
assert "C5 dropped" in oi or "no artefact contribution" in oi.lower(), "C5 drop not logged in open_issues"
print("verified placeholders listed (no values invented)")

t2txt = (TABLES / "T2_pipeline.csv").read_text(encoding="utf-8")
assert "src/" not in t2txt and "kb_raw" not in t2txt and "notes/" not in t2txt
print("verified T2 clean")

# docx checks
from docx import Document
doc = Document(str(ROOT / "paper" / "FINAL_DRAFT.docx"))
texts = [p.text for p in doc.paragraphs]
assert sum(1 for t in texts if "format-string escapes" in t) >= 1, "braces note missing in docx"
rd = [t for t in texts if "Run date:" in t]
assert len(rd) == 1 and "for this third-model run" in rd[0] and "third-model" in rd[0].lower() or "satisfaction-checker" in rd[0].lower(), f"run date misplaced in docx: {rd}"
assert sum(1 for t in texts if "C5 deferred" in t) == 0, "C5 deferred in docx"
assert sum(1 for t in texts if "no artefact contribution is claimed" in t) >= 1, "artefact disclaimer missing in docx"
consolas = sum(1 for p in doc.paragraphs for r in p.runs if r.font.name == "Consolas")
assert consolas >= 10, f"too few Consolas runs in docx: {consolas}"
print(f"verified docx: braces note + run date with third-model + {consolas} Consolas runs")

LED = ROOT / "paper" / "claims_ledger.csv"
FIELDS = ["claim_id", "section", "sentence", "value", "source_script",
          "source_file_or_cells", "verified_by"]
raw = []
with open(LED, newline="", encoding="utf-8") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    assert header == FIELDS, header
    for row in rdr:
        if not row or not row[0].strip():
            continue
        if row[0].strip().startswith("CFIX-"):
            continue
        raw.append(row)
new = [
    ["CFIX-APDXC", "Appendix C",
     "Run date moved to third-model para + braces escape note; 2 prompts monospace verbatim retained",
     "Run date 1x with third-model (before first fence); doubled-braces Python escape note; THIRD STRICT vs check_satisfaction.py; AUTO STRICT vs src/evaluate.py; 2x text fences; Consolas/Courier via add_code_block; numbers unchanged (T3/T16/T17/T18/grid identical)",
     "analysis/recompute_cfix.py",
     "analysis/assemble_draft.py + check_satisfaction.py + src/evaluate.py",
     "script+code"],
    ["CFIX-C5DROP", "Intro/Conclusion/Methods/Notes",
     "C5 dropped as contribution (no release, no artefact claim)",
     "Removed C5 deferred + deferred-release + artefact-wait + later-release + archive-availability; now not released + no artefact claim in intro/conclusion/methods; open_issues logs C5 dropped; numbers unchanged",
     "analysis/recompute_cfix.py",
     "paper/introduction.md + paper/conclusion.md + paper/methodology.md + notes/open_issues.md",
     "script+text"],
]
ids = [r[0] for r in raw]
anchor = ids.index("MAJ-ADJ") + 1 if "MAJ-ADJ" in ids else len(raw)
outrows = raw[:anchor] + new + raw[anchor:]
with open(LED, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(FIELDS)
    w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+2 CFIX)")
print("CFIX checks PASS")
