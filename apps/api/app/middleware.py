# apps/api/app/middleware.py
"""
Custom middleware for HIPAA compliance, security, and encryption
"""

import json
import time
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from app.config import settings
import logging

logger = logging.getLogger("evijnar.hipaa")

class HIPAALoggingMiddleware(BaseHTTPMiddleware):
    """
    HIPAA-compliant audit logging middleware.
    Logs all access to protected health information (PHI).
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"

        # Extract user info (from JWT token if available)
        user_id = request.headers.get("x-user-id", "anonymous")

        # Request metadata
        request_body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.body()
                # Don't log sensitive data in body
            except Exception:
                pass

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Audit log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "user_id": user_id,
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "process_time_ms": round(process_time * 1000, 2),
        }

        # Log to HIPAA audit system
        if settings.hipaa_audit_log_enabled:
            logger.info(json.dumps(audit_entry))

        # Add security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class EncryptionHeaderMiddleware(BaseHTTPMiddleware):
    """
    Validates encryption headers for sensitive endpoints.
    Ensures client supports TLS and proper encryption.
    """

    async def dispatch(self, request: Request, call_next):
        # Sensitive paths that require encryption
        sensitive_paths = [
            "/api/v1/patients",
            "/api/v1/recovery",
            "/api/v1/financing",
        ]

        # Check if this is a sensitive endpoint
        is_sensitive = any(
            request.url.path.startswith(path) for path in sensitive_paths
        )

        if is_sensitive and request.method in ["POST", "PUT", "PATCH"]:
            # Verify TLS
            if not request.scope.get("scheme") == "https" and settings.app_env != "development":
                return PlainTextResponse(
                    "HTTPS required for sensitive endpoints",
                    status_code=403,
                )

            # Validate encryption capability
            encryption_key = request.headers.get("x-encryption-key-id")
            if not encryption_key:
                logger.warning(f"Missing encryption key for {request.url.path}")

        response = await call_next(request)
        return response
