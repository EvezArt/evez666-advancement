# Living Logic Daemon scaffold for `evez-agentnet`

This subtree is designed to be dropped into `EvezArt/evez-agentnet` next to the existing ORS layer.

## What it adds

The existing repo already has a reasoning spine in `ors/`. This scaffold adds a stateful runtime layer:

- boot from latest checkpoint instead of waking blank
- preserve unresolved residue instead of flattening everything into fake certainty
- track identity attractors (`observer`, `auditor`, `builder`)
- checkpoint ontology, laws, branches, and dark-state pressure after every step
- reopen unfinished cognitive residue on next start

## File map

```text
cognition/
  __init__.py
  models.py        # state, branch, identity, valuation dataclasses
  checkpoint.py    # latest-checkpoint load/save
  daemon.py        # boot → observe → revise → checkpoint loop
run_cognition_daemon.py
```

## Integration targets inside the current repo

The repo README describes:

- `scanner/`
- `predictor/`
- `generator/`
- `shipper/`
- `worldsim/`
- `spine/`
- `orchestrator.py`

The cleanest integration path is:

1. instantiate `LivingLogicDaemon` at orchestrator startup
2. feed scanner outputs into `daemon.step(...)`
3. use `active_identity` to bias which agent acts next
4. mirror checkpoints into the repo's existing provenance spine
5. use unresolved residue as a work queue for evidence-seeking runs

## Example

```bash
python run_cognition_daemon.py --state-dir .state --input "deploying a builder identity requires preserving unresolved risk branches"
```

## Why this matters

This is not a full AGI stack. It is the missing persistence kernel:

- cognition survives restarts through checkpoints
- identities are earned from repeated executive use
- unresolvedness is carried forward instead of erased
- ontology can widen without pretending every branch was settled

That is enough to stop the system from acting like every session is the first morning after a fucking lobotomy.
