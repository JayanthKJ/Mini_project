from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Dimensions"])



CORE_DIMENSIONS_DATA = {
    'Control': {
        'questions': ['Q1', 'Q5', 'Q9'],
        'description': 'Belief in personal agency and problem-solving ability',
        'full_description': 'Control measures whether you believe your actions can influence outcomes and that you can solve problems when they arise. It reflects personal agency.',
        'low_indicators': ['Feeling helpless when faced with challenges', 'Believing others control outcomes'],
        'improvement_tips': ['Set small achievable goals', 'Practice problem-solving daily']
    },
    'Ownership': {
        'questions': ['Q2', 'Q6'],
        'description': 'Taking responsibility and learning from mistakes',
        'full_description': 'Ownership is about taking responsibility for your actions and their consequences. It means not blaming others excessively and being willing to learn from mistakes.',
        'low_indicators': ['Blaming external factors exclusively', 'Resistance to self-reflection'],
        'improvement_tips': ['Keep a reflection journal', 'Create improvement plans']
    },
    'Reach': {
        'questions': ['Q3', 'Q7'],
        'description': 'Preventing setbacks from affecting all life areas',
        'full_description': 'Reach is about compartmentalizing setbacks so they do not spill over and affect your confidence in other areas of life.',
        'low_indicators': ['One failure destroys overall confidence', 'Difficulty separating domains of life'],
        'improvement_tips': ['Practice compartmentalization', 'Celebrate successes in other areas']
    },
    'Endurance': {
        'questions': ['Q4', 'Q8', 'Q10'],
        'description': 'Belief that problems are temporary and solvable',
        'full_description': 'Endurance is about believing that difficulties are temporary and that effort will eventually lead to improvement. It\'s the motivation to persist.',
        'low_indicators': ['Viewing problems as permanent', 'Losing motivation with slow progress'],
        'improvement_tips': ['Set milestone goals', 'Track progress over time']
    }
}

@router.get("/core-dimensions")
async def get_core_dimensions_info():
    """Returns definitions of the CORE dimensions for frontend display."""
    try:
        return CORE_DIMENSIONS_DATA
    except Exception as e:
        logger.error(f"Error retrieving CORE dimensions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))