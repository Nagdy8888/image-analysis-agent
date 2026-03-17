"""Build LangGraph pipeline: preprocessor → vision → season_tagger → END (Phase 2)."""
from langgraph.graph import END, START, StateGraph

from .nodes import image_preprocessor, vision_analyzer, tag_season
from .schemas.states import ImageTaggingState


def build_graph():
    """Linear graph: START → image_preprocessor → vision_analyzer → season_tagger → END."""
    builder = StateGraph(ImageTaggingState)

    builder.add_node("image_preprocessor", image_preprocessor)
    builder.add_node("vision_analyzer", vision_analyzer)
    builder.add_node("season_tagger", tag_season)

    builder.add_edge(START, "image_preprocessor")
    builder.add_edge("image_preprocessor", "vision_analyzer")
    builder.add_edge("vision_analyzer", "season_tagger")
    builder.add_edge("season_tagger", END)

    return builder.compile()
