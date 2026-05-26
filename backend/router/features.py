from fastapi import APIRouter, HTTPException
from typing import List, Dict
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Features"])

class FeatureImportance(BaseModel):
    feature: str
    importance: float
    rank: int

class FeatureImportanceResponse(BaseModel):
    features: List[FeatureImportance]
    total_features: int
    interpretation: Dict[str, str]

# Kept purely for English string mapping for the UI
QUESTION_DESCRIPTIONS = {
    'Q1': 'Can overcome academic difficulties', 'Q2': 'Takes responsibility for improvement',
    'Q3': 'Setback doesn\'t affect confidence', 'Q4': 'Academic problems are temporary',
    'Q5': 'Control response under pressure', 'Q6': 'Reflects on mistakes to improve',
    'Q7': 'Failures don\'t define overall ability', 'Q8': 'Motivated when results not immediate',
    'Q9': 'Actions influence academic outcomes', 'Q10': 'Recovers quickly from disappointment'
}

@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_global_feature_importance():
    try:
        from app import model_registry
        
        if not model_registry.global_feature_importance:
             raise HTTPException(status_code=404, detail="Global feature importance JSON not found. Please run the training script.")
             
        dynamic_features = model_registry.global_feature_importance

        features = [
            FeatureImportance(
                feature=f['feature'],
                importance=f['importance'],
                rank=f.get('rank', idx + 1)
            ) for idx, f in enumerate(dynamic_features)
        ]
        
        interpretation = {
            f['feature']: f"{QUESTION_DESCRIPTIONS.get(f['feature'], 'N/A')} - Rank #{f.get('rank', idx + 1)}"
            for idx, f in enumerate(dynamic_features)
        }
        
        return FeatureImportanceResponse(
            features=features,
            total_features=len(dynamic_features),
            interpretation=interpretation
        )
        
    except Exception as e:
        logger.error(f"Error retrieving feature importance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))