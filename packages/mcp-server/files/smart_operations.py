#!/usr/bin/env python3
"""
Smart File Operations Module
============================

This module provides advanced file operations with enhanced error handling,
encoding detection, backup management, and comprehensive metadata tracking.

Functions:
- smart_write_file: Multi-mode writing (overwrite, append, prepend) with backups
- smart_read_file: Auto-encoding detection with metadata
- smart_edit_file: Precise line-based editing operations
- patch_file: Atomic multi-change operations

All operations include comprehensive error handling, security validation,
and detailed metadata reporting for AI assistants.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging

# Import dependencies from core modules
try:
    from ..core.security import validate_path_security, SecurityError
    from ..core.error_handling import enhanced_handle_error
    from ..agents.agent_management import get_agent_name
except ImportError:
    # Fallback for direct script execution
    from core.security import validate_path_security, SecurityError
    from core.error_handling import enhanced_handle_error
    from agents.agent_management import get_agent_name

logger = logging.getLogger(__name__)

# Global variable for current working directory (will be set by main server)
cwd = Path.cwd()

def set_working_directory(directory: Path):
    """Set the working directory for relative path operations."""
    global cwd
    cwd = directory

def smart_write_file(
    file_path: str, 
    content: str, 
    mode: str = "overwrite",
    backup: bool = True,
    create_dirs: bool = True,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Advanced file writing with multiple modes and comprehensive error handling.
    
    Args:
        file_path: Path to the file to write 
        content: Content to write
        mode: Write mode ('overwrite', 'append', 'insert_at_line', 'replace_section')
        backup: Create backup before writing
        create_dirs: Create parent directories if they don't exist
        encoding: File encoding (default: utf-8)
        
    Returns:
        Detailed write result with metadata
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        try:
            file_path = validate_path_security(file_path)
        except SecurityError as error:
            return enhanced_handle_error("smart_write_file", error, 
                                       {"file_path": str(file_path), "mode": mode}, agent_name)
        
        original_content = ""
        file_existed = file_path.exists()
        original_size = 0
        
        # Read original content if file exists
        if file_existed:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    original_content = f.read()
                    original_size = len(original_content.encode(encoding))
            except UnicodeDecodeError:
                # Try different encodings
                for alt_encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=alt_encoding) as f:
                            original_content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise UnicodeDecodeError(f"Could not decode file with any supported encoding")
        
        # Create backup if requested and file exists
        backup_path = None
        if backup and file_existed and original_content:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding=encoding) as f:
                f.write(original_content)
            logger.info(f"Created backup: {backup_path}")
        
        # Create parent directories if requested
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle different write modes
        final_content = content
        
        if mode == "append":
            final_content = original_content + content
        elif mode == "prepend":
            final_content = content + original_content
        elif mode == "overwrite":
            final_content = content
        else:
            # Default to overwrite for unknown modes
            logger.warning(f"Unknown write mode '{mode}', defaulting to overwrite")
            final_content = content
        
        # Write the file
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(final_content)
        
        new_size = len(final_content.encode(encoding))
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_write_file",
            "file_path": str(file_path.relative_to(cwd)),
            "mode": mode,
            "file_existed": file_existed,
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "original_size": original_size,
            "new_size": new_size,
            "size_change": new_size - original_size,
            "lines_written": len(final_content.split('\n')),
            "encoding": encoding,
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully wrote {new_size} bytes to {file_path} in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "mode": mode,
            "content_length": len(content),
            "backup": backup,
            "create_dirs": create_dirs,
            "encoding": encoding
        }
        return enhanced_handle_error("smart_write_file", e, context, agent_name)

def smart_read_file(
    file_path: str,
    encoding: str = "auto",
    max_size: int = 50 * 1024 * 1024,  # 50MB default
    return_metadata: bool = True
) -> Dict[str, Any]:
    """
    Advanced file reading with encoding detection and metadata.
    
    Args:
        file_path: Path to the file to read
        encoding: Encoding ('auto', 'utf-8', 'latin-1', etc.)
        max_size: Maximum file size to read (bytes)
        return_metadata: Include file metadata in response
        
    Returns:
        File content and metadata or error information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        try:
            file_path = validate_path_security(file_path)
        except SecurityError as error:
            return enhanced_handle_error("smart_read_file", error, 
                                       {"file_path": str(file_path)}, agent_name)
        
        if not file_path.exists():
            return enhanced_handle_error("smart_read_file", 
                                       FileNotFoundError(f"File not found: {file_path}"), 
                                       {"file_path": str(file_path)}, agent_name)
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            return enhanced_handle_error("smart_read_file", 
                                       ValueError(f"File size {file_size} exceeds maximum {max_size} bytes"), 
                                       {"file_path": str(file_path), "file_size": file_size}, agent_name)
        
        # Detect encoding if auto
        actual_encoding = encoding
        if encoding == "auto":
            # Try common encodings
            for test_encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=test_encoding) as f:
                        f.read(1024)  # Test read
                    actual_encoding = test_encoding
                    break
                except UnicodeDecodeError:
                    continue
            else:
                actual_encoding = 'utf-8'  # Fallback
        
        # Read file content
        with open(file_path, 'r', encoding=actual_encoding) as f:
            content = f.read()
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_read_file",
            "file_path": str(file_path.relative_to(cwd)),
            "content": content,
            "encoding": actual_encoding,
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        if return_metadata:
            stat = file_path.stat()
            result["metadata"] = {
                "size": file_size,
                "lines": len(content.split('\n')),
                "characters": len(content),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:]
            }
        
        logger.info(f"Successfully read {file_size} bytes from {file_path} in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "encoding": encoding,
            "max_size": max_size,
            "return_metadata": return_metadata
        }
        return enhanced_handle_error("smart_read_file", e, context, agent_name)

