"""
Server state management for MCP server.

This module provides enhanced server state management with proper async cleanup
and resource tracking.
"""

import asyncio
import logging
import weakref
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)


class ServerState:
    """Enhanced server state management with proper async cleanup."""
    
    def __init__(self):
        self.active_tasks: weakref.WeakSet = weakref.WeakSet()
        self.chrome_instances: Dict[str, Any] = {}
        self.connection_lock: asyncio.Lock = asyncio.Lock()
        self.cleanup_registered: bool = False
        self.console_logs: list = []
        self.websocket_connections: Dict[str, Any] = {}
    
    async def add_task(self, task: asyncio.Task) -> None:
        """Add a task to be tracked for cleanup."""
        self.active_tasks.add(task)
    
    async def cleanup_all(self) -> None:
        """Clean up all active resources."""
        logger.info("Cleaning up server resources...")
        
        # Cancel all active tasks
        tasks_to_cancel = list(self.active_tasks)
        for task in tasks_to_cancel:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error during task cleanup: {e}")
        
        # Close WebSocket connections
        for ws in list(self.websocket_connections.values()):
            try:
                if hasattr(ws, 'close'):
                    await ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        logger.info(f"Cleaned up {len(tasks_to_cancel)} tasks and WebSocket connections")


# Global server state instance
server_state = ServerState()


async def run_background_task(coro, task_name: str = "unnamed"):
    """Run a coroutine as a background task with proper tracking."""
    try:
        task = asyncio.create_task(coro)
        task.set_name(task_name)
        await server_state.add_task(task)
        return task
    except Exception as e:
        logger.error(f"Error running background task {task_name}: {e}")
        raise


def get_server_state() -> ServerState:
    """Get the global server state instance."""
    return server_state