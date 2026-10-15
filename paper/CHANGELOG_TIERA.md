# Tier-A revision changelog (ESWA target; judge same-model; British; queries private)

Target: Expert Systems with Applications (Elsevier, elsarticle) per author 1a. Manuscript kept in md/docx; convert refs to journal style on template.
Judge: same model that answered (muse for muse, glm for glm) per author; prompt = JUDGE_PROMPT in judge code at temperature 0. Code default is a third model, so identity is reported as author-supplied and unlogged.
Labelling: initial human rating 20 (10/tier) + cross-check 11 = final 31; no per-ID log, no kappa. Noted as worth reporting for transparency.
Spelling: British throughout (verbatim title spellings preserved).
Queries: not released; planned later GitHub release noted in Methods.

1. Artefacts removed from main text: file paths, code line numbers, dates, "ledger", "Mermaid", "v1", "gold50/extra50", "List stands at 30". Detail moved to Appendix A/B. [verify: grep main md]
2. Five reasons defined once (Table 7); short labels afterwards. Counts in Table 8.
3. Plain academic English: knowledge base, response time, confidence intervals, retrieval; automated first pass (judge) vs initial human rating; exploratory labelled.
4. Visuals cut: 7 main images in 5 panels (Figs 1 pipeline, 2 rates, 3 grid, 4 reasons, 5 adversarial, 6-7 judge panel). Tables 3-5 merged panel (headline + McNemar + by-type); Tables 7-8 merged panel (definitions + counts). Config moved to Appendix Table A1. Cases capped at 5 rows (Table 9). Supplementary visuals in Appendix (Figs A1-A11).
5. Claims softened: opposing shapes as hypothesis (Fisher p about 0.20-0.24; permutation p about 0.19); Table 11 advice as candidates; abstract ends with suggestion. F7 discordant counts verified against workbook (overall b=15 c=12; adv b=4 c=6).
6. Power note added (Methods + Discussion): about 49 per group for 25% vs 5%; about 199 per group for 20% vs 10% (alpha 0.05, power 0.8); paired totals about 56/233 same order with discordant assumptions. From revision_stats.py.
7. Gap rewritten with 4 verified 2025-2026 refs [31]-[34] (all arXiv-fetched in-session). Total 34 verified; full 50-70 sweep still pending (see open issues). No unverified citations.
8. EU text updated: AI Act Art 14 + Digital Omnibus Regulation (EU) 2026/1744 (OJ 24 Jul 2026, in force 27 Jul 2026; Annex III 2 Dec 2027, Annex I 2 Aug 2028) via EUR-Lex; support bot not automatically high-risk.
9. AI-disclosure + data availability added (Methods): authors verify all claims; AI used for drafting/scripts under supervision, not an author; queries private until GitHub release.

Numbers unchanged: all headline + confusion + judge + taxonomy counts recomputed from workbook match ledger; only additions are Fisher/perm/power from revision_stats.py.
