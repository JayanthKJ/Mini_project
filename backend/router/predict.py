from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import numpy as np
import joblib
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



router = APIRouter(
    prefix="",
    tags=["Prediction"]
)

# ═════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def calculate_core_scores(responses: Dict) -> Dict:
    """Calculate CORE dimension scores"""
    return {
        'Control': (responses['Q1'] + responses['Q5'] + responses['Q9']) / 3,
        'Ownership': (responses['Q2'] + responses['Q6']) / 2,
        'Reach': (responses['Q3'] + responses['Q7']) / 2,
        'Endurance': (responses['Q4'] + responses['Q8'] + responses['Q10']) / 3,
    }

def calculate_aq_score(core_scores: Dict) -> float:
    """Calculate overall AQ score"""
    return np.mean(list(core_scores.values()))

def categorize_aq(score: float) -> str:
    """Categorize AQ score into Low, Medium, High"""
    if score < 2.5:
        return 'Low'
    elif score < 3.5:
        return 'Medium'
    else:
        return 'High'

def get_feature_importance(X, shap_explainer, top_n=3) -> List[Dict]:
    """Get top influential questions using SHAP"""
    try:
        shap_values = shap_explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = np.abs(shap_values[0])[0]
        else:
            shap_values = np.abs(shap_values)[0]
        
        feature_names = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']
        
        importance_dict = dict(zip(feature_names, shap_values))
        sorted_features = sorted(importance_dict.items(), 
                                key=lambda x: x[1], reverse=True)
        
        return [
            {
                'question': feature,
                'importance': float(value),
                'rank': idx + 1
            }
            for idx, (feature, value) in enumerate(sorted_features[:top_n])
        ]
    except Exception as e:
        logger.error(f"Error calculating feature importance: {e}")
        return []

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

def get_behavioral_pattern(core_scores: Dict) -> str:
    """Generate behavioral resilience pattern description"""
    aq_score = np.mean(list(core_scores.values()))
    strongest = max(core_scores, key=core_scores.get)
    weakest = min(core_scores, key=core_scores.get)
    
    if aq_score >= 3.5:
        return (
            f"HIGHLY RESILIENT: You demonstrate excellent resilience with AQ score of {aq_score:.2f}. "
            f"Strongest dimension: {strongest} ({core_scores[strongest]:.2f}). "
            f"You maintain confidence under pressure and can overcome most challenges. "
            f"Use these strengths to help others and take on leadership roles."
        )
    elif aq_score >= 2.5:
        return (
            f"MODERATELY RESILIENT: You have solid resilience with AQ score of {aq_score:.2f}. "
            f"Strongest: {strongest} ({core_scores[strongest]:.2f}), Weakest: {weakest} ({core_scores[weakest]:.2f}). "
            f"Some challenges trigger self-doubt. Focus on strengthening {weakest} dimension."
        )
    else:
        return (
            f"BUILDING RESILIENCE: You're developing resilience with AQ score of {aq_score:.2f}. "
            f"Priority: Build {weakest} dimension. "
            f"External support and mentorship recommended. This is normal and improvable!"
        )

def generate_recommendations(core_scores: Dict) -> List[Dict]:
    """Generate personalized improvement recommendations"""
    recommendations = []
    weak_dims = identify_weak_dimensions(core_scores)
    
    # Define recommendation templates
    templates = {
        'Control': {
            'Critical': {
                'Suggestion': 'Develop personal agency through small wins',
                'Actions': [
                    '1. Set 3 small achievable academic goals weekly',
                    '2. Practice positive self-talk: "I can solve this"',
                    '3. Keep a success journal tracking what you overcame',
                    '4. Seek mentorship for problem-solving strategies'
                ],
                'Expected Impact': 'Increase Control score by 0.5-1.0'
            },
            'High': {
                'Suggestion': 'Strengthen belief in your problem-solving ability',
                'Actions': [
                    '1. Reflect on past academic challenges you solved',
                    '2. Practice breaking problems into smaller parts',
                    '3. Seek support when needed - it\'s a sign of strength'
                ],
                'Expected Impact': 'Increase Control score by 0.3-0.5'
            },
            'Moderate': {
                'Suggestion': 'Build confidence in your abilities',
                'Actions': [
                    '1. Document your problem-solving successes',
                    '2. Challenge negative self-talk with evidence',
                    '3. Try one difficult problem daily'
                ],
                'Expected Impact': 'Increase Control score by 0.2-0.3'
            }
        },
        'Ownership': {
            'Critical': {
                'Suggestion': 'Build responsibility and learning from mistakes',
                'Actions': [
                    '1. After each test/assignment, do a 10-minute reflection',
                    '2. Identify 1 specific area to improve next time',
                    '3. Avoid completely blaming external factors',
                    '4. Create "Next time I will..." action plan'
                ],
                'Expected Impact': 'Increase Ownership score by 0.5-1.0'
            },
            'High': {
                'Suggestion': 'Increase accountability for improvement',
                'Actions': [
                    '1. Review mistakes with a learning mindset',
                    '2. Document lessons learned from failures',
                    '3. Share learning with supportive peers'
                ],
                'Expected Impact': 'Increase Ownership score by 0.3-0.5'
            }
        },
        'Reach': {
            'Critical': {
                'Suggestion': 'Build resilience in self-concept',
                'Actions': [
                    '1. Practice positive identity statements daily',
                    '2. Recognize strengths in other areas when facing setback',
                    '3. Remember: one grade doesn\'t define your entire identity',
                    '4. Build confidence in diverse skills and interests'
                ],
                'Expected Impact': 'Increase Reach score by 0.5-1.0'
            },
            'High': {
                'Suggestion': 'Prevent setbacks from affecting all life areas',
                'Actions': [
                    '1. Compartmentalize failures as specific events, not identity',
                    '2. Celebrate successes in other domains',
                    '3. Maintain balanced self-assessment'
                ],
                'Expected Impact': 'Increase Reach score by 0.3-0.5'
            }
        },
        'Endurance': {
            'Critical': {
                'Suggestion': 'Build persistence and long-term motivation',
                'Actions': [
                    '1. Break large goals into 2-4 week milestones',
                    '2. Visualize success at finish line weekly',
                    '3. Track progress - even small improvements count',
                    '4. Find peers with similar goals for mutual support'
                ],
                'Expected Impact': 'Increase Endurance score by 0.5-1.0'
            },
            'High': {
                'Suggestion': 'Strengthen belief that effort leads to results',
                'Actions': [
                    '1. Focus on growth over time',
                    '2. Celebrate effort regardless of immediate results',
                    '3. Maintain consistent effort even without quick wins'
                ],
                'Expected Impact': 'Increase Endurance score by 0.3-0.5'
            }
        }
    }
    
    
    for dim in weak_dims:
        dimension = dim['dimension']
        severity = dim['severity']
        
        if dimension in templates and severity in templates[dimension]:
            template = templates[dimension][severity]
            recommendations.append({
                'Dimension': dimension,
                'Priority': severity if severity in ['Critical', 'High'] else 'MEDIUM',
                'Suggestion': template['Suggestion'],
                'Actions': template['Actions'],
                'Expected Impact': template['Expected Impact']
            })
    
    return recommendations



