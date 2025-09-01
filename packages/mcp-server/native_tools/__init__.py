"""
Native Tools Module
==================

This module provides the infrastructure for discovering, validating, and executing
native tools through a YAML-based registry system with AI-powered discovery.

Key Components:
- ToolRegistry: Manages tool registration and discovery
- ToolValidator: Validates tool availability and configuration
- ToolExecutor: Executes tools with parameter validation
- FileWatcher: Monitors tools.yaml for hot reload

The system allows LLMs to discover tools by intent ("I want to capture something")
and execute them through a unified interface.
"""

from .registry import ToolRegistry
from .validator import ToolValidator  
from .executor import ToolExecutor
from .watcher import FileWatcher

__all__ = [
    'ToolRegistry',
    'ToolValidator', 
    'ToolExecutor',
    'FileWatcher'
]
