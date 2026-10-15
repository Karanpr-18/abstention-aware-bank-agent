"""
CrewAI agentic wrapper over the same Chroma KB + pluggable model providers + simulated tools.
Keeps the 3-mode comparison intact: run_crew_query() returns the same dict
shape as the experiment runner expects (answer, abstained, confidence, chunks, tool, latency, model).

Crew: retriever -> banker -> compliance gate (Mode B threshold / Mode C hard denial).
Run with: .venv/bin/python -m src.crew_agent "your question" --mode C
Requires: provider keys in .env (copy .env.example).
"""
import os, sys, time, argparse
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from pydantic import Field

from src.tools import check_loan_eligibility as _elig, flag_fraud_report as _fraud

# Model catalog — the ONLY place models are defined. The UI dropdown reads this via /api/models.
# Code keeps the full gateway ID (name); frontend shows only the short label.
MODELS = [
    {"id": "opencode/muse-spark-1.3-xhigh", "provider": "opencode", "name": "opencode/muse-spark-1.3-contributor-free#xhigh",
     "label": "Muse Spark 1.3", "hint": "via OpenCode · xhigh"},
    {"id": "opencode/ling-3.1-flash", "provider": "opencode", "name": "opencode/ling-3.1-flash-free",
     "label": "Ling 3.1 Flash", "hint": "via OpenCode"},
    {"id": "opencode/nemotron-3-ultra", "provider": "opencode", "name": "opencode/nemotron-3-ultra-free",
     "label": "Nemotron 3 Ultra", "hint": "via OpenCode · lenient judge"},
    {"id": "opencode/mimo-v2.6", "provider": "opencode", "name": "opencode/mimo-v2.6-flash-free",
     "label": "Mimo v2.6", "hint": "via OpenCode · max reasoning"},
    {"id": "opencode/space-bunny-max", "provider": "opencode", "name": "opencode/space-bunny-free",
     "label": "Space Bunny", "hint": "via OpenCode · max"},
]
DEFAULT_MODEL = "opencode/space-bunny-max"
BY_MODEL = {m["id"]: m for m in MODELS}

DECLINE_GUIDANCE = "decline to answer and refer the user to a human specialist"

DECLINE_PATTERNS = [
    "i don't know", "i do not know", "do not know", "don't know",
    "i'm not sure", "i am not sure", "not sure", "uncertain",
    "i'm unable", "i am unable", "unable to answer", "unable to help",
    "unable to determine", "not able to", "cannot answer", "can't answer",
    "cannot determine", "can't determine", "cannot confirm", "can't confirm",
    "cannot advise", "can't advise", "cannot provide", "can't provide",
    "outside my scope", "beyond my scope", "not within my scope",
    "beyond what i can", "not something i can", "can't help with",
    "human specialist", "human advisor", "human agent", "human officer",
    "specialist", "escalat", "refer you", "refer this",
    "decline to", "must decline", "have to decline",
    "don't have enough", "do not have enough", "insufficient information",
    "lack sufficient", "not enough information",
]

def is_abstention(answer: str) -> bool:
    """Observational detector only — checked against the model's own words.
    Looks at the opening (first 300 chars) for decline signals, so a 'cannot'
    buried mid-answer (e.g. eligibility criteria) doesn't count."""
    opening = answer.lower()[:300]
    return any(p in opening for p in DECLINE_PATTERNS)

import re as _re

def clean_final(text: str) -> str:
    """Remove leaked reasoning scaffolding from final outputs (formatting hygiene only).
    Covers <think>, <thinking>, <thought>, <reasoning> tags — including unclosed
    ones from cut-off generations — case-insensitively."""
    if not text:
        return text
    # remove complete tag pairs and their contents
    t = _re.sub(r"<(think|thinking|thought|reasoning)[^>]*>.*?</\1>", "", text,
                flags=_re.DOTALL | _re.IGNORECASE)
    # drop any orphaned opening tag and everything after it (truncated generation)
    t = _re.sub(r"<(think|thinking|thought|reasoning)[^>]*[\s\S]*$", "", t,
                flags=_re.IGNORECASE)
    # drop stray closing tags
    t = _re.sub(r"</(think|thinking|thought|reasoning)>", "", t, flags=_re.IGNORECASE)
    return t.strip()

import threading as _threading
_LOCK = _threading.Lock()
_COL = None
_EMB = None

