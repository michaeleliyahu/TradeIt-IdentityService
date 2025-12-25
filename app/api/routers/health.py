"""Health check router."""
from fastapi import APIRouter
from datetime import datetime
from app.schemas.user import HealthCheckResponse
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for service availability."""
    return HealthCheckResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
        timestamp=datetime.utcnow(),
    )
