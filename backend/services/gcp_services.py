"""
Google Cloud Platform Service Integrations for OmniBooth AI.

Provides enterprise-grade wrappers around Google Cloud Secret Manager
and Google Cloud Logging with graceful local development fallbacks.
"""

import os
import logging

logger = logging.getLogger("omnibooth")


# ---------------------------------------------------------------------------
# Google Cloud Secret Manager — Zero-Trust Credential Injection
# ---------------------------------------------------------------------------

def get_gcp_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Fetches a secret value from Google Cloud Secret Manager.
    
    On Google Cloud Run, this retrieves secrets directly from Secret Manager
    using the service account's IAM permissions — no plaintext credentials
    are stored in environment variables or source code.
    
    For local development, gracefully falls back to os.getenv() so developers
    can use a .env file without needing GCP credentials.
    
    Args:
        secret_id: The ID of the secret in Secret Manager (e.g., 'GEMINI_API_KEY').
        version_id: The version of the secret to access (default: 'latest').
    
    Returns:
        The secret value as a string.
    """
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        
        # Automatically detect GCP project ID from the environment
        project_id = os.getenv("GCP_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT"))
        
        if not project_id:
            logger.info(f"Secret Manager: No GCP project ID found, falling back to env var for '{secret_id}'")
            return os.getenv(secret_id, "")
        
        # Build the resource name for the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        
        logger.info(f"Secret Manager: Successfully retrieved secret '{secret_id}' from Google Cloud")
        return secret_value
        
    except Exception as e:
        # Graceful fallback for local development or missing IAM permissions
        logger.info(f"Secret Manager: Falling back to os.getenv() for '{secret_id}' — {type(e).__name__}")
        return os.getenv(secret_id, "")


# ---------------------------------------------------------------------------
# Google Cloud Logging — Structured Production Telemetry
# ---------------------------------------------------------------------------

def setup_gcp_logging() -> None:
    """
    Initializes Google Cloud Logging and attaches it to the Python root logger.
    
    On Google Cloud Run, this sends all log entries to Cloud Logging with
    full metadata (severity, trace, timestamp) for integration with the
    Google Cloud Console's Logs Explorer.
    
    For local development, falls back to standard console JSON logging
    so the application runs without requiring GCP credentials.
    """
    try:
        import google.cloud.logging as cloud_logging
        
        client = cloud_logging.Client()
        client.setup_logging()
        
        logger.info("Google Cloud Logging: Client attached — logs streaming to Cloud Logging")
        
    except Exception as e:
        logger.info(f"Google Cloud Logging: Unavailable ({type(e).__name__}) — using standard JSON logging")


# ---------------------------------------------------------------------------
# Google Cloud Storage — Venue Asset Management (Future-Ready)
# ---------------------------------------------------------------------------

def upload_to_gcs(bucket_name: str, blob_name: str, data: bytes) -> str:
    """
    Uploads binary data (images, documents) to Google Cloud Storage.
    
    Used for persisting venue maps, crowd snapshots, and attendee-uploaded
    media to a durable, globally-accessible storage layer.
    
    Args:
        bucket_name: Target GCS bucket name.
        blob_name: Destination path within the bucket.
        data: Raw bytes to upload.
    
    Returns:
        The public URL of the uploaded object, or empty string on failure.
    """
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data)
        
        url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
        logger.info(f"Cloud Storage: Uploaded '{blob_name}' to gs://{bucket_name}")
        return url
        
    except Exception as e:
        logger.warning(f"Cloud Storage: Upload failed — {type(e).__name__}: {e}")
        return ""
