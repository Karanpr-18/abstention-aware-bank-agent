# Abstention-Aware Banking Agent

A reliability and safety testbed evaluating when an AI financial support assistant should answer, clarify, or abstain ("I don't know") rather than provide ungrounded or misleading answers. The repository contains the multi-agent CrewAI RAG architecture, knowledge base scrapers, vector index builders, benchmark datasets, experiment runners, evaluators, and a full-stack evaluation and concierge interface.

---

## Overview

Most retrieval-augmented generation (RAG) benchmarks measure whether an answer is factually correct given adequate context. In customer-facing banking and financial services, an equally vital question is: **does the agent recognize when it lacks sufficient information or when answering poses a compliance risk?** Confident misinformation on credit eligibility or fraud procedures is far more harmful than a measured abstention with referral to a human specialist.

This system implements and evaluates three operational modes:
- **Mode A (Direct / Baseline)**: Standard generation pass-through without abstention constraints.
- **Mode B (Threshold-Guided)**: Gated response conditioned on cosine similarity retrieval thresholds.
- **Mode C (Abstention-Aware)**: Multi-agent compliance gating trained to abstain, escalate, or clarify when queries are ambiguous, high-stakes, or out-of-scope.

---

## Repository Structure

```
├── data/                       # Benchmark query datasets with gold expected behaviors
│   ├── queries_gold.json       # Core gold evaluation queries (clear, ambiguous, out-of-scope, high-stakes, adversarial)
│   ├── queries_extra.json      # Additional verified test queries
│   └── queries_extra2.json     # Extended query set
├── kb_raw/                     # Curated banking knowledge base dataset (66 policies & FAQs)
│   ├── manifest.json           # Source URLs, bank origins, topic tags, and metadata
│   └── *.md                    # Normalized knowledge documents across 16 global banks
├── src/                        # Core agent, index, evaluation, and bridge code
│   ├── crew_agent.py           # Multi-agent architecture (Retriever, Banker Specialist, Compliance Gate)
│   ├── build_index.py          # Document chunking (MiniLM-L6-v2) and ChromaDB persistent indexing
│   ├── scrape_kb.py            # Automated extractor for banking policies & FAQ documentation
│   ├── tools.py                # Synthetic loan eligibility & fraud escalation tools
│   ├── run_experiments.py      # Batch experiment runner (queries × modes × models × repeats)
│   ├── evaluate.py             # Evaluation harness (heuristic & LLM-as-judge scoring)
│   ├── judge.py                # Standalone satisfaction judge with strict rubric validation
│   └── opencode_bridge.py      # OpenAI-compatible API bridge for local model execution
├── webapp/                     # Full-stack evaluation harness and chat application
│   ├── backend/app.py          # FastAPI backend (chat API, batch runners, job tracking)
│   └── frontend/               # React + Tailwind + Vite client (Concierge chat & Registry testbed)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable configuration template
├── start.sh                    # Startup script for bridge and webapp services
└── stop.sh                     # Service shutdown script
```

---

## Datasets

1. **Banking Knowledge Base (`kb_raw/`)**:
   - 66 markdown documents covering account terms, personal loan policies, credit card regulations, and anti-fraud guidelines from 16 leading institutions across the US, UK, China, India, France, Germany, Switzerland, Spain, and Japan.
   - Complete provenance and metadata in [`kb_raw/manifest.json`](file:///home/karan/Desktop/RAG%20research/kb_raw/manifest.json).

2. **Gold Query Benchmarks (`data/`)**:
   - Stratified queries categorised into:
     - `clear`: Explicit queries decidable directly from the knowledge base.
     - `ambiguous`: Queries with incomplete user details requiring clarification.
     - `out_of_scope`: Queries outside banking support (e.g., tax, legal, medical, investment advice) requiring strict abstention.
     - `high_stakes`: Sensitive financial or fraud actions requiring human escalation.
     - `adversarial`: Prompt injections or policy bypass attempts testing guardrails.

---

## Getting Started

### 1. Prerequisites & Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Add your `GROQ_API_KEY` and/or `GEMINI_API_KEY` as needed.

### 3. Build Knowledge Base & Vector Index

```bash
# Scrape or refresh policy documentation (optional if kb_raw is already populated)
python src/scrape_kb.py

# Chunk and index markdown documents into ChromaDB
python src/build_index.py
```

### 4. Running the Agent

Run an individual query via CLI:

```bash
# Mode A: Baseline
python -m src.crew_agent "What are the eligibility criteria for an HDFC personal loan?" --mode A

# Mode C: Abstention-aware
python -m src.crew_agent "Should I invest all my savings in crypto?" --mode C
```

---

## Evaluation & Benchmarking

Execute automated evaluation runs across models, modes, and query sets:

```bash
# Run batch generation experiment
python src/run_experiments.py --repeats 5 --thresholds 0.3 0.5 0.7 --delay 3

# Compute metrics (accuracy, false confidence, appropriate abstention, helpfulness)
python src/evaluate.py --runs "logs/runs_*.jsonl" --judge
```

---

## Web Application

Launch both the background model bridge and the full-stack web application:

```bash
./start.sh
```

- Webapp UI: `http://localhost:8000`
- Interactive Concierge Chat: real-time live retrieval and compliance stream.
- Testbed Registry: batch evaluation management, per-card generation review, and live progress auditing.

To stop the services:
```bash
./stop.sh
```
