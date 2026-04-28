# Symbol‑Aware Governance and Stability Certificates

## Overview

The EVEZ platform incorporates a dedicated Information Bottleneck (IB) analysis agent, **EVEZGameShark**, and a stability‑certificate subsystem to provide continuous, phase‑aware monitoring of the autonomous control stack. This layer operates strictly in PREPARE‑ONLY mode and has read‑only access to immutable logs (spine), deterministic replays (rollbackengine), and Oracle v2.3 governance outputs. Its purpose is to:

1. **Learn emergent behavioural attractors** directly from system episodes
2. **Estimate dynamical stability** using the Quantum Entropy / EVEZ‑Laws equations
3. **Inform Tier‑0 / Tier‑1 Oracle thresholds** with a compact symbolic state

---

## IB Phase Analysis

At regular intervals, the IB agent samples recent episodes from spine, reconstructs canonical symbolic traces using rollbackengine, and trains an Information Bottleneck Transformer (IB‑Transformer) to reconstruct these sequences under a tunable mutual‑information constraint. The agent sweeps a schedule of bottleneck strengths **β** and, for each value, records symbol‑emergence metrics including:

- **Cluster separation** (silhouette score)
- **Effective rank** of the latent representation
- **Representation variance**

The resulting β–phase curve is stored as `ib_phase_latest.json` and summarized into a small profile (`ib_profile_latest.json`) containing:

- Estimated critical β (β_crit)
- Maximum cluster emergence score
- Minimum effective rank
- Integer estimate of the number of stable attractors

---

## Symbolic Regimes and Safety Profiles

From the IB phase summary, the system derives a symbolic regime label:

| Regime | Condition | Safety Profile |
|--------|-----------|----------------|
| **continuous** | max cluster score < 0.2 | EXPLORATION_GUARDED |
| **transitional** | 0.2 ≤ max cluster score < 0.5 | TRANSITIONAL_LOCKDOWN |
| **symbolic** | max cluster score ≥ 0.5 | SYMBOLIC_STABLE (or SYMBOLIC_HIGH_COMPLEXITY if >7 attractors) |

Each profile maps directly to Oracle v2.3 configuration:

- Caps on capital deployment
- Delegation depth limits
- Self‑modification permissions
- Human‑approval flags

---

## Stability Certificates using EVEZ‑Laws

For each latent attractor discovered by IB‑Transformer, the stability subsystem aggregates episode‑level statistics and computes numeric indicators inspired by the EVEZ‑Laws framework:

| Indicator | Computation | Interpretation |
|-----------|-------------|----------------|
| **Lyapunov‑like (λ)** | Mean log divergence of P&L between consecutive episodes | Negative = stable, Positive = divergent |
| **Entropy rate** | Standard deviation of P&L (proxy for KS entropy) | Low = ordered, High = disordered |
| **Dwell half‑life** | Average run length of same cluster | Long = metastable hysteresis |
| **FIRE/Override rates** | Fraction of episodes with FIRE flags or human overrides | High = operational stress |

From these, a stability tier is assigned:

- **SAFE**: λ < -3.0, entropy < 0.1, FIRE < 1%, overrides < 1%
- **MARGINAL**: λ < 0.5, entropy < 0.3, FIRE < 5%, overrides < 5%
- **UNSAFE**: otherwise

Each tier includes a human‑readable certificate referencing EVEZ‑Laws language for auditability.

---

## Coupling to Oracle v2.3

Every high‑impact decision evaluated by Comet Oracle v2.3 receives, in its decision context, the current IB safety profile and relevant stability certificates. Oracle's DCOP‑based Tier‑0 and Tier‑1 logic uses this information to adjust thresholds dynamically:

- **SAFE + SYMBOLIC_STABLE**: Normal wealth‑acquisition workflows within Financial Variance Delta and Delegation Depth limits
- **MARGINAL or TRANSITIONAL_LOCKDOWN**: Tighter constraints, block structural self‑modification, require human review
- **UNSAFE**: Enforce TRANSITIONAL_LOCKDOWN, zero capital deployment, halt non‑critical operations

The IB–Oracle coupling thus transforms emergent symbolic structure and dynamical stability estimates into real‑time control signals for the tiered governance architecture.

---

## Auditability and Red‑Teaming

All IB reports, stability certificates, and Oracle decisions that reference them are immutably logged and associated with unique identifiers. This enables:

- **Regulatory audits** to reconstruct not only what the system did, but in which symbolic regime and stability tier it was operating
- **Red‑team exercises** to stress‑test the system by deliberately driving it into high‑β and high‑entropy regimes to confirm that IB‑aware thresholds trigger expected escalation and shutdown playbooks
- **Compliance verification** that Tier‑0 constitutional constraints (controller remains stable for all t ≥ 0, failures degrade gracefully rather than catastrophically) are satisfied

---

## Files and Endpoints

| File | Description | Endpoint (ib_service.py) |
|------|-------------|--------------------------|
| `ib_phase_latest.json` | β sweep results | GET /ib/phase |
| `ib_profile_latest.json` | Derived safety profile | GET /ib/profile |
| `ib_attractors_meta.json` | Attractor semantic tags | GET /ib/attractors |
| `ib_stability_latest.json` | Stability certificates | GET /ib/stability |
| `ib_dashboard.html` | Visual monitoring UI | Serve from file server |

---

## Running the IB Analysis Pipeline

```bash
# Generate phase reports (requires spine + rollbackengine)
python3 /root/.openclaw/workspace/_evez/ib_agent/run_ib_analysis.py

# Generate stability certificates
python3 /root/.openclaw/workspace/_evez/ib_stability.py

# Start API service for dashboard
python3 /root/.openclaw/workspace/_evez/ib_service.py
```

**Dashboard URL**: `/_evez/ib_dashboard.html`
**API Base**: `http://localhost:8787`