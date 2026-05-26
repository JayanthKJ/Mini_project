from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging


logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="",
    tags=["Dimensions"]
)



CORE_DIMENSIONS_DATA = {
    'Control': {
        'questions': ['Q1', 'Q5', 'Q9'],
        'description': 'Belief in personal agency and problem-solving ability',
        'full_description': (
            'Control measures whether you believe your actions can influence outcomes '
            'and that you can solve problems when they arise. It reflects personal agency '
            'and the belief that you have some control over what happens to you.'
        ),
        'score_range': [1, 5],
        'ideal_score': 4.0,
        'low_indicators': [
            'Feeling helpless when faced with challenges',
            'Believing others control outcomes',
            'Avoidance of problem-solving'
        ],
        'high_indicators': [
            'Active problem-solving approach',
            'Belief in personal influence',
            'Taking action despite setbacks'
        ],
        'improvement_tips': [
            'Set small achievable goals',
            'Practice problem-solving daily',
            'Reflect on past successes',
            'Seek mentorship and guidance'
        ]
    },
    
    'Ownership': {
        'questions': ['Q2', 'Q6'],
        'description': 'Taking responsibility and learning from mistakes',
        'full_description': (
            'Ownership is about taking responsibility for your actions and their consequences. '
            'It means not blaming others excessively and being willing to learn from mistakes '
            'to improve in the future.'
        ),
        'score_range': [1, 5],
        'ideal_score': 4.0,
        'low_indicators': [
            'Blaming external factors exclusively',
            'Not taking responsibility for mistakes',
            'Resistance to self-reflection'
        ],
        'high_indicators': [
            'Accountability for actions',
            'Learning from failures',
            'Reflective attitude toward mistakes'
        ],
        'improvement_tips': [
            'Keep a reflection journal',
            'Analyze mistakes with curiosity',
            'Create improvement plans',
            'Discuss lessons with peers'
        ]
    },
    
    'Reach': {
        'questions': ['Q3', 'Q7'],
        'description': 'Preventing setbacks from affecting all life areas',
        'full_description': (
            'Reach is about compartmentalizing setbacks so they do not spill over and affect '
            'your confidence in other areas of life. It\'s the ability to maintain a positive '
            'self-image despite failures in one domain.'
        ),
        'score_range': [1, 5],
        'ideal_score': 4.0,
        'low_indicators': [
            'One failure destroys overall confidence',
            'Negative self-talk extends beyond specific situation',
            'Difficulty separating domains of life'
        ],
        'high_indicators': [
            'Compartmentalization of failures',
            'Maintenance of positive identity',
            'Recognition of diverse strengths'
        ],
        'improvement_tips': [
            'Practice compartmentalization',
            'Celebrate successes in other areas',
            'Maintain balanced self-view',
            'Remind yourself of diverse abilities'
        ]
    },
    
    'Endurance': {
        'questions': ['Q4', 'Q8', 'Q10'],
        'description': 'Belief that problems are temporary and solvable',
        'full_description': (
            'Endurance is about believing that difficulties are temporary and that effort '
            'will eventually lead to improvement. It\'s the motivation to persist despite '
            'slow progress or delayed results.'
        ),
        'score_range': [1, 5],
        'ideal_score': 4.0,
        'low_indicators': [
            'Viewing problems as permanent',
            'Losing motivation with slow progress',
            'Difficulty recovering from disappointment'
        ],
        'high_indicators': [
            'Belief in temporary nature of problems',
            'Persistent effort despite delays',
            'Quick recovery from setbacks'
        ],
        'improvement_tips': [
            'Set milestone goals',
            'Track progress over time',
            'Practice patience',
            'Find long-term motivation sources'
        ]
    }
}



@router.get("/core-dimensions")
async def get_core_dimensions_info():
    """
    Get comprehensive information about CORE dimensions
    
    Returns detailed information about:
    - Control: Personal agency and problem-solving
    - Ownership: Responsibility and learning
    - Reach: Compartmentalization of setbacks
    - Endurance: Persistence and hope
    
    Each includes questions, description, scoring, and improvement tips
    """
    try:
        logger.info("Retrieving CORE dimensions information")
        
        response = {}
        for dimension, data in CORE_DIMENSIONS_DATA.items():
            response[dimension] = {
                'questions': data['questions'],
                'description': data['description'],
                'full_description': data['full_description'],
                'score_range': data['score_range'],
                'ideal_score': data['ideal_score'],
                'low_indicators': data['low_indicators'],
                'high_indicators': data['high_indicators'],
                'improvement_tips': data['improvement_tips']
            }
        
        logger.info("CORE dimensions information retrieved successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving CORE dimensions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve CORE dimensions: {str(e)}"
        )

