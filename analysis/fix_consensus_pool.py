#!/usr/bin/env python3
"""Fix (1)-(5): consensus reasons + mixed, pooled Fleiss, Table7, unanimous, Fig3 majority.
All from Rag results.xlsx. Deterministic. No new experiments.
Outputs:
  paper/tables/T17_majority_reasons.csv (OVERWRITTEN: consensus + Mixed)
  paper/tables/T16_pooled.csv (NEW: pooled Fleiss + pct agree + AC1 by type)
  paper/tables/T18_unanimous.csv (NEW: unanimous sets)
  paper/figures/F3_majority_grid.png/pdf (NEW: Figure 3 on majority labels)
  paper/figures/F8_tax_maj.png/pdf (OVERWRITTEN: consensus taxonomy)
Ledger: replaces MAJ-REASON-*, MAJ-FLEISS values kept but adds MAJ-CONS-*, MAJ-POOL-*, MAJ-UNAN-*, MAJ-FIG3.
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
CATS = ["Overreach","Unsupported Assumption","Oversharing","Soft Refusal","Failure to Answer","Mixed"]
def is_miss(v): return str(v).strip().lower()!='yes'
def norm_reason(v):
    s=str(v).strip()
    if s.lower()=='yes': return None
    m=re.search(r'no\s*[-–—:]+\s*(.+)',s,re.I)
    if not m: return s
    r=m.group(1).strip().lower()
    mp={'overreach':'Overreach','unsupported assumption':'Unsupported Assumption','oversharing':'Oversharing','soft refusal':'Soft Refusal','failure to answer':'Failure to Answer'}
    return mp.get(r, m.group(1).strip())
def fleiss_3(mat):
    n=len(mat); m=3
    Pi=[((a**2+b**2)-m)/(m*(m-1)) for a,b in mat]
    Pbar=sum(Pi)/n
    p_yes=sum(a for a,b in mat)/(n*m)
    Pe=p_yes**2+(1-p_yes)**2
    return (Pbar-Pe)/(1-Pe) if Pe!=1 else 0.0
def pairwise_metrics(a,b):
    n=len(a); pa=sum(1 for x,y in zip(a,b) if x==y)/n
    p1=sum(a)/n; p2=sum(b)/n
    pe_k=p1*p2+(1-p1)*(1-p2); k=(pa-pe_k)/(1-pe_k) if pe_k!=1 else 0.0
    pi=(p1+p2)/2; pe_g=2*pi*(1-pi); ac1=(pa-pe_g)/(1-pe_g) if pe_g!=1 else 0.0
    return pa,k,ac1
wb=openpyxl.load_workbook(WB,data_only=True)
data={}
for sheet in ['glm','muse']:
    ws=wb[sheet]; hdr=[c.value for c in ws[1]]; idx={h:i+1 for i,h in enumerate(hdr) if h}
    rows=[]
    for r in range(2,ws.max_row+1):
        a=ws.cell(r,idx['satisfied']).value; t3=ws.cell(r,idx[C3]).value; fr=ws.cell(r,idx[CF]).value
        ra=norm_reason(a) if is_miss(a) else None
        rt=norm_reason(t3) if is_miss(t3) else None
        rf=norm_reason(fr) if is_miss(fr) else None
        miss=sum([is_miss(a),is_miss(t3),is_miss(fr)])
        maj=miss>=2
        unan=(miss==3)
        if maj:
            c=Counter([x for x in [ra,rt,rf] if x])
            cons=[k for k,v in c.items() if v>=2]
            consensus=cons[0] if cons else "Mixed"
        else:
            consensus=None
        rows.append({'id':ws.cell(r,idx['ID']).value,'type':str(ws.cell(r,idx['Type']).value),
                     'author_miss':is_miss(a),'third_miss':is_miss(t3),'friend_miss':is_miss(fr),
                     'ra':ra,'rt':rt,'rf':rf,'maj':maj,'unan':unan,'consensus':consensus})
    data[sheet]=rows
# (1) T17 consensus overwrite
t17=[]
for sheet in ['glm','muse']:
    sub=[x for x in data[sheet] if x['maj']]
    denom=len(sub)
    c=Counter(x['consensus'] for x in sub)
    for cat in CATS:
        ids=sorted([x['id'] for x in sub if x['consensus']==cat])
        t17.append({'model_sheet':sheet,'category':cat,'n':c.get(cat,0),
                    'pct_of_maj':round(c.get(cat,0)/denom,4) if denom else 0.0,
                    'query_ids':";".join(ids)})
with open(TABLES/"T17_majority_reasons.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['model_sheet','category','n','pct_of_maj','query_ids'])
    w.writeheader(); w.writerows(t17)
print("wrote T17 consensus")
for r in t17: print(r)
# unanimous
t18=[]
for sheet in ['glm','muse']:
    un=[x for x in data[sheet] if x['unan']]
    # consensus among unanimous
    c=Counter(x['consensus'] for x in un)
    t18.append({'model_sheet':sheet,'n_unanimous':len(un),
                'ids':";".join(sorted(x['id'] for x in un)),
                'consensus_breakdown':"; ".join(f"{k} {v}" for k,v in sorted(c.items()))})
with open(TABLES/"T18_unanimous.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['model_sheet','n_unanimous','ids','consensus_breakdown'])
    w.writeheader(); w.writerows(t18)
print("wrote T18")
for r in t18: print(r)
# (2) pooled Fleiss + pct + AC1
pooled=[]
for scope in ['overall']+TYPES:
    A=[];T=[];F=[]; mat=[]
    maj_fast=0; maj_muse=0; n_fast=0; n_muse=0
    for sheet in ['glm','muse']:
        sub=data[sheet] if scope=='overall' else [x for x in data[sheet] if x['type']==scope]
        for x in sub:
            A.append(not x['author_miss']); T.append(not x['third_miss']); F.append(not x['friend_miss'])
            nyes=sum([not x['author_miss'],not x['third_miss'],not x['friend_miss']])
            mat.append((nyes,3-nyes))
        if sheet=='glm':
            maj_fast=sum(1 for x in sub if x['maj']); n_fast=len(sub)
        else:
            maj_muse=sum(1 for x in sub if x['maj']); n_muse=len(sub)
    fk=fleiss_3(mat)
    all3=sum(1 for a,b in mat if a in (0,3))
    pa_at,k_at,ac_at=pairwise_metrics(A,T)
    pa_af,k_af,ac_af=pairwise_metrics(A,F)
    pa_tf,k_tf,ac_tf=pairwise_metrics(T,F)
    pooled.append({'scope':scope,'n':len(mat),'fleiss_kappa':round(fk,4),
                   'all3_agree':all3,'all3_prop':round(all3/len(mat),4),
                   'maj_fast':maj_fast,'maj_muse':maj_muse,
                   'at_agree':round(pa_at,4),'at_k':round(k_at,4),'at_ac1':round(ac_at,4),
                   'af_agree':round(pa_af,4),'af_k':round(k_af,4),'af_ac1':round(ac_af,4),
                   'tf_agree':round(pa_tf,4),'tf_k':round(k_tf,4),'tf_ac1':round(ac_tf,4)})
with open(TABLES/"T16_pooled.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['scope','n','fleiss_kappa','all3_agree','all3_prop','maj_fast','maj_muse','at_agree','at_k','at_ac1','af_agree','af_k','af_ac1','tf_agree','tf_k','tf_ac1'])
    w.writeheader(); w.writerows(pooled)
print("wrote T16_pooled")
for r in pooled: print(r)
# (5) Fig3 majority grid data
gmap={x['id']:x for x in data['glm']}; mmap={x['id']:x for x in data['muse']}
common=sorted(set(gmap)&set(mmap))
both_pass=sum(1 for i in common if not gmap[i]['maj'] and not mmap[i]['maj'])
only_fast=sum(1 for i in common if gmap[i]['maj'] and not mmap[i]['maj'])
only_muse=sum(1 for i in common if not gmap[i]['maj'] and mmap[i]['maj'])
both_fail=sum(1 for i in common if gmap[i]['maj'] and mmap[i]['maj'])
print(f"majority grid: both_pass {both_pass} only_fast {only_fast} only_muse {only_muse} both_fail {both_fail}")
# grid order by type sorted ID
order=[]
for t in TYPES:
    ids=sorted([i for i in common if gmap[i]['type']==t])
    order.extend(ids)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
grid=[]
for i in order:
    gu=gmap[i]['maj']; mu=mmap[i]['maj']
    if not gu and not mu: grid.append(0)
    elif gu and not mu: grid.append(1)
    elif not gu and mu: grid.append(2)
    else: grid.append(3)
grid=np.array(grid).reshape(5,20)
plt.figure(figsize=(10,3.4))
cmap=matplotlib.colors.ListedColormap(["#f0f0f0","#3776ab","#d55e00","#333333"])
plt.imshow(grid,cmap=cmap,vmin=0,vmax=3,aspect="auto")
plt.yticks(range(5),TYPES)
plt.xticks(range(20),[f"{i+1}" for i in range(20)],fontsize=7)
plt.xlabel("query index within type (sorted by ID)")
plt.tight_layout()
for ext in (".png",".pdf"):
    plt.savefig(str(FIGS/"F3_majority_grid")+ext,dpi=300,bbox_inches="tight")
plt.close(); print("saved F3_majority_grid")
# F8_tax_maj overwrite with consensus
cats_plot=["Overreach","Unsupported Assumption","Oversharing","Soft Refusal","Failure to Answer","Mixed"]
def getn(sheet,cat):
    r=[x for x in t17 if x['model_sheet']==sheet and x['category']==cat][0]
    return r['n']
gv=[getn('glm',c) for c in cats_plot]; mv=[getn('muse',c) for c in cats_plot]
print("consensus plot counts fast",gv,"muse",mv)
plt.figure(figsize=(8,4.2))
cmap2=plt.get_cmap("tab10")
x=[0,1]; wdt=0.55
bottom_g=0; bottom_m=0
for k,c in enumerate(cats_plot):
    plt.bar([0],[gv[k]],wdt,bottom=[bottom_g],color=cmap2(k),edgecolor="black",label=f"{c} ({gv[k]}/{mv[k]})")
    plt.bar([1],[mv[k]],wdt,bottom=[bottom_m],color=cmap2(k),edgecolor="black")
    if gv[k]: plt.text(0,bottom_g+gv[k]/2,str(gv[k]),ha="center",va="center",fontsize=8)
    if mv[k]: plt.text(1,bottom_m+mv[k]/2,str(mv[k]),ha="center",va="center",fontsize=8)
    bottom_g+=gv[k]; bottom_m+=mv[k]
plt.xticks([0,1],["fast tier\n(n=11 majority), consensus+mixed","reasoning tier\n(n=13 majority), consensus+mixed"])
plt.ylabel("majority misses (consensus reason, Mixed = no two agree)")
plt.legend(fontsize=7,ncol=2)
plt.tight_layout()
for ext in (".png",".pdf"):
    plt.savefig(str(FIGS/"F8_tax_maj")+ext,dpi=300,bbox_inches="tight")
plt.close(); print("saved F8_tax_maj (consensus)")
# Ledger update
LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        cid=row[0].strip()
        if cid in ('MAJ-REASON-GLM','MAJ-REASON-MUSE','MAJ-FIG4'):
            continue
        raw.append(row)
# build new rows
def t17row(sheet,cat):
    r=[x for x in t17 if x['model_sheet']==sheet and x['category']==cat][0]
    return r
new=[
 ['MAJ-CONS-GLM','Results','Majority consensus reasons fast tier (11 misses: consensus >=2 same reason, else Mixed)',
  "; ".join(f"{c} {t17row('glm',c)['n']}" for c in cats_plot)+f" | Mixed IDs {t17row('glm','Mixed')['query_ids']}",
  'analysis/fix_consensus_pool.py','paper/tables/T17_majority_reasons.csv','script+workbook'],
 ['MAJ-CONS-MUSE','Results','Majority consensus reasons reasoning tier (13 misses)',
  "; ".join(f"{c} {t17row('muse',c)['n']}" for c in cats_plot)+f" | Mixed IDs {t17row('muse','Mixed')['query_ids']}",
  'analysis/fix_consensus_pool.py','paper/tables/T17_majority_reasons.csv','script+workbook'],
 ['MAJ-POOL','Results','Pooled Fleiss kappa 3-rater over both tiers (200 replies; 40 per type)',
  "; ".join(f"{r['scope']} k={r['fleiss_kappa']} all3 {r['all3_agree']}/{r['n']}" for r in pooled),
  'analysis/fix_consensus_pool.py','paper/tables/T16_pooled.csv','script+workbook'],
 ['MAJ-UNAN','Results','Unanimous sets (all three flag)',
  f"fast 3/100 ({';'.join(sorted(x['id'] for x in data['glm'] if x['unan']))}); reasoning 4/100 ({';'.join(sorted(x['id'] for x in data['muse'] if x['unan']))})",
  'analysis/fix_consensus_pool.py','paper/tables/T18_unanimous.csv','script+workbook'],
 ['MAJ-FIG3','Results','Figure 3 majority outcome grid (100 paired queries)',
  f"both pass {both_pass}; only fast {only_fast}; only reasoning {only_muse}; both fail {both_fail}",
  'analysis/fix_consensus_pool.py','paper/figures/F3_majority_grid.png','script+workbook'],
 ['MAJ-FIG4-CONS','Results','Figure 4 consensus taxonomy (Mixed = no two agree)',
  f"fast Mixed 7/11 consensus 4; reasoning Mixed 3/13 consensus 10",
  'analysis/fix_consensus_pool.py','paper/figures/F8_tax_maj.png + paper/tables/T17_majority_reasons.csv','script+workbook'],
]
ids=[r[0] for r in raw]
anchor=ids.index('MAJ-IDS-MUSE')+1 if 'MAJ-IDS-MUSE' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows")
