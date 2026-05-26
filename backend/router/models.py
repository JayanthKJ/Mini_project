from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="",
    tags=["Models"]
)



from pydantic import BaseModel

class ModelMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    accuracy: float
    f1_score: float
    auc_roc: float
    cv_mean: float
    cv_std: float

class ModelComparisonResponse(BaseModel):
    """Response containing all model metrics"""
    algorithms: List[ModelMetrics]
    best_model: str
    best_accuracy: float



MODEL_PERFORMANCE_DATA = [
    {
        'model_name': 'XGBoost',
        'accuracy': 0.84,
        'f1_score': 0.83,
        'auc_roc': 0.92,
        'cv_mean': 0.79,
        'cv_std': 0.07,
        'description': 'Gradient boosting - Best overall performance'
    },
    {
        'model_name': 'Random Forest',
        'accuracy': 0.82,
        'f1_score': 0.81,
        'auc_roc': 0.90,
        'cv_mean': 0.77,
        'cv_std': 0.07,
        'description': 'Ensemble method - Stable and interpretable'
    },
    {
        'model_name': 'SVM',
        'accuracy': 0.80,
        'f1_score': 0.78,
        'auc_roc': 0.88,
        'cv_mean': 0.75,
        'cv_std': 0.08,
        'description': 'Support Vector Machine - Non-linear boundaries'
    },
    {
        'model_name': 'Decision Tree',
        'accuracy': 0.78,
        'f1_score': 0.76,
        'auc_roc': 0.85,
        'cv_mean': 0.72,
        'cv_std': 0.09,
        'description': 'Tree-based - Interpretable rules'
    },
    {
        'model_name': 'Logistic Regression',
        'accuracy': 0.75,
        'f1_score': 0.73,
        'auc_roc': 0.82,
        'cv_mean': 0.70,
        'cv_std': 0.08,
        'description': 'Linear baseline - Simplest model'
    }
]



@router.get("/model-comparison", response_model=ModelComparisonResponse)
async def get_model_comparison():
    
    try:
        logger.info("Fetching model comparison data")
        
        # Build response
        algorithms = [
            ModelMetrics(
                model_name=model['model_name'],
                accuracy=model['accuracy'],
                f1_score=model['f1_score'],
                auc_roc=model['auc_roc'],
                cv_mean=model['cv_mean'],
                cv_std=model['cv_std']
            )
            for model in MODEL_PERFORMANCE_DATA
        ]
        
        # Find best model
        best_model = max(MODEL_PERFORMANCE_DATA, key=lambda x: x['accuracy'])
        
        response = ModelComparisonResponse(
            algorithms=algorithms,
            best_model=best_model['model_name'],
            best_accuracy=best_model['accuracy']
        )
        
        logger.info(f"Model comparison retrieved. Best: {best_model['model_name']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving model comparison: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model comparison: {str(e)}"
        )



@router.get("/model-details/{model_name}")
async def get_model_details(model_name: str):
    """
    Get detailed information about a specific model
    
    Parameters:
    - model_name: Name of the model (e.g., "XGBoost", "Random Forest")
    
    Returns detailed metrics and description
    """
    try:
        
        model = next(
            (m for m in MODEL_PERFORMANCE_DATA if m['model_name'] == model_name),
            None
        )
        
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found"
            )
        
        logger.info(f"Retrieved details for model: {model_name}")
        
        return {
            'model_name': model['model_name'],
            'accuracy': model['accuracy'],
            'f1_score': model['f1_score'],
            'auc_roc': model['auc_roc'],
            'cv_mean': model['cv_mean'],
            'cv_std': model['cv_std'],
            'description': model['description'],
            'hyperparameters': {
                'XGBoost': {
                    'n_estimators': 100,
                    'max_depth': 3,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8
                },
                'Random Forest': {
                    'n_estimators': 100,
                    'max_depth': 5,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2
                },
                'SVM': {
                    'kernel': 'rbf',
                    'C': 1.0,
                    'gamma': 'scale'
                },
                'Decision Tree': {
                    'max_depth': 5,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2
                },
                'Logistic Regression': {
                    'C': 1.0,
                    'max_iter': 1000
                }
            }.get(model_name, {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model details: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model details: {str(e)}"
        )
