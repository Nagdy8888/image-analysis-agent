---
name: Comprehensive documentation folder
overview: Create a `documentation/` folder at the project root with 20 numbered markdown files that serve as a single, exhaustive reference for every detail of the project -- with deep agent coverage including full code walkthroughs, data flow traces, and complete function signatures.
todos:
  - id: doc-01
    content: 01-project-overview.md
    status: completed
  - id: doc-02
    content: 02-architecture.md
    status: completed
  - id: doc-03
    content: 03-langgraph-pipeline.md
    status: completed
  - id: doc-04
    content: 04-agent-state.md
    status: completed
  - id: doc-05
    content: 05-agent-data-models.md
    status: completed
  - id: doc-06
    content: 06-taxonomy-complete-reference.md
    status: completed
  - id: doc-07
    content: 07-configuration-and-settings.md
    status: completed
  - id: doc-08
    content: 08-node-preprocessor.md
    status: completed
  - id: doc-09
    content: 09-node-vision-analyzer.md
    status: completed
  - id: doc-10
    content: 10-node-taggers-overview.md
    status: completed
  - id: doc-11
    content: 11-node-taggers-per-category.md
    status: completed
  - id: doc-12
    content: 12-node-validator.md
    status: completed
  - id: doc-13
    content: 13-node-confidence-filter.md
    status: completed
  - id: doc-14
    content: 14-node-aggregator.md
    status: completed
  - id: doc-15
    content: 15-prompts.md
    status: completed
  - id: doc-16
    content: 16-database.md
    status: completed
  - id: doc-17
    content: 17-api-reference.md
    status: completed
  - id: doc-18
    content: 18-frontend.md
    status: completed
  - id: doc-19
    content: 19-docker-and-deployment.md
    status: completed
  - id: doc-20
    content: 20-development-phases.md
    status: completed
isProject: false
---

# Comprehensive Documentation Folder

Create `documentation/` at the project root with 20 numbered `.md` files. Deep focus on the agent: every node gets its own doc with full function signatures, input/output shapes, retry logic, error handling, and step-by-step walkthroughs. State, schemas, and taxonomy are each standalone files with complete field listings.

## Proposed files

### Project and architecture

- `**01-project-overview.md**` — What the project does, features table, tech stack, full repo tree with subfolders, table of contents for all 20 docs.
- `**02-architecture.md**` — High-level Mermaid (browser -> Next.js -> FastAPI -> LangGraph -> Supabase). Three request lifecycle diagrams: single analyze, bulk upload, search. Sequence diagram showing data flow from file upload through server to graph to DB and back. Component interaction map.
- `**03-langgraph-pipeline.md**` — Full agent graph Mermaid diagram. Line-by-line walkthrough of `graph_builder.py` (`build_graph()`): StateGraph creation, `add_node` for each node, `add_edge` from START, conditional fan-out with `Send` API, edge from each tagger to validator, linear tail to END. `fan_out_to_taggers()` function. `image_tagging.py` compiled graph export. How `graph.ainvoke(initial_state)` is called from `server.py`. State merge semantics (reducer via `operator.add` on `partial_tags`).

### Agent state and data models (deep)

- `**04-agent-state.md**` — `ImageTaggingState` (TypedDict, `total=False`): every field with type, default, who writes it, who reads it, and when. The `Annotated[list, operator.add]` reducer on `partial_tags` explained in detail (why it exists, how LangGraph merges). State lifecycle table: field x node matrix showing which node writes each field. Example initial state dict and example final state dict (realistic JSON).
- `**05-agent-data-models.md**` — Full Pydantic model reference. For each model (`TagResult`, `ValidatedTag`, `FlaggedTag`, `HierarchicalTag`, `TagRecord`, `TaggerOutput`): class definition, every field with type and purpose, which node creates it, which node consumes it, example JSON. `TagRecord` shown as a complete realistic example with all 8 categories populated. Relationship diagram: how `TagResult` (from taggers) becomes `ValidatedTag` (from validator) becomes part of `TagRecord` (from aggregator).

### Taxonomy (deep)

- `**06-taxonomy-complete-reference.md**` — Complete listing of every value in every category. **Flat categories:** season (19 values listed), theme (18), design_elements (33), occasion (8), mood (9) -- each value printed. **Hierarchical categories:** objects (7 parents, each with all children listed), dominant_colors (9 families with all shades), product_type (5 parents with all children). `get_flat_values(category)` behavior and return for every category. `get_parent_for_child(category, child)` behavior and examples. The `TAXONOMY` dict shape.

### Configuration

