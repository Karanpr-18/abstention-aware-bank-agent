#!/usr/bin/env python3
"""Build paper/FINAL_DRAFT.docx (v5) from paper/FINAL_DRAFT.md.

v4 (author request): title candidate 1; journal title/author header with rule
(no manuscript-meta paragraph); NO appendices; all 18 figures inline;
Mermaid fences skipped in print (source archived with figures,
print image embedded); single spacing 11pt to target ~20 pages.
Tables render as Word tables (caption above, 8pt); figures embed PNG (caption below, 9pt).
Run: ./.venv/bin/python -I analysis/build_docx.py
Requires: python-docx. Stdlib otherwise.
"""
from pathlib import Path
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
FIGS = PAPER / "figures"

TITLE = "When Should an AI Agent Say \"I Don't Know\"? Evaluating Abstention and Reliability in a Financial Support RAG Agent"

FIG_RE = re.compile(r"^!\[.*?\]\(figures/([^)]+)\.png\)\s*$")
TABLE_SEP_RE = re.compile(r"^\|(\s*:?-+:?\s*\|)+\s*$")


def add_page_number_footer(doc):
    for sec in doc.sections:
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        el = OxmlElement('w:fldSimple')
        el.set(qn('w:instr'), 'PAGE')
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = '1'
        r.append(t)
        el.append(r)
        run._element.append(el)


def set_body(par, size=11, justify=True, space_after=3, line=1.0, bold=False, italic=False):
    par.paragraph_format.space_after = Pt(space_after)
    par.paragraph_format.line_spacing = line
    par.paragraph_format.space_before = Pt(0)
    if justify:
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in par.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.bold = bold
        r.italic = italic


def add_md_table(doc, caption, header, rows):
    cap = doc.add_paragraph()
    run = cap.add_run(caption)
    run.bold = True
    run.font.size = Pt(9)
    run.font.name = "Times New Roman"
    cap.paragraph_format.space_before = Pt(6)
    cap.paragraph_format.space_after = Pt(3)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(header):
        cell = t.cell(0, j)
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(8)
        run.font.name = "Times New Roman"
    for i, row in enumerate(rows, start=1):
        for j in range(len(header)):
            v = row[j] if j < len(row) else ""
            cell = t.cell(i, j)
            cell.text = ""
            run = cell.paragraphs[0].add_run(v)
            run.font.size = Pt(8)
            run.font.name = "Times New Roman"
    doc.add_paragraph("").paragraph_format.space_after = Pt(2)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def clean_inline(txt):
    return (txt.replace("**", "").replace("`", "")
            .replace("$^{1}$", "\u00b9").replace("$^{2}$", "\u00b2")
            .replace("^1^", "\u00b9").replace("^2^", "\u00b2"))


