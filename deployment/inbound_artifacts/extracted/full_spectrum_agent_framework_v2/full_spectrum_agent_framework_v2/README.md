# Full Spectrum Agent Framework v2

This bundle collapses the framework into one deployable surface.

What it includes:
- `ALL_IN_ONE.md`: unified spec
- `config/system.json`: master registry for agents, tools, daemon loops, and schedules
- `scripts/daemon_runner.py`: runs the enabled daemon loops and logs chronicle entries
- `scripts/spawn_subagent.py`: emits a task-specific subagent bundle from the shared framework
- `cron/evez.crontab`: cron jobs for continuous operation
- `scripts/install_cron.sh`: installs the bundled cron file on Unix-like systems
- `templates/`: shared markdown templates

This is built for lawful, local control surfaces:
- local shell / server / VM / VPS
- Docker or cron-capable Unix environment
- official APIs and authorized automation only

## Quick start

```bash
cd full_spectrum_agent_framework_v2
python3 scripts/spawn_subagent.py \
  --name skeptic-entity \
  --role "Adversarial verifier" \
  --goal "Attack weak conclusions before commitment" \
  --task "Challenge any CE that survives initial scoring"

python3 scripts/daemon_runner.py --config config/system.json --once
bash scripts/install_cron.sh
```

## Cron notes

The included cron file schedules:
- 5-minute daemon pass
- 15-minute subagent maintenance
- hourly chronicle compression
- daily benchmark/report
- weekly archive/prune

Cron runs only where you install it. It does not escape device permissions or browser boundaries.