- `**07-configuration-and-settings.md`** — `settings.py`: how `dotenv` loads from project root, each env var (OPENAI_API_KEY, OPENAI_MODEL default "gpt-4o", DATABASE_URI, LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2), error if key is missing. `configuration.py`: every constant with value and purpose: `CONFIDENCE_THRESHOLD = 0.65`, `NEEDS_REVIEW_THRESHOLD = 3`, `MAX_COLORS = 5`, `MAX_OBJECTS = 10`, `VISION_MODEL`, `TAGGER_MODEL`, `CATEGORY_CONFIDENCE_OVERRIDES = {"product_type": 0.80, "season": 0.60}`. How overrides interact with the confidence filter. How to tune thresholds.

### Agent nodes (one doc per node)

- `**08-node-preprocessor.md`** — File: `nodes/preprocessor.py`. `image_preprocessor(state) -> dict`. Step by step: (1) read `image_base64` from state, (2) base64 decode, (3) open with PIL, convert to RGB, (4) check long edge vs `MAX_LONG_EDGE=1024`, resize with LANCZOS if needed, (5) re-encode as JPEG quality 88, (6) return `image_base64` (new) and `metadata` dict (`width`, `height`, `format`). Constants: `ALLOWED_EXTENSIONS`, `MAX_LONG_EDGE`. Error returns: `processing_status: "failed"` with `error` message for missing base64, invalid base64, unsupported format. Sync function (not async).
- `**09-node-vision-analyzer.md**` — File: `nodes/vision.py`. `vision_analyzer(state) -> dict`. Step by step: (1) read `image_base64`, build `data:image/jpeg;base64,...` URI, (2) construct messages: `SystemMessage(VISION_ANALYZER_PROMPT)` + `HumanMessage` with text part and `image_url` part, (3) call `ChatOpenAI(model, api_key).ainvoke(messages)` with retry loop (3 attempts, backoff 1s then 2s), (4) parse response with `_parse_vision_response(text)`: strip markdown code fence if present, JSON parse, extract `visual_description` from parsed JSON. Returns `vision_description` (str) and `vision_raw_tags` (full parsed dict). On failure: returns empty values with `processing_status: "failed"` and `error`. Full `_parse_vision_response` logic. Expected vision JSON shape: `visual_description`, `dominant_mood`, `visible_subjects`, `color_observations`, `design_observations`, `seasonal_indicators`, `style_indicators`, `text_present`.
- `**10-node-taggers-overview.md**` — File: `nodes/taggers.py`. The generic `run_tagger(state, category, instructions, max_tags)` function: step by step: (1) read `vision_description` from state, (2) get allowed values via `get_flat_values(category)`, (3) build prompt via `build_tagger_prompt(description, category, allowed, instructions)`, (4) call `ChatOpenAI.ainvoke` with retry (3 attempts, 1s/2s backoff), (5) parse with `_parse_tagger_response(text)` into `TaggerOutput(tags, confidence_scores, reasoning)`: strip code fence, JSON parse, (6) filter: keep only tags in allowed list AND confidence > 0.5, (7) optional cap via `max_tags`: sort by confidence desc, take top N, (8) wrap in `TagResult(category, tags, confidence_scores).model_dump()`, (9) return `{"partial_tags": [result]}`. How `partial_tags` uses the `operator.add` reducer to accumulate results from all 8 taggers. `ALL_TAGGERS` dict and `TAGGER_NODE_NAMES` list. Node name mapping (e.g. `"season_tagger"` -> `tag_season`).
- `**11-node-taggers-per-category.md**` — Each of the 8 tagger functions documented individually: `tag_season` (no instructions, no max_tags), `tag_theme` (instructions: "Select all aesthetic themes that apply."), `tag_objects` (instructions for hierarchical child values, `max_tags=MAX_OBJECTS=10`), `tag_colors` (instructions for shade names, `max_tags=MAX_COLORS=5`), `tag_design` (instructions for patterns/textures/layout/typography), `tag_occasion` (instructions for occasions/use cases), `tag_mood` (instructions for moods/tones), `tag_product` (instructions for single product type, `max_tags=1`). For each: function signature, custom instructions text, max_tags value, expected output example, and which taxonomy values it draws from.
- `**12-node-validator.md**` — File: `nodes/validator.py`. `validate_tags(state) -> dict`. Constants: `REQUIRED_CATEGORIES` (set of 8), `HIERARCHICAL_CATEGORIES` (objects, dominant_colors, product_type). Gate logic: only runs when `categories_seen == REQUIRED_CATEGORIES` (all 8 present in `partial_tags`). Per-tag validation: `_validate_value(category, value, confidence)` -> `(ValidatedTag | None, FlaggedTag | None)`. For hierarchical: calls `get_parent_for_child`, sets parent on ValidatedTag, or flags with reason `"invalid_taxonomy_value"`. For flat: calls `_is_valid_flat` (checks `value in TAXONOMY[category]`). Output: `validated_tags` (dict: category -> list of ValidatedTag dicts) and `flagged_tags` (list of FlaggedTag dicts). Carries forward existing `flagged_tags` from state. Example walkthrough with realistic data.
- `**13-node-confidence-filter.md**` — File: `nodes/confidence.py`. `filter_by_confidence(state) -> dict`. Reads `CONFIDENCE_THRESHOLD` (0.65), `CATEGORY_CONFIDENCE_OVERRIDES` (product_type: 0.80, season: 0.60), `NEEDS_REVIEW_THRESHOLD` (3). For each category in `validated_tags`: get threshold (override or default), keep tags >= threshold, move tags below to `flagged_tags` with reason `"low_confidence"`. Track flag count per category; if any category has >= NEEDS_REVIEW_THRESHOLD flags, set `needs_review = True`. Also `needs_review = True` if any flagged tags at all. Returns updated `validated_tags`, `flagged_tags`, `needs_review`. Example walkthrough showing a tag at 0.62 being moved to flagged for season (threshold 0.60 -- it passes) vs product_type (threshold 0.80 -- it's flagged).
- `**14-node-aggregator.md**` — File: `nodes/aggregator.py`. `aggregate_tags(state) -> dict`. Reads `validated_tags`, `flagged_tags`, `needs_review`, `image_id`. Builds `TagRecord` using: `_flat_list(validated, category)` for season, theme, design_elements, occasion, mood (extracts `value` strings); `_hierarchical_list(validated, category)` for objects, dominant_colors (extracts `{parent, child}` dicts using `get_parent_for_child`); `_product_type_single(validated)` for product_type (picks the highest-confidence item, returns single `{parent, child}` or None). Sets `processed_at` (UTC ISO), `needs_review`. Processing status: `"failed"` if `state.error`, `"needs_review"` if needs_review, else `"complete"`. Returns `tag_record` (TagRecord.model_dump()) and `processing_status`. Complete example: realistic `validated_tags` input -> resulting `TagRecord` JSON.

### Prompts (deep)

- `**15-prompts.md**` — Full verbatim text of `VISION_ANALYZER_PROMPT` from `prompts/system.py`. Full `build_tagger_prompt()` template from `prompts/tagger.py` with all sections: role, rules (allowed values, JSON structure, confidence scale 0.9+/0.7-0.9/0.5-0.7), output format (`{"tags": [...], "confidence_scores": {...}, "reasoning": "..."}`), description injection, optional instructions append. Example rendered prompt for season category with a real description. Example rendered prompt for objects category (hierarchical). Tips for tuning: how to change confidence scale, how to add new categories, how to adjust instructions.

### Database, API, frontend, Docker, phases

- `**16-database.md**` — `migration.sql` (full SQL), table schema with all columns and types, GIN indexes. `settings.py`: `DATABASE_URI`, `SUPABASE_ENABLED`. `client.py` complete: `build_search_index(tag_record)` algorithm, `SupabaseClient.__init`__, `_conn` with retry (3 attempts, 1s delay), `upsert_tag_record` (INSERT ON CONFLICT, search_index construction), `get_tag_record`, `list_tag_images`, `search_images_filtered` (`@>` operator), `get_available_filter_values` (cascading). `get_client()`. Example SQL queries.
- `**17-api-reference.md**` — Every endpoint: method, path, params, request body, response JSON (with example), status codes, error cases. Single analyze lifecycle (file -> save -> graph -> DB -> response). Bulk: BATCH_STORAGE dict, `_process_one_file`, `_run_bulk_batch`, polling. Search: `_parse_filter_params`. Global exception handler. Detailed JSON examples for each endpoint.
- `**18-frontend.md**` — Pages, layout, theme, Toaster, error boundary. Every component: props, render, API calls. Data flow diagrams for analyze, search, bulk. TypeScript types reference. Grouped: upload, result, search, layout, history, shadcn/ui.
- `**19-docker-and-deployment.md**` — Both Dockerfiles line by line. `docker-compose.yml` services, ports, env, volumes. `.dockerignore`. Build/run commands. Production NEXT_PUBLIC_API_URL.
- `**20-development-phases.md**` — Each phase (0-6): what was built, key files, verification steps. Progress diagram. Changelog.

## Key principles

- Each file is self-contained and readable on its own, with cross-links to related docs.
- Code paths are always explicit (e.g. `backend/src/image_tagging/nodes/vision.py`).
- Function signatures and data shapes are included inline with full parameter types.
- Realistic JSON examples are included wherever data structures are described.
- Every agent node gets its own dedicated doc with step-by-step walkthrough and example I/O.
- Mermaid diagrams in docs 02, 03, 04, and 18.
- The existing `docs/` folder is untouched; `documentation/` is a parallel standalone reference.