@router.post("/predict", response_model=PredictionResponse)
async def predict_aq(questionnaire: QuestionnaireInput):
    """
    
    
    Receives 10 questionnaire responses and returns complete AQ analysis including:
    - AQ category and score
    - CORE dimension breakdown
    - Weak dimension identification
    - Feature importance (top 3 questions)
    - Behavioral pattern analysis
    - Personalized recommendations
    - Model comparison predictions
    
    Example request:
    {
      "Q1": 4, "Q2": 4, "Q3": 3, "Q4": 4, "Q5": 4,
      "Q6": 4, "Q7": 3, "Q8": 4, "Q9": 4, "Q10": 5
    }
    """
    try:
        
        from app import model_registry
        
        
        responses = questionnaire.dict()
        X = np.array([[
            responses['Q1'], responses['Q2'], responses['Q3'], 
            responses['Q4'], responses['Q5'], responses['Q6'],
            responses['Q7'], responses['Q8'], responses['Q9'], 
            responses['Q10']
        ]])
        
        logger.info(f"Processing prediction for responses: {responses}")
        
        # Step 1: Calculate CORE scores
        core_scores = calculate_core_scores(responses)
        aq_score = calculate_aq_score(core_scores)
        aq_category = categorize_aq(aq_score)
        
        logger.info(f"CORE Scores: {core_scores}, AQ Score: {aq_score}, Category: {aq_category}")
        
        # Step 2: Get predictions from all models
        model_predictions = {}
        model_confidences = {}
        confidences = []
        
        for model_name in ['Logistic Regression', 'Decision Tree', 
                          'Random Forest', 'SVM', 'XGBoost']:
            try:
                pred, proba = model_registry.predict(X, model_name)
                model_predictions[model_name] = pred
                
                # Get confidence (max probability)
                confidence = float(np.max(proba))
                model_confidences[model_name] = confidence
                confidences.append(confidence)
                
                logger.info(f"{model_name}: Prediction={pred}, Confidence={confidence:.4f}")
            except Exception as e:
                logger.error(f"Error with {model_name}: {e}")
                model_predictions[model_name] = 'Error'
                model_confidences[model_name] = 0.0
        
        # Average confidence
        avg_confidence = float(np.mean(confidences)) if confidences else 0.5
        
        # Step 3: Get feature importance
        feature_importance = get_feature_importance(X, model_registry.shap_explainer, top_n=3)
        
        # Step 4: Identify weak dimensions
        weak_dimensions = identify_weak_dimensions(core_scores)
        
        # Step 5: Generate behavioral pattern
        behavioral_pattern = get_behavioral_pattern(core_scores)
        
        # Step 6: Generate recommendations
        recommendations = generate_recommendations(core_scores)
        
        logger.info(f"Prediction successful: {aq_category} AQ with confidence {avg_confidence:.4f}")
        
        # Return complete response
        return PredictionResponse(
            aq_category=aq_category,
            aq_score=float(aq_score),
            confidence=avg_confidence,
            core_scores={k: float(v) for k, v in core_scores.items()},
            model_predictions=model_predictions,
            model_confidences=model_confidences,
            feature_importance=feature_importance,
            weak_dimensions=weak_dimensions,
            behavioral_pattern=behavioral_pattern,
            recommendations=recommendations
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
