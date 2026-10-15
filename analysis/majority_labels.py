#!/usr/bin/env python3
"""2-of-3 majority primary labels (author + classmate + third-LLM).

Author = `satisfied`, Classmate = `Satisfied (Friend)`, Third-LLM = `Satisfied (3rd llm as judge)`.
Majority miss = >=2 of 3 flag (!= yes). Auto verdict is NOT part of majority; reported separately.
Outputs:
  paper/tables/T15_majority.csv (overall + by-type majority with Wilson)
  paper/tables/T16_fleiss.csv (Fleiss kappa 3-rater + pairwise Cohen/Gwet for reference)
  paper/tables/T17_majority_reasons.csv (reason counts under majority)
  paper/figures/F2b_rater_panel.{png,pdf} (per-type-by-rater, replaces old Fig2)
  paper/figures/F6_agree_panel.{png,pdf} (single agreement panel, replaces Figs 6-7)
Ledger: replaces HEAD-SENS/SENS-*/ROBUST-*/CONTEST-*/ADV/T3-*/T4-* majority-overlapping rows? No:
  keeps T3/T4/T5/T8 (author-locked) for audit trail, ADDS MAJ-* rows as new primary.
  Actually per task, majority IS primary, so MAJ-* marked primary; old rows kept but demoted.
  To avoid contradiction, ledger marks old HEAD-SENS etc as superseded (removed) and adds MAJ-*.
Deterministic, no new experiments. All from Rag results.xlsx.
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
def autopass(v): return str(v).strip().lower() in ('correct','appropriate_abstain')
def wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0,0.0)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n)
    m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return (p,max(0.0,(c-m)/d),min(1.0,(c+m)/d))
def binom_pmf(k,n,p=0.5): return math.comb(n,k)*(p**k)*((1-p)**(n-k))
def mcnemar_exact(b,c):
    n=b+c
    if n==0: return 1.0
    k=min(b,c)
    return min(1.0,2*sum(binom_pmf(i,n) for i in range(k+1)))
def holm(pvals):
    m=len(pvals); order=sorted(range(m),key=lambda i:pvals[i]); adj=[0.0]*m
    for rank,i in enumerate(order): adj[i]=min(1.0,(m-rank)*pvals[i])
    for r in range(1,m):
        i=order[r]; j=order[r-1]; adj[i]=max(adj[i],adj[j])
    return adj
def cohen_gwet(a,b):
    n=len(a); pa=sum(1 for x,y in zip(a,b) if x==y)/n
    p1=sum(a)/n; p2=sum(b)/n
    pe_k=p1*p2+(1-p1)*(1-p2)
    k=(pa-pe_k)/(1-pe_k) if pe_k!=1 else 0.0
    pi=(p1+p2)/2; pe_g=2*pi*(1-pi)
    ac1=(pa-pe_g)/(1-pe_g) if pe_g!=1 else 0.0
    return pa,k,ac1
def fleiss_3raters(mat):
    """mat: list of [n_yes, n_no] per subject, 3 raters. Returns Fleiss kappa."""
    n=len(mat); k=2; m=3
    # P_i
    Pi=[]
    for nyes,nno in mat:
        Pi.append(((nyes**2+nno**2)-m)/(m*(m-1)))
    Pbar=sum(Pi)/n
    # p_j
    p_yes=sum(r[0] for r in mat)/(n*m)
    p_no=1-p_yes
    Pe=p_yes**2+p_no**2
    return (Pbar-Pe)/(1-Pe) if Pe!=1 else 0.0
def norm_reason(v):
    s=str(v).strip()
    if s.lower()=='yes': return None
    m=re.search(r'no\s*[-–—:]+\s*(.+)',s,re.I)
    if not m: return s
    r=m.group(1).strip().lower()
    mp={'overreach':'Overreach','unsupported assumption':'Unsupported Assumption','oversharing':'Oversharing','soft refusal':'Soft Refusal','failure to answer':'Failure to Answer'}
    return mp.get(r, m.group(1).strip())

wb=openpyxl.load_workbook(WB,data_only=True)
data={}
for sheet in ['glm','muse']:
    ws=wb[sheet]
    hdr=[c.value for c in ws[1]]
    idx={h:i+1 for i,h in enumerate(hdr) if h}
    rows=[]
    for r in range(2,ws.max_row+1):
        a=ws.cell(r,idx['satisfied']).value
        t3=ws.cell(r,idx[C3]).value
        fr=ws.cell(r,idx[CF]).value
        auto=ws.cell(r,idx['Auto verdict (fill it)']).value
        miss=sum([is_miss(a),is_miss(t3),is_miss(fr)])
        maj=miss>=2
        # majority reason: author if author flagged and in majority, else third if third flagged, else friend
        if maj:
            if is_miss(a): reason=norm_reason(a)
            elif is_miss(t3): reason=norm_reason(t3)
            else: reason=norm_reason(fr)
        else: reason=None
        rows.append({'id':ws.cell(r,idx['ID']).value,'type':ws.cell(r,idx['Type']).value,
                     'author_miss':is_miss(a),'third_miss':is_miss(t3),'friend_miss':is_miss(fr),
                     'maj':maj,'reason':reason,'auto_fail':not autopass(auto),
                     'author_raw':a,'third_raw':t3,'friend_raw':fr,'auto_raw':auto})
    data[sheet]=rows

# T15 majority overall + by-type with Wilson
t15=[]
for sheet in ['glm','muse']:
    for scope in ['overall']+TYPES:
        sub=data[sheet] if scope=='overall' else [x for x in data[sheet] if x['type']==scope]
        n=len(sub); k=sum(1 for x in sub if x['maj'])
        p,lo,hi=wilson(k,n)
        # also per-source for panel
        ka=sum(1 for x in sub if x['author_miss'])
        k3=sum(1 for x in sub if x['third_miss'])
        kf=sum(1 for x in sub if x['friend_miss'])
        t15.append({'model_sheet':sheet,'scope':scope,'n':n,'maj_miss':k,'maj_prop':round(p,4),
                    'wilson_lo':round(lo,4),'wilson_hi':round(hi,4),
                    'author_miss':ka,'third_miss':k3,'friend_miss':kf})
with open(TABLES/"T15_majority.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['model_sheet','scope','n','maj_miss','maj_prop','wilson_lo','wilson_hi','author_miss','third_miss','friend_miss'])
    w.writeheader(); w.writerows(t15)
print("wrote T15")
for r in t15: print(r)

# McNemar on majority
gmap={x['id']:x for x in data['glm']}; mmap={x['id']:x for x in data['muse']}
common=sorted(set(gmap)&set(mmap))
def disc(ids):
    b=sum(1 for i in ids if gmap[i]['maj'] and not mmap[i]['maj'])
    c=sum(1 for i in ids if not gmap[i]['maj'] and mmap[i]['maj'])
    return b,c
scopes=['overall']+TYPES
mcn=[]
praw=[]
for s in scopes:
    ids=common if s=='overall' else [i for i in common if gmap[i]['type']==s]
    b,c=disc(ids); p=mcnemar_exact(b,c)
    mcn.append((s,len(ids),b,c,p)); praw.append(p)
padj=holm(praw)
with open(TABLES/"T15_mcnemar_maj.csv","w",newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['scope','n_pairs','b_glmFail_museOk','c_glmOk_museFail','p_exact','p_holm'])
    for (s,n,b,c,p),pa in zip(mcn,padj):
        w.writerow([s,n,b,c,f"{p:.4f}",f"{pa:.4f}"])
print("mcnemar majority:",mcn,padj)

# Fleiss by type + overall per model + pairwise for reference
t16=[]
for sheet in ['glm','muse']:
    for scope in ['overall']+TYPES:
        sub=data[sheet] if scope=='overall' else [x for x in data[sheet] if x['type']==scope]
        # fleiss mat: per query [n_yes, n_no] where yes=pass
        mat=[]
        a=[]; t=[]; fr=[]
        for x in sub:
            nyes=sum([not x['author_miss'],not x['third_miss'],not x['friend_miss']])
            mat.append((nyes,3-nyes))
            a.append(not x['author_miss']); t.append(not x['third_miss']); fr.append(not x['friend_miss'])
        fk=fleiss_3raters(mat)
        pa12,k12,ac12=cohen_gwet(a,t)
        pa13,k13,ac13=cohen_gwet(a,fr)
        pa23,k23,ac23=cohen_gwet(t,fr)
        t16.append({'model_sheet':sheet,'scope':scope,'n':len(sub),'fleiss_kappa':round(fk,4),
                    'pair_author_third_k':round(k12,4),'pair_author_friend_k':round(k13,4),'pair_third_friend_k':round(ac23,4) if False else round(k23,4),
                    'agree_all3':sum(1 for x in sub if (x['author_miss']==x['third_miss']==x['friend_miss'])),
                    'maj_miss':sum(1 for x in sub if x['maj'])})
        # fix: store third-friend kappa correctly
        t16[-1]['pair_third_friend_k']=round(k23,4)
        # also store AC1s? keep kappa only for brevity, AC1 in T13
with open(TABLES/"T16_fleiss.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['model_sheet','scope','n','fleiss_kappa','pair_author_third_k','pair_author_friend_k','pair_third_friend_k','agree_all3','maj_miss'])
    w.writeheader(); w.writerows(t16)
print("wrote T16")
for r in t16: print(r)

# T17 majority reasons
CAT_ORDER=["Overreach","Unsupported Assumption","Oversharing","Soft Refusal","Failure to Answer"]
t17=[]
for sheet in ['glm','muse']:
    sub=[x for x in data[sheet] if x['maj']]
    denom=len(sub)
    c=Counter(x['reason'] for x in sub)
    for code in CAT_ORDER:
        ids=sorted([x['id'] for x in sub if x['reason']==code])
        t17.append({'model_sheet':sheet,'category':code,'n':c.get(code,0),
                    'pct_of_maj':round(c.get(code,0)/denom,4) if denom else 0.0,
                    'query_ids':";".join(ids)})
with open(TABLES/"T17_majority_reasons.csv","w",newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['model_sheet','category','n','pct_of_maj','query_ids'])
    w.writeheader(); w.writerows(t17)
print("wrote T17")
for r in t17: print(r)
# majority IDs
for sheet in ['glm','muse']:
    print(sheet, "maj IDs:", sorted([x['id'] for x in data[sheet] if x['maj']]))

# Figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
GLM_C="#3776ab"; MUSE_C="#d55e00"
plt.rcParams.update({"font.size":9,"axes.unicode_minus":False})
def savefig(p):
    for ext in (".png",".pdf"): plt.savefig(str(p)+ext,dpi=300,bbox_inches="tight")
    plt.close(); print("saved",p.name)

# F2b rater panel: 2 subplots (fast, reasoning), x=type, 4 bars (author, third, classmate, majority)
order=TYPES
xlab=["clear","ambiguous","out-of-scope","high-stakes","adversarial"]
fig,ax=plt.subplots(1,2,figsize=(10,4.2),sharey=True)
for ai,sheet in enumerate(['glm','muse']):
    a=ax[ai]
    vals_author=[next(r['author_miss'] for r in t15 if r['model_sheet']==sheet and r['scope']==t) for t in order]
    vals_third=[next(r['third_miss'] for r in t15 if r['model_sheet']==sheet and r['scope']==t) for t in order]
    vals_friend=[next(r['friend_miss'] for r in t15 if r['model_sheet']==sheet and r['scope']==t) for t in order]
    vals_maj=[next(r['maj_miss'] for r in t15 if r['model_sheet']==sheet and r['scope']==t) for t in order]
    import numpy as np
    x=np.arange(len(order)); w=0.19
    a.bar(x-1.5*w,vals_author,w,label="author",color="#999999",edgecolor="black")
    a.bar(x-0.5*w,vals_third,w,label="third-LLM",color="#56B4E9",edgecolor="black")
    a.bar(x+0.5*w,vals_friend,w,label="classmate",color="#E69F00",edgecolor="black")
    a.bar(x+1.5*w,vals_maj,w,label="majority (2-of-3)",color=GLM_C if sheet=='glm' else MUSE_C,edgecolor="black")
    for i in range(len(order)):
        for j,v in enumerate([vals_author[i],vals_third[i],vals_friend[i],vals_maj[i]]):
            a.text(i+(j-1.5)*w,v+0.25,str(v),ha="center",fontsize=7)
    a.set_xticks(list(x)); a.set_xticklabels(xlab,rotation=14,fontsize=8)
    a.set_ylim(0,10.5)
    a.set_ylabel("misses (of 20)" if ai==0 else "")
    a.set_title("fast tier (majority 11/100)" if sheet=='glm' else "reasoning tier (majority 13/100)",fontsize=9)
    a.legend(fontsize=7,frameon=True)
plt.tight_layout()
savefig(FIGS/"F2b_rater_panel")

# F6 agree panel: single panel showing pairwise agree + Fleiss by type? Keep simple: grouped bars agree% + Fleiss points
# Two subplots? Single figure with 2 tiers, x=scope, bars=3 pairwise agrees, line=Fleiss? Use bars for agree, text for Fleiss.
import numpy as np
scopes6=['overall','clear','ambiguous','out_of_scope','high_stakes','adversarial']
xlab6=['all (100)','clear','ambiguous','out-of-scope','high-stakes','adversarial']
# recompute pairwise agree% from data
fig2,ax2=plt.subplots(1,2,figsize=(10,4.2),sharey=True)
for ai,sheet in enumerate(['glm','muse']):
    a=ax2[ai]
    # author-third, author-friend, third-friend agree counts
    agrees_at=[]; agrees_af=[]; agrees_tf=[]
    for s in scopes6:
        sub=data[sheet] if s=='overall' else [x for x in data[sheet] if x['type']==s]
        n=len(sub)
        at=sum(1 for x in sub if x['author_miss']==x['third_miss'])/n*100
        af=sum(1 for x in sub if x['author_miss']==x['friend_miss'])/n*100
        tf=sum(1 for x in sub if x['third_miss']==x['friend_miss'])/n*100
        agrees_at.append(at); agrees_af.append(af); agrees_tf.append(tf)
    x=np.arange(len(scopes6)); w=0.25
    a.bar(x-w,agrees_at,w,label="author vs third",color="#999999",edgecolor="black")
    a.bar(x,agrees_af,w,label="author vs classmate",color="#E69F00",edgecolor="black")
    a.bar(x+w,agrees_tf,w,label="third vs classmate",color="#009E73",edgecolor="black")
    # Fleiss text on top
    for i,s in enumerate(scopes6):
        fk=next(r['fleiss_kappa'] for r in t16 if r['model_sheet']==sheet and r['scope']==s)
        a.text(i,101.5,f"kF {fk:.2f}",ha="center",fontsize=6.5)
    a.set_xticks(list(x)); a.set_xticklabels(xlab6,rotation=16,fontsize=7)
    a.set_ylim(40,108)
    a.set_ylabel("agreement %")
    a.set_title("fast tier" if sheet=='glm' else "reasoning tier",fontsize=9)
    a.legend(fontsize=7)
plt.tight_layout()
savefig(FIGS/"F6_agree_panel")

# Ledger update: remove superseded HEAD-SENS/SENS-*/ROBUST-*/CONTEST-*, add MAJ-*
LED=ROOT/"paper"/"claims_ledger.csv"
FIELDS=['claim_id','section','sentence','value','source_script','source_file_or_cells','verified_by']
raw=[]
with open(LED,newline='',encoding='utf-8') as f:
    rdr=csv.reader(f); header=next(rdr); assert header==FIELDS,header
    for row in rdr:
        if not row or not row[0].strip(): continue
        cid=row[0].strip()
        if cid.startswith('SENS-') or cid.startswith('ROBUST-') or cid.startswith('CONTEST-') or cid.startswith('HEAD-SENS'):
            continue
        raw.append(row)
def getm(sheet,scope):
    return [r for r in t15 if r['model_sheet']==sheet and r['scope']==scope][0]
def getf(sheet,scope):
    return [r for r in t16 if r['model_sheet']==sheet and r['scope']==scope][0]
gm=getm('glm','overall'); mm=getm('muse','overall')
gm_adv=getm('glm','adversarial'); mm_adv=getm('muse','adversarial')
gm_amb=getm('glm','ambiguous'); mm_amb=getm('muse','ambiguous')
new=[
 ['MAJ-HEAD','Abstract/Results','Primary 2-of-3 majority misses (author+classmate+third-LLM)',
  f"fast {gm['maj_miss']}/100={gm['maj_prop']:.1%} (CI {gm['wilson_lo']:.1%}-{gm['wilson_hi']:.1%}); reasoning {mm['maj_miss']}/100={mm['maj_prop']:.1%} (CI {mm['wilson_lo']:.1%}-{mm['wilson_hi']:.1%}); McNemar majority overall b={mcn[0][2]} c={mcn[0][3]} p={mcn[0][4]:.2f}",
  'analysis/majority_labels.py','paper/tables/T15_majority.csv+T15_mcnemar_maj.csv+Rag results.xlsx','script+workbook'],
 ['MAJ-GLM','Results','Fast-tier majority by scope (majority/author/third/classmate of n)',
  f"clear {getm('glm','clear')['maj_miss']}/{getm('glm','clear')['author_miss']}/{getm('glm','clear')['third_miss']}/{getm('glm','clear')['friend_miss']}; amb {gm_amb['maj_miss']}/{gm_amb['author_miss']}/{gm_amb['third_miss']}/{gm_amb['friend_miss']}; oos {getm('glm','out_of_scope')['maj_miss']}/{getm('glm','out_of_scope')['author_miss']}/{getm('glm','out_of_scope')['third_miss']}/{getm('glm','out_of_scope')['friend_miss']}; high {getm('glm','high_stakes')['maj_miss']}/{getm('glm','high_stakes')['author_miss']}/{getm('glm','high_stakes')['third_miss']}/{getm('glm','high_stakes')['friend_miss']}; adv {gm_adv['maj_miss']}/{gm_adv['author_miss']}/{gm_adv['third_miss']}/{gm_adv['friend_miss']} (n=20 each)",
  'analysis/majority_labels.py','paper/tables/T15_majority.csv','script+workbook'],
 ['MAJ-MUSE','Results','Reasoning-tier majority by scope (majority/author/third/classmate of n)',
  f"clear {getm('muse','clear')['maj_miss']}/{getm('muse','clear')['author_miss']}/{getm('muse','clear')['third_miss']}/{getm('muse','clear')['friend_miss']}; amb {mm_amb['maj_miss']}/{mm_amb['author_miss']}/{mm_amb['third_miss']}/{mm_amb['friend_miss']}; oos {getm('muse','out_of_scope')['maj_miss']}/{getm('muse','out_of_scope')['author_miss']}/{getm('muse','out_of_scope')['third_miss']}/{getm('muse','out_of_scope')['friend_miss']}; high {getm('muse','high_stakes')['maj_miss']}/{getm('muse','high_stakes')['author_miss']}/{getm('muse','high_stakes')['third_miss']}/{getm('muse','high_stakes')['friend_miss']}; adv {mm_adv['maj_miss']}/{mm_adv['author_miss']}/{mm_adv['third_miss']}/{mm_adv['friend_miss']} (n=20 each)",
  'analysis/majority_labels.py','paper/tables/T15_majority.csv','script+workbook'],
 ['MAJ-MCN','Results','McNemar on majority labels (paired fast vs reasoning)',
  f"overall b={mcn[0][2]} c={mcn[0][3]} p={mcn[0][4]:.4f} Holm {padj[0]:.4f}; "+" ".join([f"{s} b={b} c={c} p={p:.4f}" for s,n,b,c,p in mcn[1:]]),
  'analysis/majority_labels.py','paper/tables/T15_mcnemar_maj.csv','script+workbook'],
 ['MAJ-FLEISS','Results','Fleiss kappa 3-rater (author/third/classmate) by scope',
  f"fast overall {getf('glm','overall')['fleiss_kappa']:.2f} ("+" ".join([f"{s} {getf('glm',s)['fleiss_kappa']:.2f}" for s in TYPES])+"); reasoning overall "+f"{getf('muse','overall')['fleiss_kappa']:.2f} ("+" ".join([f"{s} {getf('muse',s)['fleiss_kappa']:.2f}" for s in TYPES])+")",
  'analysis/majority_labels.py','paper/tables/T16_fleiss.csv','script+workbook'],
 ['MAJ-REASON-GLM','Results','Majority reason counts fast tier (11 misses)',
  "; ".join([f"{r['category']} {r['n']}" for r in t17 if r['model_sheet']=='glm']),
  'analysis/majority_labels.py','paper/tables/T17_majority_reasons.csv','script+workbook'],
 ['MAJ-REASON-MUSE','Results','Majority reason counts reasoning tier (13 misses)',
  "; ".join([f"{r['category']} {r['n']}" for r in t17 if r['model_sheet']=='muse']),
  'analysis/majority_labels.py','paper/tables/T17_majority_reasons.csv','script+workbook'],
 ['MAJ-IDS-GLM','Results','Fast-tier majority IDs (11)',
  ", ".join(sorted([x['id'] for x in data['glm'] if x['maj']])),
  'analysis/majority_labels.py','Rag results.xlsx glm author/third/classmate','script+workbook'],
 ['MAJ-IDS-MUSE','Results','Reasoning-tier majority IDs (13)',
  ", ".join(sorted([x['id'] for x in data['muse'] if x['maj']])),
  'analysis/majority_labels.py','Rag results.xlsx muse author/third/classmate','script+workbook'],
]
ids=[r[0] for r in raw]
anchor=ids.index('T7')+1 if 'T7' in ids else len(raw)
outrows=raw[:anchor]+new+raw[anchor:]
with open(LED,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(FIELDS); w.writerows(outrows)
print(f"ledger now {len(outrows)} rows")
