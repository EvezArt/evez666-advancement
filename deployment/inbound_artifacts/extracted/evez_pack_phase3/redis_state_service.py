#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

import redis
from fastapi import FastAPI

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "evez")

app = FastAPI(title="EVEZ Redis State Service", version="1.0.0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def k_run(run_id: str) -> str:
    return f"{REDIS_PREFIX}:run:{run_id}"


def k_runs() -> str:
    return f"{REDIS_PREFIX}:runs"


def k_system() -> str:
    return f"{REDIS_PREFIX}:system"


def k_watchdog() -> str:
    return f"{REDIS_PREFIX}:watchdog"


def read_json(key: str, default: Dict[str, Any]) -> Dict[str, Any]:
    raw = r.get(key)
    if not raw:
        return default.copy()
    try:
        return json.loads(raw)
    except Exception:
        return default.copy()


def write_json(key: str, value: Dict[str, Any]) -> Dict[str, Any]:
    r.set(key, json.dumps(value))
    return value


def default_system() -> Dict[str, Any]:
    return {
        "service": "evez-orchestrator",
        "status": "ok",
        "lastRunId": None,
        "lastSuccessAt": None,
        "lastFailureAt": None,
        "lastUpdatedAt": None,
        "consecutiveFailures": 0,
    }


def default_watchdog() -> Dict[str, Any]:
    return {
        "failureCount": 0,
        "lastCheckedAt": None,
        "lastPayload": {},
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    r.ping()
    return {"ok": True, "service": "evez-state-service", "updated_at": now_iso()}


@app.get("/status/{run_id}")
def status(run_id: str) -> Dict[str, Any]:
    found = read_json(k_run(run_id), {})
    if found:
        return {"ok": True, **found}
    return {
        "ok": False,
        "run_id": run_id,
        "status": "not_found",
        "summary": f"No run found for {run_id}",
        "tool_actions": [],
        "errors": [f"run_id {run_id} not found"],
        "updated_at": now_iso(),
    }


@app.patch("/runs/{run_id}")
def patch_run(run_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    current = read_json(k_run(run_id), {"run_id": run_id})
    merged = {**current, **payload, "run_id": run_id}
    write_json(k_run(run_id), merged)
    r.sadd(k_runs(), run_id)
    return merged


@app.post("/orchestrator/start")
def orchestrator_start(payload: Dict[str, Any]) -> Dict[str, Any]:
    run_id = payload["run_id"]
    now = now_iso()
    current = read_json(k_run(run_id), {})
    stored = {
        **current,
        **payload,
        "ok": False,
        "status": "running",
        "summary": "Execution started",
        "tool_actions": [],
        "errors": [],
        "retry_scheduled": False,
        "next_action": "planning",
        "updated_at": now,
        "created_at": current.get("created_at", now),
    }
    write_json(k_run(run_id), stored)
    r.sadd(k_runs(), run_id)

    system = read_json(k_system(), default_system())
    system.update({"lastRunId": run_id, "lastUpdatedAt": now})
    write_json(k_system(), system)
    return payload


@app.post("/orchestrator/finalize")
def orchestrator_finalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    run_id = payload["run_id"]
    now = payload.get("updated_at") or now_iso()
    current = read_json(k_run(run_id), {})
    merged = {**current, **payload, "run_id": run_id, "updated_at": now}
    write_json(k_run(run_id), merged)
    r.sadd(k_runs(), run_id)

    system = read_json(k_system(), default_system())
    ok = bool(merged.get("ok"))
    system["lastRunId"] = run_id
    system["lastUpdatedAt"] = now
    if ok:
        system["status"] = "ok"
        system["lastSuccessAt"] = now
        system["consecutiveFailures"] = 0
    else:
        system["status"] = "degraded"
        system["lastFailureAt"] = now
        system["consecutiveFailures"] = int(system.get("consecutiveFailures") or 0) + 1
    write_json(k_system(), system)
    return merged


@app.get("/system")
def system() -> Dict[str, Any]:
    system = read_json(k_system(), default_system())
    tracked_runs = list(r.smembers(k_runs()))
    open_runs = 0
    for run_id in tracked_runs:
        run = read_json(k_run(run_id), {})
        if run.get("status") == "running":
            open_runs += 1
    return {
        "ok": True,
        **system,
        "tracked_runs": len(tracked_runs),
        "open_runs": open_runs,
        "updated_at": now_iso(),
    }


@app.get("/watchdog")
def watchdog() -> Dict[str, Any]:
    return {"ok": True, **read_json(k_watchdog(), default_watchdog())}


@app.post("/watchdog/reset")
def watchdog_reset(payload: Dict[str, Any]) -> Dict[str, Any]:
    state = default_watchdog()
    state["lastCheckedAt"] = payload.get("checked_at") or now_iso()
    state["lastPayload"] = payload.get("last_payload") or {}
    write_json(k_watchdog(), state)
    return {"ok": True, **state}


@app.post("/watchdog/increment")
def watchdog_increment(payload: Dict[str, Any]) -> Dict[str, Any]:
    state = read_json(k_watchdog(), default_watchdog())
    state["failureCount"] = int(state.get("failureCount") or 0) + 1
    state["lastCheckedAt"] = payload.get("checked_at") or now_iso()
    state["lastPayload"] = payload.get("last_payload") or {}
    write_json(k_watchdog(), state)
    return {
        "ok": True,
        "failureCount": state["failureCount"],
        "checked_at": state["lastCheckedAt"],
        "last_payload": state["lastPayload"],
    }
