# abstention-aware-bank-agent

When should an AI banking assistant say "I don't know"? A reliability testbed:
a CrewAI RAG agent over real policies from 16 global banks, evaluated on
abstention behaviour across 3 response modes and 100 gold-labelled queries.

## What this is

Most RAG work asks *"is the answer correct?"* This study asks the production
question: *"does the system know when it should NOT answer?"* A confidently
wrong loan/fraud answer is worse than an honest referral to a human. The repo
builds the agent, then measures false-confidence, abstention precision/recall,
helpfulness, and run-to-run consistency — including a cheap-vs-capable model
comparison.

## Layout

- `src/crew_agent.py` — the agent: Retriever → Banking Specialist → Compliance
  Gate (CrewAI only), 3 modes (A always-answer baseline, B threshold-guided,
  C abstention-aware), simulated `check_loan_eligibility` / `flag_fraud_report`
  tools in `src/tools.py`
- `src/opencode_bridge.py` — OpenAI-compatible bridge in front of `opencode run`
- `src/scrape_kb.py`, `src/build_index.py` — KB scrape (34 real bank pages +
  policy docs + manual PDFs) → chunk → MiniLM → Chroma
- `src/run_experiments.py`, `src/evaluate.py` — query × mode × repeat runner,
  heuristic + LLM-judge scoring
- `data/queries_gold.json`, `data/queries_extra.json` — 100 questions, 10 per
  type (clear / ambiguous / out-of-scope / high-stakes / adversarial) with gold
  expected behaviour; gold never enters any prompt
- `kb_raw/` — the dataset (66 real docs; `manual_downloads/` holds source HTML/PDFs)
- `results/` — batch run Excels (question, agent answer, expected, verdicts)
- `webapp/` — FastAPI + React heritage-UI: chat room + researcher eval harness
  (batch runs of 20, per-card live progress, Excel export)
- `check_satisfaction.py` — standalone YES/NO auditor (own judge, 5 reasons)

## Quickstart

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # add GROQ_API_KEY and/or GEMINI_API_KEY
.venv/bin/python src/scrape_kb.py
.venv/bin/python src/build_index.py
./start.sh              # bridge :8378 + app :8000 -> http://localhost:8000
```

Batch eval + Excel:
```bash
.venv/bin/python src/run_experiments.py --repeats 5 --thresholds 0.3 0.5 0.7 --delay 8
.venv/bin/python src/evaluate.py --runs "logs/runs_*.jsonl" [--judge]
.venv/bin/python check_satisfaction.py --in "Rag results.xlsx" --out judged.xlsx
```

## Key design points

- Abstention is the model's own decision — no scripted denial sentences anywhere;
  scoring reads its words observationally (`is_abstention`)
- Mode A is a true pass-through baseline; B/C add threshold guidance and
  abstention-awareness respectively
- Model catalogue lives in one place (`MODELS` in `crew_agent.py`); the UI
  dropdown and all runners read from it