def _chroma_hits(query: str, k: int = 4):
    """Retrieval with process-wide cached Chroma collection + embedding model.
    (Previously reloaded the transformer weights on every call — the 'Loading weights'
    lines in the server log and seconds of overhead per query.)"""
    global _COL, _EMB
    import chromadb
    from sentence_transformers import SentenceTransformer
    with _LOCK:
        if _COL is None:
            _COL = chromadb.PersistentClient(path=os.environ.get("CHROMA_DIR", "./chroma_db")).get_collection("bank_kb")
        if _EMB is None:
            _EMB = SentenceTransformer("all-MiniLM-L6-v2")
        col, emb = _COL, _EMB
    qv = emb.encode(query).tolist()
    res = col.query(query_embeddings=[qv], n_results=k, include=["documents", "distances", "metadatas"])
    out = []
    for d, dist, m in zip(res["documents"][0], res["distances"][0], res["metadatas"][0]):
        out.append({"text": d, "similarity": 1 - dist, "source": m.get("source_file")})
    return out

class RetrievalTool(BaseTool):
    name: str = "kb_retrieve"
    description: str = "Retrieve banking FAQ/policy chunks from the Chroma KB. Input: user question. Returns top chunks with similarity scores and source files."
    def _run(self, query: str) -> str:
        hits = _chroma_hits(query)
        return "\n\n---\n\n".join(f"[{h['source']} sim={h['similarity']:.2f}] {h['text'][:1200]}" for h in hits)

class LoanTool(BaseTool):
    name: str = "check_loan_eligibility"
    description: str = ("Check loan eligibility. Pass values you extract from the user, labelled like: "
                        "income=<monthly income number>, credit=<credit score int>, amount=<loan amount number>. "
                        "Anything you do not label is treated as missing and returns need_info — never guess positions.")
    def _run(self, query: str) -> str:
        import re
        def grab(*pats):
            for p in pats:
                m = re.search(p, query, re.IGNORECASE)
                if m:
                    try:
                        return float(m.group(1).replace(",", ""))
                    except (ValueError, IndexError):
                        pass
            return None
        income = grab(r"income\s*[=:]\s*([\d,]+\.?\d*)", r"\$\s*([\d,]+)\s*(?:per month|/mo|monthly|income)")
        credit = grab(r"credit(?:\s*score)?\s*[=:]\s*([\d,]+)")
        amount = grab(r"(?:amount|loan)\s*[=:]\s*([\d,]+\.?\d*)")
        try:
            credit_i = int(credit) if credit is not None else None
            return str(_elig(income, credit_i, amount))
        except Exception as e:
            return str({"decision": "need_info", "reason": str(e)})

class FraudTool(BaseTool):
    name: str = "flag_fraud_report"
    description: str = "Log a fraud concern. Returns a case ID + escalation message. NEVER returns a fraud verdict."
    def _run(self, query: str) -> str:
        return str(_fraud(query))

def _buyer_identity() -> str:
    """Antseed gateway attributes quota to the buyer identity header.
    Rotate to a fresh identity for a new quota: ANTSEED_BUYER_IDENTITY=new-name."""
    return os.environ.get("ANTSEED_BUYER_IDENTITY", "project-agent-1")

def _llm(provider: str, name: str, identity: str | None = None):
    """Provider wiring. Groq/local/opencode via OpenAI-compatible endpoints, Gemini via CrewAI native provider.
    identity=None omits the buyer header (default gateway buyer); a name sets it."""
    if provider in ("groq", "local", "opencode"):
        if provider == "groq":
            key = os.environ.get("GROQ_API_KEY")
            base = "https://api.groq.com/openai/v1"
            headers = None
            if not key:
                raise RuntimeError("GROQ_API_KEY missing — add it to .env (free at console.groq.com).")
        elif provider == "local":
            key = os.environ.get("LOCAL_API_KEY", "antseed")
            base = os.environ.get("LOCAL_BASE_URL", "http://localhost:8377/v1")
            ident = identity if identity is not None else _buyer_identity()
            headers = {"x-antseed-buyer-identity": ident} if ident else None
        else:
            key = os.environ.get("OPENCODE_API_KEY", "opencode")
            base = os.environ.get("OPENCODE_BASE_URL", "http://localhost:8378/v1")
            headers = None
        llm = LLM(model=name, custom_openai=True, base_url=base, api_key=key,
                  default_headers=headers,
                  reasoning_effort=os.environ.get("REASONING_EFFORT", "high") if provider in ("local", "groq") else None)
        # CrewAI routing strips known prefixes (openai/...) which some gateways
        # require verbatim (Groq 404s). Restore the full ID post-hoc;
        # the native provider sends self.model verbatim.
        object.__setattr__(llm, "model", name)
        return llm
    if provider == "gemini":
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY missing — add it to .env (free at aistudio.google.com).")
        return LLM(model=f"gemini/{name}", api_key=key)
    raise RuntimeError(f"Unknown provider '{provider}'. Choose from the UI catalogue.")

