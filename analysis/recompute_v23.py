#!/usr/bin/env python3
"""V23: both pasted judge prompts verbatim in Appendix C (third + own RUBRIC).
Verify numbers identical, prompts verbatim (strict), run-dates lowercase, placeholders.
Updates ledger with V22 row. Reads ONLY Rag results.xlsx via openpyxl.
"""
import csv, re
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parent.parent
WB=ROOT/"Rag results.xlsx"
TABLES=ROOT/"paper"/"tables"
C3='Satisfied (3rd llm as judge)'
CF='Satisfied (Friend)'
def is_miss(v): return str(v).strip().lower()!='yes'

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
    assert len(rows)==100,(sheet,len(rows))

def read_csv(name):
    with open(TABLES/name, encoding='utf-8') as f: return list(csv.DictReader(f))

t3=read_csv("T3_merged.csv")
exp={'overall':(11,13),'clear':(1,2),'ambiguous':(6,7),'out_of_scope':(0,1),'high_stakes':(2,2),'adversarial':(2,1)}
for r in t3:
    ef,em=exp[r['scope']]
    assert int(r['fast_miss'])==ef and int(r['muse_miss'])==em,(r,exp[r['scope']])
    print(f"verified T3 {r['scope']}: fast {r['fast_miss']} muse {r['muse_miss']} b={r['b']} c={r['c']} p={r['p_exact']}")

t16=read_csv("T16_pooled.csv")
expF={'overall':0.3203,'clear':0.3905,'ambiguous':0.4665,'out_of_scope':0.1228,'high_stakes':0.1619,'adversarial':0.1}
for r in t16:
    assert abs(float(r['fleiss_kappa'])-expF[r['scope']])<1e-4,r
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
assert (bp,of,om,bf)==(80,7,9,4),(bp,of,om,bf)
print(f"verified grid: {bp}/{of}/{om}/{bf}")

