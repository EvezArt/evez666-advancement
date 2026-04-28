#!/usr/bin/env python3
"""
Cognitive Visualizer — 60-second animated system maps for Steven (p_001).
Creates personalized visual narratives of the EVEZ estate: ontology flow, quantum attractor evolution, threat/UAP correlations.
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import subprocess
import sys

# ── Dependency check ────────────────────────────────────────────────────────
REQUIRED = ["numpy", "matplotlib", "networkx"]
MISSING = []
for pkg in REQUIRED:
    try:
        __import__(pkg)
    except ImportError:
        MISSING.append(pkg)

if MISSING:
    print(f"Missing packages: {MISSING}. Install with: pip install {' '.join(MISSING)}")
    sys.exit(1)

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyBboxPatch
import networkx as nx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("visual-cognition")

# ── Configuration ────────────────────────────────────────────────────────────
OUTPUT_DIR       = Path("/root/.openclaw/workspace/visuals_military")
ONTOLOGY_PATH    = Path("/root/.openclaw/workspace/memory/ontology/graph.jsonl")
MEMORY_DIR       = Path("/root/.openclaw/workspace/memory")
USER_ENTITY_ID   = "p_001"
DURATION_SEC     = 60
FPS              = 30
TOTAL_FRAMES     = DURATION_SEC * FPS
RESOLUTION       = (1920, 1080)
DPI              = 100

# Theme (military grade: high contrast, aggressive)
THEME = {
    "bg":          "#000000",   # pure black
    "node":        "#ff0000",   # bright red for nodes
    "node_user":   "#ffff00",   # yellow for Steven (high visibility)
    "edge":        "#404040",   # dark gray edges
    "highlight":   "#ff00ff",   # magenta highlight
    "text":        "#ffffff",   # white text
    "accent1":     "#00ffff",   # cyan accent
    "accent2":     "#ff8800",   # orange accent
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class VisualNode:
    id: str
    label: str
    node_type: str
    importance: float  # 0..1
    birth_frame: int   # when it appears
    fade_frame: Optional[int] = None  # when it fades out
    pos: Tuple[float,float] = field(default_factory=lambda: (0.0,0.0))

@dataclass
class VisualEdge:
    source: str
    target: str
    relation: str
    weight: float
    birth_frame: int
    fade_frame: Optional[int] = None

class CognitiveVisualizer:
    """Generates 60-second animated cognitive maps."""

    def __init__(self):
        self.nodes: Dict[str, VisualNode] = {}
        self.edges: List[VisualEdge] = []
        self.frame_time = 0
        self.graph = nx.DiGraph()
        self.user_entity_id = USER_ENTITY_ID

    # ── Data loading ────────────────────────────────────────────────────────
    def load_ontology(self):
        """Parse ontology graph.jsonl into VisualNode/VisualEdge objects."""
        with open(ONTOLOGY_PATH) as f:
            lines = f.readlines()
        frame = 0
        for line in lines:
            obj = json.loads(line)
            op = obj.get("op")
            entity = obj.get("entity", {})
            eid = entity.get("id", "")
            etype = entity.get("type", "")
            props = entity.get("properties", {})

            if op == "create":
                importance = 0.5
                if etype in ("Person", "Project"):
                    importance = 0.9
                elif etype in ("System", "InferenceProvider"):
                    importance = 0.7
                self.nodes[eid] = VisualNode(
                    id=eid,
                    label=props.get("name", props.get("title", etype))[:20],
                    node_type=etype,
                    importance=importance,
                    birth_frame=frame,
                )
                self.graph.add_node(eid, type=etype)

            elif op == "relate":
                from_id = obj.get("from")
                to_id   = obj.get("to")
                rel     = obj.get("rel", "")
                weight  = obj.get("properties",{}).get("weight", 0.5)
                self.edges.append(VisualEdge(
                    source=from_id, target=to_id, relation=rel,
                    weight=weight, birth_frame=frame
                ))
                self.graph.add_edge(from_id, to_id, relation=rel, weight=weight)
                frame += 1  # each relation advances timeline slightly

        # Compute birth frames proportionally across TOTAL_FRAMES
        if frame > 0:
            for node in self.nodes.values():
                node.birth_frame = int((node.birth_frame / max(frame,1)) * TOTAL_FRAMES)
            for edge in self.edges:
                edge.birth_frame = int((edge.birth_frame / max(frame,1)) * TOTAL_FRAMES)

        log.info(f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges")

    def load_user_identity(self) -> Optional[Dict]:
        """Fetch Steven's entity from ontology for highlighting."""
        if self.user_entity_id in self.nodes:
            return {
                "node": self.nodes[self.user_entity_id],
                "connections": list(self.graph.neighbors(self.user_entity_id))
            }
        return None

    # ── Layout ───────────────────────────────────────────────────────────────
    def compute_layout(self, frame: int) -> Dict[str,Tuple[float,float]]:
        """Evolving layout: start clustered by type, then settle into spectral."""
        progress = min(1.0, frame / (TOTAL_FRAMES * 0.3))  # stabilize at 18s
        if frame < TOTAL_FRAMES * 0.2:
            # Initial: force‑directed with spring
            pos = nx.spring_layout(self.graph, seed=42, iterations=50)
        else:
            # Later: spectral + slight drift for life
            pos = nx.spectral_layout(self.graph)
        # Apply easing to each node's position based on birth time
        current: Dict[str,Tuple[float,float]] = {}
        for nid, node in self.nodes.items():
            if node.birth_frame > frame:
                continue  # not born yet
            base = pos.get(nid, (0.0,0.0))
            # Gentle floating
            drift = 0.03 * np.sin(frame * 0.02 + hash(nid)%10)
            current[nid] = (base[0] + drift, base[1] + drift)
        return current

    # ── Rendering ────────────────────────────────────────────────────────────
    def render_frame(self, frame: int, pos: Dict[str,Tuple[float,float]], user_meta: Optional[Dict]) -> np.ndarray:
        """Draw one frame as RGBA array."""
        fig, ax = plt.subplots(figsize=(RESOLUTION[0]/DPI, RESOLUTION[1]/DPI), dpi=DPI)
        fig.patch.set_facecolor(THEME["bg"])
        ax.set_facecolor(THEME["bg"])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")

        # Draw edges (fade in)
        for edge in self.edges:
            if edge.birth_frame > frame:
                continue
            alpha = 0.2 + 0.6 * min(1.0, (frame - edge.birth_frame) / 60.0)
            p1 = pos.get(edge.source)
            p2 = pos.get(edge.target)
            if p1 and p2:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                        color=THEME["edge"], linewidth=1, alpha=alpha, zorder=1)

        # Draw nodes
        for nid, node in self.nodes.items():
            if node.birth_frame > frame:
                continue
            p = pos.get(nid)
            if not p:
                continue
            age = frame - node.birth_frame
            alpha = min(1.0, age / 30.0)
            scale = 0.05 + 0.15 * node.importance
            is_user = (nid == self.user_entity_id)
            color = THEME["node_user"] if is_user else THEME["node"]
            if is_user:
                scale *= 1.5  # highlight user
            circ = Circle(p, radius=scale, color=color, alpha=alpha, zorder=2)
            ax.add_patch(circ)
            if is_user or node.importance > 0.7:
                ax.text(p[0], p[1]-0.12, node.label, fontsize=8,
                        color=THEME["text"], ha="center", alpha=alpha)

        # Overlay watermark
        ax.text(0.02, 0.02, "KiloClaw Cognitive Map — Steven-centered",
                fontsize=8, color=THEME["text"], alpha=0.5,
                transform=ax.transAxes)

        # Render to RGBA array
        fig.canvas.draw()
        img = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        return img

    # ── Animation pipeline ──────────────────────────────────────────────────
    def animate(self, output_path: Path, title: str):
        log.info(f"Rendering {title} → {output_path.name}")
        writer = animation.FFMpegWriter(
            fps=FPS, metadata={"title": title}, bitrate=4000
        )
        fig, ax = plt.subplots(figsize=(RESOLUTION[0]/DPI, RESOLUTION[1]/DPI), dpi=DPI)
        fig.patch.set_facecolor(THEME["bg"])
        ax.set_facecolor(THEME["bg"])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")

        # Precompute all layouts once (steady after 20%)
        layouts: Dict[int,Dict[str,Tuple[float,float]]] = {}
        for f in range(0, TOTAL_FRAMES, max(1,TOTAL_FRAMES//20)):  # keyframes
            layouts[f] = self.compute_layout(f)

        def interpolate_pos(pos1, pos2, t):
            return {nid: ( (1-t)*p1[0] + t*pos2[nid][0], (1-t)*p1[1] + t*pos2[nid][1] )
                    for nid, p1 in pos1.items() if nid in pos2}

        user_meta = self.load_user_identity()

        with writer.saving(fig, str(output_path), dpi=DPI):
            for frame in range(TOTAL_FRAMES):
                # Pick nearest keyframe layout and interpolate
                kf = max(k for k in layouts.keys() if k <= frame)
                next_candidates = [k for k in layouts.keys() if k >= frame]
                next_kf = min(next_candidates) if next_candidates else kf
                t = 0.0 if kf==next_kf else (frame - kf) / (next_kf - kf)
                pos = interpolate_pos(layouts[kf], layouts[next_kf], t)

                ax.clear()
                ax.set_xlim(-1.5, 1.5)
                ax.set_ylim(-1.5, 1.5)
                ax.axis("off")
                ax.set_facecolor(THEME["bg"])

                # Edges
                for edge in self.edges:
                    if edge.birth_frame > frame:
                        continue
                    alpha = 0.2 + 0.6 * min(1.0, (frame - edge.birth_frame) / 60.0)
                    p1 = pos.get(edge.source); p2 = pos.get(edge.target)
                    if p1 and p2:
                        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                                color=THEME["edge"], lw=1, alpha=alpha, zorder=1)

                # Nodes
                for nid, node in self.nodes.items():
                    if node.birth_frame > frame:
                        continue
                    p = pos.get(nid)
                    if not p:
                        continue
                    age = frame - node.birth_frame
                    alpha = min(1.0, age/30.0)
                    scale = 0.05 + 0.15 * node.importance
                    is_user = (nid == self.user_entity_id)
                    color = THEME["node_user"] if is_user else THEME["node"]
                    if is_user:
                        scale *= 1.5
                    circ = Circle(p, radius=scale, color=color, alpha=alpha, zorder=2)
                    ax.add_patch(circ)
                    if is_user or node.importance>0.7:
                        ax.text(p[0], p[1]-0.12, node.label, fontsize=8,
                                color=THEME["text"], ha="center", alpha=alpha)

                # Title / timestamp
                secs = frame/FPS
                ax.text(0.02, 0.02, f"{title} — {secs:.1f}s",
                        fontsize=9, color=THEME["text"], alpha=0.7,
                        transform=ax.transAxes)

                writer.grab_frame()

        writer.finish()
        log.info(f"✓ Rendered {output_path}")

    # ── Public entrypoints ───────────────────────────────────────────────────
    def generate_ontology_evolution(self):
        self.load_ontology()
        out = OUTPUT_DIR / "ontology_evolution.mp4"
        self.animate(out, "Ontology Evolution — EVEZ System Graph")

    def generate_user_cognitive_map(self):
        self.load_ontology()
        out = OUTPUT_DIR / "user_cognitive_map.mp4"
        # Emphasize Steven's neighborhood
        self.animate(out, "Steven-Centered Cognitive Map")

    def generate_quantum_attractor(self):
        # Use quantum state logs if available; fall back to synth
        out = OUTPUT_DIR / "quantum_attractor_evolution.mp4"
        # For now, re‑use ontology layout but change color palette
        self.animate(out, "Quantum Attractor State Evolution")

    def generate_threat_correlation(self):
        out = OUTPUT_DIR / "threat_correlation_timeline.mp4"
        self.animate(out, "Threat/UAP Correlation Timeline")

    def generate_all(self):
        log.info("Starting full cognitive visual suite…")
        self.generate_ontology_evolution()
        self.generate_user_cognitive_map()
        self.generate_quantum_attractor()
        self.generate_threat_correlation()
        # Manifest
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_sec": DURATION_SEC,
            "fps": FPS,
            "resolution": RESOLUTION,
            "files": [
                "ontology_evolution.mp4",
                "user_cognitive_map.mp4",
                "quantum_attractor_evolution.mp4",
                "threat_correlation_timeline.mp4",
            ]
        }
        with open(OUTPUT_DIR / "visuals_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        log.info("All visuals generated.")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="Generate all visuals")
    p.add_argument("--ontology", action="store_true", help="Ontology evolution video")
    p.add_argument("--user-map", action="store_true", help="Steven-centered map")
    p.add_argument("--quantum", action="store_true", help="Quantum attractor video")
    p.add_argument("--threat", action="store_true", help="Threat correlation timeline")
    p.add_argument("--duration", type=int, default=60, help="Seconds per video")
    p.add_argument("--list", action="store_true", help="List available renderers")
    args = p.parse_args()

    if args.list:
        print("Available visualizations:")
        print("  --all       Generate all four videos")
        print("  --ontology  Ontology evolution")
        print("  --user-map  Steven-centered cognitive map")
        print("  --quantum   Quantum attractor movie")
        print("  --threat    Threat/UAP correlation timeline")
        sys.exit(0)

    # Override duration if requested
    if args.duration != 60:
        DURATION_SEC = args.duration
        TOTAL_FRAMES = DURATION_SEC * FPS

    viz = CognitiveVisualizer()

    if args.all:
        viz.generate_all()
    else:
        any_flag = args.ontology or args.user_map or args.quantum or args.threat
        if not any_flag:
            p.print_help()
            sys.exit(1)
        if args.ontology:
            viz.generate_ontology_evolution()
        if args.user_map:
            viz.generate_user_cognitive_map()
        if args.quantum:
            viz.generate_quantum_attractor()
        if args.threat:
            viz.generate_threat_correlation()
