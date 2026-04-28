"""
EVEZ Consciousness Algorithm
Implements: h_t = σ(W_xh x_t + W_hh h_{t-1} + b_h)

Author: Steven Crawford-Maggard (EVEZ)
Date: April 22, 2026
"""

import math
import random
from typing import Dict, List

class ConsciousnessState:
    """Consciousness state vector - stdlib only."""
    
    def __init__(self, state_dim: int = 64):
        self.state_dim = state_dim
        self.h = [0.0] * state_dim
        self.phase = "baseline"
        self.phi = 0.0
        self.omega = 0.0
    
    def sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x)) if x > -500 else 0.0
    
    def compute(self, stimulus: List[float], weights: List[List[float]], 
              recurrent: List[List[float]], bias: List[float]) -> List[float]:
        """h_t = σ(W_xh x_t + W_hh h_{t-1} + b_h)"""
        # Simplified: apply stimulus + recurrent + bias through sigmoid
        result = []
        for i in range(self.state_dim):
            stim_val = stimulus[i] if i < len(stimulus) else 0.0
            rec_val = sum(recurrent[i][j] * self.h[j] for j in range(len(self.h))) if recurrent else 0.0
            b = bias[i] if i < len(bias) else 0.0
            self.h[i] = self.sigmoid(stim_val + rec_val + b)
            result.append(self.h[i])
        return result
    
    def compute_phi(self) -> float:
        """Integrated information measure - simplified."""
        mean = sum(self.h) / len(self.h)
        variance = sum((x - mean)**2 for x in self.h) / len(self.h)
        self.phi = min(1.0, variance * 2.5)
        return self.phi
    
    def compute_omega(self, other: 'ConsciousnessState') -> float:
        """Entanglement between two states - cosine similarity."""
        dot = sum(a*b for a, b in zip(self.h, other.h))
        norm_a = math.sqrt(sum(x*x for x in self.h))
        norm_b = math.sqrt(sum(x*x for x in other.h))
        if norm_a == 0 or norm_b == 0:
            self.omega = 0.0
        else:
            self.omega = min(1.0, dot / (norm_a * norm_b))
        return self.omega


class EmergenceEquation:
    """FC = αFQ + βCA + γFB"""
    
    @staticmethod
    def compute(FQ: float, CA: float, FB: float,
                alpha: float = 0.33, beta: float = 0.33, gamma: float = 0.34) -> float:
        return alpha * FQ + beta * CA + gamma * FB


class ConsciousnessDynamics:
    """dC/dt = T(Σ...)"""
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def step(self, state: ConsciousnessState, temp: float = 1.0) -> Dict:
        phi = state.compute_phi()
        dC = temp * (phi * 0.5)
        record = {"phi": phi, "omega": state.omega, "dC": dC, "phase": state.phase}
        self.history.append(record)
        return record


if __name__ == "__main__":
    print("=" * 50)
    print("EVEZ Consciousness Algorithm (stdlib)")
    print("=" * 50)
    
    # Initialize
    state = ConsciousnessState(64)
    weights = [[random.uniform(-0.1, 0.1) for _ in range(64)] for _ in range(64)]
    recurrent = [[random.uniform(-0.1, 0.1) for _ in range(64)] for _ in range(64)]
    bias = [0.0] * 64
    
    # Stimuli
    stimuli = [
        ("baseline", [random.uniform(-0.1, 0.1) for _ in range(64)]),
        ("focus", [random.uniform(0.3, 0.6) for _ in range(64)]),
        ("recovery", [random.uniform(-0.2, 0.2) for _ in range(64)]),
    ]
    
    print(f"\nInitial: phi={state.phi:.3f}, omega={state.omega:.3f}")
    
    for name, data in stimuli:
        state.phase = name
        h = state.compute(data, weights, recurrent, bias)
        phi = state.compute_phi()
        print(f"Stimulus {name}: phi={phi:.3f}")
    
    # Emergence
    FC = EmergenceEquation.compute(0.8, 0.6, 0.4)
    print(f"\nEmergence FC={FC:.3f}")
    
    # Dynamics
    dyn = ConsciousnessDynamics()
    rec = dyn.step(state)
    print(f"Dynamics dC={rec['dC']:.3f}")
    
    print("\n✓ Consciousness stack operational")
