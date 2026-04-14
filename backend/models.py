from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class KioskRequest(BaseModel):
    prompt: Optional[str] = Field("", description="The highly technical text input from the attendee.")
    image_data: Optional[str] = Field(None, description="Base64 encoded string of captured spatial image.")

class KioskResponse(BaseModel):
    media_url: str = Field(..., description="The URL to the simulated 3D mechanical animation or cinematic media.")
    message: str = Field(..., description="The rich technical description of the required physics simulation.")

class LeadCaptureRequest(BaseModel):
    notes: str = Field(..., description="The rough notes or voice transcript logged by the exhibitor.")
    attendee_name: Optional[str] = None
    attendee_email: Optional[str] = None

class LeadCaptureResponse(BaseModel):
    sentiment: str = Field(..., description="AI determined intent: Hot, Warm, or Cold.")
    drafted_email: str = Field(..., description="A technical B2B proposal drafted specifically for this lead.")
    action_items: List[str] = Field(..., description="A list of bullet points detailing next steps.")
    verification_status: Optional[str] = Field("Pending", description="Status set by the OmniEngine Critic Loop.")

class DocumentUploadRequest(BaseModel):
    text: str = Field(..., description="The highly technical manual text to add to the knowledge vault.")