# prompts verbatim STRICT
cs=(ROOT/"check_satisfaction.py").read_text()
m=re.search(r'JUDGE_PROMPT = """(.*?)"""', cs, re.S)
judge_cs=m.group(1)
asm=(ROOT/"analysis"/"assemble_draft.py").read_text()
m2=re.search(r'THIRD_MODEL_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m2 and m2.group(1)==judge_cs, "third-model prompt mismatch STRICT"
print("verified third-model prompt verbatim STRICT vs check_satisfaction.py")
ev=(ROOT/"src"/"evaluate.py").read_text()
m3=re.search(r'JUDGE_PROMPT = """(.*?)"""', ev, re.S)
judge_ev=m3.group(1)
m4=re.search(r'AUTOMATED_MARK_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m4, "auto prompt missing"
assert m4.group(1)==judge_ev, "auto prompt mismatch STRICT"
print("verified auto prompt verbatim STRICT vs src/evaluate.py")
sj=(ROOT/"src"/"judge.py").read_text()
m5=re.search(r'RUBRIC\s*=\s*"""(.*?)"""', sj, re.S)
assert m5, "src/judge RUBRIC missing"
m6=re.search(r'OWN_JUDGE_RUBRIC_TEXT="""(.*?)"""', asm, re.S)
assert m6 and m6.group(1)==m5.group(1), "own-judge RUBRIC mismatch STRICT vs src/judge.py"
print("verified own-judge RUBRIC verbatim STRICT vs src/judge.py")
assert "Own judge RUBRIC (author-supplied) copied verbatim below" in asm
assert asm.count("OWN_JUDGE_RUBRIC_TEXT")==2, "own rubric should appear def + use once"

# Appendix C labels + model/dates
assert "Workbook column 'Satisfied (3rd llm as judge)' was produced by" in asm
assert "copied verbatim below" in asm
assert "sheet mode reformats that output to YES" in asm
assert "Workbook column 'Auto verdict (fill it)' was produced by" in asm
assert "with no YES/NO reformatting" in asm
assert "Model string: opencode/mimo-v2.6-flash-free" in asm
assert "run date: 2026-10-10" in asm
assert asm.count("run date: 2026-10-10")>=2, "need both third-model + classmate dates in assemble"
assert "classmate column written day before yesterday" in asm
assert "third-model column ran day before yesterday" in asm
assert "Run date:" not in asm
# unheard allowed ONLY inside own-judge verbatim block + its one label sentence; forbid elsewhere
import re as _re
asm_norubric = _re.sub(r'OWN_JUDGE_RUBRIC_TEXT="""(.*?)"""', '', asm, flags=_re.S)
assert asm_norubric.lower().count("unheard")==1, f"expect 1 unheard (label) outside block, got {asm_norubric.lower().count('unheard')}"
assert asm_norubric.lower().count("five verdicts")==1, "expect 1 five-verdicts label outside block"
print("verified Appendix C dates + unheard only in own-judge block+label")

for fn in ["paper/methodology.md","paper/results.md","paper/discussion.md","paper/conclusion.md","paper/related_work.md","paper/introduction.md","analysis/assemble_draft.py"]:
    txt=(ROOT/fn).read_text(encoding="utf-8")
    assert "localhost" not in txt, f"localhost remnant in {fn}"
    assert "up to 4 attempts" not in txt and "timeout 240s x4" not in txt, f"retry remnant in {fn}"
    assert "src/" not in txt, f"src/ remnant in {fn}"
    if fn.startswith("paper/"):
        assert "notes/" not in txt, f"notes/ path remnant in {fn}"
    print(f"clean {fn}")
meth=(ROOT/"paper"/"methodology.md").read_text()
assert meth.count("run date: 2026-10-10")>=2 and "Run date:" not in meth and "not recoverable" not in meth
assert "classmate column written day before yesterday" in meth
disc=(ROOT/"paper"/"discussion.md").read_text()
assert disc.count("run date: 2026-10-10")>=2 and "Run date:" not in disc and disc.count("not recoverable")==0
assert "classmate column written day before yesterday" in disc
assert "with no separate bucket for disputed cases" in disc
print("verified lowercase run dates (both columns) + disputed reword")
assert "was designed but not completed" not in disc
assert "In contrast, Luo et al. [33]" in disc
print("verified discussion contrast retained")

t2txt=(TABLES/"T2_pipeline.csv").read_text(encoding="utf-8")
assert "src/" not in t2txt and "kb_raw" not in t2txt and "notes/" not in t2txt
print("verified T2 clean")

oi=(ROOT/"notes"/"open_issues.md").read_text()
assert "## Remaining placeholders" in oi
for k in ["Authors:","Affiliations:","Corresponding author","Funding:","Data release link:","Venue","run date:","Classmate run date","2026-10-10"]:
    assert k in oi, f"placeholder missing {k}"
print("verified placeholders listed")

LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        if row[0].strip().startswith('V23-'): continue
        raw.append(row)
new=[
 ['V23-BOTH-PROMPTS','Appendix C',"Both pasted prompts verbatim: third-model JUDGE_PROMPT (Satisfied column, YES/NO reformat) + own-judge RUBRIC (5 verdicts incl unheard, direct store); auto prompt retained for Auto verdict column",
  "run date 2026-10-10 added for classmate column in analysis/assemble_draft.py + paper/methodology.md + paper/discussion.md + notes/open_issues.md; third-model date unchanged; both prompts verbatim unchanged; numbers unchanged (T3/T16/T17/T18/grid identical)",
  'analysis/recompute_v22.py','analysis/assemble_draft.py + paper/methodology.md + paper/discussion.md + notes/open_issues.md','script+author-supplied'],
]
ids=[r[0] for r in raw]
anchor=ids.index('MAJ-ADJ')+1 if 'MAJ-ADJ' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+1 V23)")
