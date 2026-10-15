# 5. Discussion

Reasons are defined once in Table 4 and runs are single. Majority labels across the author, classmate, and third-model sources are primary. We claim no cause for tier gaps; the vendor-size-reasoning mix holds in each reading.

## 5.1 What the majority shows

The headline is the majority: 11 of 100 fast-tier and 13 of 100 reasoning-tier misses, tied (McNemar p 0.80). Figure 3 shows misses rarely sharing a query (both pass 80; only fast 7; only reasoning 9; both fail 4). Under consensus the reason counts are fast Mixed 7 of 11 with consensus Failure to Answer 2, Overreach 1, and Unsupported Assumption 1, and reasoning consensus Failure to Answer 8 of 13 with Oversharing 1, Soft Refusal 1, and Mixed 3. The Appendix adds that search scores, length, breadth, and response time do not explain the pattern.

Two patterns hold in every source. First, answerability on ambiguous and clear queries. Fast ambiguous misses are 5 author, 6 third-model, 5 classmate, majority 6 of 20. Reasoning ambiguous are 2, 8, 8, majority 7, and reasoning clear are 2, 7, 2, majority 2. Plain cases recur: the Rs.25,000 floor, Chase options, and FBI steps are flagged by the majority on the reasoning tier, with further ambiguous flags on the fast tier. Second, the reasoning tier withholds answerable replies. Failure to Answer counts are 8 of 13 majority misses on the reasoning tier, against 2 of 11 on the fast tier. Luo et al. [33] report scale, reasoning and scaffolding affect abstention in different ways, with larger or more capable models sometimes worse at timely abstention; our reasoning tier shows consensus Failure to Answer on answerable queries, which we state as a contrast, not as an explanation.

Adversarial refusals are the contested zone. The author source alone shows fast 6 of 20 and reasoning 8 of 20, but the other two sources show 1 and 2 of 20 on each tier, leaving majorities of 2 and 1. We therefore describe refusal wording on attacks as contested, not as a tier shape.

We make no opposing-shape claim. The majority reason mix differs between tiers but with 11 and 13 misses the test base is thin, and the mix shifts with the source. With 20 queries per type, confidence intervals are wide and no paired test separates the tiers (overall McNemar on the majority p 0.80). For planning, a two-proportion calculation (alpha 0.05, power 0.8) gives about 49 queries per group to detect 25% versus 5% and about 199 per group to detect 20% versus 10%; paired totals of about 56 and 233 are the same order once discordant-pair assumptions are added. Replication at larger n with repeated runs is needed.

Kirichenko et al. [2] earn this care on AbstentionBench. Feng et al. [14] agree refusal must be built and checked with team-of-models work. Agreement figures are read here as source sensitivity only: pooled Fleiss kappa 0.32 overall, 0.47 ambiguous strongest and 0.10 adversarial weakest (Table 6; Figure 4), while the original automated mark agrees with the author on 71/100 fast and 78/100 reasoning, falling to 13/20 and 11/20 on adversarial queries, with mismatches both ways (16 and 35).

## 5.2 Candidate controls (untested, held for future work)

Table notes list candidate controls, but none was tested in this study, so none is a recommendation here. Each is held for future work in Section 6. Ambiguous cases motivate a future no-verdict-without-inputs test, and refusal can be taught portable (Zhang et al. [15]). Withheld answers motivate a future answerable check that re-runs when refusal tuning shifts, the both-directions care of Cui et al. [16] on OR-Bench.

Oversharing cases motivate a future brevity plus secrecy test. Soft Refusal cases motivate a future firm-stop wording test. Overreach cases motivate a future role-scope test. Human review of attack and high-stakes bands is current practice in the studied rig, not a tested fix; whether a judge can triage, best tuned with human tags ARES-style (Saad-Falcon et al. [18]), is also future work.

## 5.3 Regulatory note

EU and Spain deployments face transparency and human-oversight expectations. The EU AI Act sets oversight, logging, and care duties for high-risk systems, with human oversight in Art. 14. The 2026 Digital Omnibus (in force 27 July 2026) moves high-risk application dates (Annex III to 2 December 2027; Annex I products to 2 August 2028) but does not change scope: a general banking support bot is not automatically high-risk; that depends on the Annex use or product scope. Our case-ID hand-off and three-source tags are consistent with that duty at bench scale only. Prompt injection tops the OWASP LLM list with retrieved text as carrier (OWASP LLM01:2025). We claim no legal conformity; live use needs counsel.

## 5.4 Limits

Sample is 100 queries (20 per type, one run each), so confidence intervals are wide and tier gaps rarely split. Queries are hand-written. The knowledge base is small with one set-up (64 files plus four PDFs, top-4, MiniLM). Main runs used provider defaults with no temperature, top-p, or seed set; the original automated mark alone used temperature 0; the reasoning tier ran as the xhigh model variant with per-run effort unlogged. Tier splits mix vendor, size, and reasoning at once. The author step rests on a two-stage pass (20 to 31 flags) with no per-ID log, so no kappa there; the three-source majority step is fully logged per ID with Fleiss kappa reported. Reasons are the supplied five with a Mixed bucket where no two sources agree, with no separate bucket for disputed cases. The classmate column is reported as supplied with no logged prompt or blinding protocol. The third-model prompt and coded model are logged in the archived checker (Appendix C). Free-tier routing rules response times (68.3 s fast, 40.0 s reasoning; Appendix), logged, not parsed. No real users. The reference list holds 34 verified entries. Each bound caps our claims.

## 5.5 Risks to trust

Small samples first: we meet them with Wilson confidence intervals, exact paired tests plus Holm (Table 3), and a tie headline. Source sensitivity second: we show every source side by side (Figure 2; Table 3) and keep only what the majority keeps. The mix third: named in Methods, Results, Discussion, and Limits, with same-model off-versus-high as next work.

Rater slant fourth: majority reasons plus IDs (Tables 4 and 5), per-ID log with all three sources plus majority, blind re-tags proposed for kappa. One-rig scope fifth: knowledge base, spans, vectors, pull, prompts, tools, and detector logged as built, no claim past this bench. Detector flaws sixth: abstention flag as stored only with majority truth (Figure 4).
