"""
Firebase automation tools module.

This module contains specialized Firebase project management and automation tools
that were factored out from the main MCP server to reduce complexity.
"""

from .project_management import (
    firebase_setup_new_project,
    firebase_configure_existing_project, 
    firebase_project_status,
    firebase_batch_operations
)

__all__ = [
    'firebase_setup_new_project',
    'firebase_configure_existing_project',
    'firebase_project_status', 
    'firebase_batch_operations'
]
