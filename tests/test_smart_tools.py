"""
Unit tests for AI-powered smart tools.

These tests mock the AI agent to test tool logic independently.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import TextContent

from src.mcp_server.tools.smart import (
    handle_smart_add,
    handle_search_tasks,
    handle_smart_update
)


class TestSmartAdd:
    """Tests for smart_add tool."""
    
    @pytest.mark.asyncio
    async def test_smart_add_success(self):
        """Test successful task creation from natural language."""
        mock_db = Mock()
        mock_agent = Mock()
        
        # Mock agent parsing
        mock_agent.parse_task_nl.return_value = {
            "title": "Buy groceries",
            "priority": "high",
            "category": "shopping",
            "due_date": "2026-01-03T17:00:00"
        }
        
        # Mock database creation
        mock_db.create_task.return_value = {
            "id": "123",
            "title": "Buy groceries",
            "priority": "high",
            "status": "pending",
            "category": "shopping",
            "due_date": "2026-01-03T17:00:00"
        }
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_smart_add({
                "natural_language": "Buy groceries tomorrow at 5pm, urgent"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "✅ Task created successfully!" in result[0].text
            assert "Buy groceries" in result[0].text
            mock_agent.parse_task_nl.assert_called_once()
            mock_db.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_smart_add_missing_parameter(self):
        """Test smart_add with missing natural_language parameter."""
        result = await handle_smart_add({})
        
        assert len(result) == 1
        assert "❌ Error" in result[0].text
        assert "natural_language parameter is required" in result[0].text


class TestSearchTasks:
    """Tests for search_tasks tool."""
    
    @pytest.mark.asyncio
    async def test_search_tasks_with_filters(self):
        """Test search with structured filters."""
        mock_db = Mock()
        mock_agent = Mock()
        
        # Mock agent returning filters
        mock_agent.search_tasks_nl.return_value = {"priority": "high"}
        
        # Mock database search
        mock_db.list_tasks.return_value = [
            {
                "id": "123",
                "title": "Urgent Task",
                "status": "pending",
                "priority": "high"
            }
        ]
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_search_tasks({
                "query": "Show me high priority tasks"
            })
            
            assert len(result) == 1
            assert "Found 1 task(s)" in result[0].text
            assert "Urgent Task" in result[0].text
            mock_agent.search_tasks_nl.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_tasks_text_search(self):
        """Test search with text query."""
        mock_db = Mock()
        mock_agent = Mock()
        
        # Mock agent returning text search
        mock_agent.search_tasks_nl.return_value = {"search_text": "groceries"}
        
        # Mock database text search
        mock_db.search_tasks.return_value = [
            {
                "id": "456",
                "title": "Buy groceries",
                "status": "pending",
                "priority": "medium"
            }
        ]
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_search_tasks({
                "query": "Find tasks about groceries"
            })
            
            assert len(result) == 1
            assert "Buy groceries" in result[0].text
            mock_db.search_tasks.assert_called_once_with("groceries")
    
    @pytest.mark.asyncio
    async def test_search_tasks_no_results(self):
        """Test search with no matching tasks."""
        mock_db = Mock()
        mock_agent = Mock()
        
        mock_agent.search_tasks_nl.return_value = {"status": "completed"}
        mock_db.list_tasks.return_value = []
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_search_tasks({"query": "Show completed tasks"})
            
            assert "No tasks found" in result[0].text


class TestSmartUpdate:
    """Tests for smart_update tool."""
    
    @pytest.mark.asyncio
    async def test_smart_update_success(self):
        """Test successful task update."""
        mock_db = Mock()
        mock_agent = Mock()
        
        # Mock existing tasks
        mock_db.list_tasks.return_value = [
            {"id": "123", "title": "Buy groceries", "status": "pending", "priority": "medium"}
        ]
        
        # Mock agent extraction
        mock_agent.extract_task_update.return_value = {
            "task_match": "groceries",
            "updates": {"status": "completed"}
        }
        
        # Mock fuzzy matching
        mock_agent.find_matching_task.return_value = "123"
        
        # Mock database update
        mock_db.update_task.return_value = {
            "id": "123",
            "title": "Buy groceries",
            "status": "completed",
            "priority": "medium"
        }
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_smart_update({
                "natural_language": "Mark the groceries task as done"
            })
            
            assert len(result) == 1
            assert "✅ Task updated successfully!" in result[0].text
            assert "completed" in result[0].text
    
    @pytest.mark.asyncio
    async def test_smart_update_multiple_matches(self):
        """Test update with multiple matching tasks (clarification needed)."""
        mock_db = Mock()
        mock_agent = Mock()
        
        # Mock multiple existing tasks
        mock_db.list_tasks.return_value = [
            {"id": "123", "title": "Buy groceries", "status": "pending", "priority": "medium"},
            {"id": "456", "title": "Put away groceries", "status": "pending", "priority": "low"}
        ]
        
        mock_agent.extract_task_update.return_value = {
            "task_match": "groceries",
            "updates": {"status": "completed"}
        }
        
        # Mock fuzzy matching returning None (multiple matches)
        mock_agent.find_matching_task.return_value = None
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_smart_update({
                "natural_language": "Mark groceries as done"
            })
            
            assert len(result) == 1
            assert "Found 2 tasks matching" in result[0].text
            assert "Buy groceries" in result[0].text
            assert "Put away groceries" in result[0].text
    
    @pytest.mark.asyncio
    async def test_smart_update_no_match(self):
        """Test update with no matching task."""
        mock_db = Mock()
        mock_agent = Mock()
        
        mock_db.list_tasks.return_value = [
            {"id": "123", "title": "Buy milk", "status": "pending", "priority": "medium"}
        ]
        
        mock_agent.extract_task_update.return_value = {
            "task_match": "groceries",
            "updates": {"status": "completed"}
        }
        
        mock_agent.find_matching_task.return_value = None
        
        with patch("src.mcp_server.tools.smart.db", mock_db), \
             patch("src.mcp_server.tools.smart.agent", mock_agent):
            
            result = await handle_smart_update({
                "natural_language": "Mark groceries as done"
            })
            
            assert "No task found matching" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
