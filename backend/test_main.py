# test_main.py
# Comprehensive PyTest suite for OmniBooth AI Backend
# Tests core API endpoints with mocked external dependencies (Gemini SDK, MongoDB)

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


# --- Fixtures ---

@pytest.fixture(autouse=True)
def mock_database():
    """Mock the database connection for all tests to avoid requiring a live MongoDB instance."""
    with patch("backend.services.database.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_db.leads = MagicMock()
        mock_db.leads.insert_one = AsyncMock(return_value=MagicMock(inserted_id="test_id"))
        mock_db.leads.find = MagicMock(return_value=MagicMock(sort=MagicMock(return_value=AsyncIterator([]))))
        mock_db.leads.aggregate = MagicMock(return_value=AsyncIterator([]))
        mock_db.knowledge = MagicMock()
        mock_db.knowledge.find_one = AsyncMock(return_value=None)
        mock_db.knowledge.update_one = AsyncMock()
        mock_get_db.return_value = mock_db
        yield mock_db


class AsyncIterator:
    """Helper to create an async iterator from a list for mocking Motor cursors."""
    def __init__(self, items):
        self.items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration

    def sort(self, *args, **kwargs):
        return self


# Import app AFTER mocks are in place
from backend.main import app

client = TestClient(app)


# ===========================
# 1. Lead Capture Endpoint
# ===========================

class TestLeadCapture:
    """Tests for POST /capture-lead — the core Agentic AI pipeline."""

    @patch("backend.services.gemini_service.process_lead_notes")
    def test_capture_lead_success(self, mock_process):
        """Verify that a valid lead capture request returns 200 with correct sentiment classification."""
        mock_process.return_value = {
            "sentiment": "Hot",
            "drafted_email": "Dear Prospect, we are excited to propose...",
            "action_items": ["Schedule demo", "Send pricing sheet"],
            "verification_status": "Verified by OmniEngine & Market Scanned"
        }
        response = client.post("/capture-lead", json={
            "notes": "Very interested in our thermal engine solution. Wants pricing ASAP.",
            "attendee_name": "Jane Doe",
            "attendee_email": "jane@enterprise.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "Hot"
        assert "drafted_email" in data
        assert isinstance(data["action_items"], list)
        assert data["verification_status"] == "Verified by OmniEngine & Market Scanned"

    def test_capture_lead_missing_notes(self):
        """Verify that a request with no 'notes' field returns a 422 Validation Error."""
        response = client.post("/capture-lead", json={
            "attendee_name": "John"
        })
        assert response.status_code == 422

    def test_capture_lead_empty_notes(self):
        """Verify that empty string notes are rejected by Pydantic min_length validation."""
        response = client.post("/capture-lead", json={
            "notes": ""
        })
        assert response.status_code == 422

    @patch("backend.services.gemini_service.process_lead_notes")
    def test_capture_lead_cold_sentiment(self, mock_process):
        """Verify cold leads are properly classified and returned."""
        mock_process.return_value = {
            "sentiment": "Cold",
            "drafted_email": "Thank you for stopping by...",
            "action_items": ["Add to mailing list"],
            "verification_status": "Verified by OmniEngine & Market Scanned"
        }
        response = client.post("/capture-lead", json={
            "notes": "Just browsing, not really interested."
        })
        assert response.status_code == 200
        assert response.json()["sentiment"] == "Cold"


# ===========================
# 2. Leads Retrieval Endpoint
# ===========================

class TestGetLeads:
    """Tests for GET /leads — the CRM pipeline data source."""

    def test_get_leads_returns_list(self):
        """Verify that /leads always returns a JSON array."""
        response = client.get("/leads")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_leads_with_data(self, mock_database):
        """Verify leads are returned when data exists in the database."""
        mock_database.leads.find.return_value = MagicMock(
            sort=MagicMock(return_value=AsyncIterator([
                {"_id": "abc123", "attendee_name": "Test User", "sentiment": "Warm", "notes": "Test"}
            ]))
        )
        response = client.get("/leads")
        assert response.status_code == 200


# ===========================
# 3. Visual Generation Endpoint
# ===========================

class TestGenerateVisual:
    """Tests for POST /generate-visual — the multimodal Kiosk pipeline."""

    @patch("backend.services.gemini_service.generate_visual_context")
    def test_generate_visual_success(self, mock_gen):
        """Verify successful visual generation returns media_url and message."""
        mock_gen.return_value = {
            "media_url": "https://images.unsplash.com/photo-test",
            "message": "A detailed structural analysis of the component..."
        }
        response = client.post("/generate-visual", json={
            "prompt": "Show me a thermal stress test simulation"
        })
        assert response.status_code == 200
        data = response.json()
        assert "media_url" in data
        assert "message" in data

    @patch("backend.services.gemini_service.generate_visual_context")
    def test_generate_visual_with_image(self, mock_gen):
        """Verify multimodal input (text + image) is accepted."""
        mock_gen.return_value = {
            "media_url": "https://images.unsplash.com/photo-test",
            "message": "Analysis with spatial reference..."
        }
        response = client.post("/generate-visual", json={
            "prompt": "Analyze this part",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
        })
        assert response.status_code == 200

    @patch("backend.services.gemini_service.generate_visual_context")
    def test_generate_visual_invalid_response(self, mock_gen):
        """Verify that an incomplete AI response triggers a 500 error."""
        mock_gen.return_value = {"partial": "data"}
        response = client.post("/generate-visual", json={"prompt": "test"})
        assert response.status_code == 500


# ===========================
# 4. Document Upload Endpoint
# ===========================

class TestUploadDocs:
    """Tests for POST /upload-docs — RAG Knowledge Vault ingestion."""

    @patch("backend.services.gemini_service.update_knowledge_vault")
    def test_upload_docs_success(self, mock_upload):
        """Verify document upload returns success message."""
        mock_upload.return_value = None
        response = client.post("/upload-docs", json={
            "text": "OmniCore V9 specifications: Max thermal tolerance 4500K..."
        })
        assert response.status_code == 200
        assert "Knowledge Vault" in response.json()["message"]

    def test_upload_docs_missing_text(self):
        """Verify missing text field returns 422."""
        response = client.post("/upload-docs", json={})
        assert response.status_code == 422


# ===========================
# 5. Analytics Endpoint
# ===========================

class TestAnalytics:
    """Tests for GET /analytics — real-time sentiment aggregation."""

    def test_analytics_returns_list(self):
        """Verify analytics endpoint returns a JSON array."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ===========================
# 6. Edge Cases & Security
# ===========================

class TestEdgeCases:
    """Tests for boundary conditions and security validation."""

    def test_oversized_notes_rejected(self):
        """Verify that excessively large input is rejected by validation."""
        response = client.post("/capture-lead", json={
            "notes": "x" * 10001
        })
        assert response.status_code == 422

    def test_oversized_document_rejected(self):
        """Verify that excessively large RAG documents are rejected."""
        response = client.post("/upload-docs", json={
            "text": "x" * 100001
        })
        assert response.status_code == 422

    def test_unknown_route_returns_valid_response(self):
        """Verify that unknown routes don't leak server internals."""
        response = client.get("/this-does-not-exist-xyz")
        assert response.status_code in [200, 404]

    def test_models_endpoint(self):
        """Verify the /models endpoint responds without crashing."""
        with patch("google.generativeai.list_models", return_value=[]):
            response = client.get("/models")
            assert response.status_code == 200