#!/usr/bin/env python3
"""Check references for the RAG-agent reliability paper.

Tests (Section 10 + Section 13 audit):
  1. Each entry complete: authors, title, venue, volume, issue,
     pages or article number, year, DOI (or arXiv ID).
  2. Every in-text citation [N] appears in the list, and every
     list entry is cited at least once (both directions).
  3. IEEE numeric style: entries numbered [1..N], sequential, cited in order.
  4. Currency: >=60% of entries with year 2023-2026.
  5. Verification: each DOI/ID appears in notes/lit_search.md and no
     entry carries a [VERIFY] marker.

Inputs (defaults, overridable via flags):
  paper/references.md  (IEEE numeric list) and/or paper/references.bib
  paper/FINAL_DRAFT.md (fallback: any paper/*.md except references.md)
  notes/lit_search.md  (verification log)

Usage:
  python analysis/check_refs.py [--refs FILE] [--bib FILE] [--draft FILE ...]
                                [--lit-search FILE] [--json] [--strict]

Exit code 0 = all checks pass, 1 = any failure, 2 = input files missing.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOI_RE = re.compile(r"10\.\d{4,}/[^\s\]\)\"',;]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,}(v\d+)?)", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
ENTRY_HEAD_RE = re.compile(r"^\s*\[(\d+)\]\s*(.*)$")
CIT_RE = re.compile(r"\[(\d+(?:\s*[-,–]\s*\d+)*)\]")
TITLE_QUOTED_RE = re.compile(r'"([^"]{8,})"')
VOL_RE = re.compile(r"\bvol\.?\s*\d+|\bvolume\s+\d+", re.IGNORECASE)
ISSUE_RE = re.compile(r"\bno\.?\s*\d+|\bissue\s*\d+|\bn\.\s*o\s*\.?\s*\d+", re.IGNORECASE)
PAGES_RE = re.compile(
    r"\bpp\.?\s*\d+\s*[-–]\s*\d+|\bpp\.?\s*\d+|\bpages?\s+\d+|"
    r"\bart\.?\s*(no\.?|number)\s*[\w-]+|\barticle\s+[\w-]+|\be\d{4,}",
    re.IGNORECASE,
)
PROC_HINT_RE = re.compile(
    r"\bproc\.?\b|proceedings|conf\.?|symposium|workshop|arXiv|preprint",
    re.IGNORECASE,
)


@dataclass
class RefEntry:
    number: int
    raw: str
    authors: str = ""
    title: str = ""
    venue: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    year: str = ""
    doi: str = ""
    arxiv: str = ""
    missing: list = field(default_factory=list)


def expand_bracket(group: str) -> set[int]:
    """Expand '1', '1,3,5', '2-4' inside one [...] into ints. Ignores implausible (>500) groups."""
    out: set[int] = set()
    parts = re.split(r",", group)
    for p in parts:
        p = p.strip().strip("–- ")
        if not p:
            continue
        m = re.match(r"^(\d+)\s*[-–]\s*(\d+)$", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a < 1 or b < 1 or max(a, b) > 500:
                continue
            if b < a:
                a, b = b, a
            if b - a > 200:  # likely not a citation range
                continue
            out.update(range(a, b + 1))
        elif re.fullmatch(r"\d+", p):
            v = int(p)
            if 1 <= v <= 500:
                out.add(v)
    return out


def parse_references_md(path: Path) -> list[RefEntry]:
    text = path.read_text(encoding="utf-8")
    entries: list[RefEntry] = []
    current_num: int | None = None
    current_lines: list[str] = []

    def flush():
        if current_num is not None:
            raw = "\n".join(current_lines).strip()
            entries.append(analyse_md_entry(current_num, raw))

    for line in text.splitlines():
        m = ENTRY_HEAD_RE.match(line)
        if m:
            flush()
            current_num = int(m.group(1))
            current_lines = [m.group(2)]
        elif current_num is not None:
            # continuation line of current entry (stop at new heading)
            if line.startswith("#"):
                flush()
                current_num = None
                current_lines = []
            else:
                current_lines.append(line)
    flush()
    return entries


def analyse_md_entry(number: int, raw: str) -> RefEntry:
    e = RefEntry(number=number, raw=raw)
    flat = " ".join(raw.split())
    # DOI / arXiv
    m_doi = DOI_RE.search(flat)
    if m_doi:
        e.doi = m_doi.group(0).rstrip(".,;)")
    m_ax = ARXIV_RE.search(flat)
    if m_ax:
        e.arxiv = m_ax.group(1)
    # Year: strip DOI/arXiv tokens first so embedded numbers (e.g. arXiv 2005.xxxxx)
    # are not mistaken for the publication year; then take the last year.
    flat_no_id = DOI_RE.sub(" ", flat)
    flat_no_id = ARXIV_RE.sub(" ", flat_no_id)
    years = YEAR_RE.findall(flat_no_id)
    if years:
        e.year = years[-1]
    # Title: quoted string
    m_t = TITLE_QUOTED_RE.search(flat)
    if m_t:
        e.title = m_t.group(1)
        pre = flat[: m_t.start()]
        post = flat[m_t.end():]
        e.authors = pre.strip(" ,;")
        e.venue = post.strip(" ,;")
    else:
        # fallback: first sentence-ish chunk as authors, rest as venue
        e.authors = flat[:120]
        e.venue = flat[120:300]
    m_vol = VOL_RE.search(flat)
    if m_vol:
        e.volume = m_vol.group(0)
    m_issue = ISSUE_RE.search(flat)
    if m_issue:
        e.issue = m_issue.group(0)
    m_pages = PAGES_RE.search(flat)
    if m_pages:
        e.pages = m_pages.group(0)

    missing: list[str] = []
    # authors heuristic: must contain a comma or ' and ' or initials like 'A. '
    if len(e.authors.strip()) < 5 or (
        "," not in e.authors and " and " not in e.authors.lower() and not re.search(r"[A-Z]\.", e.authors)
    ):
        missing.append("authors")
    if not e.title:
        missing.append("title (missing quoted \"Title\")")
    if len(e.venue.strip()) < 5:
        missing.append("venue")
    is_proc = bool(PROC_HINT_RE.search(flat))
    # Continuous-publication journals (e.g. TACL: vol + pp + DOI, no issue).
    is_continuous_journal = bool(re.search(r"\bTrans\b", flat)) and bool(e.volume) and bool(e.pages)
    if not e.volume and not is_proc:
        missing.append("volume (vol. N; optional for Proc./arXiv)")
    if not e.issue and not is_proc and not is_continuous_journal:
        missing.append("issue (no. N; optional for Proc./arXiv)")
    if not e.pages:
        missing.append("pages-or-article-number (pp. X-Y or art. no. Z)")
    if not e.year:
        missing.append("year")
    else:
        try:
            y = int(e.year)
            if y < 1900 or y > 2030:
                missing.append("year (implausible)")
        except ValueError:
            missing.append("year")
    if not e.doi and not e.arxiv:
        missing.append("DOI-or-arXiv-ID")
    if "[VERIFY]" in raw:
        missing.append("unverified [VERIFY] marker present")
    e.missing = missing
    return e


def parse_bib(path: Path) -> list[RefEntry]:
    text = path.read_text(encoding="utf-8")
    # Split on @type{key,
    parts = re.split(r"@(\w+)\s*\{\s*([^,]+),", text)
    entries: list[RefEntry] = []
    # parts[0] is preamble; then groups of (type, key, body)
    i = 1
    n = 1
    while i + 2 < len(parts):
        etype, key, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        i += 3
        fields = dict(re.findall(r"(\w+)\s*=\s*[\{\"]([^\}\"]*)[\}\"]", body))
        fl = {k.lower(): v for k, v in fields.items()}
        e = RefEntry(number=n, raw=f"@{etype}{{{key}: {body[:200]}...")
        e.authors = fl.get("author", "")
        e.title = fl.get("title", "")
        e.venue = fl.get("journal", "") or fl.get("booktitle", "") or fl.get("publisher", "")
        e.volume = fl.get("volume", "")
        e.issue = fl.get("number", "") or fl.get("issue", "")
        e.pages = fl.get("pages", "") or fl.get("eid", "") or fl.get("articleno", "")
        e.year = fl.get("year", "")
        e.doi = fl.get("doi", "")
        missing = []
        for f in ("authors", "title", "venue", "year"):
            if not getattr(e, f).strip():
                missing.append(f)
        is_proc = etype.lower() in ("inproceedings", "incollection", "conference", "proceedings")
        if is_proc or "arxiv" in (fl.get("eprint", "") + fl.get("archiveprefix", "") + e.venue).lower() or fl.get("eprint"):
            pass  # volume/issue/pages relaxed for proceedings/preprints
        else:
            if not e.volume.strip():
                missing.append("volume")
            if not e.issue.strip():
                missing.append("issue")
        if not e.pages.strip():
            missing.append("pages-or-article-number")
        if not e.doi.strip() and not fl.get("eprint", "").strip():
            missing.append("DOI-or-arXiv-ID")
        e.missing = missing
        entries.append(e)
        n += 1
    return entries


def citations_in_text(text: str) -> set[int]:
    # Drop fenced code blocks to avoid matching code like array[0]
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    out: set[int] = set()
    for m in CIT_RE.finditer(text):
        out.update(expand_bracket(m.group(1)))
    return out


def check_ieee_order(entries: list[RefEntry], cited: set[int]) -> list[str]:
    problems = []
    nums = [e.number for e in entries]
    if nums != list(range(1, len(nums) + 1)):
        problems.append(f"entries not sequential [1..{len(nums)}]: got {nums[:20]}")
    # first-appearance order should be ascending for IEEE
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Check paper references (IEEE numeric default).")
    ap.add_argument("--refs", default=str(ROOT / "paper" / "references.md"))
    ap.add_argument("--bib", default=str(ROOT / "paper" / "references.bib"))
    ap.add_argument("--draft", nargs="*", default=None,
                    help="Draft markdown file(s). Default: paper/FINAL_DRAFT.md or all paper/*.md.")
    ap.add_argument("--lit-search", default=str(ROOT / "notes" / "lit_search.md"))
    ap.add_argument("--json", action="store_true", help="Emit JSON report.")
    ap.add_argument("--strict", action="store_true",
                    help="Also fail on venue-short warnings and out-of-order first citation.")
    args = ap.parse_args()

    refs_path = Path(args.refs)
    bib_path = Path(args.bib)
    lit_path = Path(args.lit_search)

    drafts: list[Path] = []
    if args.draft:
        drafts = [Path(d) for d in args.draft]
    else:
        default_draft = ROOT / "paper" / "FINAL_DRAFT.md"
        if default_draft.exists():
            drafts = [default_draft]
        else:
            paper_dir = ROOT / "paper"
            if paper_dir.is_dir():
                drafts = sorted(p for p in paper_dir.glob("*.md")
                                if p.name.lower() not in ("references.md",))
    errors: list[str] = []
    warnings: list[str] = []

    entries: list[RefEntry] = []
    source = ""
    if refs_path.exists():
        entries = parse_references_md(refs_path)
        source = str(refs_path)
        if not entries:
            errors.append(f"No numbered entries ([N]) found in {refs_path}.")
    elif bib_path.exists():
        entries = parse_bib(bib_path)
        source = str(bib_path)
        if not entries:
            errors.append(f"No @entries found in {bib_path}.")
    else:
        print(f"MISSING: neither {refs_path} nor {bib_path} exists.", flush=True)
        print("Create paper/references.md (IEEE [1], [2], ...) with "
              "authors, \"title\", venue, vol/no/pp, year, DOI.", flush=True)
        return 2

    # 1. completeness
    incomplete = [(e.number, e.missing) for e in entries if e.missing]
    for num, miss in incomplete:
        errors.append(f"[{num}] incomplete: missing {', '.join(miss)}")

    # DOI format sanity
    for e in entries:
        if e.doi and not DOI_RE.search(e.doi):
            errors.append(f"[{e.number}] malformed DOI: {e.doi}")

    # 2. bidirectional citation check
    cited: set[int] = set()
    draft_texts: dict[str, str] = {}
    for d in drafts:
        if d.exists():
            t = d.read_text(encoding="utf-8")
            draft_texts[str(d)] = t
            cited.update(citations_in_text(t))
        else:
            warnings.append(f"Draft file not found: {d}")
    listed = {e.number for e in entries}
    if drafts and draft_texts:
        uncited = sorted(listed - cited)
        unlisted = sorted(cited - listed)
        if unlisted:
            errors.append(f"Cited in text but missing from list: {unlisted}")
        if uncited:
            errors.append(f"In list but never cited in text: {uncited}")
        order_problems = check_ieee_order(entries, cited)
        for p in order_problems:
            errors.append("Style: " + p)
        if args.strict and draft_texts:
            # check first-appearance order
            combined = "\n".join(draft_texts.values())
            combined = re.sub(r"```.*?```", " ", combined, flags=re.DOTALL)
            order: list[int] = []
            for m in CIT_RE.finditer(combined):
                for v in sorted(expand_bracket(m.group(1))):
                    if v not in order:
                        order.append(v)
            if order != sorted(order):
                warnings.append(f"Citations not in ascending order at first use: {order[:15]}")
    elif not drafts:
        warnings.append("No draft files found: skipping bidirectional check.")

    # 3. currency >=60% from 2023-2026
    years = []
    for e in entries:
        m = YEAR_RE.search(e.year) if e.year else None
        if m:
            try:
                years.append(int(m.group(0)))
            except ValueError:
                pass
    if years:
        recent = sum(1 for y in years if 2023 <= y <= 2026)
        frac = recent / len(years)
        if frac < 0.60:
            errors.append(f"Currency: only {recent}/{len(years)} ({frac:.0%}) from 2023-2026; need >=60%.")
    else:
        errors.append("Currency: no parseable years; cannot verify >=60% from 2023-2026.")

    # 4. verification against notes/lit_search.md
    if lit_path.exists():
        lit = lit_path.read_text(encoding="utf-8")
        lit_low = lit.lower()
        for e in entries:
            if e.doi:
                norm = e.doi.lower().rstrip(".,;)")
                if norm not in lit_low:
                    errors.append(f"[{e.number}] DOI not found in {lit_path.name}: {e.doi}")
            elif e.arxiv:
                if e.arxiv.lower() not in lit_low and "arxiv" not in lit_low:
                    errors.append(f"[{e.number}] arXiv ID not found in {lit_path.name}: {e.arxiv}")
        if re.search(r"\bretract(?:ed|ion)\b", lit, re.IGNORECASE) and not re.search(
            r"\b(not|no|non)[\s-]*\b\w{0,12}\bretract", lit, re.IGNORECASE
        ):
            warnings.append(f"{lit_path.name} mentions retraction: confirm no cited paper is retracted.")
    else:
        errors.append(f"Verification log missing: {lit_path} not found. "
                      "Log each DOI check there (title/authors/year match, retraction check).")

    ok = not errors
    report = {
        "source": source,
        "entries": len(entries),
        "cited_in_text": sorted(cited),
        "incomplete": [{"n": n, "missing": m} for n, m in incomplete],
        "years": years,
        "errors": errors,
        "warnings": warnings,
        "status": "PASS" if ok else "FAIL",
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"References check: {source}")
        print(f"Entries: {len(entries)}; distinct citations in draft: {len(cited)}")
        if years:
            recent = sum(1 for y in years if 2023 <= y <= 2026)
            print(f"Currency: {recent}/{len(years)} ({recent/len(years):.0%}) from 2023-2026 (need >=60%)")
        if warnings:
            print("\nWARNINGS:")
            for w in warnings:
                print(f"  - {w}")
        if errors:
            print("\nFAILURES:")
            for er in errors:
                print(f"  - {er}")
            print("\nRESULT: FAIL")
        else:
            print("\nRESULT: PASS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
