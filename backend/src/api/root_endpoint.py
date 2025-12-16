from fastapi import APIRouter
from src.models.api_models import APIStatus
from src.config import settings

router = APIRouter()

@router.get("/")
def read_root():
    """Get the root endpoint information."""
    return {
        "message": "Welcome to the Robotics Book API",
        "status": "running",
        "version": "0.1.0",
        "available_endpoints": [
            "/",
            "/book/content",
            "/health",
            "/status"
        ]
    }

@router.get("/status", response_model=APIStatus)
def get_status():
    """Get the API status information."""
    import time
    # In a real implementation, we would calculate actual uptime
    uptime = "0 days, 0 hours, 0 minutes"  # Placeholder

    return APIStatus(
        version="0.1.0",
        uptime=uptime,
        requests_processed=0,  # This would be tracked in a real implementation
        environment=settings.environment
    )