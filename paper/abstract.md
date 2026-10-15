# Abstract

Banking support agents should sometimes not answer. They should ask for missing facts, decline out-of-scope requests, hand high-stakes cases to a human, and firmly refuse attacks. This study tests that behaviour choice in one fixed retrieval pipeline with 100 hand-written queries covering clear, ambiguous, out-of-scope, high-stakes, and adversarial cases. Each query has one expected behaviour: answer, clarify, abstain, escalate, or refuse. The same queries run on a fast tier and a reasoning tier. The primary label is the 2-of-3 majority across three five-reason sources: the author rating, a classmate check, and a third-model check.

Majority labels flag 11 of 100 fast-tier replies (11.0%, 95% CI 6.2 to 18.6) and 13 of 100 reasoning-tier replies (13.0%, CI 7.8 to 21.0), with no separable gap (paired McNemar p 0.80). Misses gather on ambiguous queries on both tiers (6 of 20 fast, 7 of 20 reasoning), while adversarial queries draw only 2 of 20 and 1 of 20. Agreement across the three sources is fair (pooled Fleiss kappa 0.32; 0.47 ambiguous strongest and 0.10 adversarial weakest).

Two patterns hold across every source. Ambiguous queries draw flags on both tiers in all three sources, and the reasoning tier withholds answerable replies, with Failure to Answer in 8 of its 13 majority misses including both clear-query cases. Adversarial refusals are the contested zone, where the author source alone flags 6 of 20 and 8 of 20 but majorities keep only 2 and 1. Control ideas are held for future work.

Keywords: retrieval-augmented generation; abstention; banking support; human evaluation; LLM-as-judge; adversarial robustness.
