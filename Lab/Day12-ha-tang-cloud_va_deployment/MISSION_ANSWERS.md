# Day 12 Lab - Mission Answers

Student name: Trinh Thi Lan Anh 
Student id: 2A202600737
Date: 2026-06-12

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Hardcoded secret/API key directly in source code.
2. Hardcoded port (`8000`) instead of reading from environment.
3. Debug mode enabled by default in runtime.
4. No health/readiness endpoint for orchestrator checks.
5. No graceful shutdown handling (`SIGTERM`/`SIGINT`).
6. Minimal structured logging, hard to trace in cloud logs.

### Exercise 1.2: Basic version observations

- Basic version can run locally and return response.
- However it is not production-ready because config/security/reliability concerns are not addressed.

### Exercise 1.3: Comparison table


| Feature      | Basic              | Advanced               | Why Important?                                   |
| ------------ | ------------------ | ---------------------- | ------------------------------------------------ |
| Config       | Hardcoded values   | Environment variables  | Same code can run across dev/staging/prod safely |
| Secrets      | In code            | Injected via env       | Prevents leaking credentials in git/image        |
| Health check | Missing            | `/health` and `/ready` | Needed for auto-restart and traffic routing      |
| Logging      | `print()`          | Structured JSON logs   | Easier debugging/monitoring in cloud             |
| Shutdown     | Immediate stop     | Graceful shutdown flow | Reduces dropped/in-flight requests               |
| State        | In-memory tendency | Redis-backed state     | Supports horizontal scaling                      |


## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** `python:3.11-slim`.
2. **Working directory:** `/app` (runtime stage).
3. **COPY requirements.txt first:** to maximize Docker layer cache; dependencies are only reinstalled when requirements change.
4. **CMD vs ENTRYPOINT:** `CMD` provides default command (override-friendly), while `ENTRYPOINT` defines fixed executable behavior.

### Exercise 2.2: Build and run

- Built and ran container locally, API/UI became accessible through mapped host port.
- Confirmed endpoint behavior by `curl` tests.

### Exercise 2.3: Multi-stage build

- **Stage 1 (builder):** create venv and install dependencies.
- **Stage 2 (runtime):** copy venv + application code only.
- Runtime image is smaller because it excludes build-time tools and caches.

### Exercise 2.4: Docker Compose stack

- Services: `agent` + `redis` (+ `nginx` for reverse proxy/LB in complete setup).
- Communication:
  - `nginx -> agent`
  - `agent -> redis`
- Compose helps orchestrate startup order, networking, and health checks.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- Platform: Railway
- Public URL: [https://agent-production-1401.up.railway.app/](https://agent-production-1401.up.railway.app/)
- Deployment status: successful
- Verified service is reachable from public internet.

### Exercise 3.2: Render vs Railway config comparison

- `railway.toml` is concise, CLI-first workflow.
- `render.yaml` is blueprint style, declarative service definition integrated with Render dashboard/GitHub.
- Both support env vars and automated deployment, but operational UX differs by platform.

### Exercise 3.3: Cloud Run (optional)

- Reviewed conceptually; primary delivery deployed on Railway.

## Part 4: API Security

### Exercise 4.1-4.3: Test results

- Without key/token: API returns unauthorized response.
- With valid key/token: request accepted and returns successful response.
- Rate limiting strategy in implementation: fixed-window per user key (tracked in Redis/in-memory fallback depending environment).

Example observed behavior during testing:

- Unauthorized request -> `401 Unauthorized`
- Authorized request -> `200 OK`

### Exercise 4.4: Cost guard implementation

- Track spending by month key: `budget:{user_id}:{YYYY-MM}`.
- Estimate request cost before calling model.
- Deny request if `current_spend + estimated_cost > monthly_budget`.
- Persist spend in Redis with TTL (rolling monthly window).
- Return friendly error when budget exhausted.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

- Implemented liveness and readiness endpoints for runtime checks.
- Added graceful shutdown behavior for container lifecycle signals.
- Refactored state handling toward stateless service pattern (externalized state/storage).
- Added reverse proxy/load-balancing capability in Docker Compose topology.
- Verified production accessibility via public Railway domain and endpoint tests.

## Final Reflection

Main production lessons from this lab:

1. Config/secrets must be externalized (12-factor mindset).
2. Security controls (auth, rate limit, budget guard) are mandatory for public AI endpoints.
3. Reliability patterns (health checks, graceful shutdown, stateless design) are key to safe scaling.

