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
   
    try:
        logger.info("Health check requested")
        
        # Import model registry to verify models are loaded
        from backend.main import model_registry
        
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
