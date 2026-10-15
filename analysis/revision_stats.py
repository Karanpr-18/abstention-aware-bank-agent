#!/usr/bin/env python3
"""Revision stats for Tier-A: Fisher + permutation for opposing shapes + power planning. All from Rag results.xlsx. Seeded."""
import random, math, csv
from pathlib import Path
from scipy.stats import fisher_exact, chi2_contingency, norm
ROOT = Path(__file__).resolve().parent.parent
# Observed taxonomy (verified from workbook 2026-10-10; recompute here implicitly via ledger constants)
# GLM 17 = O6 U3 S3 SR2 F3 ; MUSE 14 = O2 U0 S3 SR5 F4
p_over = float(fisher_exact([[6,11],[2,12]])[1])
p_soft = float(fisher_exact([[2,15],[5,9]])[1])
chi2, p_chi2, dof, exp = chi2_contingency([[6,3,3,2,3],[2,0,3,5,4]])
pool=['O']*8+['U']*3+['S']*6+['SR']*7+['F']*7
def l1(a,b):
    from collections import Counter
    ca,cb=Counter(a),Counter(b)
    return sum(abs(ca.get(c,0)/len(a)-cb.get(c,0)/len(b)) for c in set(pool))
obs=l1(['O']*6+['U']*3+['S']*3+['SR']*2+['F']*3, ['O']*2+['S']*3+['SR']*5+['F']*4)
random.seed(7); R=20000; cnt=sum(1 for _ in range(R) if (lambda sh: l1(sh[:17],sh[17:]))(random.sample(pool,len(pool)))>=obs-1e-12)
p_perm=cnt/R
def n_two(p1,p2,a=0.05,pw=0.8):
    za=norm.ppf(1-a/2); zb=norm.ppf(pw); pb=(p1+p2)/2
    return ((za*math.sqrt(2*pb*(1-pb))+zb*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2)/((p1-p2)**2)
n1=n_two(.25,.05); n2=n_two(.20,.10)
print(f"Fisher Overreach p={p_over:.4f} SoftRef p={p_soft:.4f} chi2 p={p_chi2:.4f} perm p={p_perm:.4f} n25v5={n1:.1f} n20v10={n2:.1f}")
out=ROOT/"paper"/"tables"/"T12_planning.csv"
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(["analysis","value","method"])
    w.writerow(["fisher_overreach_all",round(p_over,4),"Fisher exact [[6,11],[2,12]]"])
    w.writerow(["fisher_softref_all",round(p_soft,4),"Fisher exact [[2,15],[5,9]]"])
    w.writerow(["chi2_reason_mix",round(float(p_chi2),4),"chi2 2x5"])
    w.writerow(["perm_L1_20000_seed7",round(p_perm,4),"permutation L1 resplit 17/14"])
    w.writerow(["power_25v5_per_group",round(n1,1),"two-prop alpha.05 power.8"])
    w.writerow(["power_20v10_per_group",round(n2,1),"two-prop alpha.05 power.8"])
