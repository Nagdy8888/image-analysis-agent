# Changelog

All notable phases and features of the Image Analysis Agent project.

## Phase 0 — Project skeleton

- Backend: FastAPI app, health check, folder structure (image_tagging, nodes, prompts, schemas, services/supabase), settings loader, uploads directory.
- Frontend: Next.js with Tailwind, shadcn/ui, Navbar (Tag Image / Search), theme toggle, placeholder pages.
- Docs: Folder tree (curriculum, quickstart, architecture, reports, errors, plans), PROGRESS.md diagram.

## Phase 1 — Simple image analyzer

- Backend: Static /uploads mount, POST /api/analyze-image (file upload, GPT-4o vision, return description + raw tags).
- Frontend: ImageUploader (dropzone), processing overlay, vision results display.

## Phase 2 — LangGraph pipeline

- Backend: Schemas (state, models), taxonomy, vision + tagger prompts, preprocessor + vision + season tagger nodes, linear graph, GET /api/taxonomy.
- Frontend: TagCategoryCard with confidence, pipeline tags on dashboard.

## Phase 3 — Full parallel tagging

- Backend: Configuration (thresholds, overrides), all 8 taggers, validator, confidence filter, aggregator, fan-out graph (Send), tag_record and flagged_tags in response.
- Frontend: TagCategories, TagChip, FlaggedTags, ProcessingOverlay (6 steps), DashboardResult with two-panel layout and tag_record JSON.

## Phase 4 — Supabase integration

- Backend: migration.sql (image_tags table, GIN indexes), Supabase settings + client (upsert, get, list, build_search_index), save after analyze, GET /api/tag-image/{id}, GET /api/tag-images.
- Frontend: Toaster, saved_to_db toast and “Saved” badge, HistoryGrid (“Recently Tagged Images”).

## Phase 5 — Search and bulk upload

- Backend: search_images_filtered, get_available_filter_values, GET /api/search-images, GET /api/available-filters, POST /api/bulk-upload, GET /api/bulk-status/{batch_id}.
- Frontend: Search page (FilterSidebar, SearchResults, DetailModal), BulkUploader (multi-file, progress, per-file status), “Bulk Upload” section on home.

## Phase 6 — Polish and documentation

- Backend: Global exception handler (structured JSON), retry in vision and taggers (2 retries, 1s/2s backoff), Supabase connection retry.
- Frontend: error.tsx (error boundary), Skeleton loading (HistoryGrid, SearchResults), empty states (HistoryGrid with icon), focus-visible for a11y.
- Docs: SETUP.md, DOCKER_SETUP.md, architecture (OVERVIEW, GRAPH_NODES, TAXONOMY, DATABASE, API, FRONTEND, PROMPTS), reports (PROJECT_SUMMARY, FEATURES, DECISIONS), curriculum (01–06), CHANGELOG, README update.
