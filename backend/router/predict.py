from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import numpy as np
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class QuestionnaireInput(BaseModel):
    """Input schema for 10-question AQ questionnaire"""
    Q1: int = Field(..., ge=1, le=5, description="Q1 Response (1-5)")
    Q2: int = Field(..., ge=1, le=5, description="Q2 Response (1-5)")
    Q3: int = Field(..., ge=1, le=5, description="Q3 Response (1-5)")
    Q4: int = Field(..., ge=1, le=5, description="Q4 Response (1-5)")
    Q5: int = Field(..., ge=1, le=5, description="Q5 Response (1-5)")
    Q6: int = Field(..., ge=1, le=5, description="Q6 Response (1-5)")
    Q7: int = Field(..., ge=1, le=5, description="Q7 Response (1-5)")
    Q8: int = Field(..., ge=1, le=5, description="Q8 Response (1-5)")
    Q9: int = Field(..., ge=1, le=5, description="Q9 Response (1-5)")
    Q10: int = Field(..., ge=1, le=5, description="Q10 Response (1-5)")
    
    @validator('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10')
    def validate_range(cls, v):
        if not (1 <= v <= 5):
            raise ValueError("Response must be between 1 and 5")
        return v

class PredictionResponse(BaseModel):
    """Response schema for prediction"""
    aq_category: str
    aq_score: float
    confidence: float
    core_scores: Dict[str, float]
    model_predictions: Dict[str, str]
    model_confidences: Dict[str, float]
    feature_importance: List[Dict[str, Any]]
    weak_dimensions: List[Dict[str, Any]]
    behavioral_pattern: str
    recommendations: List[Dict[str, Any]]
def calculate_core_scores(responses: Dict) -> Dict:
    """Calculate CORE dimension scores"""
    return {
        'Control': (responses['Q1'] + responses['Q5'] + responses['Q9']) / 3,
        'Ownership': (responses['Q2'] + responses['Q6']) / 2,
        'Reach': (responses['Q3'] + responses['Q7']) / 2,
        'Endurance': (responses['Q4'] + responses['Q8'] + responses['Q10']) / 3,
    }
def identify_weak_dimensions(core_scores: Dict, threshold=3.0) -> List[Dict]:
    """Identify weak CORE dimensions below threshold"""
    weak_dims = []
    
    for dimension, score in core_scores.items():
        if score < threshold:
            severity = (
                'Critical' if score < 2.0 else
                'High' if score < 2.5 else
                'Moderate'
            )
            
            weak_dims.append({
                'dimension': dimension,
                'score': float(score),
                'severity': severity,
                'target_score': 3.5,
                'improvement_needed': float(3.5 - score)
            })
    
    return sorted(weak_dims, key=lambda x: x['improvement_needed'], reverse=True)



router = APIRouter(prefix="", tags=["Prediction"])

def get_behavioral_pattern(ml_category: str, core_scores: Dict) -> str:
    """Dynamically generated based strictly on the ML predicted category."""
    strongest = max(core_scores, key=core_scores.get)
    weakest = min(core_scores, key=core_scores.get)
    
    if ml_category == 'High':
        return f"HIGHLY RESILIENT: ML Prediction confirms excellent resilience. Strongest dimension: {strongest}. You maintain confidence under pressure."
    elif ml_category == 'Medium':
        return f"MODERATELY RESILIENT: Solid resilience detected. Strongest: {strongest}, Weakest: {weakest}. Focus on strengthening your {weakest} dimension."
    else:
        return f"BUILDING RESILIENCE: Priority is to build your {weakest} dimension. External support and mentorship recommended."

@router.post("/predict", response_model=PredictionResponse)
async def predict_aq(questionnaire: QuestionnaireInput):
    try:
        from app import model_registry
        
        # Ensure models are actually loaded
        if not model_registry.models or 'XGBoost' not in model_registry.models:
            raise HTTPException(status_code=500, detail="ML Models are not trained/loaded. Cannot make dynamic predictions.")

        responses = questionnaire.dict()
        X = np.array([[
            responses['Q1'], responses['Q2'], responses['Q3'], responses['Q4'], 
            responses['Q5'], responses['Q6'], responses['Q7'], responses['Q8'], 
            responses['Q9'], responses['Q10']
        ]])
        
        core_scores = calculate_core_scores(responses)
        
        model_predictions = {}
        model_confidences = {}
        confidences = []
        
        
        class_mapping = {0: 'Low', 1: 'Medium', 2: 'High'}

        for model_name in ['Logistic Regression', 'Decision Tree', 'Random Forest', 'SVM', 'XGBoost']:
            pred, proba = model_registry.predict(X, model_name)
            
            # Map the integer prediction to string
            pred_str = class_mapping.get(int(pred), str(pred))
            
            model_predictions[model_name] = pred_str
            confidence = float(np.max(proba))
            model_confidences[model_name] = confidence
            confidences.append(confidence)
        
        
        final_aq_category = model_predictions['XGBoost']
        avg_confidence = float(np.mean(confidences))
        
        
        feature_importance = []
        if model_registry.shap_explainer:
            shap_vals = model_registry.shap_explainer.shap_values(X)
            vals = np.mean([np.abs(sv[0]) for sv in shap_vals], axis=0) if isinstance(shap_vals, list) else np.abs(shap_vals[0])
            feature_names = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']
            
            fi_dict = dict(zip(feature_names, vals))
            sorted_fi = sorted(fi_dict.items(), key=lambda x: x[1], reverse=True)
            feature_importance = [{'question': k, 'importance': float(v), 'rank': idx + 1} for idx, (k, v) in enumerate(sorted_fi[:3])]

        weak_dimensions = identify_weak_dimensions(core_scores)
        behavioral_pattern = get_behavioral_pattern(final_aq_category, core_scores)
        recommendations = generate_recommendations(core_scores) # Keep your existing generate_recommendations func
        
        return PredictionResponse(
            aq_category=final_aq_category,
            aq_score=float(np.mean(list(core_scores.values()))), # Retained strictly for UI charting purposes
            confidence=avg_confidence,
            core_scores={k: float(v) for k, v in core_scores.items()},
            model_predictions=model_predictions,
            model_confidences=model_confidences,
            feature_importance=feature_importance,
            weak_dimensions=weak_dimensions,
            behavioral_pattern=behavioral_pattern,
            recommendations=recommendations
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")