"""
Production AI Agent — Kết hợp tất cả Day 12 concepts.

Checklist:
  ✅ Config từ environment (12-factor)
  ✅ Structured JSON logging
  ✅ API Key authentication
  ✅ Rate limiting (Redis sliding window)
  ✅ Cost guard ($10/month per user)
  ✅ Conversation history (Redis, stateless)
  ✅ Health check + Readiness probe
  ✅ Graceful shutdown
  ✅ Security headers + CORS
"""
import json
import logging
import signal
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, estimate_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import get_redis, ping_redis
from utils.mock_llm import ask as llm_ask

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0
_request_count = 0
_error_count = 0

_memory_history: dict[str, list] = {}


def _load_history(session_id: str) -> list:
    r = get_redis()
    if r:
        try:
            data = r.lrange(f"history:{session_id}", 0, -1)
            return [json.loads(item) for item in data]
        except Exception:
            pass
    return list(_memory_history.get(session_id, []))


def _save_message(session_id: str, role: str, content: str) -> None:
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    r = get_redis()
    if r:
        try:
            key = f"history:{session_id}"
            r.rpush(key, json.dumps(message))
            r.ltrim(key, -20, -1)
            r.expire(key, 3600)
            return
        except Exception:
            pass
    history = _memory_history.setdefault(session_id, [])
    history.append(message)
    if len(history) > 20:
        _memory_history[session_id] = history[-20:]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }))
    if settings.redis_url:
        if ping_redis():
            logger.info(json.dumps({"event": "redis_connected"}))
        else:
            logger.warning(json.dumps({"event": "redis_unavailable", "fallback": "in-memory"}))
    time.sleep(0.1)
    _is_ready = True
    logger.info(json.dumps({"event": "ready"}))

    yield

    _is_ready = False
    logger.info(json.dumps({"event": "shutdown_started", "in_flight": _in_flight_requests}))
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        time.sleep(1)
        elapsed += 1
    logger.info(json.dumps({"event": "shutdown_complete"}))


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count, _error_count, _in_flight_requests
    start = time.time()
    _request_count += 1
    _in_flight_requests += 1
    try:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if "server" in response.headers:
            del response.headers["server"]
        duration = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": duration,
        }))
        return response
    except Exception:
        _error_count += 1
        raise
    finally:
        _in_flight_requests -= 1


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    session_id: str
    turn: int
    timestamp: str


@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "health": "GET /health",
            "ready": "GET /ready",
        },
    }


@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    request: Request,
    user_id: str = Depends(verify_api_key),
):
    check_rate_limit(user_id)

    input_tokens = len(body.question.split()) * 2
    check_budget(user_id, estimate_cost(input_tokens, 0))

    session_id = body.session_id or str(uuid.uuid4())
    history = _load_history(session_id)
    _save_message(session_id, "user", body.question)

    logger.info(json.dumps({
        "event": "agent_call",
        "user_id": user_id,
        "session_id": session_id,
        "q_len": len(body.question),
        "client": str(request.client.host) if request.client else "unknown",
    }))

    answer = llm_ask(body.question)
    _save_message(session_id, "assistant", answer)

    output_tokens = len(answer.split()) * 2
    check_budget(user_id, estimate_cost(0, output_tokens))

    turn = len([m for m in history if m["role"] == "user"]) + 1
    return AskResponse(
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        session_id=session_id,
        turn=turn,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/health", tags=["Operations"])
def health():
    redis_status = "ok" if ping_redis() else "degraded" if settings.redis_url else "not_configured"

    status = "ok" if redis_status != "degraded" else "degraded"
    return {
        "status": status,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "checks": {"llm": "mock" if not settings.openai_api_key else "openai", "redis": redis_status},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    if settings.redis_url and not ping_redis():
        raise HTTPException(503, "Redis not available")
    return {"ready": True, "in_flight_requests": _in_flight_requests}


@app.get("/chat/{session_id}/history", tags=["Agent"])
def get_history(session_id: str, _user_id: str = Depends(verify_api_key)):
    history = _load_history(session_id)
    if not history:
        raise HTTPException(404, f"Session {session_id} not found or expired")
    return {"session_id": session_id, "messages": history, "count": len(history)}


def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=30,
    )
