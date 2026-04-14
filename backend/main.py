import os
import logging
import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import google.generativeai as genai

from backend.models import KioskRequest, KioskResponse, LeadCaptureRequest, LeadCaptureResponse, DocumentUploadRequest
from backend.services.gemini_service import generate_visual_context, process_lead_notes, update_knowledge_vault
from backend.services.database import get_db, close_db

# --- Structured Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger("omnibooth")

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and graceful shutdown database connection severing."""
    logger.info("OmniBooth AI Backend starting — initializing services")
    logger.info(f"Gemini API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
    logger.info(f"MongoDB URI configured: {bool(os.getenv('MONGODB_URI'))}")
    logger.info(f"Discord Webhook configured: {bool(os.getenv('WEBHOOK_URL'))}")
    yield
    close_db()
    logger.info("OmniBooth AI Backend shutdown — database connections closed")

app = FastAPI(title="OmniBooth AI Backend", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
@limiter.limit("10/minute")
async def generate_visual(request: KioskRequest, req: Request):
    """
    Handles multimodal Kiosk inputs. Returns a dynamically generated
    structural contextualization string and a designated proxy media URL.
    """
    data = await generate_visual_context(request.prompt, request.image_data)
    if "media_url" not in data or "message" not in data:
        raise HTTPException(status_code=500, detail="Invalid generation response.")
    return KioskResponse(media_url=data["media_url"], message=data["message"])

@app.post("/upload-docs")
@limiter.limit("5/minute")
async def upload_docs(request: DocumentUploadRequest, req: Request):
    """Securely upserts new engineering specifications directly into the MongoDB RAG Knowledge Vault."""
    await update_knowledge_vault(request.text)
    logger.info(f"Knowledge Vault updated — document length: {len(request.text)} chars")
    return {"message": "Knowledge Vault expanded successfully in MongoDB."}

@app.post("/capture-lead", response_model=LeadCaptureResponse)
@limiter.limit("5/minute")
async def capture_lead(request: LeadCaptureRequest, req: Request):
    """
    Drives the Agentic Critic Loop. Extracts raw sales notes, identifies market competitors,
    utilizes DuckDuckGo to compile a verified technical proposal, formats battlecards, and 
    structurally commits the finalized payload to MongoDB for Dashboard consumption.
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
           logger.info(f"Lead captured — sentiment: {data.get('sentiment')}, name: {request.attendee_name}")
        except Exception as e:
           logger.error(f"Database insert failed: {e}")
    
    return LeadCaptureResponse(
        sentiment=data.get("sentiment", "Unknown"),
        drafted_email=data.get("drafted_email", ""),
        action_items=data.get("action_items", []),
        verification_status=data.get("verification_status", "Pending")
    )

@app.get("/leads")
@limiter.limit("20/minute")
async def get_leads(req: Request):
    """Retrieves the chronological descending list of processed leads for the CRM Pipeline."""
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
@limiter.limit("20/minute")
async def get_analytics(req: Request):
    """Generates the real-time Vibe Heatmap by aggregating sentiment limits over a rolling 10-minute cluster."""
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
