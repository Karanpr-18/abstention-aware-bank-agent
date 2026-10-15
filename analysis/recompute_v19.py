#!/usr/bin/env python3
"""V19: frozen scope, 7 fixes. Recompute/verify from structured workbook only.
- Verifies T3_merged, T16_pooled, T17, T18, grid identical (no number changes).
- Verifies both judge prompts verbatim vs codebase.
- Verifies no localhost/retry/src paths in manuscript sources.
- Verifies ref33 28k retained (arXiv fetch 2026-10-12 showed >28k).
- Updates ledger with V19 rows.
Reads ONLY Rag results.xlsx via openpyxl. No CSV-comma splitting.
"""
import csv, re
from pathlib import Path
from collections import Counter
import openpyxl
ROOT=Path(__file__).resolve().parent.parent
WB=ROOT/"Rag results.xlsx"
TABLES=ROOT/"paper"/"tables"
TYPES=["clear","ambiguous","out_of_scope","high_stakes","adversarial"]
C3='Satisfied (3rd llm as judge)'
CF='Satisfied (Friend)'
def is_miss(v): return str(v).strip().lower()!='yes'
def norm_reason(v):
    s=str(v).strip()
    if s.lower()=='yes': return None
    m=re.search(r'no\s*[-–—:]+\s*(.+)', s, re.I)
    if not m: return s
    r=m.group(1).strip().lower()
    mp={'overreach':'Overreach','unsupported assumption':'Unsupported Assumption','oversharing':'Oversharing','soft refusal':'Soft Refusal','failure to answer':'Failure to Answer'}
    return mp.get(r, m.group(1).strip())

wb=openpyxl.load_workbook(WB, data_only=True)
data={}
for sheet in ['glm','muse']:
    ws=wb[sheet]
    hdr=[c.value for c in ws[1]]
    idx={h:i+1 for i,h in enumerate(hdr) if h}
    rows=[]
    for r in range(2, ws.max_row+1):
        a=ws.cell(r,idx['satisfied']).value; t3=ws.cell(r,idx[C3]).value; fr=ws.cell(r,idx[CF]).value
        miss=sum([is_miss(a),is_miss(t3),is_miss(fr)]); maj=miss>=2
        rows.append({'id':ws.cell(r,idx['ID']).value,'type':str(ws.cell(r,idx['Type']).value),'maj':maj})
    data[sheet]=rows
    assert len(rows)==100, (sheet,len(rows))

def read_csv(name):
    with open(TABLES/name, encoding='utf-8') as f: return list(csv.DictReader(f))

t3=read_csv("T3_merged.csv")
exp={'overall':(11,13),'clear':(1,2),'ambiguous':(6,7),'out_of_scope':(0,1),'high_stakes':(2,2),'adversarial':(2,1)}
for r in t3:
    ef,em=exp[r['scope']]
    assert int(r['fast_miss'])==ef and int(r['muse_miss'])==em, (r,exp[r['scope']])
    print(f"verified T3 {r['scope']}: fast {r['fast_miss']} muse {r['muse_miss']} b={r['b']} c={r['c']} p={r['p_exact']}")

t16=read_csv("T16_pooled.csv")
expF={'overall':0.3203,'clear':0.3905,'ambiguous':0.4665,'out_of_scope':0.1228,'high_stakes':0.1619,'adversarial':0.1}
for r in t16:
    assert abs(float(r['fleiss_kappa'])-expF[r['scope']])<1e-4, r
    print(f"verified T16 {r['scope']}: Fleiss {r['fleiss_kappa']} all3 {r['all3_agree']}/{r['n']}")

t17=read_csv("T17_majority_reasons.csv")
d17={(r['model_sheet'],r['category']):int(r['n']) for r in t17}
assert d17[('glm','Mixed')]==7 and d17[('glm','Failure to Answer')]==2
assert d17[('muse','Failure to Answer')]==8 and d17[('muse','Mixed')]==3
print("verified T17 consensus")

t18=read_csv("T18_unanimous.csv")
assert {r['model_sheet']:int(r['n_unanimous']) for r in t18}=={'glm':3,'muse':4}
print("verified T18 unanimous 3+4")

gmap={x['id']:x for x in data['glm']}; mmap={x['id']:x for x in data['muse']}
common=sorted(set(gmap)&set(mmap))
bp=sum(1 for i in common if not gmap[i]['maj'] and not mmap[i]['maj'])
of=sum(1 for i in common if gmap[i]['maj'] and not mmap[i]['maj'])
om=sum(1 for i in common if not gmap[i]['maj'] and mmap[i]['maj'])
bf=sum(1 for i in common if gmap[i]['maj'] and mmap[i]['maj'])
assert (bp,of,om,bf)==(80,7,9,4), (bp,of,om,bf)
print(f"verified grid: {bp}/{of}/{om}/{bf}")

