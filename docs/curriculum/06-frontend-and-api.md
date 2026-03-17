# 06 — Frontend and API

This lesson ties the UI to the backend: which pages call which endpoints and how data flows.

## Pages and endpoints

- **Home (`/`):** Single upload sends a file to **POST /api/analyze-image**. The response (image_url, tags_by_category, tag_record, flagged_tags, processing_status, saved_to_db) is shown in DashboardResult. HistoryGrid calls **GET /api/tag-images** to show recently tagged images. BulkUploader sends multiple files to **POST /api/bulk-upload**, then polls **GET /api/bulk-status/{batch_id}** until the batch is complete.
- **Search (`/search`):** On load and whenever filters change, the page calls **GET /api/search-images** (with query params from the selected filters) and **GET /api/available-filters** (same params). Results go to SearchResults; available values drive which filter chips are enabled (cascading). Clicking a result opens DetailModal with that row’s tag_record. Taxonomy for the filter sidebar comes from **GET /api/taxonomy**.

## Key components and data

- **DashboardResult** — Renders tags_by_category (TagCategories), flagged_tags (FlaggedTags), tag_record (JsonViewer), and a “Saved” badge when saved_to_db is true.
- **FilterSidebar** — Holds selected filters (e.g. { season: ["christmas"], theme: ["modern"] }). When the user toggles a chip, the parent page updates state; a useEffect then refetches search-images and available-filters so the grid and chip availability stay in sync.
- **BulkUploader** — Builds FormData with multiple “files”, POSTs to bulk-upload, then polls bulk-status every 2 seconds and shows completed/total and per-file status until status is "complete".

## Constants and types

- **API base URL:** `frontend/src/lib/constants.ts` — `NEXT_PUBLIC_API_URL` (e.g. http://localhost:8000). The browser uses this for all API calls.
- **Types:** `frontend/src/lib/types.ts` — AnalyzeImageResponse, TagRecord, TagImageRow, TagImagesListResponse, etc., so the frontend and API contracts stay aligned.

This concludes the curriculum. For more detail, see the [architecture docs](../architecture/README.md) and the [phase setup guides](../plans/README.md).
