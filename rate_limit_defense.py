#!/usr/bin/env python3
"""
Rate Limit Defense — System-wide API throttle manager.
Prevents cascading failures by staggering calls, tracking quotas, and applying backoff.
"""

import json
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from threading import Lock
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rate_limit_defense")

# ── Provider quota configuration ────────────────────────────────────────────
# These are conservative defaults; tune per provider terms of service
PROVIDER_QUOTAS = {
    "github_models": {
        "requests_per_minute": 120,   # Raised from 30 — GitHub Models allows higher burst
        "requests_per_hour": 5000,    # Raised from 1000
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 300,
    },
    "exa": {
        "requests_per_minute": 100,   # Raised from 20
        "requests_per_hour": 5000,    # Raised from 400
        "backoff_multiplier": 2.5,
        "max_backoff_seconds": 600,
    },
    "composio": {
        "requests_per_minute": 200,  # Raised from 40
        "requests_per_hour": 10000,  # Raised from 2000
        "backoff_multiplier": 1.5,
        "max_backoff_seconds": 120,
    },
    "openai": {
        "requests_per_minute": 200,  # Raised from 50
        "requests_per_hour": 12000,  # Raised from 3000
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 300,
    },
    "anthropic": {
        "requests_per_minute": 150,  # Raised from 40
        "requests_per_hour": 9000,   # Raised from 2400
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 300,
    },
    "groq": {
        "requests_per_minute": 300,  # Raised from 60
        "requests_per_hour": 18000,  # Raised from 3600
        "backoff_multiplier": 1.5,
        "max_backoff_seconds": 180,
    },
    "samba_nova": {
        "requests_per_minute": 200,  # Raised from 40
        "requests_per_hour": 12000,  # Raised from 2400
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 300,
    },
    "cerebras": {
        "requests_per_minute": 150,  # Raised from 30
        "requests_per_hour": 9000,   # Raised from 1800
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 300,
    },
}

# ── Persistence path ─────────────────────────────────────────────────────────
STATE_FILE = Path("/root/.openclaw/workspace/memory/rate_limit_state.json")
LOCK_FILE = Path("/tmp/rate_limit.lock")
file_lock = Lock()

# ── Data structures ──────────────────────────────────────────────────────────
@dataclass
class ProviderState:
    provider: str
    remaining_minute: int
    remaining_hour: int
    last_reset_minute: float
    last_reset_hour: float
    backoff_until: Optional[float] = None  # epoch seconds
    consecutive_429s: int = 0

    def to_dict(self):
        d = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in d.items() if v is not None}

# ── Manager ──────────────────────────────────────────────────────────────────
class RateLimitManager:
    """Singleton-style manager with persistent state."""
    
    def __init__(self):
        self.state: Dict[str, ProviderState] = {}
        self.lock = Lock()
        self.load()
    
    def load(self):
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    data = json.load(f)
                for provider, s in data.items():
                    self.state[provider] = ProviderState(**s)
            except Exception as e:
                log.warning(f"Could not load rate limit state: {e}")
                self._initialize_all()
        else:
            self._initialize_all()
    
    def save(self):
        with self.lock:
            try:
                with open(STATE_FILE, "w") as f:
                    json.dump({k: v.to_dict() for k, v in self.state.items()}, f, indent=2)
            except Exception as e:
                log.error(f"Failed to save rate limit state: {e}")
    
    def _initialize_all(self):
        now = time.time()
        for provider, quota in PROVIDER_QUOTAS.items():
            self.state[provider] = ProviderState(
                provider=provider,
                remaining_minute=quota["requests_per_minute"],
                remaining_hour=quota["requests_per_hour"],
                last_reset_minute=now,
                last_reset_hour=now,
                backoff_until=None,
                consecutive_429s=0,
            )
        self.save()
    
    def _reset_if_needed(self, state: ProviderState):
        now = time.time()
        # Reset minute quota every 60s
        if now - state.last_reset_minute >= 60:
            state.remaining_minute = PROVIDER_QUOTAS[state.provider]["requests_per_minute"]
            state.last_reset_minute = now
        # Reset hour quota every 3600s
        if now - state.last_reset_hour >= 3600:
            state.remaining_hour = PROVIDER_QUOTAS[state.provider]["requests_per_hour"]
            state.last_reset_hour = now
    
    def consume(self, provider: str) -> Tuple[bool, int]:
        """
        Attempt to consume one request quota for provider.
        Returns (allowed: bool, backoff_seconds: int).
        """
        with self.lock:
            if provider not in self.state:
                self._initialize_all()
            
            state = self.state[provider]
            now = time.time()
            
            # Check backoff
            if state.backoff_until and now < state.backoff_until:
                remaining = int(state.backoff_until - now)
                return False, remaining
            
            self._reset_if_needed(state)
            
            if state.remaining_minute <= 0 or state.remaining_hour <= 0:
                # Apply exponential backoff
                state.consecutive_429s += 1
                mult = PROVIDER_QUOTAS[state.provider]["backoff_multiplier"]
                max_backoff = PROVIDER_QUOTAS[state.provider]["max_backoff_seconds"]
                backoff = min(max_backoff, int(mult ** state.consecutive_429s))
                state.backoff_until = now + backoff
                self.save()
                log.warning(f"{provider} rate limit hit — backoff {backoff}s (consecutive: {state.consecutive_429s})")
                return False, backoff
            
            # Consume
            state.remaining_minute -= 1
            state.remaining_hour -= 1
            state.consecutive_429s = 0  # reset on success
            self.save()
            return True, 0
    
    def record_success(self, provider: str):
        """Call after a successful request to reset consecutive counter."""
        with self.lock:
            if provider in self.state:
                self.state[provider].consecutive_429s = 0
                self.save()
    
    def report_status(self) -> Dict:
        with self.lock:
            return {p: {
                "remaining_minute": s.remaining_minute,
                "remaining_hour": s.remaining_hour,
                "backoff_until": s.backoff_until,
                "consecutive_429s": s.consecutive_429s,
            } for p, s in self.state.items()}

# ── Global singleton ─────────────────────────────────────────────────────────
_manager = RateLimitManager()

# ── Decorator / context manager ──────────────────────────────────────────────
def rate_limited(provider: str):
    """
    Decorator for functions that call external APIs.
    Automatically consumes quota and backs off on 429.
    
    Example:
        @rate_limited("github_models")
        def call_github_api(...):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            allowed, backoff = _manager.consume(provider)
            if not allowed:
                log.warning(f"SKIP {provider} — backoff {backoff}s remaining")
                # Return a safe fallback or raise
                raise RuntimeError(f"Rate limit backoff: {backoff}s remaining for {provider}")
            try:
                result = func(*args, **kwargs)
                _manager.record_success(provider)
                return result
            except Exception as e:
                # On any exception that might indicate rate limit, increment backoff manually
                if "429" in str(e) or "rate limit" in str(e).lower():
                    state = _manager.state.get(provider)
                    if state:
                        state.consecutive_429s += 1
                        _manager.save()
                raise
        return wrapper
    return decorator

# ── CLI / script entrypoint ───────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["status", "test", "reset"])
    p.add_argument("--provider", default="github_models")
    args = p.parse_args()
    
    if args.action == "status":
        print(json.dumps(_manager.report_status(), indent=2))
    elif args.action == "test":
        allowed, backoff = _manager.consume(args.provider)
        if allowed:
            print(f"✓ {args.provider}: request permitted")
        else:
            print(f"✗ {args.provider}: backoff {backoff}s")
    elif args.action == "reset":
        _manager._initialize_all()
        print("All provider quotas reset to defaults.")