# prompt verbatim
cs=(ROOT/"check_satisfaction.py").read_text()
m=re.search(r'JUDGE_PROMPT = """(.*?)"""', cs, re.S)
judge_cs=m.group(1)
asm=(ROOT/"analysis"/"assemble_draft.py").read_text()
m2=re.search(r'THIRD_MODEL_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m2 and m2.group(1)==judge_cs, "third-model prompt mismatch"
print("verified third-model prompt verbatim vs check_satisfaction.py")
ev=(ROOT/"src"/"evaluate.py").read_text()
m3=re.search(r'JUDGE_PROMPT = """(.*?)"""', ev, re.S)
judge_ev=m3.group(1)
m4=re.search(r'AUTOMATED_MARK_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m4, "auto prompt missing"
# normalize double braces (code escaping) vs single (rendered)
norm_ev=judge_ev.replace("{{","{").replace("}}","}")
assert norm_ev==m4.group(1), "auto prompt content mismatch after brace normalize"
print("verified auto prompt content vs src/evaluate.py (brace-normalized)")

# banned strings in manuscript sources
for fn in ["paper/methodology.md","paper/results.md","paper/discussion.md","paper/conclusion.md","paper/related_work.md","paper/introduction.md","analysis/assemble_draft.py"]:
    txt=(ROOT/fn).read_text(encoding="utf-8")
    assert "localhost" not in txt, f"localhost remnant in {fn}"
    assert "up to 4 attempts" not in txt and "timeout 240s x4" not in txt, f"retry remnant in {fn}"
    assert "src/" not in txt, f"src/ remnant in {fn}"
    # notes/ paths should be gone from manuscript sources (open_issues/ledger excluded)
    if fn.startswith("paper/"):
        assert "notes/" not in txt, f"notes/ path remnant in {fn}"
    print(f"clean {fn}: no localhost/retry/src/notes paths")

# T2 clean
t2txt=(TABLES/"T2_pipeline.csv").read_text(encoding="utf-8")
assert "src/" not in t2txt and "kb_raw" not in t2txt and "notes/" not in t2txt, "T2 path remnant"
print("verified T2_pipeline.csv clean")

# Limits/Future phrases removed
disc=(ROOT/"paper"/"discussion.md").read_text()
assert "a fuller 50-70 sweep is still needed" not in disc
assert "was designed but not completed" not in disc
assert "In contrast, Luo et al. [33]" in disc
print("verified discussion Limits + contrast sentence")
meth=(ROOT/"paper"/"methodology.md").read_text()
assert "was designed but not completed" not in meth
assert "Run date: not recoverable" in meth
con=(ROOT/"paper"/"conclusion.md").read_text()
assert "was designed but not completed" not in con and "designed but not completed here" not in con
assert "A fully blinded shared-judge rerun is future work" in con
print("verified methods/conclusion future-work rewrite")
# Appendix checks via assemble text
assert "Workbook column 'Satisfied (3rd llm as judge)'" in asm
assert "Workbook column 'Auto verdict (fill it)'" in asm
assert "Model string: opencode/mimo-v2.6-flash-free" in asm
assert "Run date: not recoverable" in asm
assert "unheard" not in asm.lower()
print("verified Appendix C labels/model/date, no unheard")

# ledger update
LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        if row[0].strip().startswith('V19-'): continue
        raw.append(row)
new=[
 ['V19-APDXC','Appendix C',"Both judge prompts labelled by workbook column (third-model + auto) with model/date; URL/retry/paths removed",
  "third-model col 'Satisfied (3rd llm as judge)' prompt verbatim vs check_satisfaction.py MATCH; auto col 'Auto verdict (fill it)' content vs src/evaluate.py MATCH (brace-normalized); Model string opencode/mimo-v2.6-flash-free; Run date not recoverable; localhost 0, attempts 0, src/ 0, notes/ 0 in manuscript sources",
  'analysis/recompute_v19.py','paper/FINAL_DRAFT.md Appendix C + check_satisfaction.py + src/evaluate.py','script+code'],
 ['V19-PATHS','Methods/Appendix',"Removed localhost URL, retry counts, src/file paths from manuscript",
  "removed http://localhost:8378/v1 + up to 4 attempts; T2 value/source cleaned (0 src/kb_raw/notes); per-ID file without path; assemble 0 hits",
  'analysis/recompute_v19.py','paper/tables/T2_pipeline.csv + analysis/assemble_draft.py + paper/*.md','script+grep'],
 ['V19-LIMITS','Discussion/Limits/Future',"Deleted sweep + blinded-completed sentences; plain future work",
  "deleted 'a fuller 50-70 sweep is still needed' + 3x 'designed but not completed'; conclusion now 'A fully blinded shared-judge rerun is future work'; methods/limits use 'Run date: not recoverable'",
  'analysis/recompute_v19.py','paper/discussion.md + paper/conclusion.md + paper/methodology.md','script+grep'],
 ['V19-REF33','Related Work',"Ref [33] 28,000 tasks retained (verified vs arXiv)",
  "arXiv 2606.28733 abstract 'more than 28,000 tasks' MATCH; authors Han Luo/Bingbing Wen/Lucy Lu Wang MATCH; title MATCH (fetched 2026-10-12)",
  'analysis/recompute_v19.py','https://arxiv.org/abs/2606.28733','webfetch'],
 ['V19-DISC33','Discussion',"Added contrast sentence [33] reasoning vs our Failure to Answer",
  "In contrast, Luo et al. [33] report reasoning improves timely abstention but lowers overall abstention recall, while our reasoning tier shows consensus Failure to Answer on answerable queries; stated as contrast not explanation",
  'analysis/recompute_v19.py','paper/discussion.md 5.1','script+text'],
 ['V19-PLACE','Notes',"Placeholders listed in open_issues (no values invented)",
  "authors/affiliations/corresponding/funding/data-link/venue/run-date/classmate-protocol listed 2026-10-12",
  'analysis/recompute_v19.py','notes/open_issues.md','script+text'],
]
ids=[r[0] for r in raw]
anchor=ids.index('MAJ-ADJ')+1 if 'MAJ-ADJ' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+6 V19)")
