#!/usr/bin/env python3
from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

HYPERBROWSER_API_KEY = os.getenv("HYPERBROWSER_API_KEY", "{{HYPERBROWSER_API_KEY}}")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "{{OPENAI_API_KEY}}")
HYPERBROWSER_BASE_URL = os.getenv("HYPERBROWSER_BASE_URL", "https://api.hyperbrowser.ai")

app = FastAPI(title="EVEZ Hyperbrowser Runner", version="1.0.0")


class BrowserTaskRequest(BaseModel):
    task: str
    run_id: Optional[str] = None
    llm: str = "gpt-4o"
    version: str = "1.1.0"
    maxSteps: int = Field(default=20, ge=1, le=200)
    timeoutSeconds: int = Field(default=600, ge=10, le=7200)
    pollIntervalSeconds: int = Field(default=5, ge=1, le=60)
    keepBrowserOpen: bool = False
    sessionOptions: Dict[str, Any] = Field(
        default_factory=lambda: {
            "useStealth": True,
            "acceptCookies": True,
            "enableWebRecording": True
        }
    )
    context: Dict[str, Any] = Field(default_factory=dict)


class BrowserTaskResponse(BaseModel):
    ok: bool
    run_id: str
    session_id: Optional[str] = None
    job_id: Optional[str] = None
    live_url: Optional[str] = None
    recording_status: Optional[str] = None
    recording_url: Optional[str] = None
    status: str
    final_result: Optional[str] = None
    steps: list[dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


def _headers() -> Dict[str, str]:
    return {
        "x-api-key": HYPERBROWSER_API_KEY,
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{HYPERBROWSER_BASE_URL.rstrip('/')}{path}"
    last_error: Optional[Exception] = None

    for attempt in range(1, 4):
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=_headers(),
                json=json_body,
                timeout=60,
            )
            resp.raise_for_status()
            if not resp.text.strip():
                return {}
            return resp.json()
        except Exception as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))
            else:
                raise RuntimeError(f"Hyperbrowser request failed: {exc}") from exc

    raise RuntimeError(f"Hyperbrowser request failed: {last_error}")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": "evez-hyperbrowser-runner"}


@app.post("/run", response_model=BrowserTaskResponse)
def run_task(req: BrowserTaskRequest) -> BrowserTaskResponse:
    run_id = req.run_id or f"hb_{uuid.uuid4().hex[:12]}"
    session_id: Optional[str] = None
    job_id: Optional[str] = None
    live_url: Optional[str] = None
    recording_status: Optional[str] = None
    recording_url: Optional[str] = None
    result: Dict[str, Any] = {}

    try:
        session = _request("POST", "/api/session", json_body=req.sessionOptions)
        session_id = session.get("id")
        if not session_id:
            raise RuntimeError("Hyperbrowser did not return a session id")

        started = _request(
            "POST",
            "/api/task/hyper-agent",
            json_body={
                "task": req.task,
                "version": req.version,
                "llm": req.llm,
                "maxSteps": req.maxSteps,
                "keepBrowserOpen": req.keepBrowserOpen,
                "sessionId": session_id,
                "useCustomApiKeys": True,
                "apiKeys": {"openai": OPENAI_API_KEY},
            },
        )
        job_id = started.get("jobId")
        live_url = started.get("liveUrl") or session.get("liveUrl")
        if not job_id:
            raise RuntimeError("Hyperbrowser did not return a jobId")

        deadline = time.time() + req.timeoutSeconds
        last_status = "pending"

        while time.time() < deadline:
            status_payload = _request("GET", f"/api/task/hyper-agent/{job_id}/status")
            last_status = status_payload.get("status", "pending")
            if last_status in {"completed", "failed", "stopped"}:
                break
            time.sleep(req.pollIntervalSeconds)
        else:
            _request("PUT", f"/api/task/hyper-agent/{job_id}/stop")
            raise TimeoutError(f"HyperAgent task timed out after {req.timeoutSeconds}s")

        result = _request("GET", f"/api/task/hyper-agent/{job_id}")

        try:
            recording = _request("GET", f"/api/session/{session_id}/recording-url")
            recording_status = recording.get("status")
            recording_url = recording.get("recordingUrl")
        except Exception:
            recording_status = "unavailable"
            recording_url = None

        status = result.get("status", last_status)
        data = result.get("data") or {}

        return BrowserTaskResponse(
            ok=status == "completed",
            run_id=run_id,
            session_id=session_id,
            job_id=job_id,
            live_url=live_url or result.get("liveUrl"),
            recording_status=recording_status,
            recording_url=recording_url,
            status=status,
            final_result=data.get("finalResult"),
            steps=data.get("steps") or [],
            error=result.get("error"),
            raw=result,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=BrowserTaskResponse(
                ok=False,
                run_id=run_id,
                session_id=session_id,
                job_id=job_id,
                live_url=live_url,
                recording_status=recording_status,
                recording_url=recording_url,
                status="failed",
                final_result=None,
                steps=[],
                error=str(exc),
                raw=result,
            ).model_dump(),
        ) from exc

    finally:
        if session_id and not req.keepBrowserOpen:
            try:
                _request("PUT", f"/api/session/{session_id}/stop")
            except Exception:
                pass