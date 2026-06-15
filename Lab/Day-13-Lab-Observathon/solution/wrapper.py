"""Mitigation + observability layer around the opaque LLM agent."""
from __future__ import annotations

import hashlib
import re
import time

from telemetry.cost import cost_from_usage
from telemetry.logger import logger, new_correlation_id, set_correlation_id
from telemetry.redact import redact

_RETRYABLE = frozenset({"loop", "max_steps", "wrapper_error"})
_NOTE_RE = re.compile(r"(?i)\[?\s*ghi\s*chu\s*\]?\s*:.*")
_INJECT_RE = re.compile(
    r"(?i)(?:system\s*prompt|ignore\s*(?:all|previous)|override\s*price|"
    r"new\s*instruction|gia\s*mac\s*dinh|price\s*override)"
)


def _sanitize_question(question: str) -> str:
    """Strip note sections and obvious injection phrases before the agent sees them."""
    q = _NOTE_RE.sub(" [note omitted]", question)
    q = _INJECT_RE.sub("", q)
    return re.sub(r"\s{2,}", " ", q).strip()


def _cache_key(question: str, config: dict) -> str:
    knobs = {k: config.get(k) for k in ("model", "temperature", "self_consistency", "tool_budget")}
    blob = f"{question}|{sorted(knobs.items())}"
    return hashlib.sha256(blob.encode()).hexdigest()


def _loop_detected(trace: list) -> bool:
    actions = [s.get("action") for s in trace if s.get("action")]
    return len(actions) >= 3 and len(set(actions[-3:])) == 1


def _log_call(context: dict, attempt: int, wall_ms: int, result: dict) -> None:
    meta = result.get("meta", {})
    usage = meta.get("usage", {})
    answer = result.get("answer") or ""
    logger.log_event("AGENT_CALL", {
        "qid": context.get("qid"),
        "session_id": context.get("session_id"),
        "turn_index": context.get("turn_index"),
        "attempt": attempt,
        "status": result.get("status"),
        "steps": result.get("steps"),
        "wall_ms": wall_ms,
        "latency_ms": meta.get("latency_ms"),
        "tokens": usage,
        "cost_usd": cost_from_usage(meta.get("model", ""), usage),
        "tools_used": meta.get("tools_used", []),
        "tool_count": len(meta.get("tools_used", [])),
        "loop_detected": _loop_detected(result.get("trace", [])),
        "pii_in_answer": redact(answer)[1] > 0,
    })


def mitigate(call_next, question, config, context):
    set_correlation_id(new_correlation_id())
    conf = dict(config)
    turn = context.get("turn_index", 0)
    reset_every = int(conf.get("context_reset_every") or 0)
    if reset_every and turn > 0 and turn % reset_every == 0:
        conf["session_id"] = f"{context.get('session_id')}-r{turn}"

    safe_q = _sanitize_question(question)
    cache = context.get("cache", {})
    lock = context.get("cache_lock")
    use_cache = conf.get("cache", {}).get("enabled")

    if use_cache:
        key = _cache_key(safe_q, conf)
        if lock:
            with lock:
                hit = cache.get(key)
        else:
            hit = cache.get(key)
        if hit:
            logger.log_event("CACHE_HIT", {"qid": context.get("qid"), "key": key[:12]})
            return hit

    retry = conf.get("retry", {})
    attempts = int(retry.get("max_attempts", 1)) if retry.get("enabled") else 1
    backoff_ms = int(retry.get("backoff_ms", 0))

    result = None
    for attempt in range(1, attempts + 1):
        t0 = time.time()
        result = call_next(safe_q, conf)
        _log_call(context, attempt, int((time.time() - t0) * 1000), result)
        if result.get("status") not in _RETRYABLE or attempt == attempts:
            break
        if backoff_ms:
            time.sleep(backoff_ms / 1000.0)

    if conf.get("redact_pii") and result.get("answer"):
        cleaned, _ = redact(result["answer"])
        result = dict(result)
        result["answer"] = cleaned

    if use_cache and result.get("status") == "ok":
        key = _cache_key(safe_q, conf)
        if lock:
            with lock:
                cache[key] = result
        else:
            cache[key] = result

    return result
