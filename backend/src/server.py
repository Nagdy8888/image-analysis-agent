"""
FastAPI application: CORS, routes, static uploads.
"""
import base64
import json
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Uploads directory: backend/uploads (parent of src)
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BACKEND_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

VISION_SYSTEM_PROMPT = """You are a visual product analyst for a gift product company.
Analyze this product image and return a JSON object with the following structure.
Return ONLY valid JSON, no markdown, no explanation.

{
  "visual_description": "<2-3 sentence description>",
  "dominant_mood": "<overall feel>",
  "visible_subjects": ["<list of things you see>"],
  "color_observations": "<describe the color palette in detail>",
  "design_observations": "<describe patterns, textures, layout>",
  "seasonal_indicators": "<any holiday/seasonal cues>",
  "style_indicators": "<art style, aesthetic>",
  "text_present": "<any text or lettering visible>"
}"""

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

    # Base64 for vision API
    base64_string = base64.b64encode(contents).decode("utf-8")
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png" if suffix == ".png" else "image/webp"
    data_uri = f"data:{mime};base64,{base64_string}"

    # Call OpenAI vision
    try:
        from src.image_tagging.settings import OPENAI_API_KEY, OPENAI_MODEL
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {e}")

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    messages = [
        SystemMessage(content=VISION_SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this image and return the JSON object."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        ),
    ]

    try:
        response = await llm.ainvoke(messages)
        text = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {e}")

    # Parse JSON from response (may be wrapped in markdown code block)
    vision_description = ""
    vision_raw_tags = {}
    text_stripped = text.strip()
    if text_stripped.startswith("```"):
        lines = text_stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text_stripped = "\n".join(lines)
    try:
        vision_raw_tags = json.loads(text_stripped)
        vision_description = vision_raw_tags.get("visual_description", "")
    except json.JSONDecodeError:
        vision_description = text_stripped
        vision_raw_tags = {}

    return {
        "image_url": image_url,
        "image_id": image_id,
        "vision_description": vision_description,
        "vision_raw_tags": vision_raw_tags,
    }
