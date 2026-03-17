"""Compiled graph export for image tagging pipeline."""
from .graph_builder import build_graph

graph = build_graph()

__all__ = ["graph", "build_graph"]
