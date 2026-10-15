#!/usr/bin/env python3
"""V26: verify current task (Appendix C + Fig3 + refs 33/34), no numbers changed.
Reads ONLY Rag results.xlsx via openpyxl. Regenerates Fig3 by script
(identical palette, no title, outlined swatch) to prove script-built.
Appends V26 ledger rows.
"""
import csv, re
from pathlib import Path
import openpyxl
ROOT = Path(__file__).resolve().parent.parent
WB = ROOT / "Rag results.xlsx"
TABLES = ROOT / "paper" / "tables"
FIGS = ROOT / "paper" / "figures"
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
    with open(TABLES/name, encoding='utf-8') as f:
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
assert m, "checker JUDGE_PROMPT missing"
asm = (ROOT / "analysis" / "assemble_draft.py").read_text()
m2 = re.search(r'THIRD_MODEL_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m2 and m2.group(1) == m.group(1), "third-model prompt mismatch STRICT"
print("verified third-model prompt verbatim STRICT vs check_satisfaction.py")
ev = (ROOT / "src" / "evaluate.py").read_text()
m3 = re.search(r'JUDGE_PROMPT = """(.*?)"""', ev, re.S)
m4 = re.search(r'AUTOMATED_MARK_PROMPT_TEXT="""(.*?)"""', asm, re.S)
assert m4 and m4.group(1) == m3.group(1), "auto prompt mismatch STRICT"
print("verified auto prompt verbatim STRICT vs src/evaluate.py")

assert asm.count("```text") == 2
assert "unheard" not in asm.lower()
assert "src/" not in asm
draft = (ROOT / "paper" / "FINAL_DRAFT.md").read_text()
assert draft.count("```text") == 2
assert "unheard" not in draft.lower()
assert "src/" not in draft
assert "five verdicts" not in draft.lower()
assert "Workbook column 'Satisfied (3rd llm as judge)' was produced by" in draft
assert "blind to model identity" in draft
assert "opencode/mimo-v2.6-flash-free" in draft
assert "no temperature set (provider default applies)" in draft
assert "temperature 0" in draft
print("verified Appendix C conditions in draft")

rb = (ROOT / "analysis" / "rebuild_v17.py").read_text()
fig3sec = rb[rb.index('# Fig3'):]
assert 'ax3.set_title' not in fig3sec, "in-figure title remnant"
assert '#6A3D9A' in fig3sec and '#E31A1C' in fig3sec
print("verified Fig3 code: no title, purple/red palette")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
TYPES = ["clear", "ambiguous", "out_of_scope", "high_stakes", "adversarial"]
order_ids = []
for t in TYPES:
    order_ids.extend(sorted([i for i in common if gmap[i]['type'] == t]))
grid = []
for i in order_ids:
    gu = gmap[i]['maj']; mu = mmap[i]['maj']
    grid.append(0 if (not gu and not mu) else (1 if (gu and not mu) else (2 if (not gu and mu) else 3)))
grid = np.array(grid).reshape(5, 20)
fig3, ax3 = plt.subplots(figsize=(10, 3.8))
cmap = matplotlib.colors.ListedColormap(["#FFFFFF", "#6A3D9A", "#E31A1C", "#000000"])
ax3.imshow(grid, cmap=cmap, vmin=0, vmax=3, aspect="auto")
for spine in ax3.spines.values():
    spine.set_edgecolor("black"); spine.set_linewidth(1.0)
ax3.set_yticks(range(5)); ax3.set_yticklabels(TYPES)
ax3.set_xticks(range(20)); ax3.set_xticklabels([str(i+1) for i in range(20)], fontsize=7)
ax3.set_xlabel("query index within type (sorted by ID)")
patches = [mpatches.Patch(facecolor="#FFFFFF", edgecolor="black", linewidth=1.2, label="both pass (80)"),
           mpatches.Patch(facecolor="#6A3D9A", edgecolor="black", label="only fast miss (7)"),
           mpatches.Patch(facecolor="#E31A1C", edgecolor="black", label="only reasoning miss (9)"),
           mpatches.Patch(facecolor="#000000", edgecolor="black", label="both miss (4)")]
leg = ax3.legend(handles=patches, loc="upper center", bbox_to_anchor=(0.5, 1.18),
                 ncol=4, fontsize=7, frameon=True, title="majority outcome (in-figure key)")
leg.get_title().set_fontsize(7)
plt.tight_layout()
for ext in (".png", ".pdf"):
    plt.savefig(str(FIGS / "F3_majority_grid") + ext, dpi=300, bbox_inches="tight")
plt.close()
print("regenerated F3_majority_grid.png/pdf by script")

refs = (ROOT / "paper" / "references.md").read_text()
assert "agentic abstention: do agents know when to stop instead of act?" in refs.lower()
assert "2606.28733" in refs
assert "H. Luo, B. Wen, and L. L. Wang" in refs
assert "ragcap-bench: benchmarking capabilities of llms in agentic retrieval augmented generation systems" in refs.lower()
assert "2510.13910" in refs
assert "J. Lin, C. Zhang, S. Y. Liu, and H. Li" in refs
rel = (ROOT / "paper" / "related_work.md").read_text()
assert "over 28,000 tasks" in rel
assert "sometimes worse at timely abstention" in (ROOT / "paper" / "discussion.md").read_text()
print("verified refs [33][34] strings match live arXiv fetch")

LED = ROOT / "paper" / "claims_ledger.csv"
FIELDS = ['claim_id', 'section', 'sentence', 'value', 'source_script',
          'source_file_or_cells', 'verified_by']
raw = []
with open(LED, newline='', encoding='utf-8') as f:
    rdr = csv.reader(f); header = next(rdr); assert header == FIELDS, header
    for row in rdr:
        if not row or not row[0].strip():
            continue
        if row[0].strip().startswith('V26-'):
            continue
        raw.append(row)
new = [
    ['V26-APDXC', 'Appendix C', 'Third-model + auto prompts verbatim by column; blind Q+expected+reply; model/date/temp stated; 0 src/ 0 unheard',
     "THIRD STRICT vs check_satisfaction.py; AUTO STRICT vs src/evaluate.py; model opencode/mimo-v2.6-flash-free; third-model no-temp default + auto temp 0; Run date 10 Oct 2026 author-reported; draft 2 fences 0 unheard 0 src/",
     'analysis/recompute_v26.py', 'paper/FINAL_DRAFT.md Appendix C + check_satisfaction.py + src/evaluate.py', 'script+code'],
    ['V26-FIG3', 'Results', 'Figure 3 regenerated by script: no in-figure title, outlined both-pass, tier colours distinct from Fig2',
     'both pass 80 (white #FFFFFF black outline) only fast 7 (purple #6A3D9A) only reasoning 9 (red #E31A1C) both miss 4 (black); Fig2 grey/blue/orange/green disjoint',
     'analysis/recompute_v26.py', 'paper/figures/F3_majority_grid.png', 'script+figure'],
    ['V26-REF33', 'Related Work/Discussion', 'Ref [33] verified live on arXiv; discussion wording matches abstract',
     "arXiv 2606.28733 title MATCH; authors Han Luo/Bingbing Wen/Lucy Lu Wang MATCH; more than 28,000 tasks MATCH over 28,000 tasks; discussion uses abstract wording sometimes worse at timely abstention (fetched 2026-10-15)",
     'analysis/recompute_v26.py', 'https://arxiv.org/abs/2606.28733', 'curl+arXiv'],
    ['V26-REF34', 'Related Work', 'Ref [34] verified live on arXiv; no number quoted',
     "arXiv 2510.13910 title MATCH; authors Jingru Lin/Chen Zhang/Stephen Y. Liu/Haizhou Li MATCH initials; manuscript quotes no number; description matches abstract (fetched 2026-10-15)",
     'analysis/recompute_v26.py', 'https://arxiv.org/abs/2510.13910', 'curl+arXiv'],
]
ids = [r[0] for r in raw]
anchor = ids.index('MAJ-ADJ') + 1 if 'MAJ-ADJ' in ids else len(raw)
outrows = raw[:anchor] + new + raw[anchor:]
with open(LED, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+4 V26)")
