"""
FastAPI application: CORS, routes, static uploads.
Phase 2: analyze-image uses LangGraph pipeline; GET /api/taxonomy added.
Phase 5: search-images, available-filters, bulk-upload, bulk-status.
"""
import asyncio
import base64
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Phase 5: batch state for bulk upload (in-memory; key = batch_id)
BATCH_STORAGE: dict[str, dict] = {}
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Uploads directory: backend/uploads (parent of src)
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BACKEND_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="Image Analysis Agent API")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return structured JSON for unhandled errors (Phase 6)."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/taxonomy")
def get_taxonomy():
    """Return full tag taxonomy (categories and allowed values)."""
    from src.image_tagging.taxonomy import TAXONOMY
    return TAXONOMY


@app.post("/api/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(..., alias="file")):
    # Validate file type
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: JPG, PNG, WEBP.",
        )
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: JPG, PNG, WEBP.",
        )

    # Save file
    image_id = str(uuid.uuid4())
    filename = f"{image_id}{suffix}"
    filepath = UPLOADS_DIR / filename
    contents = await file.read()
    filepath.write_bytes(contents)

    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/uploads/{filename}"

    # Base64 for graph (preprocessor expects raw then resizes)
    image_base64 = base64.b64encode(contents).decode("utf-8")

    try:
        from src.image_tagging.image_tagging import graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph load error: {e}")

    initial_state = {
        "image_id": image_id,
        "image_url": image_url,
        "image_base64": image_base64,
        "partial_tags": [],
    }

    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    # Persist to DB when Supabase is enabled
    saved_to_db = False
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
        if SUPABASE_ENABLED:
            client = get_client()
            if client:
                tag_record = result.get("tag_record")
                if isinstance(tag_record, dict):
                    client.upsert_tag_record(
                        image_id=result.get("image_id", image_id),
                        tag_record=tag_record,
                        image_url=image_url,
                        needs_review=bool(result.get("flagged_tags")),
                        processing_status=result.get("processing_status", "complete"),
                    )
                    saved_to_db = True
    except Exception as e:
        # Log but do not fail the request
        import logging
        logging.getLogger(__name__).warning("Failed to save tag record to DB: %s", e)

    # tags_by_category: dict category -> list of {value, confidence} (from validated or partial)
    validated = result.get("validated_tags") or {}
    partial = result.get("partial_tags") or []
    tags_by_category = {}
    for cat, tag_list in validated.items():
        tags_by_category[cat] = [
            {"value": t.get("value"), "confidence": t.get("confidence", 0)}
            for t in tag_list if isinstance(t, dict)
        ]
    if not tags_by_category and partial:
        for item in partial:
            if isinstance(item, dict) and item.get("category"):
                cat = item["category"]
                scores = item.get("confidence_scores") or {}
                tags_by_category[cat] = [
                    {"value": v, "confidence": scores.get(v, 0)} for v in (item.get("tags") or [])
                ]

    return {
        "image_url": result.get("image_url", image_url),
        "image_id": result.get("image_id", image_id),
        "vision_description": result.get("vision_description", ""),
        "vision_raw_tags": result.get("vision_raw_tags", {}),
        "partial_tags": result.get("partial_tags", []),
        "tags_by_category": tags_by_category,
        "tag_record": result.get("tag_record"),
        "flagged_tags": result.get("flagged_tags", []),
        "processing_status": result.get("processing_status", "complete"),
        "saved_to_db": saved_to_db,
    }


