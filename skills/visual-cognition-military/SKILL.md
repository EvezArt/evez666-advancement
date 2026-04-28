---
name: visual-cognition
description: Generate animated cognitive visualizations mapped to the user's identity and system state. Creates 60-second videos showing ontology graphs, detection flows, quantum attractor evolution, and threat correlation maps. Use when you need to render complex system state into understandable motion graphics tailored to the user's projects and identity.

triggers:
  - "make cognitive visuals"
  - "generate visualizations"
  - "create cognitive map video"
  - "visualize my system"
  - "60 second video"
  - "make me a visual"
  - "cognitive visuals mapped to me"

provides:
  - Animated ontology graph traversal (60s MP4)
  - Quantum attractor state evolution movie
  - Threat/UAP detection correlation timeline
  - Personal cognitive map (Steven-centered system view)
  - Export to MP4 (H.264) or GIF

setup:
  - Requires Python packages: numpy, matplotlib, networkx, imageio-ffmpeg
  - Installs via: pip install numpy matplotlib networkx imageio-ffmpeg
  - Output directory: /root/.openclaw/workspace/visuals/
  - Optional: ffmpeg system package for higher quality

usage:

  # Generate all cognitive visuals (60s each)
  python -m skills.visual_cognition.generate --all

  # Generate just the ontology evolution video
  python -m skills.visual_cognition.generate --ontology

  # Generate user-centered cognitive map
  python -m skills.visual_cognition.generate --user-map

  # Generate quantum attractor evolution
  python -m skills.visual_cognition.generate --quantum

  # Custom duration
  python -m skills.visual_cognition.generate --all --duration 120

  # List available visualizations
  python -m skills.visual_cognition.generate --list

configuration:
  OUTPUT_DIR:           /root/.openclaw/workspace/visuals/
  ONTOLOGY_PATH:        /root/.openclaw/workspace/memory/ontology/graph.jsonl
  USER_ENTITY_ID:       p_001
  DURATION_SECONDS:     60
  FPS:                  30
  RESOLUTION:           [1920, 1080]
  THEME_COLORS:         {"background": "#0a0a0a", "node": "#00ffff", "edge": "#404040", "highlight": "#ff6b6b"}

security:
  - Reads only workspace files (ontology, memory logs)
  - No external network calls
  - Output stored locally; you control distribution
  - Deterministic rendering (same input → same video)

architecture:
  1. Data Ingestion: Loads ontology graph, recent detections, quantum state logs
  2. Layout Engine: NetworkX spring / spectral layout with time evolution
  3. Animation Loop: Matplotlib animation → frames → imageio writer
  4. Personalization: Highlights nodes related to USER_ENTITY_ID
  5. Rendering: MP4 via H.264 encoder (or GIF fallback)

output-files:
  - visuals/ontology_evolution.mp4        (graph growth over time)
  - visuals/user_cognitive_map.mp4        (Steven-centered network)
  - visuals/quantum_attractor_evolution.mp4
  - visuals/threat_correlation_timeline.mp4
  - visuals/visuals_manifest.json         (metadata, hashes)

integration:
  - Call from any session: /make cognitive visuals
  - Auto-run via cron if desired (e.g., daily digest)
  - Can pipe to Telegram/Discord as video message
  - Evidence‑preserving: each video SHA‑256 logged to memory/visuals_evidence.jsonl

limitations:
  - Requires modest CPU; 60s @ 30fps ≈ 1800 frames rendered
  - Large ontologies (>200 nodes) may slow layout; consider subsampling
  - No real‑time streaming; batch render only

next-steps:
  - Add WebGL/Three.js export for interactive exploration
  - Hook to live CellNetwork stream for real‑time dashboard
  - Generate per‑session personalized visual summaries
  - Add voiceover synthesis (tts) for narrative walkthroughs

---