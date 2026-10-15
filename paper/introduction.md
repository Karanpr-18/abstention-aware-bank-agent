# 1. Introduction

A wrong answer in banking costs more than an honest "I don't know". A made-up loan verdict sends a family to a branch with false hope. A guessed fraud ruling delays a same-day report. A translated warning without its case number leaves a victim with nothing to track.

Each reply reads well. Each cites a real page. Each still picks the wrong action.

Past work gives three reasons to study this. First, finance sets show it at scale. Islam et al. [26] report a top model with search failing on 81% of a FinanceBench sample. Xie et al. [28] report models passing extraction yet failing reasoning over 36 sets on FinBen.

Second, search does not fix whether to answer. Chen et al. [19] find rejection the weakest skill on RGB. Ming et al. [20] find bigger models not always more faithful on FaithEval. Yang et al. [21] find top stacks erring on about a third of live asks on CRAG.

Third, this is where auto judges can fail. Zheng et al. [7] report strong judges matching humans near 80% on chat. Yet Wang et al. [30] show order flipping ranks, and Tan et al. [29] find strong judges near chance on right-or-wrong pairs. A bot that writes well but refuses badly passes the tests most teams run.

A large language model (LLM) here means a pre-trained transformer used as a chat agent (Wen et al. [1]). Retrieval-augmented generation (RAG) means pairing it with a passage index at query time (Lewis et al. [5]). Accuracy-only tests miss the point. A reply can score high on faithfulness (Es et al. [6], Niu et al. [17], Saad-Falcon et al. [18]) while answering what needed a question, a decline, a hand-off, or a firm stop.

The first call in support is behaviour: answer at all, and if not, what instead. That call is this paper's topic.

We test it with a behaviour-first protocol. Each query has one expected act. Answer means the knowledge base settles it. Clarify means facts are missing, so ask. Abstain means out of scope, so decline. Escalate means log and hand to a human. Refuse means firmly block an adversarial request. A reply passes only on matching that act. The frame follows the abstention survey of Wen et al. [1] and the RAG rejection splits of Chen et al. [19], adding a five-way support split with paired runs and a reason per miss. This protocol is our first contribution (C1). Full details, query counts, and pipeline settings appear in Section 3.

We run 100 queries through one fixed pipeline twice, once per tier: `glm-5.3-flash` (fast) and `muse-spark-1.3-xhigh` (reasoning). The set holds 20 queries of each of five types. Gold acts total answer 34, clarify 10, abstain 20, escalate 14, and refuse 22. Same queries run on both tiers, so pairs compare head to head. Tiers mix vendor, size, and reasoning mode at once. We state this mix each time tiers are compared and claim no cause.

The primary label is the 2-of-3 majority across the author rating, a classmate check, and a third-model check. Majority labels flag 11 of 100 fast-tier replies (11.0%, CI 6.2 to 18.6) and 13 of 100 reasoning-tier replies (13.0%, CI 7.8 to 21.0). A paired test cannot split them (McNemar p 0.80). The headline is a tie. We claim no winner.

Misses gather on ambiguous queries in the majority, 6 of 20 fast and 7 of 20 reasoning, with adversarial down to 2 of 20 and 1 of 20. The three sources agree fairly overall (pooled Fleiss kappa 0.32; 0.47 ambiguous strongest and 0.10 adversarial weakest; Table 6), least on adversarial refusals where the author source alone flags 6 of 20 and 8 of 20. What holds across every source is answerability on ambiguous and clear queries, including 8 reasoning-tier consensus Failure to Answer misses in the majority. Full breakdowns appear in Section 4.

We add three points past the protocol. A miss-reason set with meanings, each used by all three sources (C2). Consensus reason counts with a Mixed bucket where no two sources agree (C3). Pooled source agreement by type with Fleiss kappa, percent agreement, and Gwet AC1 (C4). Scripts rebuild each number. Queries, tags, and the codebook are not released in this manuscript, so no artefact contribution is claimed. Candidate controls are held for future work in Section 6.

Section 2 reviews work and states the gap. Section 3 details the rig. Section 4 reports results. Section 5 covers use and limits. Section 6 closes. Prompts live in the Appendix; queries and the codebook are not released.
