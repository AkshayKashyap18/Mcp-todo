"""
FastAPI Backend for MCP Todo.
Exposes MCP tools as REST endpoints for the React frontend.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from src.mcp_server.tools import (
    handle_add_task,
    handle_list_tasks,
    handle_update_task,
    handle_delete_task,
    handle_smart_add,
    handle_search_tasks,
    handle_smart_update
)

app = FastAPI(title="MCP Todo API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify generic localhost ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models for Requests ---
class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "medium"
    category: Optional[str] = None
    tags: Optional[List[str]] = []

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[str] = None

class NaturalLanguageRequest(BaseModel):
    text: str
    current_time: Optional[str] = None


# --- Routes ---

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/tasks")
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, limit: int = 100):
    """List tasks with optional filters."""
    args = {"limit": limit}
    if status and status != "All":
        args["status"] = status.lower() # DB expects lowercase
    if priority and priority != "All":
        args["priority"] = priority.lower()
        
    try:
        from database import get_db_client
        db = get_db_client()
        tasks = db.list_tasks(status=args.get("status"), priority=args.get("priority"), limit=limit)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks")
async def create_task(task: CreateTaskRequest):
    """Create a structured task."""
    try:
        from database import get_db_client
        db = get_db_client()
        
        task_data = task.model_dump(exclude_none=True)
        # Set default status
        task_data["status"] = "pending"
        
        created_task = db.create_task(task_data)
        return created_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, updates: UpdateTaskRequest):
    """Update a task."""
    try:
        from database import get_db_client
        db = get_db_client()
        
        update_data = updates.model_dump(exclude_none=True)
        if not update_data:
            return {"message": "No updates provided"}
            
        updated_task = db.update_task(task_id, update_data)
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    try:
        from database import get_db_client
        db = get_db_client()
        db.delete_task(task_id)
        return {"success": True, "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Endpoints ---

@app.post("/ai/smart-add")
async def smart_add(request: NaturalLanguageRequest):
    """Create a task from natural language."""
    try:
        # Here we CAN reuse the Smart Tool logic but we want JSON back.
        # The tool returns TextContent.
        # Better to reuse the Agent logic directly.
        from ai import get_task_agent
        from database import get_db_client
        
        agent = get_task_agent()
        db = get_db_client()
        
        # Returns a LIST of tasks now
        task_data_list = agent.parse_task_nl(request.text, current_time=request.current_time)
        
        created_tasks = []
        for task_data in task_data_list:
            if 'status' not in task_data:
                task_data['status'] = 'pending'
            
            created = db.create_task(task_data)
            created_tasks.append(created)
            
        # If single task, return object (backward compatibility/simplicity for frontend if it expects obj)
        # But frontend logic might need update if it expects array? 
        # Actually frontend `smartAdd` in utils.js just returns response.json().
        # If we return an array, frontend needs to handle it. 
        # Let's check frontend. Use `StickyBoard`? No `TasksContext`?
        
        # Let's return the list if > 1, else single object? 
        # Or better -> Always return list? 
        # Existing frontend usually expects single object if it pushes to state?
        # Let's look at frontend TasksContext.
        
        if len(created_tasks) == 1:
            return created_tasks[0]
        return created_tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/search")
async def smart_search(request: NaturalLanguageRequest):
    """Search using natural language."""
    try:
        from ai import get_task_agent
        from database import get_db_client
        
        agent = get_task_agent()
        db = get_db_client()
        
        filters = agent.search_tasks_nl(request.text)
        
        if 'search_text' in filters:
            tasks = db.search_tasks(filters['search_text'])
        else:
            tasks = db.list_tasks(
                status=filters.get('status'),
                priority=filters.get('priority'),
                limit=100
            )
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/update")
async def smart_update_endpoint(request: NaturalLanguageRequest):
    """Update using natural language with fuzzy matching."""
    try:
        from ai import get_task_agent
        from database import get_db_client
        
        agent = get_task_agent()
        db = get_db_client()
        
        all_tasks = db.list_tasks(limit=1000)
        update_info = agent.extract_task_update(request.text, all_tasks)
        
        task_match = update_info.get('task_match', '')
        updates = update_info.get('updates', {})
        
        if not task_match or not updates:
            raise HTTPException(status_code=400, detail="Could not understand update command")
            
        matching_task_id = agent.find_matching_task(task_match, all_tasks)
        
        if not matching_task_id:
            # Check for multiple matches logic
            matches = [t for t in all_tasks if task_match.lower() in t.get('title', '').lower()]
            if len(matches) > 1:
                return {
                    "status": "ambiguous",
                    "matches": matches[:5],
                    "message": f"Found {len(matches)} matching tasks. Please be more specific."
                }
            else:
                raise HTTPException(status_code=404, detail=f"No task found matching '{task_match}'")
                
        updated_task = db.update_task(matching_task_id, updates)
        return {"status": "success", "task": updated_task}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
