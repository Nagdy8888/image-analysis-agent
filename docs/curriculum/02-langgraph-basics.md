# 02 — LangGraph basics

Here we focus on how LangGraph is used in this project: a state graph with one entry, several nodes, and conditional fan-out.

## What LangGraph is for

**LangGraph** is a library for building stateful, multi-step workflows (graphs) where each step can call LLMs or other logic. Our pipeline is a **state graph**: a single state object is passed through a sequence of nodes; each node returns a dict of updates that are merged into the state. The graph is compiled and invoked with an initial state; the result is the final state after all nodes run.

## Where it lives

- **Graph definition:** `backend/src/image_tagging/graph_builder.py` — builds the graph, adds nodes, adds edges (including conditional fan-out to the eight taggers).
- **Compiled graph export:** `backend/src/image_tagging/image_tagging.py` — imports the builder and exposes the compiled graph (e.g. `graph`) for the server to call `graph.ainvoke(initial_state)`.
- **State type:** `backend/src/image_tagging/schemas/states.py` — `ImageTaggingState` TypedDict: fields like `image_id`, `image_base64`, `vision_description`, `partial_tags`, `validated_tags`, `tag_record`, etc.

## Flow in one sentence

The server builds `initial_state` (image_id, image_url, image_base64, empty partial_tags), invokes the graph, and the graph runs: preprocessor → vision_analyzer → (conditional edge that sends to all eight taggers) → tag_validator → confidence_filter → tag_aggregator → END. The returned state contains `tag_record`, `flagged_tags`, and `processing_status`.

Next: [03-state-and-nodes.md](03-state-and-nodes.md)
