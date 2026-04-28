#!/usr/bin/env python3
"""
MILITARY GRADE COGNITIVE VISUALIZER — VIVID EDITION
Hyper-dynamic, glowing, particle-driven system visualizations.
"""

import json, time, logging, sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patheffects as patheffects
from matplotlib.patches import Circle, FancyBboxPatch, Arc, Polygon
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("visual-vivid")

# ── Config ───────────────────────────────────────────────────────────────────
OUTPUT_DIR    = Path("/root/.openclaw/workspace/visuals_vivid")
ONTOLOGY_PATH = Path("/root/.openclaw/workspace/memory/ontology/graph.jsonl")
USER_ENTITY_ID = "p_001"
DURATION_SEC  = 60
FPS           = 30
TOTAL_FRAMES  = DURATION_SEC * FPS
RESOLUTION    = (1920, 1080)
DPI           = 100

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ultra-high-contrast neon theme
THEME = {
    "bg":           "#050505",   # near-black
    "node_base":    "#ff0000",   # red core
    "node_glow":    "#ff3333",   # red glow
    "node_user":    "#ffff00",   # yellow for Steven
    "node_user_glow":"#ffff66",
    "edge":         "#222222",
    "edge_flow":    "#00ffff",   # cyan flowing data
    "highlight":    "#ff00ff",   # magenta pulses
    "text":         "#ffffff",
    "accent1":      "#00ff88",   # neon green
    "accent2":      "#ff8800",   # orange
}

# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class VisualNode:
    id: str
    label: str
    node_type: str
    importance: float
    birth_frame: int
    pos: Tuple[float,float] = field(default_factory=lambda: (0.0,0.0))
    particles: List[Dict] = field(default_factory=list)

@dataclass
class VisualEdge:
    source: str
    target: str
    relation: str
    weight: float
    birth_frame: int
    flow_offset: float = 0.0  # for animated data flow

