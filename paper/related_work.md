# 2. Literature Review

Refusal is older than chat models. Geifman and El-Yaniv [8] frame it as a predictor plus a rule for when to stay silent, with a risk bound. Wen et al. [1] bring this frame to large language models, separating the query, the model, and human values. Our design follows that split. Query types set the expected act, the pipeline sets what the model can do, and banking sets the cost of a miss.

Kirichenko et al. [2] test refusal on 20 sets and six hard cases. Refusal stays unsolved and scale alone does not fix it, while tuning for reasoning can cut refusal on maths and science by about 24%. We note this result but claim no cause, since our tiers differ in vendor and size as well.

Feng et al. [14] let models quiz each other to find gaps, lifting scores by up to 19.3%. Zhang et al. [15] teach refusal as its own skill, which transfers to new tasks. We test from the other end with a fixed rig, fixed queries, and three-source majority labels on every reply.

Models also refuse when they should answer. Röttger et al. [3] built XSTest with 250 safe prompts that look risky plus 200 unsafe twins, and show that small edits can flip the call. Xie et al. [4] push the other side with SORRY-Bench, 450 unsafe asks over 45 harm types. Cui et al. [16] add OR-Bench, the first large over-refusal set at 80,000 prompts.

Our study sits between these poles. Attack queries need a firm stop, yet vague and plain queries punish a wrong stop. We therefore split Soft Refusal, where refusal is not firm enough, from Failure to Answer, where the agent abstains when an answer exists. Our sample shows why the split matters. Eight of 13 reasoning-tier majority misses are consensus Failure to Answer on cases the knowledge base settles, which is the exact shape Cui et al. [16] warn of.

Lewis et al. [5] define retrieval-augmented generation as a model plus a dense passage index with retriever and writer run jointly. Our rig copies that shape at small scale with MiniLM vectors, a ChromaDB store, top-4 spans, and a context-only writer.

Es et al. [6] built RAGAS to score faithfulness without labels. It asks whether text sticks to fetched lines, not whether the agent should have replied. Later sets keep this blind spot. Niu et al. [17] tag errors in 18,000 replies with RAGTruth. Saad-Falcon et al. [18] tune light judges so a few hundred tags can audit new domains with ARES.

Chen et al. [19] find rejection the weakest of four skills on RGB. Ming et al. [20] find bigger models not always more faithful on FaithEval. Yang et al. [21] find top stacks still err on about a third of live asks on CRAG. We add the missing layer. Each query carries an expected act, so a faithful yet wrongly chosen reply still fails.

Zheng et al. [7] show strong model judges match human taste near 80% on MT-Bench, with known place, length, and self-praise bias. Wang et al. [30] show order alone can flip ranks. Tan et al. [29] test judges on right-or-wrong pairs and find strong models near chance on JudgeBench.

Our result fits this arc in one niche. The three five-reason sources agree fairly overall (pooled Fleiss kappa 0.32; all three agree on 148 of 200) and most on ambiguous queries (pooled Fleiss 0.47), least on adversarial queries (pooled Fleiss 0.10; author agreement 65-70%) where single sources diverge. Scores near 1.0 should not end debate.

Guo et al. [9] show networks are often too sure. Kadavath et al. [10] find mixed transfer of self-knowledge. Tian et al. [11] find asked-for scores beat raw odds. Xiong et al. [12] find steady over-trust. Kuhn et al. [13] add meaning-level spread that beats token odds. Our Confidence field is search closeness rather than self-belief, so we claim no tuning result and report only that high search scores sit next to wrong acts here too.

Attacks on retrieval and tools follow a common shape. Greshake et al. [22] name indirect injection, where orders hidden in fetched text steer the model. Zou et al. [23] prove it for retrieval with PoisonedRAG, where five planted notes steer answers about 90% of the time. Zhan et al. [24] extend it to agents with InjecAgent, 1,054 cases where a top agent breaks in about 25% of runs.

Wallace et al. [25] state the fix as rank order, with system above user above tool. Our leak, override, omission, and translate variants copy this shape at small scale. Prompt injection also tops the OWASP list for LLM applications (OWASP LLM01:2025).

Banking tests show the same act problem at scale. Islam et al. [26] built FinanceBench with 10,231 asks over filings, where a top model with search fails on 81% of a sample. Xie et al. [27] built PIXIU, then Xie et al. [28] built FinBen with 36 sets over 24 tasks, where models pass extraction yet fail reasoning.

Our 100-query study is far smaller but rhymes, since search does not remove the act choice where money sits. EU and Spain bots face oversight and openness duties. The EU AI Act sets human oversight, logging, and care duties for high-risk systems, with human oversight in Art. 14. The 2026 Digital Omnibus moves high-risk application dates (Annex III to 2 December 2027; Annex I products to 2 August 2028) but does not change scope: a general banking support bot is not automatically high-risk; that depends on the Annex use or product scope. Our case-ID hand-off and three-source tags map to that duty at bench scale, with no claim of legal fit.

Recent agentic work sharpens the gap. Liu et al. [31] introduce AgentAbstain, a paired act-versus-abstain benchmark over 263 tasks where the best agent reaches only 59.5% paired accuracy. Luo et al. [33] frame agentic abstention as a sequential stop-versus-act decision over 28,000 tasks, where timing matters as much as the call. Xie et al. [32] diagnose refusal inside multi-hop search over 889 unanswerable items, with the best correct-halting rate only 42.9%. Lin et al. [34] benchmark intermediate capabilities in agentic retrieval workflows. None of these run a paired fast-versus-reasoning comparison on a banking support pipeline with a compliance gate and 2-of-3 majority labels across three five-reason sources.

After our logged search, no study joins all four of: (a) a five-act banking protocol; (b) five structured failure reasons with meanings scored by three sources with majority labels on a search-plus-tools pipeline; (c) paired fast-versus-reasoning runs with the mix stated; (d) scored three-source agreement with Fleiss kappa on refusal. Refusal sets (Kirichenko et al. [2]), safety suites (Röttger et al. [3], Xie et al. [4], Cui et al. [16]), RAG scores (Es et al. [6], Niu et al. [17]-Yang et al. [21]), judge studies (Zheng et al. [7], Tan et al. [29], Wang et al. [30]), and finance sets (Islam et al. [26]-Xie et al. [28]) each cover part. The join is what we add, in 100 queries and with limits stated. Table 1 compares each strand.
