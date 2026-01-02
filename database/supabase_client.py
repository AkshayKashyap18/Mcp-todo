"""
Supabase database client for task management.
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase database client for task operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task in the database.
        
        Args:
            task_data: Dictionary containing task fields
            
        Returns:
            Created task data
        """
        try:
            # Ensure updated_at is set
            task_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("tasks").insert(task_data).execute()
            logger.info(f"Task created successfully: {response.data[0]['id']}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single task by ID.
        
        Args:
            task_id: UUID of the task
            
        Returns:
            Task data or None if not found
        """
        try:
            response = self.client.table("tasks").select("*").eq("id", task_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}")
            raise
    
    def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.
        
        Args:
            user_id: Filter by user ID
            status: Filter by status (pending, in_progress, completed)
            priority: Filter by priority (low, medium, high)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of task data
        """
        try:
            query = self.client.table("tasks").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
            if priority:
                query = query.eq("priority", priority)
            
            # Order by created_at descending (newest first)
            query = query.order("created_at", desc=True)
            query = query.limit(limit).offset(offset)
            
            response = query.execute()
            logger.info(f"Retrieved {len(response.data)} tasks")
            return response.data
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            raise
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id: UUID of the task to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated task data
        """
        try:
            # Always update the updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            response = (
                self.client.table("tasks")
                .update(updates)
                .eq("id", task_id)
                .execute()
            )
            
            if not response.data:
                raise ValueError(f"Task {task_id} not found")
            
            logger.info(f"Task {task_id} updated successfully")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: UUID of the task to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.table("tasks").delete().eq("id", task_id).execute()
            logger.info(f"Task {task_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
    
    def search_tasks(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search tasks by title or description.
        
        Args:
            query: Search query string
            user_id: Optional user ID filter
            
        Returns:
            List of matching tasks
        """
        try:
            # Use ilike for case-insensitive search
            db_query = self.client.table("tasks").select("*")
            
            if user_id:
                db_query = db_query.eq("user_id", user_id)
            
            # Search in title or description
            db_query = db_query.or_(f"title.ilike.%{query}%,description.ilike.%{query}%")
            
            response = db_query.execute()
            logger.info(f"Search found {len(response.data)} tasks")
            return response.data
        except Exception as e:
            logger.error(f"Error searching tasks: {str(e)}")
            raise
    
    def get_task_count(self, user_id: Optional[str] = None, status: Optional[str] = None) -> int:
        """
        Get count of tasks matching filters.
        
        Args:
            user_id: Optional user ID filter
            status: Optional status filter
            
        Returns:
            Count of matching tasks
        """
        try:
            query = self.client.table("tasks").select("id", count="exact")
            
            if user_id:
                query = query.eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else len(response.data)
        except Exception as e:
            logger.error(f"Error counting tasks: {str(e)}")
            raise


# Global instance
_db_client: Optional[SupabaseClient] = None


def get_db_client() -> SupabaseClient:
    """
    Get or create the global database client instance.
    
    Returns:
        SupabaseClient instance
    """
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client
