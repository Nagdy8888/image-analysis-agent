"""
FastAPI application: CORS, routes, static uploads.
Phase 2: analyze-image uses LangGraph pipeline; GET /api/taxonomy added.
"""
import base64
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Uploads directory: backend/uploads (parent of src)
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BACKEND_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="Image Analysis Agent API")

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

    return {
        "image_url": result.get("image_url", image_url),
        "image_id": result.get("image_id", image_id),
        "vision_description": result.get("vision_description", ""),
        "vision_raw_tags": result.get("vision_raw_tags", {}),
        "partial_tags": result.get("partial_tags", []),
    }
