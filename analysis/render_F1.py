#!/usr/bin/env python3
"""Render journal-grade pipeline figure (PNG 300dpi + PDF vector).

Mirrors paper/figures/F1_pipeline.mmd. Colour-blind-safe, greyscale-readable:
white boxes, dark navy headers, grey lane bands, black text.
No title or figure number inside the image; caption lives in the text below.
Run: ./.venv/bin/python -I analysis/render_F1.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "paper" / "figures"

NAVY = "#1f3a5f"
GREY_LANE = "#eef1f4"
BOX_EDGE = "#1f3a5f"

lanes = [
    ("A · KNOWLEDGE BASE", [
        "Public bank pages",
        "8 countries · FAQ/help",
        "4 manual PDFs",
        "64 markdown files",
    ]),
    ("B · INDEXING", [
        "Chunks: 1000 chars",
        "overlap 200 · drop <200",
        "all-MiniLM-L6-v2",
        "ChromaDB bank_kb",
        "cosine · fresh rebuild",
    ]),
    ("C · QUERY-TIME AGENT", [
        "Query + gold act",
        "Top-4 chunks",
        "Specialist draft ≤80w",
        "2 mock tools",
        "Gate: pass/decline ≤40w",
        "Reply + flag + score",
    ]),
    ("D · SCORING (100×2)", [
        "author + classmate",
        "+ blind third-model",
        "2-of-3 majority",
        "each source sensitivity",
        "Wilson · McNemar · kappa",
    ]),
]

fig, ax = plt.subplots(figsize=(12, 5.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.9)
ax.axis("off")

xs = [0.15, 3.15, 6.15, 9.15]
w = 2.7
for i, (title, items) in enumerate(lanes):
    x = xs[i]
    bg = FancyBboxPatch((x, 0.15), w, 5.45, boxstyle="round,pad=0.02,rounding_size=0.12",
                        facecolor=GREY_LANE, edgecolor="#9aa4ae", linewidth=1.0)
    ax.add_patch(bg)
    hb = FancyBboxPatch((x, 4.85), w, 0.75, boxstyle="round,pad=0.02,rounding_size=0.12",
                        facecolor=NAVY, edgecolor=NAVY, linewidth=1.0)
    ax.add_patch(hb)
    ax.text(x + w/2, 5.22, title,
            ha="center", va="center", fontsize=8, weight="bold", color="white")
    n = len(items)
    top, bottom = 4.65, 0.35
    step = (top - bottom) / n
    for j, it in enumerate(items):
        y1 = top - (j+1)*step + 0.04
        h = step - 0.08
        bx = FancyBboxPatch((x+0.12, y1), w-0.24, h,
                            boxstyle="round,pad=0.01,rounding_size=0.06",
                            facecolor="white", edgecolor=BOX_EDGE, linewidth=0.9)
        ax.add_patch(bx)
        ax.text(x + w/2, y1 + h/2, it, ha="center", va="center",
                fontsize=7.0, color="#111111", linespacing=1.2, wrap=True)
    if i < 3:
        ax.annotate("", xy=(xs[i+1]-0.02, 2.9), xytext=(x+w+0.02, 2.9),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))

for ext, dpi in (("png", 300), ("pdf", None)):
    out = FIGS / f"F1_pipeline.{ext}"
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    print("wrote", out, f"{out.stat().st_size/1024:.0f} KB")
