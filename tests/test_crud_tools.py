"""
Unit tests for CRUD tools.

These tests mock the database client to test tool logic independently.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from mcp.types import TextContent

from src.mcp_server.tools.crud import (
    handle_add_task,
    handle_list_tasks,
    handle_update_task,
    handle_delete_task
)


class TestAddTask:
    """Tests for add_task tool."""
    
    @pytest.mark.asyncio
    async def test_add_task_minimal(self):
        """Test adding a task with only required fields."""
        mock_db = Mock()
        mock_db.create_task.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Task",
            "priority": "medium",
            "status": "pending"
        }
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_add_task({"title": "Test Task"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "✅ Task created successfully!" in result[0].text
            assert "Test Task" in result[0].text
            mock_db.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_task_full(self):
        """Test adding a task with all fields."""
        mock_db = Mock()
        mock_db.create_task.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete Project",
            "description": "Finish the MCP todo project",
            "priority": "high",
            "status": "pending",
            "category": "work",
            "tags": ["urgent", "project"]
        }
        
        arguments = {
            "title": "Complete Project",
            "description": "Finish the MCP todo project",
            "priority": "high",
            "category": "work",
            "tags": ["urgent", "project"],
            "due_date": "2026-01-10T17:00:00"
        }
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_add_task(arguments)
            
            assert len(result) == 1
            assert "Complete Project" in result[0].text
            assert "high" in result[0].text
            
            # Verify database was called with correct data
            call_args = mock_db.create_task.call_args[0][0]
            assert call_args["title"] == "Complete Project"
            assert call_args["priority"] == "high"
            assert call_args["due_date"] == "2026-01-10T17:00:00"


class TestListTasks:
    """Tests for list_tasks tool."""
    
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self):
        """Test listing tasks when none exist."""
        mock_db = Mock()
        mock_db.list_tasks.return_value = []
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_list_tasks({})
            
            assert len(result) == 1
            assert "No tasks found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_results(self):
        """Test listing tasks with results."""
        mock_db = Mock()
        mock_db.list_tasks.return_value = [
            {
                "id": "123",
                "title": "Task 1",
                "status": "pending",
                "priority": "high"
            },
            {
                "id": "456",
                "title": "Task 2",
                "status": "completed",
                "priority": "low",
                "due_date": "2026-01-05"
            }
        ]
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_list_tasks({})
            
            assert len(result) == 1
            assert "Found 2 task(s)" in result[0].text
            assert "Task 1" in result[0].text
            assert "Task 2" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(self):
        """Test listing tasks with status and priority filters."""
        mock_db = Mock()
        mock_db.list_tasks.return_value = [
            {
                "id": "123",
                "title": "High Priority Task",
                "status": "pending",
                "priority": "high"
            }
        ]
        
        arguments = {
            "status": "pending",
            "priority": "high",
            "limit": 50
        }
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_list_tasks(arguments)
            
            mock_db.list_tasks.assert_called_once_with(
                status="pending",
                priority="high",
                limit=50
            )
            assert "High Priority Task" in result[0].text


class TestUpdateTask:
    """Tests for update_task tool."""
    
    @pytest.mark.asyncio
    async def test_update_task_single_field(self):
        """Test updating a single field."""
        mock_db = Mock()
        mock_db.update_task.return_value = {
            "id": "123",
            "title": "Updated Task",
            "status": "completed",
            "priority": "medium"
        }
        
        arguments = {
            "task_id": "123",
            "status": "completed"
        }
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_update_task(arguments)
            
            assert len(result) == 1
            assert "✅ Task updated successfully!" in result[0].text
            mock_db.update_task.assert_called_once_with("123", {"status": "completed"})
    
    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self):
        """Test updating multiple fields."""
        mock_db = Mock()
        mock_db.update_task.return_value = {
            "id": "123",
            "title": "New Title",
            "status": "in_progress",
            "priority": "high"
        }
        
        arguments = {
            "task_id": "123",
            "title": "New Title",
            "status": "in_progress",
            "priority": "high"
        }
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_update_task(arguments)
            
            call_args = mock_db.update_task.call_args[0][1]
            assert call_args["title"] == "New Title"
            assert call_args["status"] == "in_progress"
            assert call_args["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_update_task_no_updates(self):
        """Test update with no fields provided."""
        mock_db = Mock()
        
        arguments = {"task_id": "123"}
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_update_task(arguments)
            
            assert "No updates provided" in result[0].text
            mock_db.update_task.assert_not_called()


class TestDeleteTask:
    """Tests for delete_task tool."""
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Test successful task deletion."""
        mock_db = Mock()
        mock_db.delete_task.return_value = True
        
        arguments = {"task_id": "123"}
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            result = await handle_delete_task(arguments)
            
            assert len(result) == 1
            assert "✅ Task 123 deleted successfully!" in result[0].text
            mock_db.delete_task.assert_called_once_with("123")
    
    @pytest.mark.asyncio
    async def test_delete_task_error(self):
        """Test task deletion with error."""
        mock_db = Mock()
        mock_db.delete_task.side_effect = ValueError("Task not found")
        
        arguments = {"task_id": "nonexistent"}
        
        with patch("src.mcp_server.tools.crud.db", mock_db):
            with pytest.raises(ValueError, match="Task not found"):
                await handle_delete_task(arguments)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
