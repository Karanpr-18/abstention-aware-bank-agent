# 3. Methodology

## 3.1 Task

We study a banking help agent built as a large language model (LLM) (Wen et al. [1]) with retrieval-augmented generation (RAG) (Lewis et al. [5]). Per query it picks one of five acts: answer, clarify, abstain, escalate, or refuse. Abstain means decline or hand to a human. Escalate means log and refer on. Refuse means firmly block an attack. A reply passes only on the expected act, not on smooth wording. This behaviour-first protocol (C1) extends the abstention survey of Wen et al. [1] and the RAG rejection splits of Chen et al. [19] to support work with a gate and tools.

## 3.2 Query set

The set has 100 hand-written queries in two batches of 50, joined before runs. Each of five types has 20. Table 2 lists gold splits; the design plot is in the Appendix. The gold field is the expected act.

Clear (20) are settled by the knowledge base, e.g. SBI pay floors and FBI report steps; gold is answer throughout. Ambiguous (20) lack facts; gold is clarify for 9 and answer for 11 the knowledge base still settles. Out-of-scope (20) ask stock, tax, legal, or off-topic help; gold is abstain throughout.

High-stakes (20) touch fraud, sureties, and privacy; gold is escalate for 14, answer for 3 safety rules, refuse for 2, clarify for 1. Adversarial (20) use jailbreaks, role play, and omission tricks; gold is refuse throughout, mirroring the hidden-instruction attacks of Greshake et al. [22] and the tool-agent attacks of Zhan et al. [24] at small scale. Gold totals are answer 34, clarify 10, abstain 20, escalate 14, refuse 22. Same queries run on both tiers, so tests pair by query. Query texts are archived with the study materials and scored replies live in the verified workbook.

## 3.3 Knowledge base and search

The knowledge base holds 64 markdown files from public bank help pages across eight countries, plus four hand-saved PDFs (1788 indexed chunks in collection bank_kb). Eight script-made policy notes exist in archived code only (0 synthetic files indexed), and we claim no search over them. Figure 1 summarises the workflow. Full component settings are in the Appendix.

Files are cut into 1000-character spans (overlap 200, drop under 200). Vectors use MiniLM embeddings in a fresh ChromaDB store (cosine). Each query pulls the top 4 spans. The sources field often repeats one file, showing span hits without dedup. We report this as seen.

`Confidence` is top-1 search closeness (1 minus cosine gap), not model self-belief (Tian et al. [11], Xiong et al. [12], Kuhn et al. [13]). Section 4.6 is thus a search-score check, marked as exploratory.

## 3.4 Agent and tools

One flow serves both tiers. Three agents run in turn: retriever, banking writer, compliance gate. The writer drafts from context only (max 80 words) and may call two mock tools. The gate passes safe drafts or swaps risky ones for a short decline plus referral (max 40 words), a weak rank order of Wallace et al. [25] where system rules should beat user and fetched text. Section 4.4 shows where it slips. One mock tool checks loan eligibility by fixed cut-offs and returns need-info, deny, or review. The other logs a fraud report with a case ID plus hand-off; it never calls fraud.

The stored abstention flag scans the opening text for decline words and misses soft forms. We keep it as stored. Main runs used provider defaults with no temperature, top-p, or seed set; the original automated mark alone used temperature 0. The reasoning tier ran as the xhigh model variant with per-run effort unlogged. One row per query per tier means one run each, a stated limit. Tuning tricks like R-Tuning of Zhang et al. [15] are out of scope. Full prompts and decoding notes are in the Appendix.

## 3.5 Models

We compare `glm-5.3-flash` (fast tier) with `muse-spark-1.3-xhigh` (reasoning tier, run at xhigh as the model variant). The mix is plain: vendor, size, and reasoning mode differ at once. Nothing splits reasoning apart as a cause, a care Kirichenko et al. [2] earn on AbstentionBench. We report only what this sample shows.

## 3.6 Scoring protocol

The primary label is the 2-of-3 majority across three five-reason sources on the verified workbook (sheets `glm` and `muse`, 100 rows each). The sources are the author rating, a classmate check, and a third-model check, each recorded as pass or fail with one of five structured reasons: Overreach (went beyond its role), Unsupported Assumption (assumed facts not given), Oversharing (shared unnecessary internal information), Soft Refusal (refusal not firm enough), Failure to Answer (abstained when answer existed). A reply counts as a majority miss when at least two of the three flag it. Its consensus reason is the reason named by at least two of the three sources; where no two agree it is Mixed. No tie-break rule is used. No adjudication was done: disagreements were not resolved by discussion or a tie-breaker. The 2-of-3 majority of author, classmate and third-model labels is the primary label, chosen after seeing disagreement across the three sources. The per-ID file (200 replies) lists all three sources plus the majority without resolving disagreements.

One author rater scored each tier with a cross-check by the other rater. The initial rating flagged 20 replies (10 per tier) and the cross-check added 11 more to reach 31 author flags (17 fast, 14 reasoning). No per-ID addition log was kept for that step, so no kappa is reported for it. The majority step is fully logged per ID, so Fleiss kappa is reported for the three sources. The original automated mark (four labels at temperature 0) is not part of the majority and is reported separately as a sensitivity source. By author account each tier was first judged by the same model that answered it, so it shares blind spots. The classmate column is reported as supplied with no logged prompt or blinding protocol. The third-model column uses the archived satisfaction-checker prompt in Appendix C, which sends only question plus expected behaviour plus agent answer and is blind to model identity and prior labels; its coded model is opencode/mimo-v2.6-flash-free with max_tokens 150, timeout 240 s and no temperature set (provider default), so the cells are reported as supplied.

Rule: the majority is truth for the headline; rates count majority misses. Sensitivity shows each source beside the majority. This fits the judge research of Zheng et al. [7] on place and length bias, Wang et al. [30] on order flips, and Tan et al. [29] on near-chance scores on hard items.

## 3.7 Measures and stats

Positive means "should not just answer" (clarify, abstain, escalate, refuse; 66 of 100). The sign is the stored abstention flag. The Appendix reports accuracy, precision, recall, F1, plus withheld-answer rate on answer-expected items, the over-refusal worry of Cui et al. [16] on OR-Bench and Röttger et al. [3] on XSTest moved to banking.

Shares carry Wilson 95% confidence intervals. Paired splits use exact McNemar on the same queries, whole and per type with Holm fix. Three-rater agreement uses Fleiss kappa pooled over both tiers by type (200 replies overall; 40 per type), with percent agreement and Gwet AC1 beside it; per-tier Fleiss is archived for traceability. The headline comparison is the majority by type; each source is shown beside it. Response times are reported as stored only. Scripts build all tables, and each number is produced by a script. Reasons are defined once in Table 4 and short labels are used afterwards. Planned tests are confirmatory; the analyses in Section 4.6 are exploratory and marked as such.

For planning, a two-proportion calculation (alpha 0.05, power 0.8) gives about 49 queries per group to detect 25% versus 5% and about 199 per group to detect 20% versus 10%. Paired totals of about 56 and 233 are the same order once discordant-pair assumptions are added. Full component settings and prompts are in the Appendix.

## 3.8 Ethics and data

Queries are hand-written; pages are public bank notes or mocks. No client data appears. The rig is a bench test, not advice software. Provider data rules cover API calls. Names are placeholders with no funding to state. Queries and tags are not released in this manuscript; no release link is claimed. The authors verify every claim and number and are accountable for the paper. AI assistance was used for drafting and analysis scripts under author supervision and is disclosed here as required; AI is not listed as an author.
