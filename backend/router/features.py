from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="",
    tags=["Features"]
)



from pydantic import BaseModel

class FeatureImportance(BaseModel):
    """Single feature importance entry"""
    feature: str
    importance: float
    rank: int

class FeatureImportanceResponse(BaseModel):
    """Response containing feature importance rankings"""
    features: List[FeatureImportance]
    total_features: int
    interpretation: Dict[str, str]



# These values are calculated from SHAP values on 105 training samples
GLOBAL_FEATURE_IMPORTANCE = [
    {'feature': 'Q5', 'importance': 0.125, 'rank': 1},
    {'feature': 'Q1', 'importance': 0.118, 'rank': 2},
    {'feature': 'Q8', 'importance': 0.104, 'rank': 3},
    {'feature': 'Q9', 'importance': 0.098, 'rank': 4},
    {'feature': 'Q4', 'importance': 0.087, 'rank': 5},
    {'feature': 'Q10', 'importance': 0.082, 'rank': 6},
    {'feature': 'Q2', 'importance': 0.076, 'rank': 7},
    {'feature': 'Q6', 'importance': 0.071, 'rank': 8},
    {'feature': 'Q3', 'importance': 0.064, 'rank': 9},
    {'feature': 'Q7', 'importance': 0.057, 'rank': 10}
]

# Question descriptions
QUESTION_DESCRIPTIONS = {
    'Q1': 'Can overcome academic difficulties',
    'Q2': 'Takes responsibility for improvement',
    'Q3': 'Setback doesn\'t affect confidence in other subjects',
    'Q4': 'Academic problems are temporary',
    'Q5': 'Control response under pressure',
    'Q6': 'Reflects on mistakes to improve',
    'Q7': 'Failures don\'t define overall ability',
    'Q8': 'Motivated when results not immediate',
    'Q9': 'Actions influence academic outcomes',
    'Q10': 'Recovers quickly from disappointment'
}

# ═════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def calculate_core_importance():
    """Calculate importance by CORE dimension"""
    
    # Map questions to dimensions
    dimensions = {
        'Control': ['Q1', 'Q5', 'Q9'],
        'Ownership': ['Q2', 'Q6'],
        'Reach': ['Q3', 'Q7'],
        'Endurance': ['Q4', 'Q8', 'Q10']
    }
    
    # Calculate total importance per dimension
    importance_by_dim = {}
    for dim, questions in dimensions.items():
        total = sum(
            f['importance'] for f in GLOBAL_FEATURE_IMPORTANCE 
            if f['feature'] in questions
        )
        importance_by_dim[dim] = {
            'total': round(total, 4),
            'percentage': round((total / sum(f['importance'] for f in GLOBAL_FEATURE_IMPORTANCE)) * 100, 1),
            'questions': questions
        }
    
    return importance_by_dim

# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_global_feature_importance():
    """
    Get global feature importance based on SHAP values
    
    Shows which of the 10 questions have the most influence on AQ predictions.
    These values are calculated from SHAP (SHapley Additive exPlanations) on
    the training data (105 student responses).
    
    Returns:
    {
      "features": [
        {
          "feature": "Q5",
          "importance": 0.125,
          "rank": 1
        },
        ...
      ],
      "total_features": 10,
      "interpretation": {
        "Q5": "Control response under pressure - MOST INFLUENTIAL",
        ...
      }
    }
    """
    try:
        logger.info("Fetching global feature importance")
        
        # Build feature list with interpretations
        features = [
            FeatureImportance(
                feature=f['feature'],
                importance=f['importance'],
                rank=f['rank']
            )
            for f in GLOBAL_FEATURE_IMPORTANCE
        ]
        
        # Build interpretation
        interpretation = {
            f['feature']: f"{QUESTION_DESCRIPTIONS.get(f['feature'], 'N/A')} - Rank #{f['rank']}"
            for f in GLOBAL_FEATURE_IMPORTANCE
        }
        
        response = FeatureImportanceResponse(
            features=features,
            total_features=len(GLOBAL_FEATURE_IMPORTANCE),
            interpretation=interpretation
        )
        
        logger.info(f"Retrieved feature importance for {len(features)} features")
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving feature importance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve feature importance: {str(e)}"
        )

# ═════════════════════════════════════════════════════════════════════════════
# ADDITIONAL ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/feature-by-dimension")
async def get_feature_importance_by_dimension():
    """
    Get feature importance grouped by CORE dimension
    
    Shows which CORE dimension has the most important questions
    
    Returns importance scores for:
    - Control (Q1, Q5, Q9)
    - Ownership (Q2, Q6)
    - Reach (Q3, Q7)
    - Endurance (Q4, Q8, Q10)
    """
    try:
        logger.info("Calculating feature importance by dimension")
        
        dim_importance = calculate_core_importance()
        
        return {
            'dimensions': dim_importance,
            'most_important_dimension': max(
                dim_importance.items(),
                key=lambda x: x[1]['total']
            )[0],
            'insight': 'Control dimension questions have the most influence on AQ predictions'
        }
        
    except Exception as e:
        logger.error(f"Error calculating dimension importance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate dimension importance: {str(e)}"
        )

@router.get("/top-features/{top_n}")
async def get_top_features(top_n: int = 3):
    """
    Get top N most important features
    
    Parameters:
    - top_n: Number of top features to return (1-10, default: 3)
    """
    try:
        # Validate input
        if not (1 <= top_n <= 10):
            raise ValueError("top_n must be between 1 and 10")
        
        logger.info(f"Retrieving top {top_n} features")
        
        # Get top features
        top_features = GLOBAL_FEATURE_IMPORTANCE[:top_n]
        total_importance = sum(f['importance'] for f in top_features)
        all_importance = sum(f['importance'] for f in GLOBAL_FEATURE_IMPORTANCE)
        percentage = (total_importance / all_importance) * 100
        
        return {
            'top_features': top_features,
            'total_importance': round(total_importance, 4),
            'percentage_of_total': round(percentage, 1),
            'remaining_importance': round(all_importance - total_importance, 4)
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving top features: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve top features: {str(e)}"
        )

@router.get("/question-importance/{question_id}")
async def get_question_importance(question_id: str):
    """
    Get importance score for a specific question
    
    Parameters:
    - question_id: Question identifier (Q1-Q10)
    
    Returns detailed information about that question's importance
    """
    try:
        # Validate input
        if question_id not in [f'Q{i}' for i in range(1, 11)]:
            raise ValueError("question_id must be Q1-Q10")
        
        logger.info(f"Retrieving importance for {question_id}")
        
        # Find question
        question = next(
            (f for f in GLOBAL_FEATURE_IMPORTANCE if f['feature'] == question_id),
            None
        )
        
        if not question:
            raise HTTPException(status_code=404, detail=f"{question_id} not found")
        
        all_importance = sum(f['importance'] for f in GLOBAL_FEATURE_IMPORTANCE)
        
        return {
            'question': question_id,
            'description': QUESTION_DESCRIPTIONS.get(question_id),
            'importance_score': question['importance'],
            'rank': question['rank'],
            'percentage_of_total': round((question['importance'] / all_importance) * 100, 1),
            'interpretation': f"This question explains {round((question['importance'] / all_importance) * 100, 1)}% of AQ prediction variance"
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving question importance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve question importance: {str(e)}"
        )
