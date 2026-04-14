import os
import json
import time
import logging
import traceback
import httpx
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from backend.services.gcp_services import get_gcp_secret

load_dotenv()

logger = logging.getLogger("omnibooth")

# Retrieve API keys via Google Cloud Secret Manager (falls back to .env locally)
GEMINI_API_KEY = get_gcp_secret("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if GEMINI_API_KEY and GEMINI_API_KEY != "<YOUR_GEMINI_API_KEY_HERE>":
    genai.configure(api_key=GEMINI_API_KEY)
    
MODEL_NAME = "gemini-2.5-flash-lite"

from backend.services.database import get_db

# --- Knowledge Vault Cache (TTL: 60 seconds) ---
_vault_cache = {"text": "", "timestamp": 0}
VAULT_CACHE_TTL = 60


def clean_json_response(text: str) -> dict:
    """Strips markdown code boundaries dynamically from raw LLM outputs before JSON serialization."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        return {} 

async def update_knowledge_vault(doc_text: str):
    """Asynchronously pushes raw text into the RAG knowledge collection and invalidates cache."""
    global _vault_cache
    db = get_db()
    if db is not None:
        await db.knowledge.update_one(
            {"_id": "main_vault"},
            {"$set": {"text": doc_text}},
            upsert=True
        )
        _vault_cache = {"text": doc_text, "timestamp": time.time()}
        logger.info("Knowledge Vault updated and cache refreshed")

async def get_knowledge_vault() -> str:
    """Extracts internal company documentation with in-memory TTL caching to reduce DB load."""
    global _vault_cache
    if time.time() - _vault_cache["timestamp"] < VAULT_CACHE_TTL and _vault_cache["text"]:
        return _vault_cache["text"]
    
    db = get_db()
    if db is not None:
        doc = await db.knowledge.find_one({"_id": "main_vault"})
        if doc:
            _vault_cache = {"text": doc.get("text", ""), "timestamp": time.time()}
            return _vault_cache["text"]
    return ""

async def generate_visual_context(user_prompt: str, image_data: str = None) -> dict:
    """
    Processes the Smart Venue Kiosk input alongside an optional camera capture.
    Queries Gemini for crowd flow visualization and venue spatial analysis,
    then maps output deterministically via a lightweight keyword proxy.
    """
    KNOWLEDGE_VAULT = await get_knowledge_vault()
    system_prompt = (
        "You are an AI assistant for a smart venue kiosk at a large-scale physical event. "
        "Analyze the user's query (and attached venue imagery if provided) about crowd levels, "
        f"wait times, navigation, or facilities. Venue Information Base: {KNOWLEDGE_VAULT} "
        "Output exactly in JSON format with exactly 3 fields: 'message' (detailed venue guidance for the attendee), 'media_url' (leave blank for now), and 'image_prompt' (a 5-10 word descriptive string of the venue scenario, e.g., 'crowd density map, stadium entrance, real-time heatmap')."
    )
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "<YOUR_GEMINI_API_KEY_HERE>":
        return {
            "media_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200",
            "message": f"Simulated Render of: {user_prompt} (API Key Missing, Image provided: {'Yes' if image_data else 'No'})"
        }

    contents = [user_prompt]
    if image_data:
        import base64
        import re
        b64 = re.sub('^data:image/.+;base64,', '', image_data)
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64decode(b64)
        }
        contents.append(image_part)

    try:
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
        response = model.generate_content(
            contents,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        data = clean_json_response(response.text)
        
        # Deterministic Demo Router (No external APIs to prevent live failures)
        dynamic_image_url = "https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?q=80&w=1200" 

        if image_data:
            dynamic_image_url = image_data
        elif "image_prompt" in data and data["image_prompt"]:
            prompt_lower = data["image_prompt"].lower()
            if "thermal" in prompt_lower or "heat" in prompt_lower:
                dynamic_image_url = "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1200"
            elif "cryogenic" in prompt_lower or "cold" in prompt_lower or "freeze" in prompt_lower:
                dynamic_image_url = "https://images.unsplash.com/photo-1542840410-3092f99611a3?q=80&w=1200"
            elif "stress" in prompt_lower or "pressure" in prompt_lower:
                dynamic_image_url = "https://images.unsplash.com/photo-1581092335397-9583eb92d232?q=80&w=1200"

        data["media_url"] = dynamic_image_url
            
        return data
    except ResourceExhausted:
        logger.warning("Gemini rate limit hit during visual generation")
        return {
            "media_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
            "message": "Fallback: Hit Gemini Rate Limits! Slow down your requests."
        }
    except Exception as e:
        logger.error(f"Visual pipeline error: {e}")
        return {
            "media_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
            "message": f"Fallback: Python Engine Error Block: {str(e)}"
        }

async def process_lead_notes(notes: str, attendee_name: str = "Unknown Attendee") -> dict:
    """
    The Core Agentic Crowd Intelligence Pipeline. Uses a cascading multi-agent structure 
    (Classifier, Analyst, Verifier) to categorize attendee query urgency, dynamically 
    search for live venue/event information, and verify AI-generated guidance against 
    the Venue Information Base before delivering it to operators.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "<YOUR_GEMINI_API_KEY_HERE>":
        return {
            "sentiment": "Warm",
            "drafted_email": f"Draft for: {notes} (API Key Missing)",
            "action_items": ["Review notes manually"],
            "verification_status": "Bypassed (API Key Missing)"
        }
        
    KNOWLEDGE_VAULT = await get_knowledge_vault()
    
    # AGENT A: The Classifier
    writer_prompt = (
        "You are a smart venue assistant for crowd management at large-scale physical events like stadiums, expos, and metro stations. "
        "Analyze the attendee's query. Classify urgency/sentiment (Hot = urgent crowd safety issue, Warm = moderate wait-time or navigation concern, Cold = general information request). "
        "Draft a detailed, helpful guidance response addressing their question about crowd levels, wait times, navigation, or venue facilities. "
        "List recommended action items for the venue operations team. Also output a boolean 'competitor_mentioned' and a string 'competitor_name' (the specific venue area or event mentioned, e.g. 'Gate 4' or 'Food Court', else empty). "
        "Output exactly JSON: 'sentiment', 'drafted_email', 'action_items', 'competitor_mentioned', 'competitor_name'."
        f"\n\nVenue Information Base: {KNOWLEDGE_VAULT}"
    )
    
    try:
        model_a = genai.GenerativeModel(MODEL_NAME, system_instruction=writer_prompt)
        resp_a = model_a.generate_content(
            notes,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        draft_data = clean_json_response(resp_a.text)
        logger.info(f"Agent A classified query urgency as: {draft_data.get('sentiment', 'Unknown')}")
        
        # AGENT C: The Venue Analyst
        market_intelligence = ""
        if draft_data.get("competitor_mentioned") and draft_data.get("competitor_name"):
            comp_name = draft_data.get("competitor_name")
            try:
                results = DDGS().text(f"{comp_name} venue crowd management real-time info", max_results=3)
                market_intelligence = "LIVE VENUE INTELLIGENCE:\n"
                for r in results:
                    market_intelligence += f"- {r['title']}: {r['body']}\n"
                logger.info(f"Agent C gathered venue intel on: {comp_name}")
            except Exception as e:
                logger.warning(f"Agent C web search suppressed: {e}")
                
        # AGENT B: The Verifier
        critic_prompt = (
            "You are a venue operations expert verifying AI-generated crowd guidance for accuracy. Review the drafted guidance "
            f"against this venue information base exactly: {KNOWLEDGE_VAULT}. "
            "If the guidance contains incorrect venue information, wrong directions, or inaccurate crowd estimates, FIX IT. "
        )
        
        if market_intelligence:
            critic_prompt += (
                f"Additionally, using this live venue intelligence: {market_intelligence} "
                "append 3 actionable crowd management recommendations for the operations team. "
            )
            
        critic_prompt += (
            "IMPORTANT: The 'action_items' array MUST strictly remain a flat list of text strings (list[str]). Do NOT create nested dictionaries or JSON objects inside it. "
        )
        
        if market_intelligence:
            critic_prompt += "Prefix each of the 3 new recommendations with the exact string 'Crowd Action: ' and just add them as flat strings to the array. "
            
        critic_prompt += "Output exactly in JSON format with fields: 'verified_email' and the updated 'action_items'."
        
        CRITIC_MODEL = os.getenv("CRITIC_MODEL_OVERRIDE", MODEL_NAME)
        model_b = genai.GenerativeModel(CRITIC_MODEL, system_instruction=critic_prompt)
        
        payload_data = {"email": draft_data.get("drafted_email", ""), "action_items": draft_data.get("action_items", [])}
        resp_b = model_b.generate_content(
            json.dumps(payload_data),
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        critic_data = clean_json_response(resp_b.text)
        logger.info("Agent B verification complete")
        
        # Merge results
        draft_data["drafted_email"] = critic_data.get("verified_email", draft_data.get("drafted_email", ""))
        if "action_items" in critic_data:
             draft_data["action_items"] = critic_data["action_items"]
        draft_data["verification_status"] = "Verified by AI Crowd Intelligence Engine"
        
        # Deploy Webhook for URGENT Crowd Situations
        if draft_data.get("sentiment", "").lower() == "hot" and WEBHOOK_URL:
            payload = {
                "content": f"🚨 **URGENT CROWD ALERT** 🚨\n**Attendee:** {attendee_name}\n**Query:** {notes}\n**Auto-Action:** Guidance drafted and verified by AI Crowd Intelligence."
            }
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(WEBHOOK_URL, json=payload)
                logger.info(f"Urgent query webhook dispatched for: {attendee_name}")
            except Exception as e:
                logger.warning(f"Webhook dispatch failed: {e}")

        return draft_data
        
    except ResourceExhausted:
        logger.error("Gemini rate limit hit during lead processing")
        return {
            "sentiment": "Unknown",
            "drafted_email": "Error generating email. Hit API Rate Limits.",
            "action_items": [],
            "verification_status": "Failed Validation (Rate Limited)"
        }
    except Exception as e:
        logger.error(f"Lead pipeline error: {e}")
        traceback.print_exc()
        return {
            "sentiment": "Unknown",
            "drafted_email": "Error generating email.",
            "action_items": [],
            "verification_status": "Failed Validation"
        }
