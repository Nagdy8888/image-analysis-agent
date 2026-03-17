"""Category tagger nodes: run_tagger (generic) + tag_season (spec 4.3)."""
import json
from typing import Any

from langchain_openai import ChatOpenAI

from ..prompts.tagger import build_tagger_prompt
from ..schemas.models import TagResult, TaggerOutput
from ..schemas.states import ImageTaggingState
from ..settings import OPENAI_API_KEY, OPENAI_MODEL
from ..taxonomy import get_flat_values, TAXONOMY


def _parse_tagger_response(text: str) -> TaggerOutput | None:
    """Parse LLM response into TaggerOutput."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        data = json.loads(stripped)
        return TaggerOutput(
            tags=data.get("tags", []),
            confidence_scores=data.get("confidence_scores", {}),
            reasoning=data.get("reasoning", ""),
        )
    except Exception:
        return None


async def run_tagger(
    state: ImageTaggingState,
    category: str,
    instructions: str | None = None,
) -> dict[str, Any]:
    """Generic tagger: vision_description + category → TagResult appended to partial_tags."""
    description = state.get("vision_description") or ""
    allowed = get_flat_values(category) if category in TAXONOMY else []
    if not allowed:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    prompt = build_tagger_prompt(description, category, allowed, instructions)
    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    try:
        response = await llm.ainvoke([{"role": "user", "content": prompt}])
        text = response.content if isinstance(response.content, str) else str(response.content)
    except Exception:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    out = _parse_tagger_response(text)
    if not out:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    # Filter to allowed only and confidence > 0.5
    tags = [t for t in out.tags if t in allowed]
    confidence_scores = {k: v for k, v in out.confidence_scores.items() if k in allowed and v > 0.5}
    tags = [t for t in tags if confidence_scores.get(t, 0) > 0.5]

    result = TagResult(category=category, tags=tags, confidence_scores=confidence_scores)
    return {"partial_tags": [result.model_dump()]}


async def tag_season(state: ImageTaggingState) -> dict[str, Any]:
    """Season tagger node."""
    return await run_tagger(state, "season")
