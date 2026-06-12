"""Monthly cost guard — Redis-backed with in-memory fallback."""
from datetime import datetime

from fastapi import HTTPException

from app.config import settings
from app.redis_client import get_redis

_memory_spending: dict[str, float] = {}


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006


def check_budget(user_id: str, estimated_cost: float) -> None:
    """
    Return True if budget remains; raise HTTPException(402) if exceeded.
    Each user has settings.monthly_budget_usd per calendar month.
    """
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    budget = settings.monthly_budget_usd

    r = get_redis()
    if r:
        try:
            current = float(r.get(key) or 0)
            if current + estimated_cost > budget:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "Monthly budget exceeded",
                        "used_usd": round(current, 4),
                        "budget_usd": budget,
                        "resets_at": "first day of next month",
                    },
                )
            r.incrbyfloat(key, estimated_cost)
            r.expire(key, 32 * 24 * 3600)
            return
        except HTTPException:
            raise
        except Exception:
            pass

    current = _memory_spending.get(key, 0.0)
    if current + estimated_cost > budget:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Monthly budget exceeded",
                "used_usd": round(current, 4),
                "budget_usd": budget,
            },
        )
    _memory_spending[key] = current + estimated_cost