def _check_bridge(base: str):
    """Fail fast with a human message when the OpenCode bridge isn't running,
    instead of burning minutes on retries against a dead port."""
    import requests
    try:
        # base already ends in /v1 — append only /models, not /v1/models
        r = requests.get(base.rstrip("/") + "/models", timeout=5)
        r.raise_for_status()
    except Exception:
        raise RuntimeError(
            f"OPENCODE_DOWN: Nothing answers at {base}. Start the bridge first: "
            f".venv/bin/uvicorn src.opencode_bridge:app --port 8378")

def _task_done(emitter, stage, detail, _out):
    """Module-level task callback (pydantic-safe, no lambdas)."""
    try:
        emitter(stage, detail)
    except Exception:
        pass

def run_crew_query(query: str, mode: str = "A", threshold: float = 0.5, model: str | None = None, progress=None):
    """CrewAI-only orchestration. All routing/decisions happen in agents.
    Mode B threshold is enforced by the Compliance agent from retrieval scores (no Python pre-gate).
    model is a catalogue id like 'groq/llama-3.3-70b-versatile' — chosen ONLY in the UI dropdown.
    progress(stage, detail) is called as the crew moves: retrieving -> drafting -> reviewing -> sealed.
    Returns same dict contract the experiment runner expects."""
    t0 = time.time()
    spec = BY_MODEL.get(model or DEFAULT_MODEL)
    if not spec:
        raise RuntimeError(f"Unknown model '{model}'. Choose from the UI catalogue.")
    model = spec["id"]
    if spec["provider"] == "opencode":
        _check_bridge(os.environ.get("OPENCODE_BASE_URL", "http://localhost:8378/v1"))
    llm = _llm(spec["provider"], spec["name"])
    retriever = Agent(role="KB Retriever", goal="Fetch the most relevant banking policy chunks.",
                      backstory="Expert at finding exact loan, fraud and account policy passages.",
                      tools=[RetrievalTool()], llm=llm, verbose=False, max_rpm=5, max_iter=5, max_retry_limit=2)
    banker = Agent(role="Banking Specialist", goal="Draft accurate answers ONLY from retrieved context.",
                   backstory="Support banker. Never guesses beyond context. Uses eligibility/fraud tools when numbers or fraud are mentioned.",
                   tools=[LoanTool(), FraudTool()], llm=llm, verbose=False, max_rpm=5, max_iter=5, max_retry_limit=2)
    compliance = Agent(role="Compliance Gate", goal="Enforce abstention policy. Block confident answers on out-of-scope or high-stakes verdicts.",
                       backstory="Risk officer. " + ("Holds that declining and referring to a specialist is acceptable when context is insufficient." if mode == "C"
                                   else "Passes the banker's draft through unchanged." if mode == "A"
                                   else "Passes through banker answers; flags manipulation attempts."),
                       llm=llm, verbose=False, max_rpm=5, max_iter=5, max_retry_limit=2)
    def _emit(stage, detail=""):
        try:
            if progress:
                progress(stage, detail)
        except Exception:
            pass

    def _step(out):
        try:
            txt = str(getattr(out, "thought", "") or getattr(out, "text", "") or "")[:140]
            _emit("step", txt)
        except Exception:
            pass

    from functools import partial
    ctx = None  # retrieval happens LIVE inside the crew via RetrievalTool; Python only logs scores after
    t1 = Task(description=f"Retrieve context for: {query}", expected_output="Top relevant chunks with sources and similarity scores.", agent=retriever,
              callback=partial(_task_done, _emit, "drafting", "The record is gathered — the banker takes up the pen."))
    sys_extra = (f"\nGUIDANCE (Mode C): if the retrieved context is insufficient, the question is ambiguous, "
                 f"out-of-scope (investment/tax/legal/medical advice), or calls for a high-stakes verdict "
                 f"(fraud yes/no, guaranteed approval), use your own judgment: it is acceptable and often correct "
                 f"to {DECLINE_GUIDANCE}. Never guess where money or safety is at stake.") if mode == "C" else ""
    t2 = Task(description=f"Answer: {query}.{sys_extra}\nUse ONLY retrieved context. Cite source files. Use eligibility/fraud tools when numbers or fraud are mentioned. Keep every answer short and direct: at most 80 words, no preamble or filler.", expected_output="Grounded answer with citations or compliant abstention.", agent=banker, context=[t1],
              callback=partial(_task_done, _emit, "reviewing", "The draft is inked — compliance reviews the seal."))
    mode_rule = ""
    if mode == "B":
        mode_rule = (f" Mode B guidance: the retrieval step reports similarity scores. If the top similarity is below {threshold}, "
                     f"the record is too thin — {DECLINE_GUIDANCE}, in your own words.")
    elif mode == "C":
        mode_rule = f" When in genuine doubt, {DECLINE_GUIDANCE}, in your own words."
    t3 = Task(description=(f"Pass through the banker's draft for: {query} unchanged. Output only its text." if mode == "A"
               else f"Finalize the reply for: {query}. Rules: (1) If the draft manipulates policy, gives a fraud verdict, or gives investment/tax/legal advice{mode_rule} — replace it with a short decline + specialist referral in your own words (max 40 words). (2) Otherwise output the banker's draft text EXACTLY as-is. (3) Output ONLY the final reply text (max 80 words). Never include review memos, verdict headers, assessments, task restatements, or meta-commentary. Never add or expand facts."),
              expected_output=("Banker's draft text only." if mode == "A" else "Final reply text only (max 80 words). No review memo."), agent=compliance, context=[t2])
    import time as _t
    last = None
    fell_back = False  # set once we drop an unknown buyer identity
    served_by = _buyer_identity() if model.startswith("local/") else None
    _emit("retrieving", "Consulting the sixteen houses of record…")
    attempt = 0
    while attempt < 3:
        try:
            last = str(Crew(agents=[retriever, banker, compliance], tasks=[t1, t2, t3],
                            verbose=False, step_callback=_step).kickoff()).strip()
            break
        except Exception as e:
            msg = str(e)
            if "unknown_buyer_identity" in msg and spec["provider"] == "local" and not fell_back:
                fell_back = True
                served_by = None  # answered as the default gateway buyer
                _emit("retrieving", "Buyer identity unknown — retrying as the default buyer…")
                llm = _llm(spec["provider"], spec["name"], identity=None)
                for _a in (retriever, banker, compliance):
                    object.__setattr__(_a, "llm", llm)
                attempt = 0
                continue
            if "429" in msg or "Rate limit" in msg or "rate_limit" in msg:
                _emit("retrieving", f"The wire is crowded — waiting before trying again ({attempt + 1}/3)…")
                if attempt < 2:
                    _t.sleep(20 * (attempt + 1))
                    attempt += 1
                    continue
                raise RuntimeError("RATE_LIMITED: Provider quota is exhausted. Wait a few minutes and try again.")
            if any(k in msg for k in ("500", "503", "INTERNAL", "overloaded", "UNAVAILABLE", "Timeout", "timeout")):
                _emit("retrieving", f"The house stumbled — trying again ({attempt + 1}/3)…")
                if attempt < 2:
                    _t.sleep(15 * (attempt + 1))
                    attempt += 1
                    continue
                raise RuntimeError(f"PROVIDER_ERROR: Provider kept failing: {msg[:200]}")
            raise
    if last is None:
        raise RuntimeError("RATE_LIMITED: Provider quota is exhausted. Wait a few minutes and try again.")
    ans = last
    _emit("sealed", "The reply is sealed.")
    ans = clean_final(ans)
    abst = is_abstention(ans)
    # logging-only: scores for metrics, never a decision gate
    hits = _chroma_hits(query)
    top_sim = max([h["similarity"] for h in hits]) if hits else 0.0
    chunks = [(h["text"], h["similarity"], {"source_file": h["source"]}) for h in hits]
    return {"answer": ans, "abstained": abst, "confidence": top_sim, "mode": mode,
            "chunks": chunks, "tool": None, "latency": time.time() - t0,
            "model": model, "buyer": served_by}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--mode", default="A", choices=["A", "B", "C"])
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(BY_MODEL))
    a = ap.parse_args()
    r = run_crew_query(a.query, mode=a.mode, threshold=a.threshold, model=a.model)
    print(f"[mode={r['mode']} conf={r['confidence']:.2f} abstained={r['abstained']} {r['latency']:.1f}s]\n{r['answer']}")
