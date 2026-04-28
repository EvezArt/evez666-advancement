# evez-agentnet cognition scaffold

Repo-ready local scaffold for a restartable cognition daemon intended for `EvezArt/evez-agentnet`.

## What it adds

- persistent checkpoints instead of blank restarts
- unresolved branch preservation instead of fake certainty
- identity attractors: `observer`, `auditor`, `builder`
- executive arbitration for watch / evidence-seek / prepare / construct
- append-only lineage hashing
- build queue + draft artifact emission
- ORS-aware input tagging

## Run

```bash
python run_cognition_daemon.py --state-dir .state --input "boot the builder and preserve unresolved branches"
```

Or with multiple events:

```bash
cat > /tmp/events.txt <<'EOF'
observed contradictory market signals; unresolved branch should stay live
build the artifact but do not erase acquisition gaps
EOF
python run_cognition_daemon.py --state-dir .state --input-file /tmp/events.txt
```

## Deliverables

- `cognition/` package
- `run_cognition_daemon.py` entrypoint
- `docs/living-logic-daemon.md`
- `docs/evez-agentnet-integration-plan.md`

## Notes

The GitHub connector write path was blocked upstream during this session, so this bundle was built locally as a repo-ready subtree instead of being committed directly.
