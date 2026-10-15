# lit_search.md — verification log (updated 2026-10-10)

> Rule (§10): no citation enters the paper until verified here
> (title, authors, venue, year, DOI or arXiv ID, retraction check).
> All entries below verified in-session via search + fetch on 2026-10-10.
> No retraction flags found on publisher/arXiv pages checked.

## Query log (2026-10-10)
- `LLM abstention selective prediction survey 2024 2025` → Wen et al. 2025 TACL survey [V1]
- `Zheng et al 2023 MT-Bench` / `Judging LLM as a judge MT-Bench Zheng 2023 arXiv 2306.05685` → Zheng et al. 2023 [V2]
- `Lewis et al 2020 Retrieval-Augmented Generation RAG NeurIPS` → Lewis et al. 2020 [V3]
- `Es et al 2023 RAGAS RAG evaluation` → Es et al. 2024 EACL demo (arXiv 2023) [V4]
- `Rottger et al XSTest over-refusal exaggerated safety` → Röttger et al. 2024 NAACL [V5]
- `Guo et al 2017 calibration modern neural networks ICML` → Guo et al. 2017 [V6]
- `Kadavath et al 2022 Language models know what they know` → Kadavath et al. 2022 arXiv [V7]
- `AbstentionBench reasoning LLMs unanswerable questions 2025` → Kirichenko et al. 2025 [V8]
- `selective classification Geifman El-Yaniv abstention 2017` → Geifman & El-Yaniv 2017 [V9]
- `SORRY-Bench refusal evaluation LLM 2024` → Xie et al. 2024/2025 ICLR [V10]
- `EU AI Act transparency human oversight high-risk official journal 2024` → Regulation (EU) 2024/1689, Art. 14 [V11]
- `prompt injection RAG adversarial robustness 2024 2025` + `LLM01:2025 Prompt Injection OWASP` → OWASP GenAI LLM01:2025 [V12, grey literature]
- `financial domain LLM assistant evaluation banking 2024 2025` → surveyed; no single canonical benchmark found — FinBEN / CreditLLM / deployment reports noted as background only, NOT cited until individually verified.

## Verification table

