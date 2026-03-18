---
name: Undergraduate Curriculum
overview: Replace the existing 6 brief lessons in `docs/curriculum/` with a comprehensive 14-lesson undergraduate curriculum that covers all project concepts and code in depth, with theory, code walkthroughs, exercises, and guidance for building similar projects in the future.
todos:
  - id: curr-01
    content: 01-what-is-an-ai-agent.md
    status: completed
  - id: curr-02
    content: 02-project-overview-and-architecture.md
    status: completed
  - id: curr-03
    content: 03-python-fastapi-foundations.md
    status: completed
  - id: curr-04
    content: 04-langgraph-core-concepts.md
    status: completed
  - id: curr-05
    content: 05-state-and-data-models.md
    status: completed
  - id: curr-06
    content: 06-graph-builder-walkthrough.md
    status: completed
  - id: curr-07
    content: 07-preprocessor-and-vision.md
    status: completed
  - id: curr-08
    content: 08-taggers-taxonomy-and-prompts.md
    status: completed
  - id: curr-09
    content: 09-validation-confidence-aggregation.md
    status: completed
  - id: curr-10
    content: 10-api-design-and-endpoints.md
    status: completed
  - id: curr-11
    content: 11-database-persistence-and-search.md
    status: completed
  - id: curr-12
    content: 12-frontend-nextjs-and-components.md
    status: completed
  - id: curr-13
    content: 13-docker-and-deployment.md
    status: completed
  - id: curr-14
    content: 14-end-to-end-and-future-projects.md
    status: completed
  - id: curr-readme
    content: Update docs/curriculum/README.md with new 14-lesson index
    status: completed
isProject: false
---

# Comprehensive Undergraduate Curriculum

Replace the 6 existing lessons in [docs/curriculum/](docs/curriculum/) with **14 detailed lessons** and an updated [docs/curriculum/README.md](docs/curriculum/README.md). Each lesson follows a consistent structure: **What you will learn** (objectives), **Concepts** (theory at undergrad level), **In this project** (code walkthrough with file paths), **Key takeaways**, **Exercises** (practice questions to reinforce understanding), and **Next** (link to next lesson). The curriculum is designed so you can study it front to back and come away understanding not just this project but the patterns for building similar AI agent systems.

## Lesson plan (14 lessons)

### Part 1 -- Foundations (lessons 01-03)

- **01-what-is-an-ai-agent.md** -- What AI agents are (vs plain chatbots), the concept of state + tools + LLM reasoning loops, why agents matter in MIS (Management Information Systems), types of agent architectures (ReAct, plan-and-execute, DAG/pipeline). No code yet -- pure theory with diagrams.
- **02-project-overview-and-architecture.md** -- What this project does end to end. The four layers (browser, Next.js, FastAPI, LangGraph+GPT-4o, Supabase). The request lifecycle for single analyze, bulk, and search. Full architecture Mermaid diagram. Key terms glossary (state, node, taxonomy, tag record, confidence, etc.).
- **03-python-fastapi-foundations.md** -- Python async/await, virtual environments, pip, dotenv. FastAPI basics: routes, request/response, UploadFile, middleware (CORS), static files, exception handlers. How the server ([backend/src/server.py](backend/src/server.py)) is structured. Background tasks with asyncio.create_task. This lesson ensures you can read and modify the backend even if FastAPI is new to you.

### Part 2 -- The LangGraph Agent (lessons 04-09)