@app.get("/api/tag-image/{image_id}")
def get_tag_image(image_id: str):
    """Return stored tag record for an image. 503 if DB disabled, 404 if not found."""
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    row = client.get_tag_record(image_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return row


@app.get("/api/tag-images")
def list_tag_images(limit: int = 20, offset: int = 0):
    """List recently tagged images. 503 if DB disabled."""
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    rows = client.list_tag_images(limit=limit, offset=offset)
    return {"items": rows, "limit": limit, "offset": offset}


def _parse_filter_params(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
) -> dict[str, list[str]]:
    """Parse comma-separated query params into filters dict."""
    filters = {}
    for key, param in [
        ("season", season),
        ("theme", theme),
        ("objects", objects),
        ("dominant_colors", dominant_colors),
        ("design_elements", design_elements),
        ("occasion", occasion),
        ("mood", mood),
        ("product_type", product_type),
    ]:
        if param:
            values = [v.strip() for v in param.split(",") if v.strip()]
            if values:
                filters[key] = values
    return filters


@app.get("/api/search-images")
def search_images(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
    limit: int = 50,
):
    """Search images by tag filters (AND across categories). 503 if DB disabled."""
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    filters = _parse_filter_params(
        season=season, theme=theme, objects=objects, dominant_colors=dominant_colors,
        design_elements=design_elements, occasion=occasion, mood=mood, product_type=product_type,
    )
    rows = client.search_images_filtered(filters, limit=limit)
    return {"items": rows, "limit": limit}


@app.get("/api/available-filters")
def available_filters(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
):
    """Return available filter values for current selection (cascading). 503 if DB disabled."""
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    filters = _parse_filter_params(
        season=season, theme=theme, objects=objects, dominant_colors=dominant_colors,
        design_elements=design_elements, occasion=occasion, mood=mood, product_type=product_type,
    )
    return client.get_available_filter_values(filters)


async def _process_one_file(
    request: Request,
    filename_orig: str,
    contents: bytes,
    batch_id: str,
    index: int,
) -> None:
    """Process a single file: save, run graph, save to DB. Updates BATCH_STORAGE[batch_id]."""
    image_id = ""
    try:
        suffix = Path(filename_orig or "").suffix.lower()
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            BATCH_STORAGE[batch_id]["results"][index] = {"image_id": "", "status": "failed", "error": "Invalid file type"}
            BATCH_STORAGE[batch_id]["completed"] += 1
            return
        image_id = str(uuid.uuid4())
        filename = f"{image_id}{suffix}"
        filepath = UPLOADS_DIR / filename
        filepath.write_bytes(contents)
        base_url = str(request.base_url).rstrip("/")
        image_url = f"{base_url}/uploads/{filename}"
        image_base64 = base64.b64encode(contents).decode("utf-8")
        from src.image_tagging.image_tagging import graph
        initial_state = {
            "image_id": image_id,
            "image_url": image_url,
            "image_base64": image_base64,
            "partial_tags": [],
        }
        result = await graph.ainvoke(initial_state)
        tag_record = result.get("tag_record")
        try:
            from src.services.supabase import SUPABASE_ENABLED, get_client
            if SUPABASE_ENABLED and isinstance(tag_record, dict):
                client = get_client()
                if client:
                    client.upsert_tag_record(
                        image_id=image_id,
                        tag_record=tag_record,
                        image_url=image_url,
                        needs_review=bool(result.get("flagged_tags")),
                        processing_status=result.get("processing_status", "complete"),
                    )
        except Exception as e:
            logger.warning("Bulk save to DB failed for %s: %s", image_id, e)
        BATCH_STORAGE[batch_id]["results"][index] = {
            "image_id": image_id,
            "status": "complete",
            "image_url": image_url,
        }
    except Exception as e:
        logger.exception("Bulk process failed for file %s: %s", index, e)
        BATCH_STORAGE[batch_id]["results"][index] = {
            "image_id": image_id or "",
            "status": "failed",
            "error": str(e),
        }
    BATCH_STORAGE[batch_id]["completed"] += 1
    if BATCH_STORAGE[batch_id]["completed"] >= BATCH_STORAGE[batch_id]["total"]:
        BATCH_STORAGE[batch_id]["status"] = "complete"


def _run_bulk_batch(request: Request, batch_id: str, file_list: list[tuple[str, bytes]]):
    """Background: process each file and update BATCH_STORAGE."""
    async def run():
        for i, (filename_orig, contents) in enumerate(file_list):
            await _process_one_file(request, filename_orig, contents, batch_id, i)

    asyncio.create_task(run())


@app.post("/api/bulk-upload")
async def bulk_upload(request: Request, files: list[UploadFile] = File(..., alias="files")):
    """Accept multiple images; return batch_id and start background processing."""
    if not files:
        raise HTTPException(status_code=400, detail="At least one file required")
    file_list: list[tuple[str, bytes]] = []
    for f in files:
        contents = await f.read()
        file_list.append((f.filename or "image.jpg", contents))
    batch_id = str(uuid.uuid4())
    total = len(file_list)
    BATCH_STORAGE[batch_id] = {
        "total": total,
        "completed": 0,
        "results": [{"image_id": "", "status": "pending"} for _ in range(total)],
        "status": "processing",
    }
    _run_bulk_batch(request, batch_id, file_list)
    return {"batch_id": batch_id, "total": total, "status": "processing"}


@app.get("/api/bulk-status/{batch_id}")
def bulk_status(batch_id: str):
    """Return batch state: total, completed, results, status."""
    if batch_id not in BATCH_STORAGE:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BATCH_STORAGE[batch_id]