| # | title | authors | venue | year | DOI / arXiv | match? | retracted? | URL |
|---|---|---|---|---|---|---|---|---|
| V1 | Know Your Limits: A Survey of Abstention in Large Language Models | Wen, Yao, Feng, Xu, Tsvetkov, Howe, Wang | Trans. Assoc. Comput. Linguistics (TACL), vol. 13, pp. 529–556 | 2025 | DOI 10.1162/tacl_a_00754 | yes | no flag on ACL/MIT pages | https://aclanthology.org/2025.tacl-1.26/ |
| V2 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng, Chiang, Sheng, Zhuang, Wu, Li, Lin, Li, Xing, Zhang, Gonzalez, Stoica et al. | Adv. Neural Inf. Process. Syst. (NeurIPS) 2023, Datasets and Benchmarks Track | 2023 | arXiv:2306.05685 | yes | no | https://arxiv.org/abs/2306.05685 |
| V3 | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | P. Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Küttler, M. Lewis, Yih, Rocktäschel, Riedel, Kiela | Adv. Neural Inf. Process. Syst. (NeurIPS) 33, pp. 9459–9474 | 2020 | arXiv:2005.11401 | yes | no | https://arxiv.org/abs/2005.11401 |
| V4 | RAGAs: Automated Evaluation of Retrieval Augmented Generation | Es, James, Espinosa Anke, Schockaert | Proc. EACL 2024 System Demonstrations, pp. 150–158 | 2024 (arXiv 2023) | arXiv:2309.15217 | yes | no | https://aclanthology.org/2024.eacl-demo.16 — https://arxiv.org/abs/2309.15217 |
| V5 | XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models | Röttger, Kirk, Vidgen, Attanasio, Bianchi, Hovy | Proc. NAACL 2024 (Long), pp. 5377–5400 | 2024 | DOI 10.18653/v1/2024.naacl-long.301 / arXiv:2308.01263 | yes | no | https://aclanthology.org/2024.naacl-long.301 |
| V6 | On Calibration of Modern Neural Networks | Guo, Pleiss, Sun, Weinberger | Proc. ICML 2017, PMLR 70, pp. 1321–1330 | 2017 | arXiv:1706.04599 | yes | no | https://proceedings.mlr.press/v70/guo17a.html |
| V7 | Language Models (Mostly) Know What They Know | Kadavath, Conerly, Askell et al. (Anthropic) | arXiv preprint (no published venue; cite as preprint) | 2022 | arXiv:2207.05221 | yes | no | https://arxiv.org/abs/2207.05221 |
| V8 | AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions | Kirichenko, Ibrahim, Chaudhuri, Bell | NeurIPS 2025 poster; arXiv preprint | 2025 | arXiv:2506.09038 | yes | no | https://arxiv.org/abs/2506.09038 |
| V9 | Selective Classification for Deep Neural Networks | Geifman, El-Yaniv | Adv. Neural Inf. Process. Syst. (NeurIPS) 2017 | 2017 | arXiv:1705.08500 | yes | no | https://arxiv.org/abs/1705.08500 |
| V10 | SORRY-Bench: Systematically Evaluating Large Language Model Safety Refusal Behaviors | Xie, Qi, Zeng et al. | Proc. ICLR 2025 | 2025 (arXiv 2024) | arXiv:2406.14598 | yes | no | https://arxiv.org/abs/2406.14598 |
| V11 | Regulation (EU) 2024/1689 (EU Artificial Intelligence Act), Art. 14 Human oversight | European Parliament and Council | Official Journal of the EU, 12 July 2024; in force 1 Aug 2024 | 2024 | ELI Regulation 2024/1689 | yes | n/a (law) | https://artificialintelligenceact.eu/ — https://www.artificial-intelligence-act.com/ |
| V12 | LLM01:2025 Prompt Injection (OWASP Top 10 for LLM Applications) | OWASP Gen AI Security Project | Technical report / project documentation (grey literature, not peer-reviewed) | 2025 | n/a | yes | n/a | https://genai.owasp.org/llmrisk/llm01-prompt-injection |

## Expansion pass 2 (2026-10-10, 20 new entries verified by direct arXiv fetch)