def main():
    md = (PAPER / "FINAL_DRAFT.md").read_text(encoding="utf-8").splitlines()
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    for sec in doc.sections:
        sec.top_margin = Inches(0.7)
        sec.bottom_margin = Inches(0.7)
        sec.left_margin = Inches(0.7)
        sec.right_margin = Inches(0.7)
        sec.header_distance = Inches(0.35)
        sec.footer_distance = Inches(0.35)

    # ---- title block: journal style (title, authors, affiliations, contact, rule) ----
    # Title
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h.add_run(TITLE)
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = "Times New Roman"
    h.paragraph_format.space_after = Pt(6)
    # Authors
    auth = doc.add_paragraph()
    auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = auth.add_run("A. Author\u00b9, B. Author\u00b9, C. Author\u00b2, D. Author\u00b2")
    run.font.size = Pt(11)
    run.font.name = "Times New Roman"
    auth.paragraph_format.space_after = Pt(2)
    # Affiliations
    aff = doc.add_paragraph()
    aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = aff.add_run("\u00b9Affiliation one (to be supplied); \u00b2Affiliation two (to be supplied)")
    run.italic = True
    run.font.size = Pt(10)
    run.font.name = "Times New Roman"
    aff.paragraph_format.space_after = Pt(2)
    # Corresponding
    cor = doc.add_paragraph()
    cor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cor.add_run("Corresponding author: name@institution.edu (to be supplied)")
    run.italic = True
    run.font.size = Pt(10)
    run.font.name = "Times New Roman"
    cor.paragraph_format.space_after = Pt(2)
    # Thin rule under the header
    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = rule.add_run("\u2500" * 72)
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run.font.name = "Times New Roman"
    rule.paragraph_format.space_after = Pt(8)
    add_page_number_footer(doc)

    # Skip past the markdown title block (title + author lines + note + ---)
    i = 0
    n = len(md)
    # find first "# Abstract" heading
    while i < n and not md[i].strip().startswith("# Abstract"):
        i += 1

    pending_caption = None
    in_refs = False
    in_fence = False
    fence_is_mermaid = False
    code_buf = []
    def add_code_block(doc, lines):
        # Monospace block for Appendix C prompts (Consolas/Courier).
        # One Word paragraph per line to preserve line breaks.
        if not lines and True:
            pass
        # Drop single trailing empty line artefact from split, keep intentional blanks.
        for cl in lines:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(cl if cl else " ")
            run.font.name = "Consolas"
            # Fallback chain: Word uses this when Consolas missing.
            try:
                rPr = run._element.get_or_add_rPr()
                from docx.oxml.ns import qn as _qn
                rFonts = rPr.find(_qn('w:rFonts'))
                if rFonts is None:
                    from docx.oxml import OxmlElement as _OE
                    rFonts = _OE('w:rFonts')
                    rPr.append(rFonts)
                rFonts.set(_qn('w:ascii'), 'Consolas')
                rFonts.set(_qn('w:hAnsi'), 'Consolas')
                rFonts.set(_qn('w:cs'), 'Courier New')
            except Exception:
                pass
            run.font.size = Pt(8.5)
        # Small gap after block.
        gap = doc.add_paragraph()
        gap.paragraph_format.space_before = Pt(0)
        gap.paragraph_format.space_after = Pt(3)
    while i < n:
        ln = md[i]
        s = ln.strip()

        # Fenced code blocks: mermaid -> archived note (legacy); all other
        # fences (Appendix C prompts) -> monospace Consolas block.
        if s.startswith("```"):
            if not in_fence:
                if "mermaid" in s.lower():
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run("Mermaid source archived with the figures; print rendering appears with Table T2 at the end of \u00a73.4.")
                    run.italic = True
                    run.font.size = Pt(8)
                    run.font.name = "Times New Roman"
                    p.paragraph_format.space_after = Pt(3)
                    in_fence = True
                    fence_is_mermaid = True
                    code_buf = []
                else:
                    in_fence = True
                    fence_is_mermaid = False
                    code_buf = []
            else:
                # Closing fence.
                if not fence_is_mermaid:
                    add_code_block(doc, code_buf)
                in_fence = False
                fence_is_mermaid = False
                code_buf = []
            i += 1
            continue
        if in_fence:
            if fence_is_mermaid:
                i += 1
                continue
            else:
                # Preserve raw line (no strip) for prompt fidelity.
                code_buf.append(ln.rstrip("\n"))
                i += 1
                continue

        m = FIG_RE.match(s)
        if m:
            png = FIGS / (m.group(1) + ".png")
            if png.exists():
                pic = doc.add_paragraph()
                pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pic.paragraph_format.space_before = Pt(3)
                pic.paragraph_format.space_after = Pt(1)
                pic.add_run().add_picture(str(png), width=Inches(5.0))
            i += 1
            continue

        if s.startswith("|") and i + 1 < n and TABLE_SEP_RE.match(md[i + 1].strip()):
            header = split_row(s)
            rows = []
            j = i + 2
            while j < n and md[j].strip().startswith("|"):
                rows.append(split_row(md[j].strip()))
                j += 1
            cap = pending_caption or "Table"
            pending_caption = None
            add_md_table(doc, cap, header, rows)
            i = j
            continue

        if not s:
            i += 1
            continue
        if s.startswith("# ") and not s.startswith("# Abstract"):
            p = doc.add_heading(clean_inline(s[2:].strip()), level=1)
            for r in p.runs:
                r.font.size = Pt(14)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            in_refs = s[2:].strip().lower() == "references"
            i += 1
            continue
        if s.startswith("# Abstract"):
            p = doc.add_heading("Abstract", level=1)
            for r in p.runs:
                r.font.size = Pt(14)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            in_refs = False
            i += 1
            continue
        if s.startswith("## "):
            p = doc.add_heading(clean_inline(s[3:].strip()), level=2)
            for r in p.runs:
                r.font.size = Pt(12)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue
        if s.startswith("### "):
            p = doc.add_heading(clean_inline(s[4:].strip()), level=3)
            for r in p.runs:
                r.font.size = Pt(11)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue
        if s.startswith("---"):
            i += 1
            continue
        if s.startswith(">"):
            i += 1
            continue
        if s.startswith("**Table") or s.startswith("**Figure"):
            txt = clean_inline(s.strip("*").strip())
            if txt.startswith("Table"):
                pending_caption = txt
            else:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(txt)
                run.bold = False
                run.font.size = Pt(9)
                run.font.name = "Times New Roman"
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(6)
            i += 1
            continue
        # skip leftover title-block author lines if any remain in body
        if s.startswith("A. Author") or "Affiliation" in s[:40] or s.startswith("Corresponding author") or s.startswith("Manuscript"):
            i += 1
            continue
        if s.startswith(("- ", "* ")):
            p = doc.add_paragraph(clean_inline(s[2:].strip()), style="List Bullet")
            set_body(p, size=11, justify=False, line=1.0)
            i += 1
            continue
        if in_refs and re.match(r"^\[\d+\]", s):
            buf = [s]
            j = i + 1
            while j < n and md[j].strip() and not re.match(r"^\[\d+\]", md[j].strip()) \
                    and not md[j].strip().startswith("#") and not md[j].strip().startswith("L") \
                    and not md[j].strip().startswith("---"):
                buf.append(md[j].strip())
                j += 1
            p = doc.add_paragraph(" ".join(buf))
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Inches(-0.4)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                r.font.size = Pt(8.5)
                r.font.name = "Times New Roman"
            i = j
            continue
        buf = [s]
        j = i + 1
        while j < n and md[j].strip() and not md[j].strip().startswith(("#", "|", "!", "-", "* ", ">", "---", "```")) \
                and not FIG_RE.match(md[j].strip()) and not re.match(r"^\[\d+\]", md[j].strip()):
            buf.append(md[j].strip())
            j += 1
        txt = clean_inline(" ".join(buf))
        # affiliation-looking lines inside body: centre them
        p = doc.add_paragraph(txt)
        set_body(p, size=11, line=1.0)
        i = j

    out = PAPER / "FINAL_DRAFT.docx"
    doc.save(str(out))
    print(f"Saved -> {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
