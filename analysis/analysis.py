#!/usr/bin/env python3
"""Deterministic analysis for RAG abstention study (Phase A/C).
Reads ../Rag results.xlsx (root), writes paper/tables/*.csv.
Seeded, stdlib + openpyxl only. Run: .venv/bin/python -I analysis/analysis.py
"""
import csv, math
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
WB = ROOT / "Rag results.xlsx"
OUT = ROOT / "paper" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

TYPES = ["clear", "ambiguous", "out_of_scope", "high_stakes", "adversarial"]
POS = {"clarify", "abstain", "escalate", "refuse"}

def is_unsat(v):
    return str(v).strip().lower() != "yes"

def judge_pass(a):
    return str(a).strip().lower() in ("correct", "appropriate_abstain")

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, (c - m) / d), min(1.0, (c + m) / d))

def binom_pmf(k, n, p=0.5):
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))

def mcnemar_exact(b, c):
    """Two-sided exact McNemar; b=GLM fail/MUSE ok, c=GLM ok/MUSE fail."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(binom_pmf(i, n) for i in range(k + 1)))

def kappa_from(a_agree, b_dis1, c_dis2, d_agree):
    n = a_agree + b_dis1 + c_dis2 + d_agree
    if n == 0:
        return 0.0
    po = (a_agree + d_agree) / n
    pe = ((a_agree + b_dis1) * (a_agree + c_dis2) + (c_dis2 + d_agree) * (b_dis1 + d_agree)) / (n * n)
    return (po - pe) / (1 - pe) if pe != 1 else 0.0

def load():
    import openpyxl
    wb = openpyxl.load_workbook(WB, data_only=True)
    data = {}
    for name in wb.sheetnames:
        ws = wb[name]
        hdr = [c.value for c in ws[1]]
        idx = {h: i + 1 for i, h in enumerate(hdr)}
        rows = []
        for r in range(2, ws.max_row + 1):
            rows.append({
                "id": ws.cell(r, idx["ID"]).value,
                "type": ws.cell(r, idx["Type"]).value,
                "gold": str(ws.cell(r, idx["Expected answer (gold - researcher only)"]).value).strip().lower(),
                "abst": bool(ws.cell(r, idx["Abstained"]).value),
                "auto": str(ws.cell(r, idx["Auto verdict (fill it)"]).value).strip().lower(),
                "sat": ws.cell(r, idx["satisfied"]).value,
            })
        data[name] = rows
    return data

def main():
    data = load()
    names = sorted(data.keys())
    # T4: unsat by type with Wilson CI
    with open(OUT / "T4_by_type.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model_sheet", "type", "n", "unsat", "prop", "wilson_lo", "wilson_hi"])
        for name in names:
            rows = data[name]
            for t in TYPES:
                sub = [x for x in rows if x["type"] == t]
                k = sum(1 for x in sub if is_unsat(x["sat"]))
                p, lo, hi = wilson(k, len(sub))
                w.writerow([name, t, len(sub), k, f"{p:.4f}", f"{lo:.4f}", f"{hi:.4f}"])
            k = sum(1 for x in rows if is_unsat(x["sat"]))
            p, lo, hi = wilson(k, len(rows))
            w.writerow([name, "overall", len(rows), k, f"{p:.4f}", f"{lo:.4f}", f"{hi:.4f}"])
    # T5-ish confusion per model
    with open(OUT / "confusion.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model_sheet", "TP", "FP", "FN", "TN", "precision", "recall", "f1", "over_abstention"])
        for name in names:
            TP = FP = FN = TN = 0
            for x in data[name]:
                gp = x["gold"] in POS
                pa = x["abst"]
                if gp and pa: TP += 1
                elif not gp and pa: FP += 1
                elif gp and not pa: FN += 1
                else: TN += 1
            prec = TP / max(1, TP + FP)
            rec = TP / max(1, TP + FN)
            f1 = 2 * prec * rec / max(1e-9, prec + rec)
            w.writerow([name, TP, FP, FN, TN, f"{prec:.4f}", f"{rec:.4f}", f"{f1:.4f}", f"{FP/max(1,FP+TN):.4f}"])
    # McNemar paired (align by ID, order sheets as GLM vs MUSE)
    glm = {x["id"]: x for x in data[names[0]]}
    mse = {x["id"]: x for x in data[names[1]]}
    common = sorted(set(glm) & set(mse))
    with open(OUT / "T5_mcnemar.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scope", "n_pairs", "b_glmFail_museOk", "c_glmOk_museFail", "p_exact"])
        def disc(ids):
            b = sum(1 for i in ids if is_unsat(glm[i]["sat"]) and not is_unsat(mse[i]["sat"]))
            c = sum(1 for i in ids if not is_unsat(glm[i]["sat"]) and is_unsat(mse[i]["sat"]))
            return b, c
        b, c = disc(common)
        w.writerow(["overall", len(common), b, c, f"{mcnemar_exact(b, c):.4f}"])
        for t in TYPES:
            ids = [i for i in common if glm[i]["type"] == t]
            b, c = disc(ids)
            w.writerow([t, len(ids), b, c, f"{mcnemar_exact(b, c):.4f}"])
    # T8 judge vs human
    with open(OUT / "T8_judge_human.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model_sheet", "scope", "n", "agree", "agree_prop", "kappa"])
        for name in names:
            rows = data[name]
            for scope in ["overall"] + TYPES:
                sub = rows if scope == "overall" else [x for x in rows if x["type"] == scope]
                aa = sum(1 for x in sub if judge_pass(x["auto"]) and not is_unsat(x["sat"]))
                bb = sum(1 for x in sub if judge_pass(x["auto"]) and is_unsat(x["sat"]))
                cc = sum(1 for x in sub if not judge_pass(x["auto"]) and not is_unsat(x["sat"]))
                dd = sum(1 for x in sub if not judge_pass(x["auto"]) and is_unsat(x["sat"]))
                ag = aa + dd
                w.writerow([name, scope, len(sub), ag, f"{ag/max(1,len(sub)):.4f}", f"{kappa_from(aa,bb,cc,dd):.4f}"])
    print(f"Wrote {len(list(OUT.glob('*.csv')))} tables -> {OUT}")

if __name__ == "__main__":
    main()
