"""
Run full experiment: queries x modes x repeats x models (100 questions).
Logs one JSONL row per generation. Multiprocessed with a provider preflight.
Usage: .venv/bin/python src/run_experiments.py --repeats 5 --thresholds 0.3 0.5 0.7 --workers 4
"""
import argparse, json, os, sys, time, threading
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from src.crew_agent import run_crew_query as generate, DEFAULT_MODEL, BY_MODEL

_LOCK = threading.Lock()


def preflight(models):
    """Fail fast naming the dead backend instead of burning retries per query."""
    import requests
    need = set()
    for m in models:
        spec = BY_MODEL.get(m)
        if not spec:
            raise SystemExit(f"unknown model '{m}'")
        need.add(spec["provider"])
    if "local" in need:
        base = os.environ.get("LOCAL_BASE_URL", "http://localhost:8377/v1")
        try:
            requests.get(base.rstrip("/") + "/models", timeout=8).raise_for_status()
        except Exception:
            raise SystemExit(f"gateway down at {base} — start it first")
    if "opencode" in need:
        base = os.environ.get("OPENCODE_BASE_URL", "http://localhost:8378/v1")
        try:
            requests.get(base.rstrip("/") + "/models", timeout=8).raise_for_status()
        except Exception:
            raise SystemExit(f"bridge down at {base} — start it: .venv/bin/uvicorn src.opencode_bridge:app --port 8378")
    print("preflight ok:", ", ".join(sorted(need)))


def one(task):
    q, model, mode, threshold, run, delay = task
    try:
        res = generate(q["query"], mode=mode, threshold=threshold, model=model)
        row = {"qid": q["id"], "qtype": q["type"], "query": q["query"], "gold": q["gold"],
               "mode": f"B@{threshold}" if mode == "B" else mode, "threshold": threshold,
               "run": run, "model": model,
               "answer": res["answer"], "abstained": res["abstained"],
               "confidence": res["confidence"], "latency": res["latency"],
               "tool": res["tool"]}
    except Exception as e:
        row = {"qid": q["id"], "qtype": q["type"], "query": q["query"], "gold": q["gold"],
               "mode": f"B@{threshold}" if mode == "B" else mode, "threshold": threshold,
               "run": run, "model": model, "error": str(e)[:300]}
    time.sleep(delay)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.3, 0.5, 0.7])
    ap.add_argument("--models", nargs="+", default=None, help="Catalogue ids from the UI dropdown")
    ap.add_argument("--out", default=None)
    ap.add_argument("--delay", type=float, default=3.0, help="Seconds after each generation")
    ap.add_argument("--workers", type=int, default=4, help="Parallel generations")
    ap.add_argument("--limit", type=int, default=0, help="Only first N tasks (smoke test)")
    args = ap.parse_args()
    models = args.models or [DEFAULT_MODEL]
    preflight(models)
    queries = json.loads(Path("data/queries_gold.json").read_text())
    if Path("data/queries_extra.json").exists():
        queries += json.loads(Path("data/queries_extra.json").read_text())
    tasks = []
    for q in queries:
        for model in models:
            for mode in ["A", "C"]:
                for r in range(args.repeats):
                    tasks.append((q, model, mode, None, r, args.delay))
            for th in args.thresholds:
                for r in range(args.repeats):
                    tasks.append((q, model, "B", th, r, args.delay))
    if args.limit:
        tasks = tasks[:args.limit]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(args.out or f"logs/runs_{ts}.jsonl")
    out.parent.mkdir(exist_ok=True)
    total = len(tasks)
    print(f"{total} generations x {args.workers} workers -> {out}")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    done = 0
    with open(out, "a") as f, ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(one, t): t for t in tasks}
        for fut in as_completed(futs):
            row = fut.result()
            with _LOCK:
                f.write(json.dumps(row) + "\n")
                f.flush()
                done += 1
                tag = row.get("error", "ok")[:40] if row.get("error") else "ok"
                print(f"[{done}/{total}] {row['qid']} {row['mode']} {row['model'].split('/')[-1].split('@')[-1]} -> {tag}", flush=True)
    print(f"Wrote {done} rows -> {out}")


if __name__ == "__main__":
    main()