# ═════════════════════════════════════════════════════════════════════════════
# ADDITIONAL ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/core-dimension/{dimension_name}")
async def get_dimension_details(dimension_name: str):
    """
    Get detailed information about a specific CORE dimension
    
    Parameters:
    - dimension_name: One of Control, Ownership, Reach, or Endurance
    
    Returns comprehensive details including:
    - Questions that measure this dimension
    - Full description and explanation
    - Indicators of low/high scores
    - Tips for improvement
    """
    try:
        # Validate input
        if dimension_name not in CORE_DIMENSIONS_DATA:
            raise HTTPException(
                status_code=404,
                detail=f"Dimension '{dimension_name}' not found. Use: Control, Ownership, Reach, or Endurance"
            )
        
        logger.info(f"Retrieving details for dimension: {dimension_name}")
        
        data = CORE_DIMENSIONS_DATA[dimension_name]
        
        return {
            'dimension': dimension_name,
            'questions': data['questions'],
            'description': data['description'],
            'full_description': data['full_description'],
            'score_range': data['score_range'],
            'ideal_score': data['ideal_score'],
            'assessment': {
                'low_score_indicators': data['low_indicators'],
                'high_score_indicators': data['high_indicators']
            },
            'improvement_strategy': {
                'tips': data['improvement_tips'],
                'expected_timeline': '2-4 weeks for noticeable improvement',
                'key_habits': f"Focus on the {len(data['improvement_tips'])} tips above"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dimension details: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dimension details: {str(e)}"
        )

@router.get("/dimension-questions/{dimension_name}")
async def get_dimension_questions(dimension_name: str):
    """
    Get the specific questions that measure a dimension
    
    Parameters:
    - dimension_name: Control, Ownership, Reach, or Endurance
    
    Returns the questions and their descriptions
    """
    try:
        if dimension_name not in CORE_DIMENSIONS_DATA:
            raise HTTPException(
                status_code=404,
                detail=f"Dimension '{dimension_name}' not found"
            )
        
        logger.info(f"Retrieving questions for: {dimension_name}")
        
        data = CORE_DIMENSIONS_DATA[dimension_name]
        questions = data['questions']
        
        
        question_descriptions = {
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
        
        question_details = [
            {
                'question': q,
                'text': question_descriptions.get(q),
                'dimension': dimension_name
            }
            for q in questions
        ]
        
        return {
            'dimension': dimension_name,
            'total_questions': len(questions),
            'questions': question_details,
            'calculation': f"Score = Average of {', '.join(questions)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dimension questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dimension questions: {str(e)}"
        )

@router.get("/all-dimensions-summary")
async def get_all_dimensions_summary():
    """
    Get a quick summary of all CORE dimensions
    
    Returns one-line descriptions and ideal scores for all dimensions
    """
    try:
        logger.info("Retrieving all dimensions summary")
        
        summary = {
            'total_dimensions': len(CORE_DIMENSIONS_DATA),
            'dimensions': {
                dimension: {
                    'description': data['description'],
                    'ideal_score': data['ideal_score'],
                    'questions_count': len(data['questions'])
                }
                for dimension, data in CORE_DIMENSIONS_DATA.items()
            },
            'overall_aq_calculation': (
                'AQ Score = Average of (Control + Ownership + Reach + Endurance) / 4'
            ),
            'aq_categories': {
                'Low': '< 2.5',
                'Medium': '2.5 - 3.4',
                'High': '>= 3.5'
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving dimensions summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dimensions summary: {str(e)}"
        )

@router.post("/calculate-core-scores")
async def calculate_core_from_responses(responses: Dict[str, int]):
    """
    Calculate CORE dimension scores from raw questionnaire responses
    
    Input:
    {
      "Q1": 4, "Q2": 4, "Q3": 3, "Q4": 4, "Q5": 4,
      "Q6": 4, "Q7": 3, "Q8": 4, "Q9": 4, "Q10": 5
    }
    
    Returns:
    {
      "Control": 4.0,
      "Ownership": 4.0,
      "Reach": 3.0,
      "Endurance": 4.33,
      "aq_score": 3.83
    }
    """
    try:
        logger.info("Calculating CORE scores from responses")
        
        # Validate input
        required_questions = [f'Q{i}' for i in range(1, 11)]
        for q in required_questions:
            if q not in responses:
                raise ValueError(f"Missing response for {q}")
            if not (1 <= responses[q] <= 5):
                raise ValueError(f"{q} must be between 1 and 5")
        
        # Calculate CORE scores
        core_scores = {
            'Control': (responses['Q1'] + responses['Q5'] + responses['Q9']) / 3,
            'Ownership': (responses['Q2'] + responses['Q6']) / 2,
            'Reach': (responses['Q3'] + responses['Q7']) / 2,
            'Endurance': (responses['Q4'] + responses['Q8'] + responses['Q10']) / 3
        }
        
        aq_score = sum(core_scores.values()) / 4
        
        # Categorize
        if aq_score < 2.5:
            category = 'Low'
        elif aq_score < 3.5:
            category = 'Medium'
        else:
            category = 'High'
        
        logger.info(f"CORE scores calculated: {core_scores}, AQ: {aq_score:.2f}")
        
        return {
            'control': round(core_scores['Control'], 2),
            'ownership': round(core_scores['Ownership'], 2),
            'reach': round(core_scores['Reach'], 2),
            'endurance': round(core_scores['Endurance'], 2),
            'aq_score': round(aq_score, 2),
            'aq_category': category
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating CORE scores: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate CORE scores: {str(e)}"
        )
