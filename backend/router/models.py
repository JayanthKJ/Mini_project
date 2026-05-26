from fastapi import APIRouter, HTTPException
from typing import List
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Models"])

class ModelMetrics(BaseModel):
    model_name: str
    accuracy: float
    f1_score: float
    auc_roc: float
    cv_mean: float
    cv_std: float

class ModelComparisonResponse(BaseModel):
    algorithms: List[ModelMetrics]
    best_model: str
    best_accuracy: float

@router.get("/model-comparison", response_model=ModelComparisonResponse)
async def get_model_comparison():
    try:
        from app import model_registry
        
        if not model_registry.evaluation_metrics:
            raise HTTPException(status_code=404, detail="ML evaluation metrics not found. Please run the training script.")

        metrics_data = model_registry.evaluation_metrics
        
        algorithms = [ModelMetrics(**model) for model in metrics_data]
        best_model = max(metrics_data, key=lambda x: x['accuracy'])
        
        return ModelComparisonResponse(
            algorithms=algorithms,
            best_model=best_model['model_name'],
            best_accuracy=best_model['accuracy']
        )
        
    except Exception as e:
        logger.error(f"Error retrieving model comparison: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model comparison: {str(e)}")