"""
AI-powered smart tools for MCP Todo Server.

These tools use natural language understanding via Groq API.
"""
import logging
from typing import Any, Dict, List
from mcp.types import TextContent

from database import get_db_client
from ai import get_task_agent

logger = logging.getLogger(__name__)

# Get database and AI clients
db = get_db_client()
agent = get_task_agent()


async def handle_smart_add(arguments: dict) -> list[TextContent]:
    """
    Handle smart_add tool call - create task from natural language.
    
    Args:
        arguments: Tool arguments containing natural_language string
        
    Returns:
        List of text content responses
    """
    try:
        natural_language = arguments.get("natural_language", "")
        if not natural_language:
            return [TextContent(type="text", text="❌ Error: natural_language parameter is required")]
        
        logger.info(f"Processing smart_add: {natural_language}")
        
        # Parse task using AI agent
        task_data = agent.parse_task_nl(natural_language)
        
        # Ensure status is set
        if 'status' not in task_data:
            task_data['status'] = 'pending'
        
        # Create task in database
        created_task = db.create_task(task_data)
        
        # Format response
        response_text = f"✅ Task created successfully!\n\n"
        response_text += f"📝 Title: {created_task['title']}\n"
        response_text += f"🎯 Priority: {created_task['priority']}\n"
        response_text += f"📊 Status: {created_task['status']}\n"
        
        if created_task.get('category'):
            response_text += f"🏷️ Category: {created_task['category']}\n"
        
        if created_task.get('due_date'):
            response_text += f"📅 Due: {created_task['due_date']}\n"
        
        if created_task.get('tags'):
            response_text += f"🏷️ Tags: {', '.join(created_task['tags'])}\n"
        
        response_text += f"\n🆔 ID: {created_task['id']}"
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error in handle_smart_add: {str(e)}")
        return [TextContent(type="text", text=f"❌ Error creating task: {str(e)}")]


async def handle_search_tasks(arguments: dict) -> list[TextContent]:
    """
    Handle search_tasks tool call - search using natural language.
    
    Args:
        arguments: Tool arguments containing query string
        
    Returns:
        List of text content responses
    """
    try:
        query = arguments.get("query", "")
        if not query:
            return [TextContent(type="text", text="❌ Error: query parameter is required")]
        
        logger.info(f"Processing search: {query}")
        
        # Convert natural language to filters using AI
        filters = agent.search_tasks_nl(query)
        
        # Query database with filters
        if 'search_text' in filters:
            # Use text search
            tasks = db.search_tasks(filters['search_text'])
        else:
            # Use structured filters
            tasks = db.list_tasks(
                status=filters.get('status'),
                priority=filters.get('priority'),
                limit=100
            )
        
        if not tasks:
            return [TextContent(type="text", text=f"🔍 No tasks found matching: '{query}'")]
        
        # Format results
        response_text = f"🔍 Found {len(tasks)} task(s) matching '{query}':\n\n"
        
        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
        priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🔴"}
        
        for task in tasks:
            response_text += (
                f"{status_emoji.get(task['status'], '•')} "
                f"{priority_emoji.get(task['priority'], '•')} "
                f"{task['title']}\n"
                f"   ID: {task['id']}\n"
                f"   Status: {task['status']} | Priority: {task['priority']}\n"
            )
            
            if task.get('category'):
                response_text += f"   Category: {task['category']}\n"
            
            if task.get('due_date'):
                response_text += f"   Due: {task['due_date']}\n"
            
            response_text += "\n"
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error in handle_search_tasks: {str(e)}")
        return [TextContent(type="text", text=f"❌ Error searching tasks: {str(e)}")]


async def handle_smart_update(arguments: dict) -> list[TextContent]:
    """
    Handle smart_update tool call - update task using natural language.
    
    Args:
        arguments: Tool arguments containing natural_language update command
        
    Returns:
        List of text content responses
    """
    try:
        natural_language = arguments.get("natural_language", "")
        if not natural_language:
            return [TextContent(type="text", text="❌ Error: natural_language parameter is required")]
        
        logger.info(f"Processing smart_update: {natural_language}")
        
        # Get all tasks for fuzzy matching
        all_tasks = db.list_tasks(limit=1000)
        
        if not all_tasks:
            return [TextContent(type="text", text="❌ No tasks found in the database")]
        
        # Extract update information using AI
        update_info = agent.extract_task_update(natural_language, all_tasks)
        
        # Find matching task
        task_match = update_info.get('task_match', '')
        updates = update_info.get('updates', {})
        
        if not task_match or not updates:
            return [TextContent(
                type="text",
                text=f"❌ Could not understand the update command: '{natural_language}'\n"
                     f"Please be more specific about which task to update and what to change."
            )]
        
        # Find task by fuzzy matching
        matching_task_id = agent.find_matching_task(task_match, all_tasks)
        
        if not matching_task_id:
            # Check if multiple matches
            matches = [t for t in all_tasks if task_match.lower() in t.get('title', '').lower()]
            
            if len(matches) > 1:
                # Multiple matches - ask for clarification
                response_text = f"🤔 Found {len(matches)} tasks matching '{task_match}':\n\n"
                for i, task in enumerate(matches[:5], 1):  # Show max 5
                    response_text += f"{i}. {task['title']} (ID: {task['id']})\n"
                    response_text += f"   Status: {task['status']} | Priority: {task['priority']}\n\n"
                
                response_text += "\nPlease use the update_task tool with the specific task ID."
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ No task found matching '{task_match}'"
                )]
        
        # Update the task
        updated_task = db.update_task(matching_task_id, updates)
        
        # Format response
        response_text = f"✅ Task updated successfully!\n\n"
        response_text += f"📝 Title: {updated_task['title']}\n"
        response_text += f"📊 Status: {updated_task['status']}\n"
        response_text += f"🎯 Priority: {updated_task['priority']}\n"
        
        if updated_task.get('category'):
            response_text += f"🏷️ Category: {updated_task['category']}\n"
        
        if updated_task.get('due_date'):
            response_text += f"📅 Due: {updated_task['due_date']}\n"
        
        response_text += f"\n🆔 ID: {updated_task['id']}"
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error in handle_smart_update: {str(e)}")
        return [TextContent(type="text", text=f"❌ Error updating task: {str(e)}")]
