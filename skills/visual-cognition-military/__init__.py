# Skill: visual-cognition
# Generates 60-second animated cognitive visualizations mapped to user identity.
# Entry point: python -m skills.visual_cognition.generate [options]

from .generate import CognitiveVisualizer, main

__all__ = ["CognitiveVisualizer", "main"]
