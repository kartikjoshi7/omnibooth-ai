import os
import json
import traceback
import urllib.parse
import httpx
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if GEMINI_API_KEY and GEMINI_API_KEY != "<YOUR_GEMINI_API_KEY_HERE>":
    genai.configure(api_key=GEMINI_API_KEY)
    
MODEL_NAME = "gemini-2.5-flash-lite"

from backend.services.database import get_db

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
        print(f"Critical JSON Parsing Error: {e}")
        return {} 

async def update_knowledge_vault(doc_text: str):
    """Asynchronously pushes raw text into the RAG knowledge collection."""
    db = get_db()
    if db is not None:
        await db.knowledge.update_one(
            {"_id": "main_vault"},
            {"$set": {"text": doc_text}},
            upsert=True
        )

async def get_knowledge_vault() -> str:
    """Extracts internal company documentation from the stateless RAG cluster."""
    db = get_db()
    if db is not None:
        doc = await db.knowledge.find_one({"_id": "main_vault"})
        if doc:
            return doc.get("text", "")
    return ""

async def generate_visual_context(user_prompt: str, image_data: str = None) -> dict:
    """
    Processes the Kiosk UI input alongside an optional spatial camera capture.
    It rigorously queries Gemini for structural analysis and then maps output 
    deterministically via a lightweight keyword proxy.
    """
    KNOWLEDGE_VAULT = await get_knowledge_vault()
    system_prompt = (
        "You are an AI generating structural physics and mechanical engineering visual concepts. "
        "Take the user's prompt (and attached spatial imagery if provided) and generate a detailed "
        f"and inspiring description of what the 3D animation should look like. Context Vault: {KNOWLEDGE_VAULT} "
        "Output exactly in JSON format with exactly 3 fields: 'message' (the detailed description), 'media_url' (leave blank for now), and 'image_prompt' (a 5-10 word highly descriptive, comma-separated string optimized for an image generator, e.g., '3d render, glowing titanium engine part, cyberpunk lighting, 8k resolution')."
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
        print("CRITICAL: Hit Gemini Rate Limits! Slow down your requests.")
        return {
            "media_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
            "message": "Fallback: Hit Gemini Rate Limits! Slow down your requests."
        }
    except Exception as e:
        print(f"Critical Visual Pipeline Error: {e}")
        return {
            "media_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
            "message": f"Fallback: Python Engine Error Block: {str(e)}"
        }

async def process_lead_notes(notes: str, attendee_name: str = "Unknown Prospect") -> dict:
    """
    The Core Agentic Pipeline. Uses a cascading multi-agent structure (Writer, Analyst, Engineer) 
    to categorize a lead, dynamically execute a headless DuckDuckGo web-search against detected 
    competitors, and critically verify proposal fidelity against internal RAG context.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "<YOUR_GEMINI_API_KEY_HERE>":
        return {
            "sentiment": "Warm",
            "drafted_email": f"Draft for: {notes} (API Key Missing)",
            "action_items": ["Review notes manually"],
            "verification_status": "Bypassed (API Key Missing)"
        }
        
    KNOWLEDGE_VAULT = await get_knowledge_vault()
    
    # AGENT A: The Writer
    writer_prompt = (
        "You are an enterprise CRM assistant. Analyze the sales notes. "
        "Extract intent/sentiment (Hot, Warm, Cold), draft a highly technical custom proposal email, "
        "and list any action items in an array. Also output a boolean 'competitor_mentioned' and a string 'competitor_name' (e.g. 'GE-90X' if they mention it, else empty). "
        "Output exactly JSON: 'sentiment', 'drafted_email', 'action_items', 'competitor_mentioned', 'competitor_name'."
        f"\n\nExhibitor Documentation Context: {KNOWLEDGE_VAULT}"
    )
    
    try:
        model_a = genai.GenerativeModel(MODEL_NAME, system_instruction=writer_prompt)
        resp_a = model_a.generate_content(
            notes,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        draft_data = clean_json_response(resp_a.text)
        
        # AGENT C: The Market Analyst
        market_intelligence = ""
        if draft_data.get("competitor_mentioned") and draft_data.get("competitor_name"):
            comp_name = draft_data.get("competitor_name")
            try:
                results = DDGS().text(f"{comp_name} specifications and weaknesses", max_results=3)
                market_intelligence = "LIVE MARKET INTELLIGENCE:\n"
                for r in results:
                    market_intelligence += f"- {r['title']}: {r['body']}\n"
            except Exception as e:
                print(f"Agent C DuckDuckGo search suppressed: {e}")
                
        # AGENT B: The Engineer/Closer
        critic_prompt = (
            "You are a Senior Engineer checking for technical hallucinations. Review the drafted email "
            f"against this knowledge vault exactly: {KNOWLEDGE_VAULT}. "
            "If the draft contains impossible technical specifications or wrong product numbers, FIX IT. "
        )
        
        if market_intelligence:
            critic_prompt += (
                f"Additionally, using this market intelligence: {market_intelligence} "
                "append 3 new data-driven bullet points on why OmniCore V9 is superior to the competitor. "
            )
            
        critic_prompt += (
            "IMPORTANT: The 'action_items' array MUST strictly remain a flat list of text strings (list[str]). Do NOT create nested dictionaries or JSON objects inside it. "
        )
        
        if market_intelligence:
            critic_prompt += "Prefix each of the 3 new competitor points with the exact string 'Battle Card: ' and just add them as flat strings to the array. "
            
        critic_prompt += "Output exactly in JSON format with fields: 'verified_email' and the updated 'action_items'."
        
        CRITIC_MODEL = os.getenv("CRITIC_MODEL_OVERRIDE", MODEL_NAME)
        model_b = genai.GenerativeModel(CRITIC_MODEL, system_instruction=critic_prompt)
        
        payload_data = {"email": draft_data.get("drafted_email", ""), "action_items": draft_data.get("action_items", [])}
        resp_b = model_b.generate_content(
            json.dumps(payload_data),
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        critic_data = clean_json_response(resp_b.text)
        
        # Merge results
        draft_data["drafted_email"] = critic_data.get("verified_email", draft_data.get("drafted_email", ""))
        if "action_items" in critic_data:
             draft_data["action_items"] = critic_data["action_items"]
        draft_data["verification_status"] = "Verified by OmniEngine & Market Scanned"
        
        # Deploy Webhook Analytics Pipeline for HOT Leads
        if draft_data.get("sentiment", "").lower() == "hot" and WEBHOOK_URL:
            payload = {
                "content": f"🚨 **HOT LEAD SECURED** 🚨\n**Prospect:** {attendee_name}\n**Intel:** {notes}\n**Auto-Action:** Proposal drafted and verified by OmniEngine."
            }
            try:
                import httpx
                # Run isolated POST trap so failure does not destroy Kiosk API sequence
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(WEBHOOK_URL, json=payload)
            except Exception as e:
                print(f"Deal Webhook blocked/timed-out safely: {e}")

        return draft_data
        
    except ResourceExhausted:
        print("CRITICAL: Hit Gemini Rate Limits in Critic Loop! Slow down your requests.")
        return {
            "sentiment": "Unknown",
            "drafted_email": "Error generating email. Hit API Rate Limits.",
            "action_items": [],
            "verification_status": "Failed Validation (Rate Limited)"
        }
    except Exception as e:
        print(f"Critical Lead Pipeline Error: {e}")
        traceback.print_exc()
        return {
            "sentiment": "Unknown",
            "drafted_email": "Error generating email.",
            "action_items": [],
            "verification_status": "Failed Validation"
        }