def smart_edit_file(
    file_path: str,
    operation: str,
    content: str = "",
    line_number: int = None,
    start_line: int = None,
    end_line: int = None,
    find_text: str = None,
    replace_text: str = None,
    backup: bool = True
) -> Dict[str, Any]:
    """
    Advanced file editing with line-specific operations.
    
    Args:
        file_path: Path to the file to edit
        operation: Edit operation ('insert_at_line', 'replace_line', 'replace_range', 'find_replace', 'delete_line', 'delete_range')
        content: Content to insert/replace (required for insert/replace operations)
        line_number: Line number for single-line operations (1-based)
        start_line: Start line for range operations (1-based)
        end_line: End line for range operations (1-based, inclusive)
        find_text: Text to find for find_replace operation
        replace_text: Replacement text for find_replace operation
        backup: Create backup before editing
        
    Returns:
        Edit result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        try:
            file_path = validate_path_security(file_path)
        except SecurityError as error:
            return enhanced_handle_error("smart_edit_file", error, 
                                       {"file_path": str(file_path), "operation": operation}, agent_name)
        
        if not file_path.exists():
            return enhanced_handle_error("smart_edit_file", 
                                       FileNotFoundError(f"File not found: {file_path}"), 
                                       {"file_path": str(file_path)}, agent_name)
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        original_content = ''.join(original_lines)
        total_lines = len(original_lines)
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Perform the edit operation
        modified_lines = original_lines.copy()
        lines_changed = 0
        
        if operation == "insert_at_line":
            if line_number is None:
                raise ValueError("line_number required for insert_at_line operation")
            if line_number < 1 or line_number > total_lines + 1:
                raise ValueError(f"line_number {line_number} out of range (1-{total_lines + 1})")
            
            insert_lines = content.split('\n')
            if not content.endswith('\n'):
                insert_lines = [line + '\n' for line in insert_lines[:-1]] + [insert_lines[-1]]
            else:
                insert_lines = [line + '\n' for line in insert_lines]
            
            modified_lines[line_number-1:line_number-1] = insert_lines
            lines_changed = len(insert_lines)
            
        elif operation == "replace_line":
            if line_number is None:
                raise ValueError("line_number required for replace_line operation")
            if line_number < 1 or line_number > total_lines:
                raise ValueError(f"line_number {line_number} out of range (1-{total_lines})")
            
            new_line = content + '\n' if not content.endswith('\n') else content
            modified_lines[line_number-1] = new_line
            lines_changed = 1
            
        elif operation == "replace_range":
            if start_line is None or end_line is None:
                raise ValueError("start_line and end_line required for replace_range operation")
            if start_line < 1 or end_line > total_lines or start_line > end_line:
                raise ValueError(f"Invalid range {start_line}-{end_line} for file with {total_lines} lines")
            
            replacement_lines = content.split('\n')
            if not content.endswith('\n'):
                replacement_lines = [line + '\n' for line in replacement_lines[:-1]] + [replacement_lines[-1]]
            else:
                replacement_lines = [line + '\n' for line in replacement_lines]
            
            modified_lines[start_line-1:end_line] = replacement_lines
            lines_changed = end_line - start_line + 1
            
        elif operation == "find_replace":
            if find_text is None or replace_text is None:
                raise ValueError("find_text and replace_text required for find_replace operation")
            
            new_content = original_content.replace(find_text, replace_text)
            modified_lines = new_content.split('\n')
            modified_lines = [line + '\n' for line in modified_lines[:-1]] + [modified_lines[-1]]
            if new_content.endswith('\n'):
                modified_lines.append('')
            lines_changed = original_content.count(find_text)
            
        elif operation == "delete_line":
            if line_number is None:
                raise ValueError("line_number required for delete_line operation")
            if line_number < 1 or line_number > total_lines:
                raise ValueError(f"line_number {line_number} out of range (1-{total_lines})")
            
            del modified_lines[line_number-1]
            lines_changed = 1
            
        elif operation == "delete_range":
            if start_line is None or end_line is None:
                raise ValueError("start_line and end_line required for delete_range operation")
            if start_line < 1 or end_line > total_lines or start_line > end_line:
                raise ValueError(f"Invalid range {start_line}-{end_line} for file with {total_lines} lines")
            
            del modified_lines[start_line-1:end_line]
            lines_changed = end_line - start_line + 1
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Write the modified content
        final_content = ''.join(modified_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_edit_file",
            "file_path": str(file_path.relative_to(cwd)),
            "edit_operation": operation,
            "original_lines": total_lines,
            "final_lines": len(modified_lines),
            "lines_changed": lines_changed,
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully edited {file_path} ({operation}) in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "operation": operation,
            "line_number": line_number,
            "start_line": start_line,
            "end_line": end_line,
            "content_length": len(content) if content else 0
        }
        return enhanced_handle_error("smart_edit_file", e, context, agent_name)

def patch_file(
    file_path: str,
    patches: List[Dict[str, Any]],
    backup: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Apply multiple patches to a file in a single operation.
    
    Args:
        file_path: Path to the file to patch
        patches: List of patch operations, each containing:
                 - operation: 'insert', 'replace', 'delete', 'find_replace'
                 - line_number: Line number (for insert/replace/delete)
                 - content: Content to insert/replace (for insert/replace)
                 - find_text: Text to find (for find_replace)
                 - replace_text: Replacement text (for find_replace)
        backup: Create backup before patching
        validate: Validate patch operations before applying
        
    Returns:
        Patch result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        try:
            file_path = validate_path_security(file_path)
        except SecurityError as error:
            return enhanced_handle_error("patch_file", error, 
                                       {"file_path": str(file_path), "patches": len(patches)}, agent_name)
        
        if not file_path.exists():
            return enhanced_handle_error("patch_file", 
                                       FileNotFoundError(f"File not found: {file_path}"), 
                                       {"file_path": str(file_path)}, agent_name)
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Validate patches if requested
        if validate:
            for i, patch in enumerate(patches):
                if 'operation' not in patch:
                    raise ValueError(f"Patch {i}: missing 'operation' field")
                
                op = patch['operation']
                if op in ['insert', 'replace', 'delete'] and 'line_number' not in patch:
                    raise ValueError(f"Patch {i}: 'line_number' required for {op} operation")
                
                if op in ['insert', 'replace'] and 'content' not in patch:
                    raise ValueError(f"Patch {i}: 'content' required for {op} operation")
                
                if op == 'find_replace' and ('find_text' not in patch or 'replace_text' not in patch):
                    raise ValueError(f"Patch {i}: 'find_text' and 'replace_text' required for find_replace operation")
        
        # Apply patches sequentially
        current_content = original_content
        patches_applied = 0
        
        for patch in patches:
            operation = patch['operation']
            
            if operation == 'find_replace':
                find_text = patch['find_text']
                replace_text = patch['replace_text']
                if find_text in current_content:
                    current_content = current_content.replace(find_text, replace_text)
                    patches_applied += 1
            else:
                # For line-based operations, we need to work with lines
                lines = current_content.split('\n')
                line_number = patch['line_number']
                
                if operation == 'insert':
                    content = patch['content']
                    if 1 <= line_number <= len(lines) + 1:
                        lines.insert(line_number - 1, content)
                        patches_applied += 1
                
                elif operation == 'replace':
                    content = patch['content']
                    if 1 <= line_number <= len(lines):
                        lines[line_number - 1] = content
                        patches_applied += 1
                
                elif operation == 'delete':
                    if 1 <= line_number <= len(lines):
                        del lines[line_number - 1]
                        patches_applied += 1
                
                current_content = '\n'.join(lines)
        
        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(current_content)
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "patch_file",
            "file_path": str(file_path.relative_to(cwd)),
            "patches_total": len(patches),
            "patches_applied": patches_applied,
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "original_size": len(original_content),
            "final_size": len(current_content),
            "size_change": len(current_content) - len(original_content),
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully applied {patches_applied}/{len(patches)} patches to {file_path} in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "patches_count": len(patches),
            "backup": backup,
            "validate": validate
        }
        return enhanced_handle_error("patch_file", e, context, agent_name)