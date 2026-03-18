# Image Analysis Agent — Backend

FastAPI server and LangGraph image-tagging agent. Exposes REST endpoints for image upload, analysis, persistence, search, and bulk processing; runs the pipeline (vision + 8 taggers → validation → aggregation) and optionally stores results in Supabase.

---

## Tech stack

- **FastAPI** — REST API, CORS, static `/uploads`
- **LangGraph** — State graph (preprocessor → vision → parallel taggers → validator → confidence → aggregator)
- **langchain-openai** — GPT-4o vision and chat for taggers
- **Pillow** — Image validation and resize
- **psycopg2** — Supabase (PostgreSQL) client when `DATABASE_URI` is set
- **python-dotenv** — Load `.env` from project root

---

## Prerequisites

- **Python 3.11+**
- `.env` at the **project root** with `OPENAI_API_KEY` (required). Optional: `DATABASE_URI` for Supabase.

---

## Getting started

From the repository root (so the backend can find the root `.env`):

```bash
cd backend
pip install -r requirements.txt
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

API: [http://localhost:8000](http://localhost:8000). Try `GET /api/health` and `GET /api/taxonomy`.

For **Docker**, run from the repo root: `docker compose up --build` (see [Docker setup](../docs/quickstart/DOCKER_SETUP.md)).

---

## Main endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/taxonomy` | Full tag taxonomy (categories and values) |
| POST | `/api/analyze-image` | Single image: multipart `file` → pipeline → tags + optional DB save |
| GET | `/api/tag-image/{id}` | One stored record (503 if DB disabled) |
| GET | `/api/tag-images` | List recent tag records (query: `limit`, `offset`) |
| GET | `/api/search-images` | Filtered search (query: category params, `limit`) |
| GET | `/api/available-filters` | Cascading filter values (same query params as search) |
| POST | `/api/bulk-upload` | Multiple `files` → batch_id, background processing |
| GET | `/api/bulk-status/{batch_id}` | Batch progress and per-file status |
| GET | `/uploads/{filename}` | Static uploaded images |

Full reference: [API.md](../docs/architecture/API.md).

---

## Project structure

```
backend/
├── src/
│   ├── server.py              # FastAPI app, routes, exception handler
│   ├── image_tagging/         # LangGraph agent
│   │   ├── image_tagging.py   # Compiled graph
│   │   ├── graph_builder.py   # Nodes and edges
│   │   ├── taxonomy.py        # Tag categories and allowed values
│   │   ├── configuration.py  # Confidence thresholds, overrides
│   │   ├── settings.py        # OPENAI_API_KEY, OPENAI_MODEL
│   │   ├── nodes/             # Preprocessor, vision, 8 taggers, validator, confidence, aggregator
│   │   ├── prompts/          # Vision and tagger prompts
│   │   ├── schemas/           # State and data models
│   │   └── tools/             # Agent tools (placeholder)
│   └── services/
│       └── supabase/         # DB client, migration.sql, settings
├── uploads/                   # Stored images (created at runtime)
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

Pipeline diagram: [GRAPH_STRUCTURE.md](../docs/architecture/GRAPH_STRUCTURE.md). Full repo: [root README](../README.md).
