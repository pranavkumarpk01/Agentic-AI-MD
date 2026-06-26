import redis
import json
from typing import List

# Redis running in Docker (docker-compose.yml)
_redis = redis.Redis(host="localhost", port=6379, decode_responses=True)


def load_user_memory(user_id: str) -> List[str]:
    """Load all remembered facts for a user from Redis."""
    key = f"memory:{user_id}"
    try:
        data = _redis.get(key)
        if data:
            return json.loads(data)
        return []
    except Exception as e:
        print(f"[Memory] Redis load failed: {e}")
        return []


def save_user_memory(user_id: str, new_facts: List[str]) -> None:
    """Append new facts to user's memory. Keeps the last 20 facts (LRU)."""
    key = f"memory:{user_id}"
    try:
        existing = load_user_memory(user_id)
        all_facts = existing + new_facts
        all_facts = all_facts[-20:]  # keep last 20
        _redis.set(key, json.dumps(all_facts))
        print(f"[Memory] Saved {len(new_facts)} new facts. Total: {len(all_facts)}")
    except Exception as e:
        print(f"[Memory] Redis save failed: {e}")


def clear_user_memory(user_id: str) -> None:
    """Wipe all memory for a user."""
    _redis.delete(f"memory:{user_id}")
    print(f"[Memory] Cleared memory for {user_id}")
