from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="",
    tags=["Health"]
)



@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Verifies that the backend is running and accessible.
    Use this to check if the server is alive.
    
    Returns:
    {
      "status": "OK",
      "service": "AQ Prediction System",
      "timestamp": "2026-05-26T10:30:00",
      "version": "1.0.0"
    }
    """
    try:
        logger.info("Health check requested")
        
        # Import model registry to verify models are loaded
        from app import model_registry
        
        models_loaded = len(model_registry.models) == 5 if model_registry else False
        
        response = {
            "status": "OK",
            "service": "AQ Prediction System",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "models_loaded": models_loaded,
            "endpoints_available": [
                "POST /predict",
                "GET /model-comparison",
                "GET /feature-importance",
                "GET /core-dimensions",
                "GET /health"
            ]
        }
        
        logger.info(f"Health check successful: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "ERROR",
                "message": f"Health check failed: {str(e)}"
            }
        )
