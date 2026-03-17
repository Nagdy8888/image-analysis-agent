# 05 — Database and search

This lesson explains how results are stored and how filtered search works when the database is enabled.

## When the DB is used

If the project root `.env` has **DATABASE_URI** set, the backend treats the DB as enabled. After a successful analyze, the server calls the Supabase client to **upsert** the tag record (and image_url, needs_review, processing_status). The client builds a **search_index** (flat list of all tag values, including parent/child for hierarchical fields) and stores it in the `image_tags` table. If the DB is unavailable, the client retries the connection a few times; if save still fails, the server logs and continues — the API response still returns the analysis result, with `saved_to_db: false`.

## Supabase client

**Location:** `backend/src/services/supabase/client.py`.

- **upsert_tag_record(image_id, tag_record, image_url, needs_review, processing_status):** Inserts or updates one row; `search_index` is computed by `build_search_index(tag_record)`.
- **get_tag_record(image_id), list_tag_images(limit, offset):** Read one or many rows.
- **search_images_filtered(filters, limit):** Builds a flat list of selected values from the `filters` dict (e.g. season=christmas, theme=modern). Runs a query: `WHERE search_index @> array_of_values` (PostgreSQL “array contains”), ordered by created_at DESC. So results must contain *all* selected values (AND logic).
- **get_available_filter_values(filters):** Runs the same filtered search (with a higher limit), then scans the result rows and collects unique tag values per category. That powers **cascading filters** in the UI: as you select filters, the dropdowns only show values that still exist in the current result set.

## API endpoints

- **GET /api/tag-images** — List recent (uses list_tag_images). Returns 503 if DB is disabled.
- **GET /api/search-images** — Query params per category (comma-separated); returns items from search_images_filtered. 503 if DB disabled.
- **GET /api/available-filters** — Same query params; returns the dict from get_available_filter_values. 503 if DB disabled.

Next: [06-frontend-and-api.md](06-frontend-and-api.md)
