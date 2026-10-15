#!/usr/bin/env python3
"""V18 recompute: verify counts unchanged, redraw Fig3 (no in-figure title,
outlined both-pass swatch, tier colours distinct from Fig2 sources), log ref checks.
Reads ONLY Rag results.xlsx via openpyxl (structured cells). No CSV-comma splitting.
"""
import csv, math, re
from pathlib import Path
from collections import Counter
import openpyxl
ROOT = Path(__file__).resolve().parent.parent
WB = ROOT/"Rag results.xlsx"
TABLES = ROOT/"paper"/"tables"
FIGS = ROOT/"paper"/"figures"
TYPES = ["clear","ambiguous","out_of_scope","high_stakes","adversarial"]
C3 = 'Satisfied (3rd llm as judge)'
CF = 'Satisfied (Friend)'
def is_miss(v): return str(v).strip().lower()!='yes'
def norm_reason(v):
    import re as _re
    s=str(v).strip()
    if s.lower()=='yes': return None
    m=_re.search(r'no\s*[-–—:]+\s*(.+)', s, _re.I)
    if not m: return s
    r=m.group(1).strip().lower()
    mp={'overreach':'Overreach','unsupported assumption':'Unsupported Assumption','oversharing':'Oversharing','soft refusal':'Soft Refusal','failure to answer':'Failure to Answer'}
    return mp.get(r, m.group(1).strip())
def wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0,0.0)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return (p,max(0.0,(c-m)/d),min(1.0,(c+m)/d))
wb = openpyxl.load_workbook(WB, data_only=True)
data={}
for sheet in ['glm','muse']:
    ws=wb[sheet]
    hdr=[c.value for c in ws[1]]
    idx={h:i+1 for i,h in enumerate(hdr) if h}
    rows=[]
    for r in range(2, ws.max_row+1):
        a=ws.cell(r,idx['satisfied']).value; t3=ws.cell(r,idx[C3]).value; fr=ws.cell(r,idx[CF]).value
        ra=norm_reason(a) if is_miss(a) else None; rt=norm_reason(t3) if is_miss(t3) else None; rf=norm_reason(fr) if is_miss(fr) else None
        miss=sum([is_miss(a),is_miss(t3),is_miss(fr)]); maj=miss>=2
        rows.append({'id':ws.cell(r,idx['ID']).value,'type':str(ws.cell(r,idx['Type']).value),'maj':maj})
    data[sheet]=rows
    assert len(rows)==100
# verify T3_merged unchanged
def read_csv(name):
    with open(TABLES/name, encoding='utf-8') as f: return list(csv.DictReader(f))
t3=read_csv("T3_merged.csv")
exp={'overall':(11,13),'clear':(1,2),'ambiguous':(6,7),'out_of_scope':(0,1),'high_stakes':(2,2),'adversarial':(2,1)}
for r in t3:
    ef,em=exp[r['scope']]
    assert int(r['fast_miss'])==ef and int(r['muse_miss'])==em, (r,exp[r['scope']])
    print(f"verified T3 {r['scope']}: fast {r['fast_miss']} muse {r['muse_miss']} b={r['b']} c={r['c']} p={r['p_exact']}")
# verify T16 pooled Fleiss unchanged
t16=read_csv("T16_pooled.csv")
expF={'overall':0.3203,'clear':0.3905,'ambiguous':0.4665,'out_of_scope':0.1228,'high_stakes':0.1619,'adversarial':0.1}
for r in t16:
    assert abs(float(r['fleiss_kappa'])-expF[r['scope']])<1e-4, r
    print(f"verified T16 {r['scope']}: Fleiss {r['fleiss_kappa']} all3 {r['all3_agree']}/{r['n']}")
# verify T17 consensus + T18 unanimous unchanged
t17=read_csv("T17_majority_reasons.csv")
d17={(r['model_sheet'],r['category']):int(r['n']) for r in t17}
assert d17[('glm','Mixed')]==7 and d17[('glm','Failure to Answer')]==2 and d17[('glm','Overreach')]==1 and d17[('glm','Unsupported Assumption')]==1
assert d17[('muse','Failure to Answer')]==8 and d17[('muse','Mixed')]==3 and d17[('muse','Oversharing')]==1 and d17[('muse','Soft Refusal')]==1
print("verified T17 consensus")
t18=read_csv("T18_unanimous.csv")
assert {r['model_sheet']:int(r['n_unanimous']) for r in t18}=={'glm':3,'muse':4}
print("verified T18 unanimous 3+4")
# grid counts
gmap={x['id']:x for x in data['glm']}; mmap={x['id']:x for x in data['muse']}
common=sorted(set(gmap)&set(mmap))
bp=sum(1 for i in common if not gmap[i]['maj'] and not mmap[i]['maj'])
of=sum(1 for i in common if gmap[i]['maj'] and not mmap[i]['maj'])
om=sum(1 for i in common if not gmap[i]['maj'] and mmap[i]['maj'])
bf=sum(1 for i in common if gmap[i]['maj'] and mmap[i]['maj'])
assert (bp,of,om,bf)==(80,7,9,4), (bp,of,om,bf)
print(f"verified grid: both pass {bp} only fast {of} only muse {om} both fail {bf}")
# redraw Fig3 only: no in-figure title, outlined both-pass, tier colours distinct from Fig2 sources
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
order_ids=[]
for t in TYPES:
    order_ids.extend(sorted([i for i in common if gmap[i]['type']==t]))
