"""
Parsers for natural language task information.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import dateparser
import re

logger = logging.getLogger(__name__)


def parse_datetime(text: str, timezone: str = "UTC") -> Optional[str]:
    """
    Parse natural language datetime to ISO 8601 string.
    
    Args:
        text: Natural language datetime (e.g., "tomorrow at 5pm", "next Friday")
        timezone: Timezone for parsing
        
    Returns:
        ISO 8601 datetime string or None if parsing fails
    """
    try:
        # Use dateparser to handle natural language
        parsed_date = dateparser.parse(
            text,
            settings={
                'TIMEZONE': timezone,
                'RETURN_AS_TIMEZONE_AWARE': False,
                'PREFER_DATES_FROM': 'future'
            }
        )
        
        if parsed_date:
            return parsed_date.isoformat()
        
        logger.warning(f"Could not parse datetime: {text}")
        return None
        
    except Exception as e:
        logger.error(f"Error parsing datetime '{text}': {str(e)}")
        return None


def extract_priority(text: str) -> str:
    """
    Extract priority from text based on keywords.
    
    Args:
        text: Text to analyze
        
    Returns:
        Priority level: "low", "medium", or "high"
    """
    text_lower = text.lower()
    
    # High priority keywords
    high_keywords = [
        'urgent', 'asap', 'critical', 'important', 'emergency',
        'high priority', 'crucial', 'vital', 'pressing'
    ]
    
    # Low priority keywords
    low_keywords = [
        'low priority', 'whenever', 'someday', 'maybe',
        'not urgent', 'low', 'minor'
    ]
    
    for keyword in high_keywords:
        if keyword in text_lower:
            return "high"
    
    for keyword in low_keywords:
        if keyword in text_lower:
            return "low"
    
    return "medium"


def infer_category(text: str) -> Optional[str]:
    """
    Infer task category from text content.
    
    Args:
        text: Task text to analyze
        
    Returns:
        Inferred category or None
    """
    text_lower = text.lower()
    
    # Category keywords mapping
    categories = {
        'work': ['work', 'meeting', 'project', 'deadline', 'presentation', 'report', 'email'],
        'personal': ['personal', 'self', 'health', 'exercise', 'doctor', 'appointment'],
        'shopping': ['buy', 'purchase', 'shop', 'groceries', 'store', 'order'],
        'home': ['home', 'house', 'clean', 'repair', 'fix', 'maintenance'],
        'finance': ['pay', 'bill', 'bank', 'money', 'budget', 'invoice'],
        'learning': ['learn', 'study', 'read', 'course', 'tutorial', 'practice'],
        'social': ['call', 'meet', 'visit', 'party', 'event', 'friend', 'family']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return None


def extract_tags(text: str) -> List[str]:
    """
    Extract potential tags from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of extracted tags
    """
    tags = []
    text_lower = text.lower()
    
    # Common tag keywords
    tag_keywords = {
        'urgent': ['urgent', 'asap', 'emergency'],
        'important': ['important', 'critical', 'crucial'],
        'recurring': ['daily', 'weekly', 'monthly', 'recurring'],
        'quick': ['quick', 'fast', 'brief', '5 minutes', '10 minutes'],
        'long': ['long', 'extended', 'lengthy']
    }
    
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if keyword in text_lower and tag not in tags:
                tags.append(tag)
    
    return tags


def clean_title(text: str) -> str:
    """
    Clean and format task title.
    
    Args:
        text: Raw title text
        
    Returns:
        Cleaned title
    """
    # Remove common time expressions
    time_patterns = [
        r'\b(tomorrow|today|tonight)\b',
        r'\bat\s+\d{1,2}(:\d{2})?\s*(am|pm)?\b',
        r'\bby\s+\w+\b',
        r'\b(urgent|asap|high priority|low priority)\b'
    ]
    
    cleaned = text
    for pattern in time_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = ' '.join(cleaned.split())
    
    # Capitalize first letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    
    return cleaned.strip()


def parse_task_metadata(text: str) -> Dict[str, Any]:
    """
    Parse all metadata from natural language task description.
    
    This is a fallback parser that doesn't use LLM.
    
    Args:
        text: Natural language task description
        
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        'title': clean_title(text),
        'priority': extract_priority(text),
        'category': infer_category(text),
        'tags': extract_tags(text)
    }
    
    # Try to extract due date
    # Common patterns: "tomorrow", "at 5pm", "by Friday"
    due_date_patterns = [
        r'(tomorrow|today|tonight)',
        r'at\s+(\d{1,2}(:\d{2})?\s*(am|pm)?)',
        r'by\s+(\w+)',
        r'on\s+(\w+)',
        r'next\s+(\w+)'
    ]
    
    for pattern in due_date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            due_date = parse_datetime(match.group(0))
            if due_date:
                metadata['due_date'] = due_date
                break
    
    return metadata


def validate_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean task data.
    
    Args:
        task_data: Raw task data dictionary
        
    Returns:
        Validated task data
    """
    validated = {}
    
    # Required field
    if 'title' in task_data and task_data['title']:
        validated['title'] = str(task_data['title']).strip()
    else:
        raise ValueError("Task title is required")
    
    # Optional fields with validation
    if 'description' in task_data and task_data['description']:
        validated['description'] = str(task_data['description']).strip()
    
    if 'priority' in task_data:
        priority = str(task_data['priority']).lower()
        if priority in ['low', 'medium', 'high']:
            validated['priority'] = priority
        else:
            validated['priority'] = 'medium'
    
    if 'status' in task_data:
        status = str(task_data['status']).lower()
        if status in ['pending', 'in_progress', 'completed']:
            validated['status'] = status
    
    if 'category' in task_data and task_data['category']:
        validated['category'] = str(task_data['category']).strip()
    
    if 'due_date' in task_data and task_data['due_date']:
        due_date = str(task_data['due_date'])
        # Handle ISO 8601 intervals (e.g. "2023-01-01/2023-01-02")
        if '/' in due_date:
            due_date = due_date.split('/')[0]
        validated['due_date'] = due_date
    
    if 'tags' in task_data and isinstance(task_data['tags'], list):
        validated['tags'] = [str(tag).strip() for tag in task_data['tags'] if tag]
    
    return validated
