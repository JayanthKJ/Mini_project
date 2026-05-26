from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Simple endpoint to verify the API is running."""
    return {
        "status": "online",
        "message": "AQ Prediction API is running successfully."
    }