- **04-langgraph-core-concepts.md** -- What LangGraph is and why (vs plain function chains). Core concepts: StateGraph, state (TypedDict), nodes (functions), edges (linear, conditional), reducers (Annotated with operator.add), Send API for fan-out, compile, ainvoke. All explained with small standalone examples before looking at project code.
- **05-state-and-data-models.md** -- `ImageTaggingState` field by field ([schemas/states.py](backend/src/image_tagging/schemas/states.py)). The `partial_tags` reducer explained with a diagram. Pydantic models: TagResult, ValidatedTag, FlaggedTag, HierarchicalTag, TagRecord, TaggerOutput ([schemas/models.py](backend/src/image_tagging/schemas/models.py)). How data transforms from taggers to validator to aggregator. Lifecycle table (which node writes which field).
- **06-graph-builder-walkthrough.md** -- Line-by-line walkthrough of [graph_builder.py](backend/src/image_tagging/graph_builder.py): creating the StateGraph, add_node for each of the 12 nodes, add_edge for linear segments, add_conditional_edges with fan_out_to_taggers (Send), edges from each tagger to validator. How compile() produces the runnable. How the server imports and calls it. Full agent Mermaid diagram with annotations.
- **07-preprocessor-and-vision.md** -- The preprocessor node: PIL, resize, base64 ([nodes/preprocessor.py](backend/src/image_tagging/nodes/preprocessor.py)). The vision analyzer node: building multimodal messages (SystemMessage + HumanMessage with image_url), calling ChatOpenAI.ainvoke, retry with exponential backoff, parsing JSON from LLM output, handling code fences ([nodes/vision.py](backend/src/image_tagging/nodes/vision.py)). The system prompt ([prompts/system.py](backend/src/image_tagging/prompts/system.py)) -- what it asks for and why.
- **08-taggers-taxonomy-and-prompts.md** -- Taxonomy design: flat vs hierarchical categories, get_flat_values, get_parent_for_child ([taxonomy.py](backend/src/image_tagging/taxonomy.py)). The generic run_tagger function: building the prompt, calling the LLM, parsing, filtering to allowed values, confidence threshold (> 0.5), capping with max_tags ([nodes/taggers.py](backend/src/image_tagging/nodes/taggers.py)). Prompt engineering: the tagger prompt template, confidence scale, JSON output format ([prompts/tagger.py](backend/src/image_tagging/prompts/tagger.py)). All 8 tagger functions and their specific instructions/max_tags.
- **09-validation-confidence-aggregation.md** -- Tag validator: REQUIRED_CATEGORIES gate, flat vs hierarchical validation, _validate_value, FlaggedTag reasons ([nodes/validator.py](backend/src/image_tagging/nodes/validator.py)). Confidence filter: CONFIDENCE_THRESHOLD, CATEGORY_CONFIDENCE_OVERRIDES, NEEDS_REVIEW_THRESHOLD, how overrides change behavior per category ([nodes/confidence.py](backend/src/image_tagging/nodes/confidence.py), [configuration.py](backend/src/image_tagging/configuration.py)). Aggregator: building TagRecord from validated_tags, flat vs hierarchical helpers, product_type_single, processing_status logic ([nodes/aggregator.py](backend/src/image_tagging/nodes/aggregator.py)). Complete end-to-end example from partial_tags to final tag_record.

### Part 3 -- Backend and Database (lessons 10-11)

- **10-api-design-and-endpoints.md** -- REST API design principles (routes, status codes, error handling). Every endpoint in [server.py](backend/src/server.py): health, taxonomy, analyze-image (full lifecycle), tag-image, tag-images, search-images, available-filters, bulk-upload, bulk-status. The global exception handler. _parse_filter_params. BATCH_STORAGE for in-memory batch state. How the server ties together graph invocation and DB persistence.
- **11-database-persistence-and-search.md** -- Why a database is needed (persistence, search, history). PostgreSQL basics: tables, columns, indexes. The migration SQL ([migration.sql](backend/src/services/supabase/migration.sql)): image_tags table, JSONB, TEXT[], GIN indexes. The Supabase client ([client.py](backend/src/services/supabase/client.py)): connection retry, build_search_index (flattening tag_record), upsert (INSERT ON CONFLICT), search_images_filtered (the @> containment operator), get_available_filter_values (cascading). Settings and SUPABASE_ENABLED.

### Part 4 -- Frontend and Deployment (lessons 12-13)

