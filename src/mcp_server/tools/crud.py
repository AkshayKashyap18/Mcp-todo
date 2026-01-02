"""
CRUD tools for MCP Todo Server.

These are deterministic tools that don't use AI.
"""
import logging
from typing import Any, Dict, List
from mcp.types import TextContent

from database import get_db_client

logger = logging.getLogger(__name__)

# Get database client
db = get_db_client()


async def handle_add_task(arguments: dict) -> list[TextContent]:
    """
    Handle add_task tool call.
    
    Args:
        arguments: Tool arguments containing task data
        
    Returns:
        List of text content responses
    """
    try:
        # Create task data
        task_data = {
            "title": arguments["title"],
            "description": arguments.get("description"),
            "priority": arguments.get("priority", "medium"),
            "category": arguments.get("category"),
            "tags": arguments.get("tags", []),
            "status": "pending"
        }
        
        # Handle due_date if provided
        if "due_date" in arguments and arguments["due_date"]:
            task_data["due_date"] = arguments["due_date"]
        
        # Create task in database
        created_task = db.create_task(task_data)
        
        return [
            TextContent(
                type="text",
                text=f"✅ Task created successfully!\n\n"
                     f"ID: {created_task['id']}\n"
                     f"Title: {created_task['title']}\n"
                     f"Priority: {created_task['priority']}\n"
                     f"Status: {created_task['status']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_add_task: {str(e)}")
        raise


async def handle_list_tasks(arguments: dict) -> list[TextContent]:
    """
    Handle list_tasks tool call.
    
    Args:
        arguments: Tool arguments containing filters
        
    Returns:
        List of text content responses
    """
    try:
        status = arguments.get("status")
        priority = arguments.get("priority")
        limit = arguments.get("limit", 100)
        
        # Get tasks from database
        tasks = db.list_tasks(status=status, priority=priority, limit=limit)
        
        if not tasks:
            return [TextContent(type="text", text="No tasks found.")]
        
        # Format task list
        task_list = f"📋 Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🔴"}
            
            task_list += (
                f"{status_emoji.get(task['status'], '•')} "
                f"{priority_emoji.get(task['priority'], '•')} "
                f"{task['title']}\n"
                f"   ID: {task['id']}\n"
                f"   Status: {task['status']} | Priority: {task['priority']}\n"
            )
            if task.get('due_date'):
                task_list += f"   Due: {task['due_date']}\n"
            task_list += "\n"
        
        return [TextContent(type="text", text=task_list)]
    except Exception as e:
        logger.error(f"Error in handle_list_tasks: {str(e)}")
        raise


async def handle_update_task(arguments: dict) -> list[TextContent]:
    """
    Handle update_task tool call.
    
    Args:
        arguments: Tool arguments containing task_id and updates
        
    Returns:
        List of text content responses
    """
    try:
        task_id = arguments["task_id"]
        
        # Build updates dictionary (only include provided fields)
        updates = {}
        for field in ["title", "description", "status", "priority", "category", "due_date"]:
            if field in arguments and arguments[field] is not None:
                updates[field] = arguments[field]
        
        if not updates:
            return [TextContent(type="text", text="No updates provided.")]
        
        # Update task in database
        updated_task = db.update_task(task_id, updates)
        
        return [
            TextContent(
                type="text",
                text=f"✅ Task updated successfully!\n\n"
                     f"ID: {updated_task['id']}\n"
                     f"Title: {updated_task['title']}\n"
                     f"Status: {updated_task['status']}\n"
                     f"Priority: {updated_task['priority']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_update_task: {str(e)}")
        raise


async def handle_delete_task(arguments: dict) -> list[TextContent]:
    """
    Handle delete_task tool call.
    
    Args:
        arguments: Tool arguments containing task_id
        
    Returns:
        List of text content responses
    """
    try:
        task_id = arguments["task_id"]
        
        # Delete task from database
        db.delete_task(task_id)
        
        return [
            TextContent(
                type="text",
                text=f"✅ Task {task_id} deleted successfully!"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_delete_task: {str(e)}")
        raise
