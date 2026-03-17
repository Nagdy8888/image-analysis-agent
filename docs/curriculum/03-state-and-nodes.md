# 03 — State and nodes

This lesson describes the shared state and how each node updates it.

## State shape

**ImageTaggingState** (in `backend/src/image_tagging/schemas/states.py`) is a TypedDict. Important fields:

- **Inputs:** `image_id`, `image_url`, `image_base64`, `partial_tags` (initially empty).
- **After vision:** `vision_description`, `vision_raw_tags`.
- **After taggers:** `partial_tags` — list of per-category results (tags + confidence_scores).
- **After validator:** `validated_tags` (category → list of validated items), `flagged_tags` (invalid or low-confidence).
- **After aggregator:** `tag_record` (final flat/hierarchical structure), `processing_status`, `needs_review`.

Nodes are async functions that receive the full state and return a **dict of updates** (e.g. `{"vision_description": "...", "vision_raw_tags": {...}}`). LangGraph merges these into the state; they do not replace the whole state.

## Node responsibilities

- **image_preprocessor** (`nodes/preprocessor.py`): Validates and resizes image, ensures base64 is set.
- **vision_analyzer** (`nodes/vision.py`): One GPT-4o vision call; parses JSON into description and raw tags; writes `vision_description`, `vision_raw_tags`; on failure can set `processing_status: "failed"`.
- **tag_* nodes** (`nodes/taggers.py`): Each runs one LLM call for one category (season, theme, objects, etc.), appends one entry to `partial_tags` with `category`, `tags`, `confidence_scores`.
- **tag_validator** (`nodes/validator.py`): Runs when all eight categories are in `partial_tags`; validates against taxonomy; fills `validated_tags` and `flagged_tags`.
- **confidence_filter** (`nodes/confidence.py`): Applies per-category thresholds; moves low-confidence to `flagged_tags`; sets `needs_review` if needed.
- **tag_aggregator** (`nodes/aggregator.py`): Builds `tag_record` from `validated_tags` (flat lists and hierarchical objects), sets `processing_status` and `needs_review`.

Understanding state and who writes what makes the graph easy to follow.

Next: [04-vision-and-taggers.md](04-vision-and-taggers.md)
