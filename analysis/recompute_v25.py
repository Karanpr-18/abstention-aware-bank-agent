#!/usr/bin/env python3
"""V25: frozen scope fixes for Appendix C / Fig3 / refs 33-34.
- Numbers recomputed from Rag results.xlsx, asserted identical.
- Prompts verbatim STRICT vs check_satisfaction.py and src/evaluate.py.
- Appendix C: 2 fences, no src/, no unheard, single run date.
- Fig3 code: no in-figure title, outlined both-pass swatch, tier colours
  distinct from Fig2 source colours; PNG regenerated.
- Refs 33/34 verified vs arXiv abs (authors/title/numbers); discussion
  contrast sentence fixed to abstract-supported wording.
"""
import csv, re
from pathlib import Path
import openpyxl
ROOT = Path(__file__).resolve().parent.parent
WB = ROOT / "Rag results.xlsx"
TABLES = ROOT / "paper" / "tables"
C3 = 'Satisfied (3rd llm as judge)'
CF = 'Satisfied (Friend)'
def is_miss(v): return str(v).strip().lower() != 'yes'
wb = openpyxl.load_workbook(WB, data_only=True)
data = {}
for sheet in ['glm', 'muse']:
    ws = wb[sheet]
    hdr = [c.value for c in ws[1]]
    idx = {h: i+1 for i, h in enumerate(hdr) if h}
    rows = []
    for r in range(2, ws.max_row+1):
        a = ws.cell(r, idx['satisfied']).value
        t3 = ws.cell(r, idx[C3]).value
        fr = ws.cell(r, idx[CF]).value
        miss = sum([is_miss(a), is_miss(t3), is_miss(fr)])
        rows.append({'id': ws.cell(r, idx['ID']).value,
                     'type': str(ws.cell(r, idx['Type']).value), 'maj': miss >= 2})
    data[sheet] = rows
    assert len(rows) == 100, (sheet, len(rows))
def read_csv(name):
    with open(TABLES / name, encoding='utf-8') as f:
        return list(csv.DictReader(f))
t3 = read_csv("T3_merged.csv")
exp = {'overall': (11, 13), 'clear': (1, 2), 'ambiguous': (6, 7),
       'out_of_scope': (0, 1), 'high_stakes': (2, 2), 'adversarial': (2, 1)}
for r in t3:
    ef, em = exp[r['scope']]
    assert int(r['fast_miss']) == ef and int(r['muse_miss']) == em, r
    print(f"verified T3 {r['scope']}: fast {r['fast_miss']} muse {r['muse_miss']}")
t16 = read_csv("T16_pooled.csv")
expF = {'overall': 0.3203, 'clear': 0.3905, 'ambiguous': 0.4665,
        'out_of_scope': 0.1228, 'high_stakes': 0.1619, 'adversarial': 0.1}
for r in t16:
    assert abs(float(r['fleiss_kappa']) - expF[r['scope']]) < 1e-4, r
    print(f"verified T16 {r['scope']}: Fleiss {r['fleiss_kappa']}")
t17 = read_csv("T17_majority_reasons.csv")
d17 = {(r['model_sheet'], r['category']): int(r['n']) for r in t17}
assert d17[('glm', 'Mixed')] == 7 and d17[('glm', 'Failure to Answer')] == 2
assert d17[('muse', 'Failure to Answer')] == 8 and d17[('muse', 'Mixed')] == 3
print("verified T17 consensus")
t18 = read_csv("T18_unanimous.csv")
assert {r['model_sheet']: int(r['n_unanimous']) for r in t18} == {'glm': 3, 'muse': 4}
print("verified T18 unanimous 3+4")
gmap = {x['id']: x for x in data['glm']}
mmap = {x['id']: x for x in data['muse']}
common = sorted(set(gmap) & set(mmap))
bp = sum(1 for i in common if not gmap[i]['maj'] and not mmap[i]['maj'])
of = sum(1 for i in common if gmap[i]['maj'] and not mmap[i]['maj'])
om = sum(1 for i in common if not gmap[i]['maj'] and mmap[i]['maj'])
bf = sum(1 for i in common if gmap[i]['maj'] and mmap[i]['maj'])
assert (bp, of, om, bf) == (80, 7, 9, 4), (bp, of, om, bf)
print(f"verified grid: {bp}/{of}/{om}/{bf}")
cs = (ROOT / "check_satisfaction.py").read_text()
m = re.search(r'JUDGE_PROMPT = """(.*?)"""', cs, re.S)
assert m, "checker prompt missing"
asm = (ROOT / "analysis" / "assemble_draft.py").read_text()
m2 = re.search(r'THIRD_MODEL_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m2 and m2.group(1) == m.group(1), "third-model prompt mismatch"
print("verified third-model prompt verbatim vs check_satisfaction.py")
ev = (ROOT / "src" / "evaluate.py").read_text()
m3 = re.search(r'JUDGE_PROMPT = """(.*?)"""', ev, re.S)
m4 = re.search(r'AUTOMATED_MARK_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m4 and m4.group(1) == m3.group(1), "auto prompt mismatch"
print("verified auto prompt verbatim vs src/evaluate.py")
assert asm.count("```text") == 2, "need 2 monospace fences"
assert "unheard" not in asm.lower(), "unheard remnant"
assert "src/" not in asm, "src/ remnant in assemble"
assert asm.count("Run date: 10 October 2026 (author-reported)") == 1, "run date count"
print("verified Appendix C structure (2 fences, no src/unheard, 1 run date)")
rb = (ROOT / "analysis" / "rebuild_v17.py").read_text()
fig3 = rb[rb.index("# Fig3"):rb.index("# Fig4")]
assert "ax3.set_title" not in fig3, "in-figure title remnant in Fig3 code"
assert 'facecolor="#FFFFFF",edgecolor="black"' in fig3 or 'facecolor="#FFFFFF", edgecolor' in fig3, "both-pass outline missing"
assert '"#6A3D9A"' in fig3 and '"#E31A1C"' in fig3, "tier colours missing"
assert '"#0072B2"' not in fig3 and '"#E69F00"' not in fig3 and '"#009E73"' not in fig3, "Fig3 reuses Fig2 source colours"
print("verified Fig3 code: no title, outlined swatch, distinct tier colours")
disc = (ROOT / "paper" / "discussion.md").read_text()
assert "reasoning improves timely abstention but lowers overall abstention recall" not in disc, "unverified contrast remnant"
assert "sometimes worse at timely abstention" in disc, "fixed contrast missing"
assert "In contrast, Luo et al. [33]" not in disc, "In-contrast framing remnant"
print("verified discussion [33] contrast fixed to abstract wording")
print("V25 checks PASS")
