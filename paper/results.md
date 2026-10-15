# 4. Results

All numbers come from scripts that read the verified workbook. The primary label is the 2-of-3 majority across the author, classmate, and third-model sources; each source is shown beside it. Plots are archived as PNG plus PDF. Reasons are defined once in Table 4; short labels are used afterwards.

## 4.1 Overall miss rate (planned, majority primary)

Majority labels flag near the same share on both tiers (Table 3): fast 11 in 100 (11.0%, CI 6.2 to 18.6), reasoning 13 in 100 (13.0%, CI 7.8 to 21.0). Pairs split 7 only-fast-fail versus 9 only-reasoning-fail (McNemar p 0.80; Holm 1.00; Table 3). Figure 3 shows the per-query majority grid (both pass 80; only fast 7; only reasoning 9; both fail 4). No per-type test nears cut-offs (all raw p 1.00, Holm 1.00).

What this means: the sample cannot split tiers on headline rate. We claim no winner, matching the large finance sets of Islam et al. [26] and Xie et al. [28] where top lines move little.

## 4.2 By query type and rater (planned plus sensitivity)

Under majority labels, confidence intervals are wide at n = 20 per cell (Table 3; Figure 2). Fast tier majority: clear 1/20, ambiguous 6/20 (30%, CI 15 to 52), out of scope 0/20, high stakes 2/20, adversarial 2/20 (10%, CI 3 to 30). Reasoning tier majority: clear 2/20, ambiguous 7/20 (35%, CI 18 to 57), out of scope 1/20, high stakes 2/20, adversarial 1/20 (5%, CI 1 to 24).

Figure 2 shows each type with four bars: author, third-model, classmate, and majority. Ambiguous queries peak in the majority and in the third-model and classmate sources on both tiers (fast 5 author, 6 third-model, 5 classmate, majority 6; reasoning 2 author, 8 third-model, 8 classmate, majority 7). Adversarial queries peak only in the author source (6 of 20 fast and 8 of 20 reasoning), while the third-model and classmate sources flag only 1 and 2 of 20 on each tier, leaving majorities of 2 and 1. Out-of-scope majorities are 0 and 1 of 20.

What this means: the peak sits on ambiguous queries in the majority and in the third-model and classmate sources; adversarial peaks only in the author source. Any claim about where misses gather must still name its standard.

## 4.3 Miss reasons (majority primary)

Table 4 defines the five reasons once and counts consensus reasons under majority labels (consensus means at least two sources name the same reason, else Mixed).

Fast majority 11: consensus Failure to Answer 2 (amb_15, amb_19), Overreach 1 (adv_10), Unsupported Assumption 1 (clear_16), Mixed 7. Reasoning majority 13: consensus Failure to Answer 8, Oversharing 1 (high_15), Soft Refusal 1 (adv_20), Mixed 3 (amb_02, high_06, oos_14).

Fast misses spread over ambiguous 6 plus high stakes 2, adversarial 2, and clear 1. Reasoning puts 7 of 13 on ambiguous plus both clear-query flags. The Appendix reports the abstention confusion as background (accuracy 70.0% fast, 78.0% reasoning; full report in Table A1); it uses the stored abstention flag and does not change with the label standard.

What this means: reason counts in this section describe consensus only; most fast-tier majorities are Mixed with no two sources agreeing. The reasoning tier withholds answerable replies in consensus (8 of 13), and no tier claim rests on the retired tie-break rule.

## 4.4 Adversarial detail (author source as contested-zone illustration)

Adversarial sets are gold refuse throughout (Table 5). Because the majority keeps only 2 fast and 1 reasoning adversarial misses, this subsection uses author labels to show what the majority filters out, stated as such. Fast author fails 6: Overreach 5 plus Oversharing 1. Reasoning author fails 8: Soft Refusal 4 plus Overreach 2 plus Oversharing 2. The shape fits attack work: framed orders beat refusal (Greshake et al. [22]), wraps lift success (Zhan et al. [24]), and few crafted inputs beat thin guards (Zou et al. [23]).

Only 1 of the 6 fast-tier author adversarial flags (adv_10) survives to the majority, and only 1 of the 8 reasoning-tier ones (adv_20) does. The rank order of Wallace et al. [25] predicts this: without hard rank of system rules, seen risk does not turn into refusal.

What this means: refusal wording on attacks is where sources disagree most. The majority treats most author-flagged adversarial replies as passes.

## 4.5 Agreement across the three sources (planned)

Table 6 reports pooled agreement over both tiers (200 replies; 40 per type) with Fleiss kappa, percent agreement, and Gwet AC1; per-tier Fleiss is archived for traceability. Overall pooled Fleiss is 0.32 (fair; all three agree on 148 of 200). By type, pooled Fleiss is strongest on ambiguous queries (0.47; all three agree on 27 of 40) and weakest on adversarial queries (0.10; all three agree on 25 of 40), then out of scope (0.12) and high stakes (0.16); clear is 0.39. Pooled pairwise agreement is lowest on adversarial queries for author pairs (author-third 65.0%, author-classmate 70.0%) and highest where misses are rare. Figure 4 shows pooled agreement by type with Fleiss kappa, percent agreement, and Gwet AC1 (see Table 6). The per-ID file (200 replies) lists all three sources plus the majority without resolving disagreements; no adjudication was done. The original automated mark agrees with the author on 71/100 fast (kappa 0.18) and 78/100 reasoning (kappa 0.26), falling on adversarial queries to 13/20 and 11/20, with mismatches in both directions (16 automated-pass-to-author-fail and 35 automated-fail-to-author-pass); it is not part of the majority.

Unanimous across all three sources are 3 fast-tier replies (adv_10, amb_15, amb_19) and 4 reasoning-tier replies (amb_07, amb_18, clear_14, clear_16). Six of the 7 unanimous misses are consensus Failure to Answer; adv_10 is consensus Overreach. The reasoning unanimous set includes both clear-query withholds (clear_14, clear_16).

Zheng et al. [7] report place and length bias, Wang et al. [30] report order flips, and Tan et al. [29] report near-chance scores on hard items. Saad-Falcon et al. [18] show light judges with human tags can audit RAG; refusal wording needs that anchor more.

What this means: pooled sources agree most on ambiguous queries by kappa (0.47) and least on adversarial queries (0.10; author agreement 65-70%). The next section keeps only what the majority keeps, with consensus reasons reported separately (Table 4).

## 4.6 Search score, length, sources, response time (exploratory)

`Confidence` is search closeness, so this subsection is exploratory, not tuning. The Appendix plots it by outcome: misses are not stuck low, several sit above 0.60. Strong retrieval does not stop wrong acts, the asked-score arc where error halves yet stays too sure (Tian et al. [11]), outside tricks narrow gaps (Xiong et al. [12]), and meaning spread beats token odds (Kuhn et al. [13]).

Length runs longer for misses on fast (57 vs 46 words; Appendix) and slightly longer on reasoning (34 vs 32, exact medians 34.0 vs 31.5), fitting padded refusals, not proving them. Breadth is capped: 4 span hits each; distinct files 1 in 26/200, 2 in 78/200, 3 in 56/200, 4 in 40/200 (Appendix). Response times as stored: median 68.3 s fast, 40.0 s reasoning (Appendix); free-tier routing rules them, so no speed read.

What this means: in this sample, wrong acts occurred even when retrieval scores looked strong. Whether decision rules or retrieval should change is held for future work, not decided here.
