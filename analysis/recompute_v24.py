#!/usr/bin/env python3
"""V24: Appendix C 2 prompts monospace, own-judge deleted, single Run date.
Verify numbers identical, prompts verbatim (strict), single Run date, placeholders.
Reads ONLY Rag results.xlsx via openpyxl.
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

# prompts verbatim STRICT (2 only)
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
# own-judge must be deleted (no reported number depends on src/judge.py RUBRIC)
assert "OWN_JUDGE_RUBRIC_TEXT" not in asm, "own-judge block not deleted"
assert "Own judge RUBRIC" not in asm, "own-judge label not deleted"
print("verified own-judge deleted (no number depends on src/judge.py RUBRIC)")

# Appendix C: 2 fences, monospace note, single Run date
assert asm.count("```text")==2, f"need 2 monospace fences, got {asm.count('```text')}"
assert "Consolas" in asm or "monospace" in asm.lower(), "monospace note missing in assemble"
assert "Workbook column 'Satisfied (3rd llm as judge)' was produced by" in asm
assert "Workbook column 'Auto verdict (fill it)' was produced by" in asm
assert asm.count("Run date: 10 October 2026 (author-reported).")==1, "need exactly 1 Run date in assemble"
assert "day before yesterday" not in asm, "day-before wording remnant in assemble"
assert "run date: 2026-10-10" not in asm and "Run date: 2026-10-10" not in asm, "old numeric date remnant"
assert "unheard" not in asm.lower(), "unheard remnant (own-judge deleted)"
print("verified Appendix C 2 monospace blocks + single Run date + no own-judge")

for fn in ["paper/methodology.md","paper/results.md","paper/discussion.md","paper/conclusion.md","paper/related_work.md","paper/introduction.md","analysis/assemble_draft.py","analysis/build_docx.py"]:
    txt=(ROOT/fn).read_text(encoding="utf-8")
    assert "localhost" not in txt, f"localhost remnant in {fn}"
    assert "up to 4 attempts" not in txt and "timeout 240s x4" not in txt, f"retry remnant in {fn}"
    # src/ allowed in build_docx comments? forbid in manuscript + assemble only
    if fn in ["paper/methodology.md","paper/discussion.md","paper/conclusion.md","analysis/assemble_draft.py"]:
        assert "src/" not in txt, f"src/ remnant in {fn}"
    if fn.startswith("paper/"):
        assert "notes/" not in txt, f"notes/ path remnant in {fn}"
    print(f"clean {fn}")
# build_docx must render fences as Consolas (not skip)
bd=(ROOT/"analysis"/"build_docx.py").read_text()
assert "Consolas" in bd and "Courier New" in bd, "docx monospace fonts missing"
assert "add_code_block" in bd, "code-block renderer missing"
print("verified build_docx renders fenced code as Consolas/Courier")

meth=(ROOT/"paper"/"methodology.md").read_text()
assert "Run date:" not in meth and "run date:" not in meth and "day before yesterday" not in meth
disc=(ROOT/"paper"/"discussion.md").read_text()
assert "Run date:" not in disc and "run date:" not in disc and "day before yesterday" not in disc
assert "with no separate bucket for disputed cases" in disc
print("verified methods/discussion have zero run-date copies")
draft=(ROOT/"paper"/"FINAL_DRAFT.md").read_text()
assert draft.count("Run date: 10 October 2026 (author-reported).")==1, f"need 1 Run date in draft, got {draft.count('Run date:')}"
assert "day before yesterday" not in draft
assert "Own judge" not in draft and "OWN_JUDGE" not in draft
assert draft.count("```text")==2, "need 2 fences in draft"
assert "unheard" not in draft.lower(), "unheard remnant in draft"
print("verified draft single Run date + 2 fences + no own-judge")
assert "was designed but not completed" not in disc
assert "In contrast, Luo et al. [33]" in disc
print("verified discussion contrast retained")

t2txt=(TABLES/"T2_pipeline.csv").read_text(encoding="utf-8")
assert "src/" not in t2txt and "kb_raw" not in t2txt and "notes/" not in t2txt
print("verified T2 clean")

oi=(ROOT/"notes"/"open_issues.md").read_text()
assert "## Remaining placeholders" in oi
for k in ["Authors:","Affiliations:","Corresponding author","Funding:","Data release link:","Venue"]:
    assert k in oi, f"placeholder missing {k}"
print("verified placeholders listed")

LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        if row[0].strip().startswith('V24-'): continue
        raw.append(row)
new=[
 ['V24-APDXC','Appendix C',"2 prompts monospace verbatim (third-model Satisfied + auto Auto-verdict); own-judge deleted as unused; single Run date",
  "THIRD STRICT vs check_satisfaction.py; AUTO STRICT vs src/evaluate.py; OWN deleted (no number uses src/judge RUBRIC); 2x ```text fences; Consolas/Courier in docx via add_code_block; draft has 1x Run date + 0 unheard + 0 day-before; numbers unchanged (T3/T16/T17/T18/grid identical)",
  'analysis/recompute_v24.py','analysis/assemble_draft.py + analysis/build_docx.py + check_satisfaction.py + src/evaluate.py','script+code'],
]
ids=[r[0] for r in raw]
anchor=ids.index('MAJ-ADJ')+1 if 'MAJ-ADJ' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+1 V24)")
