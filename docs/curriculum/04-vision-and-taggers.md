# 04 — Vision and taggers

This lesson covers how the vision node and the eight tagger nodes work and where prompts and taxonomy are used.

## Vision node

**File:** `backend/src/image_tagging/nodes/vision.py` — `vision_analyzer(state)`.

- Reads `image_base64` from state, builds a data URI, and sends one **HumanMessage** with text + image to GPT-4o.
- **System prompt** comes from `prompts/system.py` (`VISION_ANALYZER_PROMPT`): it asks the model to act as a visual product analyst and return JSON with `visual_description`, `dominant_mood`, `visible_subjects`, `color_observations`, etc.
- The response is parsed by `_parse_vision_response(text)` (handles optional markdown code fence); the result is split into `vision_description` and `vision_raw_tags` and returned as state updates.
- Retries: the node retries up to two times with exponential backoff (1s, 2s) on OpenAI/network errors before returning a failed state.

## Tagger nodes

**File:** `backend/src/image_tagging/nodes/taggers.py`.

- **Generic entry:** `run_tagger(state, category, instructions=None, max_tags=None)`. It reads `vision_description`, gets allowed values for the category from **taxonomy** (`get_flat_values(category)`), and builds a user prompt via `build_tagger_prompt(...)` in `prompts/tagger.py`. The LLM is invoked once per category; the response is parsed into tags and confidence_scores, filtered to allowed values and a minimum confidence, and optionally capped (e.g. max_tags for colors/objects). The result is appended to `partial_tags`.
- **Eight nodes:** `tag_season`, `tag_theme`, `tag_objects`, `tag_colors`, `tag_design`, `tag_occasion`, `tag_mood`, `tag_product` — each calls `run_tagger` with the appropriate category and options (e.g. max_tags for colors and objects).
- **Taxonomy** (`taxonomy.py`): Defines allowed values for each category (flat lists or hierarchical dicts). Validator and aggregator use the same taxonomy to validate and to map hierarchical values (e.g. parent/child for objects and product_type).

Next: [05-database-and-search.md](05-database-and-search.md)
