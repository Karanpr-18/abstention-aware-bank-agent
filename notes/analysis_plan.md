# analysis_plan.md — confirmatory vs exploratory (written BEFORE running exploratory)

Seed: 42. Input: `Rag results.xlsx` (root). Human truth: `satisfied != yes` → unsatisfactory.

## Confirmatory (pre-registered)
- C-A: per-model + per-type unsatisfactory proportions with Wilson 95% CI.
- C-B: paired model comparison (same 100 queries, outcome = unsatisfactory yes/no): exact McNemar overall + per-type (exploratory, Holm correction). Report discordant counts.
- C-C: confusion matrices per model (positive = should-not-simply-answer; predictor = `Abstained`): precision/recall/F1 + over-abstention rate on answer-expected (FP/(FP+TN)).
- C-D: judge-vs-human: percent agreement + Cohen kappa overall and by type (judge pass = `correct`/`appropriate_abstain`).
- C-E: failure taxonomy counts per model × type from `satisfied` free text + answer text (codebook needs author approval).

## Exploratory (labelled as such in text)
- E-1: confidence (retrieval similarity) distributions by outcome; reliability-style plot — ONLY after `Confidence` semantics confirmed.
- E-2: answer length vs outcome (over-sharing check).
- E-3: source counts/kinds vs outcome.
- E-4: latency medians + Wilcoxon signed-rank (provider caveat; deprioritised per authors).
- E-5: hedging/refusal phrasing frequencies (lexicon stated openly).
- E-6: per-query discordance grid (both fine / only GLM fails / only MUSE fails / both fail).

## Guardrails
- Report every comparison run, not only significant ones. No "significant" without test. n=20/type → wide CIs; strength from taxonomy + protocol, not model-beats-model.
- All tables → `paper/tables/*.csv`; figures → `paper/figures/*.png+*.pdf`. Every number logged in `paper/claims_ledger.csv`.
