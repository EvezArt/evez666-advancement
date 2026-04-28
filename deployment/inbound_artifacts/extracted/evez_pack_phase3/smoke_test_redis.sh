#!/usr/bin/env bash
set -euo pipefail

N8N_BASE="${N8N_BASE:-http://localhost:5678/webhook}"
STATE_BASE="${STATE_BASE:-http://localhost:8100}"
HYPER_BASE="${HYPER_BASE:-http://localhost:8000}"

echo "[1/5] state-service health"
curl -fsS "$STATE_BASE/health" | tee /tmp/evez-state-health.json

echo "[2/5] hyperbrowser-runner health"
curl -fsS "$HYPER_BASE/health" | tee /tmp/evez-hyper-health.json

echo "[3/5] orchestrator health"
curl -fsS "$N8N_BASE/evez-health" | tee /tmp/evez-orchestrator-health.json

echo "[4/5] dispatching non-mutating smoke task"
RUN_JSON=$(curl -fsS -X POST "$N8N_BASE/evez-orchestrator"   -H 'Content-Type: application/json'   -d '{
    "task": "Smoke test readiness check",
    "objective": "Return a readiness summary only. Do not call GitHub or browser tools.",
    "context": {"smoke_test": true, "non_mutating": true},
    "browser": {"required": false},
    "github": {
      "issue": {"required": false},
      "commit": {"required": false},
      "workflow": {"required": false}
    }
  }')
echo "$RUN_JSON" | tee /tmp/evez-run.json

RUN_ID=$(python - <<'PY2'
import json
with open('/tmp/evez-run.json') as f:
    data = json.load(f)
print(data.get('run_id', ''))
PY2
)

if [ -z "$RUN_ID" ]; then
  echo "No run_id returned" >&2
  exit 1
fi

echo "[5/5] reading run status for $RUN_ID"
curl -fsS "$N8N_BASE/evez-status?run_id=$RUN_ID" | tee /tmp/evez-status.json

echo "Smoke test completed."
