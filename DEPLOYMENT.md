# Quantum-Evez Integration - Deployed

## Status: ✅ Active Components

### Skills Created
- `/root/.openclaw/workspace/skills/quantum-ez/SKILL.md` - Skill documentation
- `/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.py` - Python implementation
- `/root/.openclaw/workspace/skills/quantum-ez/quantum-ez.sh` - CLI wrapper

### Available Commands
```bash
./quantum-ez.sh metrics          # System metrics
./quantum-ez.sh algo list        # List quantum algorithms
./quantum-ez.sh algo run <name>  # Run algorithm (grover, qaoa, vqe, qft, shors)
./quantum-ez.sh state list       # List saved states
./quantum-ez.sh network status   # Network peer status
./quantum-ez.sh dashboard start  # Launch dashboard
./quantum-ez.sh auth generate <user>  # Generate quantum token
```

### Cron Jobs
- `/etc/cron.d/quantum-analysis` - Runs quantum analysis every 5 minutes

### Network
- Tailscale: Installed but requires systemd (container limitation)
- State storage: `/root/.openclaw/workspace/state/quantum/`

### Notes
- Tailscale requires host-level systemd to function properly
- Quantum algorithms run in simulated mode (no real QPU)
- Dashboard serves HTML file at `state/quantum/dashboard.html`