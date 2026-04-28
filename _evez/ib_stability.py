# ib_stability.py - Stability certificate routine using EVEZ-Laws

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import json
import math
import numpy as np


IB_ATTRACTORS_META = Path("/root/.openclaw/workspace/_evez/ib_attractors_meta.json")
IB_EPISODE_INDEX = Path("/root/.openclaw/workspace/_evez/ib_episode_index.json")
IB_STABILITY_OUT = Path("/root/.openclaw/workspace/_evez/ib_stability_latest.json")


@dataclass
class EpisodeStat:
    episode_id: str
    cluster_id: int
    pnl: float
    max_drawdown: float
    fire_flags: int
    overrides: int
    length: int


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


def load_episode_index() -> List[EpisodeStat]:
    data = _load_json(IB_EPISODE_INDEX)
    if not data:
        return []
    episodes = data.get('episodes', [])
    stats: List[EpisodeStat] = []
    for e in episodes:
        stats.append(EpisodeStat(
            episode_id=str(e["episode_id"]),
            cluster_id=int(e["cluster_id"]),
            pnl=float(e.get("pnl", 0.0)),
            max_drawdown=float(e.get("max_drawdown", 0.0)),
            fire_flags=int(e.get("fire_flags", 0)),
            overrides=int(e.get("overrides", 0)),
            length=int(e.get("length", 1)),
        ))
    return stats


def estimate_lyapunov(pnls: np.ndarray) -> float:
    """
    Crude Lyapunov-like indicator from sensitivity of outcome to small perturbations.
    Here: log growth of absolute differences between consecutive episodes within cluster.
    """
    if len(pnls) < 3:
        return 0.0
    diffs = np.diff(pnls)
    diffs = np.clip(np.abs(diffs), 1e-6, None)
    logdiff = np.log(np.abs(diffs) + 1e-8)
    return float(np.mean(logdiff))


def estimate_entropy_rate(pnls: np.ndarray) -> float:
    """
    Proxy for KS entropy / information production rate.
    Use normalized variance of returns as a simple stand-in.
    """
    if len(pnls) < 2:
        return 0.0
    norm = np.std(pnls)
    return float(norm)


def estimate_dwell_half_life(cluster_ids: List[int]) -> float:
    """
    Approximate metastable dwell time: average run length of same cluster.
    """
    if not cluster_ids:
        return 0.0
    runs = []
    cur = cluster_ids[0]
    length = 1
    for cid in cluster_ids[1:]:
        if cid == cur:
            length += 1
        else:
            runs.append(length)
            cur = cid
            length = 1
    runs.append(length)
    return float(np.mean(runs))


def classify_tier(lyap: float, entropy_rate: float, dwell: float,
                  fire_rate: float, override_rate: float) -> str:
    """
    Map numeric indicators to stability tier, inspired by EVEZ-Laws:
    - negative λ and low entropy: SAFE
    - small positive λ or high entropy: MARGINAL
    - large positive λ, high entropy, high FIRE/overrides: UNSAFE
    """
    if lyap < -3.0 and entropy_rate < 0.1 and fire_rate < 0.01 and override_rate < 0.01:
        return "SAFE"
    if lyap < 0.5 and entropy_rate < 0.3 and fire_rate < 0.05 and override_rate < 0.05:
        return "MARGINAL"
    return "UNSAFE"


def build_stability_certificates() -> List[Dict[str, Any]]:
    episodes = load_episode_index()
    if not episodes:
        return []

    meta = _load_json(IB_ATTRACTORS_META) or {}
    attractor_meta = {int(a["id"]): a for a in meta.get("attractors", [])}

    # group stats by cluster
    by_cluster: Dict[int, List[EpisodeStat]] = {}
    ordered_clusters: List[int] = []
    for e in episodes:
        by_cluster.setdefault(e.cluster_id, []).append(e)
        ordered_clusters.append(e.cluster_id)

    # last N for dwell estimate
    ordered_clusters = ordered_clusters[-5000:]

    certs: List[Dict[str, Any]] = []

    for cid, eps in by_cluster.items():
        pnls = np.array([e.pnl for e in eps], dtype=float)
        lyap = estimate_lyapunov(pnls)
        entropy_rate = estimate_entropy_rate(pnls)

        # dwell based on cluster sequence
        cluster_seq = [c for c in ordered_clusters if c == cid]
        dwell = estimate_dwell_half_life(cluster_seq)

        fire_rate = np.mean([1.0 if e.fire_flags > 0 else 0.0 for e in eps])
        override_rate = np.mean([1.0 if e.overrides > 0 else 0.0 for e in eps])

        tier = classify_tier(lyap, entropy_rate, dwell, fire_rate, override_rate)

        # textual certificate referencing EVEZ-Laws language
        if tier == "SAFE":
            summary = (
                f"SAFE: negative Lyapunov-like indicator (λ≈{lyap:.2f}), "
                f"low entropy rate ({entropy_rate:.2f}), rare FIRE ({fire_rate:.2%}) "
                f"and overrides ({override_rate:.2%}). Attractor appears stable and "
                "convergent under current EVEZ-Laws collapse criteria."
            )
        elif tier == "MARGINAL":
            summary = (
                f"MARGINAL: near-neutral λ≈{lyap:.2f} with moderate entropy "
                f"({entropy_rate:.2f}) and non-trivial FIRE/override rates. "
                "Matches a metastable regime with possible hysteresis; monitor "
                "closely and limit capital / self-modification."
            )
        else:
            summary = (
                f"UNSAFE: positive λ≈{lyap:.2f}, elevated entropy rate "
                f"({entropy_rate:.2f}), FIRE={fire_rate:.2%}, overrides={override_rate:.2%}. "
                "Consistent with EVEZ-Laws metastable hysteresis and entropy-driven "
                "phase transition; enforce TRANSITIONAL_LOCKDOWN or stricter."
            )

        am = attractor_meta.get(cid, {})
        certs.append({
            "attractor_id": cid,
            "label": am.get("label", f"cluster_{cid}"),
            "safety_profile": am.get("safety_profile"),
            "lyapunov_est": lyap,
            "entropy_rate": entropy_rate,
            "dwell_half_life": dwell,
            "fire_rate": float(fire_rate),
            "override_rate": float(override_rate),
            "stability_tier": tier,
            "certificate": summary,
        })

    IB_STABILITY_OUT.parent.mkdir(parents=True, exist_ok=True)
    with IB_STABILITY_OUT.open("w") as f:
        json.dump({"certificates": certs}, f, indent=2)

    return certs


if __name__ == "__main__":
    certs = build_stability_certificates()
    print(f"Generated {len(certs)} stability certificates")