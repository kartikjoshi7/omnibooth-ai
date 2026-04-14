import os
import json
import logging
import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse, JSONResponse
import google.generativeai as genai

from backend.models import KioskRequest, KioskResponse, LeadCaptureRequest, LeadCaptureResponse, DocumentUploadRequest
from backend.services.gemini_service import generate_visual_context, process_lead_notes, update_knowledge_vault
from backend.services.database import get_db, close_db
from backend.services.gcp_services import setup_gcp_logging, upload_to_gcs

# --- Structured Logging with Google Cloud Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger("omnibooth")

# Initialize Google Cloud Logging (falls back to JSON console logging locally)
setup_gcp_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and graceful shutdown database connection severing."""
    logger.info("OmniBooth AI Backend starting — initializing Google Cloud services")
    logger.info(f"Gemini API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
    logger.info(f"MongoDB URI configured: {bool(os.getenv('MONGODB_URI'))}")
    logger.info(f"Discord Webhook configured: {bool(os.getenv('WEBHOOK_URL'))}")
    yield
    close_db()
    logger.info("OmniBooth AI Backend shutdown — database connections closed")

app = FastAPI(title="OmniBooth AI — Smart Venue Assistant", version="1.0.0", lifespan=lifespan)

# --- CORS: Explicit Origin Allowlist ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://omnibooth-ai-828381244603.asia-south1.run.app,http://localhost:4200,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.post("/generate-visual", response_model=KioskResponse)
async def generate_visual(request: KioskRequest, req: Request):
    """
    Handles multimodal Venue Kiosk inputs. Returns AI-generated crowd guidance
    and a contextual venue visualization URL for the attendee.
    Persists generated assets to Google Cloud Storage when available.
    """
    data = await generate_visual_context(request.prompt, request.image_data)
    if "media_url" not in data or "message" not in data:
        raise HTTPException(status_code=500, detail="Invalid generation response.")

    # Persist venue visualization metadata to Google Cloud Storage
    try:
        gcs_bucket = os.getenv("GCS_BUCKET_NAME", "omnibooth-venue-assets")
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_name = f"venue-visuals/{timestamp}.json"
        asset_payload = json.dumps({"prompt": request.prompt, "media_url": data["media_url"], "message": data["message"]}).encode("utf-8")
        upload_to_gcs(gcs_bucket, blob_name, asset_payload)
    except Exception as e:
        logger.debug(f"GCS persistence skipped: {e}")

    return KioskResponse(media_url=data["media_url"], message=data["message"])

@app.post("/upload-docs")
async def upload_docs(request: DocumentUploadRequest, req: Request):
    """Securely upserts venue information (maps, schedules, policies) into the MongoDB Venue Info Base."""
    await update_knowledge_vault(request.text)
    logger.info(f"Venue Info Base updated — document length: {len(request.text)} chars")
    return {"message": "Venue Information Base updated successfully."}

@app.post("/capture-lead", response_model=LeadCaptureResponse)
async def capture_lead(request: LeadCaptureRequest, req: Request):
    """
    Drives the Agentic Crowd Intelligence Pipeline. Classifies attendee query urgency,
    searches for live venue/event data, verifies AI guidance against the Venue Info Base,
    and commits the processed query to MongoDB for the Operations Dashboard.
    """
    data = await process_lead_notes(request.notes, request.attendee_name)
    
    lead_doc = {
        "attendee_name": request.attendee_name,
        "attendee_email": request.attendee_email,
        "notes": request.notes,
        "sentiment": data.get("sentiment", "Unknown"),
        "drafted_email": data.get("drafted_email", ""),
        "action_items": data.get("action_items", []),
        "verification_status": data.get("verification_status", "Pending"),
        "timestamp": datetime.datetime.utcnow()
    }
    
    db = get_db()
    if db is not None:
        try:
           await db.leads.insert_one(lead_doc)
           logger.info(f"Query processed — urgency: {data.get('sentiment')}, attendee: {request.attendee_name}")
        except Exception as e:
           logger.error(f"Database insert failed: {e}")
    
    return LeadCaptureResponse(
        sentiment=data.get("sentiment", "Unknown"),
        drafted_email=data.get("drafted_email", ""),
        action_items=data.get("action_items", []),
        verification_status=data.get("verification_status", "Pending")
    )

@app.get("/leads")
async def get_leads(req: Request):
    """Retrieves the chronological descending list of processed attendee queries for the Venue Operations Dashboard."""
    db = get_db()
    if db is None:
         return []
    
    leads = []
    try:
        cursor = db.leads.find({}).sort("timestamp", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            leads.append(doc)
    except Exception as e:
        logger.error(f"Database read failed: {e}")
    return leads

@app.get("/analytics")
async def get_analytics(req: Request):
    """Generates the real-time Crowd Density Heatmap by aggregating query urgency over a rolling 10-minute window."""
    db = get_db()
    if db is None: return []
    try:
        ten_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
        pipeline = [
            {"$match": {"timestamp": {"$gte": ten_mins_ago}}},
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
        ]
        cursor = db.leads.aggregate(pipeline)
        results = [doc async for doc in cursor]
        return results
    except Exception as e:
        logger.error(f"Analytics aggregation failed: {e}")
        return []

@app.get("/models")
async def get_models():
    """Returns the internal array of available Generative UI models mapped by the active API keys."""
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    return {"models": models}

# Mount Angular static files for production
angular_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist", "frontend", "browser"))

@app.get("/{full_path:path}")
async def serve_angular(full_path: str):
    """
    Wildcard route securely mounting the Angular production build while aggressively 404ing invalid API routes.
    """
    if full_path.startswith("api/") or full_path in ["generate-visual", "capture-lead", "upload-docs", "leads", "analytics", "models"]:
        raise HTTPException(status_code=404, detail="API Route Not Found")

    if os.path.exists(angular_dist_path):
        file_path = os.path.join(angular_dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(angular_dist_path, "index.html"))
    return {"message": f"Angular frontend not built or not found at {angular_dist_path}"}
