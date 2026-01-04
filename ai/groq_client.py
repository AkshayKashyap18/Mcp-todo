"""
Groq API client for LLM interactions.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq's LLM API."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client.
        
        Args:
            model: Model to use for completions
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"Groq client initialized with model: {model}")
    
    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Get a chat completion from Groq.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.info(f"Groq API call successful. Tokens used: {response.usage.total_tokens}")
            return content
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def parse_task_from_nl(self, natural_language: str, current_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse task information from natural language.
        
        Args:
            natural_language: Natural language task description
            current_time: Optional ISO timestamp of the user's current time for reference
            
        Returns:
            List of dictionaries with extracted task fields
        """
        
        time_context = f"Current User Time: {current_time}" if current_time else "Current User Time: Unknown"

        system_prompt = f"""You are a high-precision task parser. Extract structured task information from natural language.
        
{time_context}

CRITICAL RULES:
1. RELATIVE DATES: "today", "tomorrow", "tonight", "this friday" etc. MUST be calculated relative to the '{time_context}'.
   - If today is Saturday, Jan 3rd, then "today" is Saturday Jan 3rd.
   - If today is Saturday, Jan 3rd, then "tomorrow" is Sunday Jan 4th.
2. TIMEZONES: You MUST return the `due_date` with the SAME timezone offset as the Current User Time provided.
   - If the user time ends in '+05:30' or 'GMT+5:30', your `due_date` must use '+05:30'.
   - DO NOT return UTC (Z) if the user provides a local offset.
3. DEFAULT TIME: If a date is mentioned but no specific time is given (e.g., "today"), default to 23:59:59 of that day.
   - DO NOT default to 00:00:00 as it causes timezone flip issues.

Return a JSON array of objects (even for one task) with these fields:
- title: string (required, concise)
- description: string (optional)
- priority: "low" | "medium" | "high" (default: "medium")
- category: string (optional, e.g., "work", "personal", "sport")
- due_date: ISO 8601 datetime string with timezone (optional)
- tags: array of strings (optional)

Example:
Input: "batmitton today"
User Time: Saturday, January 3, 2026, 8:50 AM GMT+5:30
Output: [{{"title": "Badminton", "priority": "medium", "due_date": "2026-01-03T23:59:59+05:30", "category": "sport"}}]

Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        # Parse JSON response
        import json
        try:
            # Clean up the response
            content = response.strip()
            
            # Check for Markdown code blocks and strip them
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            # Attempt to parse directly first
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Greedy search for the largest possible JSON object/array
                # Look for first [ and last ] or first { and last }
                bracket_start = content.find('[')
                bracket_end = content.rfind(']')
                brace_start = content.find('{')
                brace_end = content.rfind('}')

                # Prioritize array if it spans further or exists
                if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
                    if brace_start == -1 or bracket_start < brace_start:
                        try:
                            data = json.loads(content[bracket_start:bracket_end + 1])
                        except:
                            # If array fails, maybe try brace if it exists inside/outside? 
                            # But usually [ is what we want for List
                            pass

                if 'data' not in locals():
                    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                        data = json.loads(content[brace_start:brace_end + 1])
                    else:
                        raise ValueError("No JSON structure found in response")

            # Normalize to list
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("Parsed data is neither dict nor list")

        except Exception as e:
            logger.error(f"Failed to parse JSON from Groq response. Error: {str(e)}. Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
    
    def search_query_to_filters(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language search query to database filters.
        
        Args:
            query: Natural language search query
            
        Returns:
            Dictionary with filter parameters
        """
        system_prompt = """You are a search query parser. Convert natural language queries into database filters.

Return a JSON object with these optional fields:
- status: "pending" | "in_progress" | "completed"
- priority: "low" | "medium" | "high"
- search_text: string (for title/description search)
- category: string

Examples:
Input: "Show me all high priority tasks"
Output: {"priority": "high"}

Input: "What tasks are completed?"
Output: {"status": "completed"}

Input: "Find tasks about groceries"
Output: {"search_text": "groceries"}

Only return valid JSON, no additional text."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        import json
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq response: {response}")
            return {"search_text": query}  # Fallback to text search


# Global instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """
    Get or create the global Groq client instance.
    
    Returns:
        GroqClient instance
    """
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
