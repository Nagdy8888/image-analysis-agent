# 01 — Project overview

This lesson explains what the Image Analysis Agent does and how the pieces fit together.

## What the project does

The **Image Analysis Agent** is a full-stack app that takes a product image and returns **structured tags**: season (e.g. christmas), theme (e.g. modern), objects (e.g. santa, reindeer), dominant colors, design elements, occasion, mood, and product type. The pipeline is driven by a **LangGraph** workflow that calls **OpenAI GPT-4o** for vision and for each tag category. Results can be stored in **Supabase** and searched in the UI. Users can also upload a single image or run **bulk upload** and track progress.

## Main parts

- **Frontend** (`frontend/`): Next.js app. Pages: home (upload, result, history, bulk) and search (filters + results grid). The browser talks to the backend API.
- **Backend** (`backend/`): FastAPI server in `backend/src/server.py`. It exposes routes for health, taxonomy, analyze-image, tag-images, search, and bulk upload. The analyze route runs the **agent** and optionally saves to the DB.
- **Agent** (`backend/src/image_tagging/`): LangGraph pipeline: preprocess image → vision call → eight parallel taggers → validate → confidence filter → aggregate. State (image id, vision result, partial tags, final tag record) flows through the graph.
- **Database** (optional): Supabase/PostgreSQL. Table `image_tags` holds one row per analyzed image (tag_record, search_index). Used for persistence and filtered search.

## Terms used in the rest of the curriculum

- **State** — The shared data structure (e.g. `ImageTaggingState`) that every node reads and updates.
- **Node** — One step in the graph (e.g. vision_analyzer, tag_season); each is an async function that takes state and returns updates.
- **Tag record** — The final structured object (season, theme, objects, etc.) produced by the aggregator and optionally stored in the DB.

Next: [02-langgraph-basics.md](02-langgraph-basics.md)