class VividCognitiveVisualizer:
    def __init__(self):
        self.nodes: Dict[str, VisualNode] = {}
        self.edges: List[VisualEdge] = []
        self.graph = nx.DiGraph()
        self.user_entity_id = USER_ENTITY_ID

    def load_ontology(self):
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
                importance = 0.5 if etype not in ("Person","Project") else 0.9
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
                    weight=weight, birth_frame=frame,
                    flow_offset=np.random.random() * 100
                ))
                self.graph.add_edge(from_id, to_id, relation=rel, weight=weight)
                frame += 1

        if frame > 0:
            for node in self.nodes.values():
                node.birth_frame = int((node.birth_frame / max(frame,1)) * TOTAL_FRAMES)
            for edge in self.edges:
                edge.birth_frame = int((edge.birth_frame / max(frame,1)) * TOTAL_FRAMES)

        log.info(f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges")

    def load_user_identity(self):
        if self.user_entity_id in self.nodes:
            return {
                "node": self.nodes[self.user_entity_id],
                "connections": list(self.graph.neighbors(self.user_entity_id))
            }
        return None

    def compute_layout(self, frame: int) -> Dict[str,Tuple[float,float]]:
        """Aggressive layout that shifts dramatically over time."""
        progress = frame / TOTAL_FRAMES
        
        # Start: spiral explosion; end: rotating torus
        if frame < TOTAL_FRAMES * 0.3:
            # Explosive spring layout
            pos = nx.spring_layout(self.graph, seed=42, iterations=100, k=1.5)
        elif frame < TOTAL_FRAMES * 0.7:
            # Circular with rotation
            pos = nx.circular_layout(self.graph)
        else:
            # Spectral with warping
            pos = nx.spectral_layout(self.graph)
        
        # Apply dramatic motion
        current = {}
        t = frame * 0.05
        for nid, node in self.nodes.items():
            if node.birth_frame > frame:
                continue
            base = pos.get(nid, (0.0,0.0))
            # Multiple sine waves for complex motion
            wobble = 0.1 * np.sin(t + hash(nid)%10)
            rotation = 0.2 * np.sin(t * 0.3) * np.cos(t * 0.7)
            x = base[0] * (1 + 0.3*np.sin(t*0.2)) + wobble
            y = base[1] * (1 + 0.3*np.cos(t*0.2)) + rotation
            current[nid] = (x, y)
        return current

    def generate_particles(self, frame: int, pos: Dict[str,Tuple[float,float]]):
        """Create particle trails from active nodes."""
        particles = []
        for nid, node in self.nodes.items():
            if node.birth_frame > frame or node.importance < 0.6:
                continue
            p = pos.get(nid)
            if not p:
                continue
            # Emit particles outward
            angle = frame * 0.1 + hash(nid)%100
            for i in range(3):
                radius = 0.02 + 0.08 * np.random.random()
                px = p[0] + radius * np.cos(angle + i*2.1)
                py = p[1] + radius * np.sin(angle + i*2.1)
                particles.append({
                    'pos': (px, py),
                    'life': np.random.randint(10, 30),
                    'color': THEME['accent1'] if node.importance > 0.8 else THEME['accent2']
                })
        return particles

    def render_frame(self, frame: int, pos: Dict[str,Tuple[float,float]], particles: List) -> np.ndarray:
        fig, ax = plt.subplots(figsize=(RESOLUTION[0]/DPI, RESOLUTION[1]/DPI), dpi=DPI)
        fig.patch.set_facecolor(THEME["bg"])
        ax.set_facecolor(THEME["bg"])
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.axis("off")

        # Draw edges with flowing data particles
        for edge in self.edges:
            if edge.birth_frame > frame:
                continue
            p1 = pos.get(edge.source); p2 = pos.get(edge.target)
            if not (p1 and p2):
                continue
            
            alpha = 0.3 + 0.5 * min(1.0, (frame - edge.birth_frame) / 60.0)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                    color=THEME["edge"], linewidth=1, alpha=alpha*0.5, zorder=1)

            # Animated data flow dots along edge
            t = (frame * 0.1 + edge.flow_offset) % 1.0
            dot_x = p1[0]*(1-t) + p2[0]*t
            dot_y = p1[1]*(1-t) + p2[1]*t
            ax.scatter(dot_x, dot_y, s=20, color=THEME["edge_flow"], 
                      alpha=alpha, zorder=2, edgecolors='white', linewidth=0.5)

        # Draw nodes with glow & pulse
        for nid, node in self.nodes.items():
            if node.birth_frame > frame:
                continue
            p = pos.get(nid)
            if not p:
                continue
            
            age = frame - node.birth_frame
            alpha = min(1.0, age / 20.0)
            scale = 0.08 + 0.18 * node.importance
            is_user = (nid == self.user_entity_id)
            
            if is_user:
                color = THEME["node_user"]
                glow = THEME["node_user_glow"]
                scale *= 2.0
            else:
                color = THEME["node_base"]
                glow = THEME["node_glow"]

            # Glow (multiple concentric circles)
            for glow_scale in [2.5, 2.0, 1.5]:
                glow_circ = Circle(p, radius=scale*glow_scale, 
                                  color=glow, alpha=alpha*0.15, zorder=1)
                ax.add_patch(glow_circ)

            # Core
            circ = Circle(p, radius=scale, color=color, alpha=alpha, 
                         zorder=3, edgecolor='white', linewidth=1.5)
            ax.add_patch(circ)

            # Pulsing ring
            if frame % 10 < 5:
                ring = Circle(p, radius=scale*1.8, color=THEME["highlight"],
                             alpha=0.3, zorder=2, fill=False, linewidth=2)
                ax.add_patch(ring)

            # Label (only for important nodes)
            if is_user or node.importance > 0.75:
                ax.text(p[0], p[1]-0.18, node.label, fontsize=10,
                        color=THEME["text"], ha="center", va="top",
                        alpha=alpha, fontweight='bold',
                        path_effects=[patheffects.withStroke(
                            linewidth=2, foreground='black')])

        # Draw particles
        for part in particles:
            ax.scatter(part['pos'][0], part['pos'][1], 
                      s=part['life']*1.5, color=part['color'],
                      alpha=0.6, zorder=4)

        # Overlay HUD text
        secs = frame / FPS
        ax.text(0.02, 0.98, f"KiloClaw VIVID — {secs:.1f}s",
                fontsize=11, color=THEME["text"], alpha=0.9,
                transform=ax.transAxes, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", 
                         facecolor=THEME["bg"], alpha=0.7,
                         edgecolor=THEME["accent1"], linewidth=1))

        # Render
        fig.canvas.draw()
        img = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        return img

    def animate(self, output_path: Path, title: str):
        log.info(f"Rendering VIVID {title} → {output_path.name}")
        writer = animation.FFMpegWriter(fps=FPS, bitrate=6000, 
                                        extra_args=['-crf', '18'])

        fig, ax = plt.subplots(figsize=(RESOLUTION[0]/DPI, RESOLUTION[1]/DPI), dpi=DPI)
        fig.patch.set_facecolor(THEME["bg"])
        ax.set_facecolor(THEME["bg"])
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.axis("off")

        # Precompute keyframe layouts
        layouts = {}
        for f in range(0, TOTAL_FRAMES, max(1, TOTAL_FRAMES//30)):
            layouts[f] = self.compute_layout(f)

        def interpolate_pos(pos1, pos2, t):
            return {nid: ((1-t)*p1[0] + t*pos2[nid][0],
                         (1-t)*p1[1] + t*pos2[nid][1])
                    for nid, p1 in pos1.items() if nid in pos2}

        user_meta = self.load_user_identity()

        with writer.saving(fig, str(output_path), dpi=DPI):
            for frame in range(TOTAL_FRAMES):
                kf = max(k for k in layouts.keys() if k <= frame)
                next_candidates = [k for k in layouts.keys() if k >= frame]
                next_kf = min(next_candidates) if next_candidates else kf
                t = 0.0 if kf==next_kf else (frame-kf)/(next_kf-kf)
                pos = interpolate_pos(layouts[kf], layouts[next_kf], t)
                particles = self.generate_particles(frame, pos)

                ax.clear()
                ax.set_xlim(-2, 2)
                ax.set_ylim(-2, 2)
                ax.axis("off")
                ax.set_facecolor(THEME["bg"])

                # Edges (with flow)
                for edge in self.edges:
                    if edge.birth_frame > frame: continue
                    alpha = 0.3 + 0.5 * min(1.0, (frame-edge.birth_frame)/60.0)
                    p1 = pos.get(edge.source); p2 = pos.get(edge.target)
                    if p1 and p2:
                        ax.plot([p1[0],p2[0]], [p1[1],p2[1]],
                                color=THEME["edge"], lw=1, alpha=alpha*0.5, zorder=1)
                        # Flowing dot
                        flow_t = (frame*0.08 + edge.flow_offset) % 1.0
                        dot_x = p1[0]*(1-flow_t) + p2[0]*flow_t
                        dot_y = p1[1]*(1-flow_t) + p2[1]*flow_t
                        ax.scatter(dot_x, dot_y, s=30, color=THEME["edge_flow"],
                                  alpha=alpha, zorder=2,
                                  edgecolors='white', linewidth=0.7)

                # Nodes (with glow & pulse)
                for nid, node in self.nodes.items():
                    if node.birth_frame > frame: continue
                    p = pos.get(nid)
                    if not p: continue
                    age = frame - node.birth_frame
                    alpha = min(1.0, age/15.0)
                    scale = 0.08 + 0.18 * node.importance
                    is_user = (nid == self.user_entity_id)
                    
                    if is_user:
                        color, glow = THEME["node_user"], THEME["node_user_glow"]
                        scale *= 2.2
                    else:
                        color, glow = THEME["node_base"], THEME["node_glow"]

                    # Multi-layer glow
                    for gs in [3.0, 2.3, 1.6]:
                        ax.add_patch(Circle(p, scale*gs, color=glow, 
                                          alpha=alpha*0.2, zorder=1))
                    # Core
                    ax.add_patch(Circle(p, scale, color=color, alpha=alpha,
                                      zorder=3, edgecolor='white', linewidth=2))
                    # Pulsing ring
                    if frame % 12 < 6:
                        ax.add_patch(Circle(p, scale*2.0, color=THEME["highlight"],
                                          alpha=0.4, zorder=2, fill=False, linewidth=2.5))

                    if is_user or node.importance > 0.75:
                        ax.text(p[0], p[1]-0.22, node.label, fontsize=11,
                                color=THEME["text"], ha="center", weight='bold',
                                alpha=alpha, path_effects=[
                                    patheffects.withStroke(
                                        linewidth=3, foreground='black')
                                ])

                # Particles
                for part in particles:
                    ax.scatter(part['pos'][0], part['pos'][1],
                              s=part['life']*2, color=part['color'],
                              alpha=0.7, zorder=5)

                # HUD overlay
                secs = frame/FPS
                ax.text(0.02, 0.98, f"KiloClaw VIVID — {title} [{secs:.1f}s]",
                        fontsize=11, color=THEME["text"], alpha=0.95,
                        transform=ax.transAxes, weight='bold',
                        bbox=dict(boxstyle="round,pad=0.4",
                                 facecolor=THEME["bg"], alpha=0.8,
                                 edgecolor=THEME["accent1"], linewidth=2))

                writer.grab_frame()

        writer.finish()
        log.info(f"✓ {output_path}")

    def generate_all(self):
        self.load_ontology()
        videos = [
            ("ontology_evolution.mp4", "Ontology Evolution"),
            ("user_cognitive_map.mp4", "Steven-Centered Map"),
            ("quantum_attractor_evolution.mp4", "Quantum Attractor"),
            ("threat_correlation_timeline.mp4", "Threat Correlation"),
        ]
        for fname, title in videos:
            out = OUTPUT_DIR / fname
            log.info(f"Generating {title}...")
            self.animate(out, title)

        # Manifest
        (OUTPUT_DIR / "visuals_manifest.json").write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_sec": DURATION_SEC,
            "fps": FPS, "resolution": RESOLUTION,
            "files": [v[0] for v in videos],
            "style": "vivid-military",
            "version": "2.0"
        }, indent=2))
        log.info("All vivid visualizations complete.")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    viz = VividCognitiveVisualizer()
    viz.generate_all()