| # | title | authors | venue | year | DOI / arXiv | URL |
|---|---|---|---|---|---|---|
| V13 | Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback | Tian, Mitchell, Zhou, Sharma, Rafailov, Yao, Finn, Manning | Proc. EMNLP 2023, pp. 5433-5442 | 2023 | arXiv:2305.14975 | https://arxiv.org/abs/2305.14975 |
| V14 | Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs | Xiong, Hu, Lu, Li, Fu, He, Hooi | Proc. ICLR 2024 | 2024 | arXiv:2306.13063 | https://arxiv.org/abs/2306.13063 |
| V15 | Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation | Kuhn, Gal, Farquhar | Proc. ICLR 2023 (Spotlight) | 2023 | arXiv:2302.09664 | https://arxiv.org/abs/2302.09664 |
| V16 | Don't Hallucinate, Abstain: Identifying LLM Knowledge Gaps via Multi-LLM Collaboration | Feng, Shi, Wang, Ding, Balachandran, Tsvetkov | Proc. ACL 2024 | 2024 | arXiv:2402.00367 | https://arxiv.org/abs/2402.00367 |
| V17 | R-Tuning: Instructing Large Language Models to Say `I Don't Know' | Zhang, Diao, Lin, Fung, Lian, Wang, Chen, Ji, Zhang | Proc. NAACL 2024 | 2024 | arXiv:2311.09677 | https://arxiv.org/abs/2311.09677 |
| V18 | OR-Bench: An Over-Refusal Benchmark for Large Language Models | Cui, Chiang, Stoica, Hsieh | Proc. ICML 2025 | 2025 | arXiv:2405.20947 | https://arxiv.org/abs/2405.20947 |
| V19 | RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models | Niu, Wu, Zhu, Xu, Shum, Zhong, Song, Zhang | Proc. ACL 2024 (long) | 2024 | arXiv:2401.00396 | https://arxiv.org/abs/2401.00396 |
| V20 | ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems | Saad-Falcon, Khattab, Potts, Zaharia | Proc. NAACL 2024 | 2024 | arXiv:2311.09476 | https://arxiv.org/abs/2311.09476 |
| V21 | Benchmarking Large Language Models in Retrieval-Augmented Generation (RGB) | Chen, Lin, Han, Sun | Proc. AAAI 2024 | 2024 | arXiv:2309.01431 | https://arxiv.org/abs/2309.01431 |
| V22 | FaithEval: Can Your Language Model Stay Faithful to Context, Even If "The Moon is Made of Marshmallows" | Ming, Purushwalkam, Pandit, Ke, Nguyen, Xiong, Joty | Proc. ICLR 2025 | 2025 | arXiv:2410.03727 | https://arxiv.org/abs/2410.03727 |
| V23 | CRAG — Comprehensive RAG Benchmark | Yang et al. (Dong et al.) | Proc. NeurIPS 2024 Datasets & Benchmarks | 2024 | arXiv:2406.04744 | https://arxiv.org/abs/2406.04744 |
| V24 | Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection | Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz | arXiv preprint | 2023 | arXiv:2302.12173 | https://arxiv.org/abs/2302.12173 |
| V25 | PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models | Zou, Geng, Wang, Jia | Proc. USENIX Security 2025 | 2025 | arXiv:2402.07867 | https://arxiv.org/abs/2402.07867 |
| V26 | InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents | Zhan, Liang, Ying, Kang | Proc. ACL 2024 Findings | 2024 | arXiv:2403.02691 | https://arxiv.org/abs/2403.02691 |
| V27 | The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions | Wallace, Xiao, Leike, Weng, Heidecke, Beutel | arXiv preprint (OpenAI) | 2024 | arXiv:2404.13208 | https://arxiv.org/abs/2404.13208 |
| V28 | FinanceBench: A New Benchmark for Financial Question Answering | Islam, Kannappan, Kiela, Qian, Scherrer, Vidgen | arXiv preprint (Patronus AI) | 2023 | arXiv:2311.11944 | https://arxiv.org/abs/2311.11944 |
| V29 | PIXIU: A Large Language Model, Instruction Data and Evaluation Benchmark for Finance | Xie, Han, Zhang, Lai, Peng, Lopez-Lira, Huang | Proc. NeurIPS 2023 Datasets & Benchmarks | 2023 | arXiv:2306.05443 | https://arxiv.org/abs/2306.05443 |
| V30 | FinBen: A Holistic Financial Benchmark for Large Language Models | Xie et al. (34 authors) | arXiv preprint | 2024 | arXiv:2402.12659 | https://arxiv.org/abs/2402.12659 |
| V31 | JudgeBench: A Benchmark for Evaluating LLM-based Judges | Tan, Zhuang, Montgomery, Tang, Cuadron, Wang, Popa, Stoica | Proc. ICLR 2025 | 2025 | arXiv:2410.12784 | https://arxiv.org/abs/2410.12784 |
| V32 | Large Language Models are not Fair Evaluators | Wang, Li, Chen, Cai, Zhu, Lin, Cao, Liu, Liu, Sui | arXiv preprint | 2023 | arXiv:2305.17926 | https://arxiv.org/abs/2305.17926 |

All 20 above: title/authors/venue/year confirmed against arXiv abs page (Comments field for venue) on 2026-10-10; abstract matches topic; no retraction flags. Venue years: ICLR/ICML/ACL/NAACL/AAAI/USENIX/EMNLP per Comments; preprints marked as arXiv preprint in the paper list.

## Gap statement (what the search shows, 2026-10-10, updated after 32-entry verification)
- Abstention is surveyed as query/model/human-values framework (V1) and benchmarked at scale across 20 datasets and 6 scenarios (V8), with the finding that reasoning tuning can degrade abstention.
- Refusal is tested both ways: exaggerated safety / over-refusal (V5) and systematic safety refusal with balanced taxonomy (V10).
- RAG is founded (V3) and its faithfulness/relevance evaluated reference-free (V4), but neither judges behaviour choice (answer vs clarify vs abstain vs escalate vs refuse).
- LLM-as-judge is scaled via MT-Bench/Arena (V2) with known position/verbosity biases, but judge reliability specifically on abstention decisions in a high-stakes domain is thinly quantified.
- Selective classification (V9) and calibration (V6, V7) treat the answer/abstain trade-off formally, but on classifiers and short QA, not on RAG agents with retrieval + tools + compliance gates.
- What we did not find in this session: a behaviour-conditional, human-verified study of a banking-support RAG agent that (a) stratifies by expected behaviour, (b) builds a failure taxonomy bottom-up from rater reasons, and (c) quantifies judge-vs-human disagreement on abstention. That is the stated gap for this paper — framed as "to our knowledge after this search" and pending a fuller 50–70-ref sweep.
- TODO for full venue bar: verify 40–60 more (faithfulness beyond RAGAS, calibration elicitation 2024–2026, prompt-injection defences for RAG, FinBEN/financial benchmarks, OR-Bench over-refusal, human-oversight doctrine). No gap claim beyond the above until those are logged.

## 2026-10-10 revision verification (4 arXiv + EU Omnibus, all fetched in-session)
- V33 AgentAbstain 2607.10059: X. Liu et al., "AgentAbstain: Do LLM Agents Know When Not to Act?", arXiv:2607.10059 [cs.AI], submitted 11 Jul 2026, 56pp. Verified via https://arxiv.org/abs/2607.10059 (title/authors/date/ID match). Use: agentic abstention paired benchmark; gap context.
- V34 HopRefusalBench 2608.01358: J. Xie et al., "HopRefusalBench: Diagnosing Refusal Failures in Search-Augmented Agents for Multi-Hop Reasoning", arXiv:2608.01358 [cs.CL], submitted 2 Aug 2026, 20pp. Verified via https://arxiv.org/abs/2608.01358. Use: refusal in multi-hop search; gap context.
- V35 Agentic Abstention 2606.28733: H. Luo, B. Wen, L. L. Wang, "Agentic Abstention: Do Agents Know When to Stop Instead of Act?", arXiv:2606.28733 [cs.AI], submitted 27 Jun 2026. Verified via https://arxiv.org/abs/2606.28733. Use: sequential stop-vs-act framing; gap context.
- V36 RAGCap-Bench 2510.13910: J. Lin et al., "RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic RAG Systems", arXiv:2510.13910 [cs.CL], v1 15 Oct 2025, v2 21 May 2026. Verified via https://arxiv.org/abs/2510.13910. Use: agentic RAG capability benchmark; gap context.
- EU Digital Omnibus: Regulation (EU) 2026/1744, OJ 24 Jul 2026, in force 27 Jul 2026; verified via EUR-Lex https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng and summary https://eur-lex.europa.eu/EN/legal-content/summary/rules-for-trustworthy-artificial-intelligence-in-the-eu.html. Amends AI Act high-risk dates (Annex III 2 Dec 2027; Annex I 2 Aug 2028). Support bot not auto high-risk (risk-based Annex I/III scope). Secondary reporting (Paul Weiss, DLA Piper) consistent; EUR-Lex is source of truth.
- Full 50-70 sweep still pending beyond these 4; gap statement bounded to V1-V36 search.

## Re-verification 2026-10-15 (refs 33-34, webfetch)
- [33] arXiv:2606.28733 (Han Luo, Bingbing Wen, Lucy Lu Wang, "Agentic Abstention: Do Agents Know When to Stop Instead of Act?", 27 Jun 2026): title/authors MATCH references.md initials; "more than 28,000 tasks" MATCHES manuscript "over 28,000 tasks". CONVOLVE 26.7->57.4 in abstract, not quoted in manuscript (ledger only). Discussion contrast "reasoning improves timely but lowers overall recall" NOT in abstract -> REMOVED and replaced with abstract wording on 2026-10-15.
- [34] arXiv:2510.13910 (Jingru Lin, Chen Zhang, Stephen Y. Liu, Haizhou Li, "RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic Retrieval Augmented Generation Systems", v1 15 Oct 2025, v2 21 May 2026): title/authors MATCH; year 2025 kept; manuscript quotes no numbers; "benchmark intermediate capabilities" MATCHES abstract. No change.
