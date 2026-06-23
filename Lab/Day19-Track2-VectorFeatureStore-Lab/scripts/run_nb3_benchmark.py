"""Run NB3 benchmark standalone — start server, measure latency, print results."""
import json, statistics, subprocess, sys, time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus_vn.jsonl"
GOLDEN = ROOT / "data" / "golden_set.jsonl"
URL = "http://localhost:8000"
VENV = ROOT / ".venv" / "Scripts"

assert CORPUS.exists(), "Run make seed first"
assert GOLDEN.exists(), "Run make seed first"

print("Starting uvicorn server...")
proc = subprocess.Popen(
    [str(VENV / "uvicorn"), "app.main:app", "--port", "8000", "--log-level", "warning"],
    cwd=str(ROOT),
)

ready = False
for i in range(120):
    time.sleep(1)
    try:
        r = httpx.get(f"{URL}/healthz", timeout=2.0)
        if r.status_code == 200 and r.json().get("ready"):
            ready = True
            print(f"Server ready after {i+1}s")
            break
    except Exception:
        pass

if not ready:
    proc.terminate()
    sys.exit("Server not ready after 120s")

print(httpx.get(f"{URL}/healthz").json())

golden = [json.loads(l) for l in GOLDEN.open(encoding="utf-8")]

# Warmup
print("Warming up (10 queries)...")
for q in golden[:10]:
    httpx.get(f"{URL}/search", params={"q": q["query"], "mode": "hybrid"})

def percentile(vals, p):
    n = len(vals)
    return sorted(vals)[min(int(n * p), n - 1)]

def benchmark_mode(mode, reps=2):
    srv, wall = [], []
    for _ in range(reps):
        for q in golden:
            t0 = time.perf_counter()
            r = httpx.get(f"{URL}/search", params={"q": q["query"], "mode": mode}, timeout=30)
            wall.append((time.perf_counter() - t0) * 1000)
            srv.append(r.json()["latency_ms"])
    return {
        "p50_server": percentile(srv, 0.50),
        "p95_server": percentile(srv, 0.95),
        "p99_server": percentile(srv, 0.99),
        "p99_wall":   percentile(wall, 0.99),
    }

print(f"\n  {'mode':10}  {'P50':>7}  {'P95':>7}  {'P99':>7}  {'P99(wall)':>9}")
results = {}
for mode in ("keyword", "semantic", "hybrid"):
    res = benchmark_mode(mode)
    results[mode] = res
    print(f"  {mode:10}  {res['p50_server']:>5.1f}ms  {res['p95_server']:>5.1f}ms  "
          f"{res['p99_server']:>5.1f}ms  {res['p99_wall']:>7.1f}ms")

hybrid_p99 = results["hybrid"]["p99_server"]
print(f"\nHybrid P99 server-side: {hybrid_p99:.1f}ms")
if hybrid_p99 < 50:
    print(f"PASS — hybrid P99 < 50ms ({hybrid_p99:.1f}ms)")
else:
    print(f"WARN — hybrid P99 >= 50ms ({hybrid_p99:.1f}ms)")

# Save results for notebook injection
(ROOT / "data" / "nb3_results.json").write_text(json.dumps(results, indent=2))
print("\nResults saved to data/nb3_results.json")

proc.terminate()
proc.wait(timeout=5)
print("Server stopped.")
