# ib_service.py - FastAPI service for EVEZ IB dashboard + stability

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

BASE = Path("/root/.openclaw/workspace/_evez")

PHASE_FILE = BASE / "ib_phase_latest.json"
PROFILE_FILE = BASE / "ib_profile_latest.json"
ATTRACTOR_FILE = BASE / "ib_attractors_meta.json"
STABILITY_FILE = BASE / "ib_stability_latest.json"

app = FastAPI(title="EVEZGameShark IB Service", version="0.1.0")

# allow local dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _load_json(path: Path):
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{path.name} not found")
    with path.open() as f:
        return json.load(f)


@app.get("/ib/phase")
def get_phase():
    return _load_json(PHASE_FILE)


@app.get("/ib/profile")
def get_profile():
    return _load_json(PROFILE_FILE)


@app.get("/ib/attractors")
def get_attractors():
    return _load_json(ATTRACTOR_FILE)


@app.get("/ib/stability")
def get_stability():
    return _load_json(STABILITY_FILE)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8787)