grid=[]
for i in order_ids:
    gu=gmap[i]['maj']; mu=mmap[i]['maj']
    grid.append(0 if (not gu and not mu) else (1 if (gu and not mu) else (2 if (not gu and mu) else 3)))
grid=np.array(grid).reshape(5,20)
fig3,ax3=plt.subplots(figsize=(10,3.8))
cmap=matplotlib.colors.ListedColormap(["#FFFFFF","#6A3D9A","#E31A1C","#000000"])
ax3.imshow(grid,cmap=cmap,vmin=0,vmax=3,aspect="auto")
for spine in ax3.spines.values():
    spine.set_edgecolor("black"); spine.set_linewidth(1.0)
ax3.set_yticks(range(5)); ax3.set_yticklabels(TYPES)
ax3.set_xticks(range(20)); ax3.set_xticklabels([str(i+1) for i in range(20)],fontsize=7)
ax3.set_xlabel("query index within type (sorted by ID)")
patches=[mpatches.Patch(facecolor="#FFFFFF",edgecolor="black",linewidth=1.2,label="both pass (80)"),
  mpatches.Patch(facecolor="#6A3D9A",edgecolor="black",label="only fast miss (7)"),
  mpatches.Patch(facecolor="#E31A1C",edgecolor="black",label="only reasoning miss (9)"),
  mpatches.Patch(facecolor="#000000",edgecolor="black",label="both miss (4)")]
leg=ax3.legend(handles=patches,loc="upper center",bbox_to_anchor=(0.5,1.18),ncol=4,fontsize=7,frameon=True,title="majority outcome (in-figure key)")
leg.get_title().set_fontsize(7)
plt.tight_layout()
for ext in (".png",".pdf"):
    plt.savefig(str(FIGS/"F3_majority_grid")+ext,dpi=300,bbox_inches="tight")
plt.close(); print("saved F3_majority_grid (no title, outlined swatch, purple/red tiers)")
# verify no title text in figure object (we never called set_title)
print("Fig3 title removed: verified (no set_title call)")
# verify tier colours differ from Fig2 source colours
fig2cols={"#757575","#0072B2","#E69F00","#009E73"}
fig3cols={"#FFFFFF","#6A3D9A","#E31A1C","#000000"}
assert fig2cols.isdisjoint(fig3cols), (fig2cols,fig3cols)
print(f"colour disjoint verified: Fig2 {sorted(fig2cols)} vs Fig3 {sorted(fig3cols)}")
# ledger: add V18 rows
LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        cid=row[0].strip()
        if cid.startswith('V18-'): continue
        raw.append(row)
new=[
 ['V18-APDXC','Appendix C','Third-model prompt + coded run details from archived checker (verbatim match to checker file)',
  'model opencode/mimo-v2.6-flash-free; base http://localhost:8378/v1; max_tokens 150; timeout 240s x4; temperature unset (provider default); date unlogged (no execution log)',
  'analysis/recompute_v18.py','paper/FINAL_DRAFT.md Appendix C + check_satisfaction.py JUDGE_PROMPT','script+code'],
 ['V18-FIG3','Results','Figure 3 redrawn: no in-figure title, outlined both-pass swatch, tier colours distinct from Fig2 sources',
  'both pass 80 (white, black outline) only fast 7 (purple #6A3D9A) only muse 9 (red #E31A1C) both fail 4 (black); disjoint from Fig2 grey/blue/orange/green',
  'analysis/recompute_v18.py','paper/figures/F3_majority_grid.png','script+figure'],
 ['V18-REF33','Related Work','Agentic Abstention [33] verified on arXiv (authors/title/28k tasks)',
  'H. Luo et al. title match; >28,000 tasks verified; CONVOLVE 26.7->57.4 in abstract (not quoted in manuscript)',
  'analysis/recompute_v18.py','https://arxiv.org/abs/2606.28733 (fetched 2026-10-12)','webfetch'],
 ['V18-REF34','Related Work','RAGCap-Bench [34] verified on arXiv (authors/title; no number quoted)',
  'J. Lin et al. title match; v1 15 Oct 2025 v2 21 May 2026; manuscript quotes no number, description matches abstract',
  'analysis/recompute_v18.py','https://arxiv.org/abs/2510.13910 (fetched 2026-10-12)','webfetch'],
]
ids=[r[0] for r in raw]
anchor=ids.index('MAJ-ADJ')+1 if 'MAJ-ADJ' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows (+4 V18)")