- **12-frontend-nextjs-and-components.md** -- Next.js App Router basics (pages, layout, error boundary). The two pages (/ and /search). Key components and their roles: ImageUploader, BulkUploader, DashboardResult, TagCategories, FilterSidebar, SearchResults, DetailModal, HistoryGrid. Data flow diagrams for single analyze, search, and bulk. TypeScript types (lib/types.ts). Styling with Tailwind and shadcn/ui. How the frontend calls the backend (fetch, FormData, polling).
- **13-docker-and-deployment.md** -- What Docker is and why (reproducibility, isolation). The backend Dockerfile (python:3.11-slim, pip install, uvicorn). The frontend Dockerfile (multi-stage: node builder + production runner, standalone output). docker-compose.yml (services, ports, env_file, volumes, depends_on). Build args (NEXT_PUBLIC_API_URL). Commands: docker compose up --build, down, logs. .dockerignore. Production considerations.

### Part 5 -- Synthesis (lesson 14)

- **14-end-to-end-and-future-projects.md** -- Full end-to-end trace: user uploads image on frontend -> POST to FastAPI -> graph runs all nodes -> DB upsert -> response to frontend -> UI renders result. What you learned (checklist). How to apply these patterns to new projects: different domains (medical images, document analysis, e-commerce), different LLMs, different databases, adding new tag categories, adding human-in-the-loop review. Recommended next steps and resources (LangGraph docs, FastAPI docs, Next.js docs, prompt engineering guides).

## Changes

- **Delete** existing 6 lesson files (01 through 06) in [docs/curriculum/](docs/curriculum/).
- **Create** 14 new lesson files (01 through 14) in [docs/curriculum/](docs/curriculum/).
- **Rewrite** [docs/curriculum/README.md](docs/curriculum/README.md) with the new 14-lesson table and a brief intro explaining the curriculum structure and how to use it.

## Principles

- Each lesson is **self-contained** with clear objectives, theory, code references, and exercises.
- **Concept first, code second** -- explain the "why" before showing the "how."
- **Undergrad level** -- no assumed familiarity with LangGraph, agents, or advanced Python; assumes basic programming knowledge.
- **Transferable** -- lessons emphasize patterns (agent pipelines, prompt engineering, API design, containerization) that apply to any similar project, not just this one.
- **Exercises** at the end of each lesson to test understanding and encourage hands-on exploration.
- **Visual-first** -- every lesson includes Mermaid diagrams wherever they help understanding. Planned visuals per lesson:

## Visual aids per lesson

- **01** -- Flowchart: chatbot vs agent (input-output vs state loop). Diagram: agent architecture types (ReAct loop, DAG pipeline).
- **02** -- Full system architecture (browser to Supabase). Request lifecycle sequence diagrams for single analyze, bulk, and search.
- **03** -- Flowchart: FastAPI request lifecycle (middleware, route, response). Diagram: server.py structure (routes, static files, exception handler).
- **04** -- LangGraph concepts: StateGraph with nodes and edges. Diagram: linear graph vs fan-out graph. Diagram: reducer (operator.add) merging partial_tags.
- **05** -- Data transformation flowchart: TagResult -> ValidatedTag -> TagRecord. State lifecycle table as a field x node matrix diagram.
- **06** -- Full annotated agent graph (preprocessor -> vision -> 8 taggers -> validator -> confidence -> aggregator). Diagram: how Send creates parallel branches.
- **07** -- Flowchart: preprocessor steps (decode -> open -> resize -> encode). Sequence diagram: vision node (build message -> call LLM -> retry -> parse).
- **08** -- Flowchart: run_tagger steps (get allowed -> build prompt -> call LLM -> filter -> cap). Diagram: taxonomy structure (flat vs hierarchical tree).
- **09** -- Flowchart: validator decision tree (hierarchical? -> get_parent -> valid/flagged). Diagram: confidence filter with threshold comparison. Flowchart: aggregator building TagRecord.
- **10** -- Sequence diagram: POST /api/analyze-image full lifecycle. Diagram: bulk upload flow (BATCH_STORAGE, background task, polling).
- **11** -- Diagram: image_tags table schema. Flowchart: build_search_index flattening. Diagram: search_index @> containment query.
- **12** -- Component tree diagram (layout -> pages -> components). Data flow diagrams for analyze, search, bulk.
- **13** -- Diagram: Docker multi-stage build. Diagram: docker-compose services and ports.
- **14** -- Full end-to-end trace diagram (user click to UI render). Diagram: how to adapt the pattern for new domains.

