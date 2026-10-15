# 6. Conclusion and Future Scope

We scored what two tiers of a banking help agent do when the right move is not to answer. On 100 paired queries, majority labels across the author, classmate, and third-model sources flag 11 of 100 fast-tier replies (11.0%, 95% CI 6.2 to 18.6) and 13 of 100 reasoning-tier replies (13.0%, CI 7.8 to 21.0). A paired test ties them (McNemar p 0.80, Holm 1.00; Table 3).

Misses gather on ambiguous queries in the majority (6 of 20 fast, 7 of 20 reasoning; Figure 2), with adversarial down to 2 of 20 and 1 of 20. What holds across every source is answerability on ambiguous and clear queries, including 8 reasoning-tier consensus Failure to Answer misses in the majority with both clear-query withholds. Adversarial refusals are the contested zone, where the author source alone flags 6 of 20 and 8 of 20 but majorities keep only 2 and 1. Agreement is fair overall (pooled Fleiss kappa 0.32; 0.47 ambiguous strongest and 0.10 adversarial weakest; Table 6; Figure 4). Wrong acts occurred even when search scores looked strong (Appendix); whether rules or retrieval should change is future work.

## Future Scope

Reruns come first: more queries to trim ranges, repeat runs to gauge spread, and blind re-tags of 20 to 30% of replies for kappa. The cleanest next test splits reasoning on the same model (off versus high), which this mix cannot do. A fully blinded shared-judge rerun is future work in this rerun band.

Controls are all untested in this study and belong here, not in deployment advice. Candidates are a hard-refusal rule for adversarial intents, a no-verdict-without-inputs rule, an answerable check for withheld replies, a brevity plus secrecy cap, firm-stop wording, and a role-scope guard. A no-search baseline and wording variants belong here too. Zhang et al. [15] on R-Tuning and Wallace et al. [25] on rank order give ready frames for the training arm. A Spanish and Catalan arm would tie the protocol to EU and Spain use.

Tuned hold-back cut-offs, from the selective theory of Geifman and El-Yaniv [8], asked-for scores (Tian et al. [11]), outside-only tricks (Xiong et al. [12]), and meaning spread (Kuhn et al. [13]), plus human hand-off studies would test if any candidate holds with live users.

Scoring should move from single judges to the right-or-wrong judge tests of Tan et al. [29] with the bias checks of Wang et al. [30] and the human-anchored RAG audit of Saad-Falcon et al. [18], and from the accuracy-only finance sets of Islam et al. [26]-Xie et al. [28] to act-first ones. Queries, tags, and the codebook are not released in this manuscript; no artefact contribution is claimed.
