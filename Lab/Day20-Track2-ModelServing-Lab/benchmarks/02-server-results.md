# 02 — llama-server Load Test Results

Server: `python -m llama_cpp.server` (llama-cpp-python 0.3.31, Metal) on Apple M4 / 16 GB.
Model: `Llama-3.2-3B-Instruct-Q4_K_M.gguf` · `--n_gpu_layers 99 --n_ctx 2048 --n_threads 10`.
Load mix (locust `load-test.py`): 80% short chat prompts, 20% long RAG-style prompts.

| Concurrency | Total reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Max (ms) | Failures |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 10 (`-u 10 -r 1 -t 1m`) | 22 | 0.41 | 18000 | 27000 | 29000 | 29293 | 0 |
| 50 (`-u 50 -r 2 -t 1m`) | 27 | 0.47 | 27000 | 46000 | 46000 | 46475 | 0 |

Raw CSVs: `benchmarks/locust-10_stats.csv`, `benchmarks/locust-50_stats.csv` (+ `_stats_history.csv`).

## Observation

Going from 10 → 50 concurrent users, throughput barely moved (0.41 → 0.47 req/s) while
P95 latency nearly doubled (27 s → 46 s) and P99 went 29 s → 46 s, with **zero failures**.
That is the classic *saturation* signature: the single 3B model on one M4 GPU is already
at its decode-bandwidth ceiling at 10 users, so extra concurrency only lengthens the
queue — latency inflates but **goodput@SLO does not improve**. If the SLO were, say,
"P95 < 5 s", this server already misses it at 10 users; piling on more users makes the
miss worse, not the throughput better.

The Python `llama_cpp.server` does not expose a Prometheus `/metrics` endpoint
(GET `/metrics` → 404). The continuous-batching counters
(`llamacpp:n_busy_slots_per_decode`, `requests_processing`) come from the **native**
`llama-server` built from source — see `benchmarks/02-server-metrics.csv`.
