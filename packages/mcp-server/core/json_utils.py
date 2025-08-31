"""
JSON utility functions for MCP server.

This module provides functions for converting objects to JSON-safe formats
with comprehensive Unicode handling.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def make_json_safe(obj: Any) -> Any:
    """Convert object to JSON-safe format with comprehensive Unicode handling."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        if isinstance(obj, str):
            try:
                # Handle Unicode encoding issues including surrogate pairs
                obj.encode('utf-8', 'strict')
                return obj
            except UnicodeEncodeError as e:
                logger.warning(f"Unicode encoding issue: {e}")
                # Handle surrogate pairs and invalid Unicode safely
                return obj.encode('utf-8', 'replace').decode('utf-8')
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    else:
        try:
            str_obj = str(obj)
            str_obj.encode('utf-8', 'strict')
            return str_obj
        except UnicodeEncodeError:
            return str(obj).encode('utf-8', 'replace').decode('utf-8')