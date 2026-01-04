"""
LangChain agent for natural language task processing.
"""
import logging
from typing import Dict, Any, Optional, List

from ai.groq_client import get_groq_client
from ai.parsers import parse_task_metadata, validate_task_data

logger = logging.getLogger(__name__)


class TaskAgent:
    """LangChain agent for intelligent task processing."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the task agent.
        
        Args:
            model: Groq model to use
        """
        self.groq_client = get_groq_client()
        self.model = model
        logger.info(f"TaskAgent initialized with model: {model}")
    
    def parse_task_nl(self, natural_language: str, current_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse task from natural language using LLM.
        
        Args:
            natural_language: Natural language task description
            current_time: Optional ISO timestamp of the user's current time for reference
            
        Returns:
            List of validated task data dictionaries
        """
        try:
            # Use Groq client for parsing (now returns a list)
            task_data_list = self.groq_client.parse_task_from_nl(natural_language, current_time=current_time)
            
            validated_list = []
            for task_data in task_data_list:
                # Validate and clean each task
                try:
                    validated = validate_task_data(task_data)
                    validated_list.append(validated)
                    logger.info(f"Successfully parsed task: {validated.get('title')}")
                except Exception as val_err:
                    logger.warning(f"Skipping invalid task in batch: {val_err}")
            
            if not validated_list:
                 raise ValueError("No valid tasks found in parsed output")
                 
            return validated_list
            
        except Exception as e:
            logger.warning(f"LLM parsing failed, using fallback parser: {str(e)}")
            # Fallback to rule-based parsing (likely single task)
            task_data = parse_task_metadata(natural_language)
            return [validate_task_data(task_data)]
    
    def search_tasks_nl(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language search query to database filters.
        
        Args:
            query: Natural language search query
            
        Returns:
            Dictionary with filter parameters
        """
        try:
            filters = self.groq_client.search_query_to_filters(query)
            logger.info(f"Search filters: {filters}")
            return filters
            
        except Exception as e:
            logger.error(f"Error parsing search query: {str(e)}")
            # Fallback to simple text search
            return {"search_text": query}
    
    def extract_task_update(self, natural_language: str, existing_tasks: list) -> Dict[str, Any]:
        """
        Extract task update information from natural language.
        
        Args:
            natural_language: Natural language update command
            existing_tasks: List of existing tasks for fuzzy matching
            
        Returns:
            Dictionary with task_id and updates
        """
        system_prompt = """You are a task update parser. Extract the task identifier and updates from natural language.

Given a list of existing tasks and an update command, identify which task to update and what changes to make.

Return a JSON object with:
- task_match: string (keywords to match the task)
- updates: object with fields to update (status, priority, title, etc.)

Examples:
Input: "Mark the groceries task as done"
Output: {"task_match": "groceries", "updates": {"status": "completed"}}

Input: "Change the meeting priority to high"
Output: {"task_match": "meeting", "updates": {"priority": "high"}}

Only return valid JSON, no additional text."""

        user_message = f"""Update command: {natural_language}

Existing tasks:
{self._format_tasks_for_prompt(existing_tasks)}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.groq_client.chat_completion(messages, temperature=0.3)
            
            import json
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
                
        except Exception as e:
            logger.error(f"Error extracting task update: {str(e)}")
            raise ValueError(f"Could not parse update command: {natural_language}")
    
    def _format_tasks_for_prompt(self, tasks: list) -> str:
        """Format tasks for LLM prompt."""
        if not tasks:
            return "No existing tasks"
        
        formatted = []
        for task in tasks[:10]:  # Limit to 10 tasks to avoid token limits
            formatted.append(
                f"- {task.get('title')} (ID: {task.get('id')}, Status: {task.get('status')})"
            )
        
        return "\n".join(formatted)
    
    def find_matching_task(self, task_match: str, tasks: list) -> Optional[str]:
        """
        Find task ID that matches the search string.
        
        Args:
            task_match: String to match against task titles
            tasks: List of tasks to search
            
        Returns:
            Task ID if single match found, None otherwise
        """
        task_match_lower = task_match.lower()
        matches = []
        
        for task in tasks:
            title_lower = task.get('title', '').lower()
            if task_match_lower in title_lower:
                matches.append(task)
        
        if len(matches) == 1:
            return matches[0]['id']
        elif len(matches) > 1:
            # Multiple matches - need clarification
            logger.warning(f"Multiple tasks match '{task_match}': {[t['title'] for t in matches]}")
            return None
        else:
            logger.warning(f"No tasks match '{task_match}'")
            return None


# Global instance
_task_agent: Optional[TaskAgent] = None


def get_task_agent() -> TaskAgent:
    """
    Get or create the global task agent instance.
    
    Returns:
        TaskAgent instance
    """
    global _task_agent
    if _task_agent is None:
        _task_agent = TaskAgent()
    return _task_agent
