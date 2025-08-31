#!/usr/bin/env python3
"""
Advanced File Manager Module
============================

This module provides advanced file management operations including:
- Copy, move, delete operations with safety checks
- Directory creation and removal
- Backup and restore functionality
- Batch operations with pattern matching
- Security validation and confirmation for destructive operations

All operations include comprehensive error handling and detailed metadata reporting.
"""

import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging

# Import dependencies from core modules
try:
    from ..core.security import SecurityError
    from ..core.error_handling import enhanced_handle_error
    from ..agents.agent_management import get_agent_name
except ImportError:
    # Fallback for direct script execution
    from core.security import SecurityError
    from core.error_handling import enhanced_handle_error
    from agents.agent_management import get_agent_name

logger = logging.getLogger(__name__)

def file_manager(
    operation: str,
    file_path: str = None,
    destination: str = None,
    pattern: str = None,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Advanced file management operations.
    
    Args:
        operation: File operation ('copy', 'move', 'delete', 'mkdir', 'rmdir', 'backup', 'restore')
        file_path: Source file/directory path
        destination: Destination path (for copy/move operations)
        pattern: Pattern for batch operations
        confirm: Confirmation for destructive operations
        
    Returns:
        Operation result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        if operation in ['copy', 'move'] and not destination:
            raise ValueError(f"{operation} operation requires destination parameter")
        
        if operation in ['delete', 'rmdir'] and not confirm:
            return {
                "success": False,
                "message": f"Confirmation required for {operation} operation. Set confirm=True to proceed.",
                "warning": "This action cannot be undone.",
                "operation": operation,
                "file_path": file_path
            }
        
        cwd = Path.cwd().resolve()
        
        if file_path:
            source_path = Path(file_path).resolve()
            # Security validation
            if not str(source_path).startswith(str(cwd)):
                error = SecurityError("Access denied: source path outside working directory")
                return enhanced_handle_error("file_manager", error, 
                                           {"operation": operation, "file_path": file_path}, agent_name)
        
        if destination:
            dest_path = Path(destination).resolve()
            # Security validation
            if not str(dest_path).startswith(str(cwd)):
                error = SecurityError("Access denied: destination path outside working directory")
                return enhanced_handle_error("file_manager", error, 
                                           {"operation": operation, "destination": destination}, agent_name)
        
        result = {
            "success": True,
            "operation": operation,
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if operation == "copy":
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
                result.update({
                    "source": str(source_path.relative_to(cwd)),
                    "destination": str(dest_path.relative_to(cwd)),
                    "size": source_path.stat().st_size,
                    "type": "file"
                })
            elif source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                result.update({
                    "source": str(source_path.relative_to(cwd)),
                    "destination": str(dest_path.relative_to(cwd)),
                    "type": "directory"
                })
            else:
                raise FileNotFoundError(f"Source not found: {source_path}")
                
        elif operation == "move":
            shutil.move(str(source_path), str(dest_path))
            result.update({
                "source": str(source_path.relative_to(cwd)),
                "destination": str(dest_path.relative_to(cwd)),
                "type": "file" if source_path.is_file() else "directory"
            })
            
        elif operation == "delete":
            if source_path.is_file():
                source_path.unlink()
                result.update({
                    "deleted": str(source_path.relative_to(cwd)),
                    "type": "file"
                })
            elif source_path.is_dir():
                shutil.rmtree(source_path)
                result.update({
                    "deleted": str(source_path.relative_to(cwd)),
                    "type": "directory"
                })
            else:
                raise FileNotFoundError(f"Path not found: {source_path}")
                
        elif operation == "mkdir":
            source_path.mkdir(parents=True, exist_ok=True)
            result.update({
                "created": str(source_path.relative_to(cwd)),
                "type": "directory"
            })
            
        elif operation == "backup":
            if not source_path.exists():
                raise FileNotFoundError(f"Source not found: {source_path}")
            
            backup_path = source_path.with_suffix(source_path.suffix + f'.backup.{int(time.time())}')
            
            if source_path.is_file():
                shutil.copy2(source_path, backup_path)
            else:
                shutil.copytree(source_path, backup_path)
            
            result.update({
                "source": str(source_path.relative_to(cwd)),
                "backup": str(backup_path.relative_to(cwd)),
                "type": "file" if source_path.is_file() else "directory"
            })
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        elapsed_time = time.time() - start_time
        result["execution_time"] = round(elapsed_time, 3)
        
        logger.info(f"Successfully completed {operation} operation in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "operation": operation,
            "file_path": file_path,
            "destination": destination,
            "pattern": pattern,
            "confirm": confirm
        }
        return enhanced_handle_error("file_manager", e, context, agent_name)