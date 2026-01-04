"""
Tools package for MCP Todo Server.
"""
from .crud import (
    handle_add_task,
    handle_list_tasks,
    handle_update_task,
    handle_delete_task
)
from .smart import (
    handle_smart_add,
    handle_search_tasks,
    handle_smart_update
)

__all__ = [
    "handle_add_task",
    "handle_list_tasks",
    "handle_update_task",
    "handle_delete_task",
    "handle_smart_add",
    "handle_search_tasks",
    "handle_smart_update"
]
