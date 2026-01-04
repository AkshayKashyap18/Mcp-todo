"""
MCP Server for Todo List Management.

This server provides MCP tools for task management with both deterministic
and AI-powered capabilities.
"""
import asyncio
import logging
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from database import get_db_client
from src.mcp_server.models import Task, TaskCreate, TaskUpdate
from src.mcp_server.tools import (
    handle_add_task,
    handle_list_tasks,
    handle_update_task,
    handle_delete_task,
    handle_smart_add,
    handle_search_tasks,
    handle_smart_update
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("mcp-todo-server")

# Get database client
db = get_db_client()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.
    
    Returns:
        List of tool definitions
    """
    return [
        Tool(
            name="add_task",
            description="Create a new task with basic information (deterministic, no AI)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO 8601 format (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority (optional, default: medium)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Task category (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task tags (optional)"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks with optional filters (deterministic, no AI)",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filter by status (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task (deterministic, no AI)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to update (required)"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "New status (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority (optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "New category (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO 8601 format (optional)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task (deterministic, no AI)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to delete (required)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="smart_add",
            description="Create a task from natural language (AI-powered)",
            inputSchema={
                "type": "object",
                "properties": {
                    "natural_language": {
                        "type": "string",
                        "description": "Natural language task description (e.g., 'Buy groceries tomorrow at 5pm, urgent')"
                    }
                },
                "required": ["natural_language"]
            }
        ),
        Tool(
            name="search_tasks",
            description="Search tasks using natural language (AI-powered)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'Show me high priority tasks')"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="smart_update",
            description="Update a task using natural language with fuzzy matching (AI-powered)",
            inputSchema={
                "type": "object",
                "properties": {
                    "natural_language": {
                        "type": "string",
                        "description": "Natural language update command (e.g., 'Mark the groceries task as done')"
                    }
                },
                "required": ["natural_language"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    
    Args:
        name: Name of the tool to call
        arguments: Tool arguments
        
    Returns:
        List of text content responses
    """
    try:
        # Deterministic tools
        if name == "add_task":
            return await handle_add_task(arguments)
        elif name == "list_tasks":
            return await handle_list_tasks(arguments)
        elif name == "update_task":
            return await handle_update_task(arguments)
        elif name == "delete_task":
            return await handle_delete_task(arguments)
        # AI-powered tools
        elif name == "smart_add":
            return await handle_smart_add(arguments)
        elif name == "search_tasks":
            return await handle_search_tasks(arguments)
        elif name == "smart_update":
            return await handle_smart_update(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error handling tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting MCP Todo Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio transport")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
