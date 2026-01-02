"""
Pydantic models for task management.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class TaskBase(BaseModel):
    """Base task model with common fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed task description")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    user_id: Optional[str] = None  # Will be set by the server if using auth


class TaskUpdate(BaseModel):
    """Model for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class Task(TaskBase):
    """Complete task model with all fields including DB-generated ones."""
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows creation from ORM objects


class TaskList(BaseModel):
    """Model for returning a list of tasks."""
    tasks: List[Task]
    total: int
    
    
class TaskResponse(BaseModel):
    """Standard response for task operations."""
    success: bool
    message: str
    task: Optional[Task] = None
    tasks: Optional[List[Task]] = None
