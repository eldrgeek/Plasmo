"""
Automation and orchestration tools module.

This module contains automation tools that were factored out from the main
MCP server to reduce complexity and provide specialized automation functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

from .orchestration import (
    send_orchestration_command
)

from .native_automation import (
    inject_prompt_native,
    focus_and_type_native
)

__all__ = [
    'send_orchestration_command',
    'inject_prompt_native',
    'focus_and_type_native'
]
