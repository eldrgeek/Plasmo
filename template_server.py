#!/usr/bin/env python3
"""
Template MCP Server
==================

A modular template for creating new MCP (Model Context Protocol) servers.
This template provides a clean foundation with organized tool categories,
proper error handling, and flexible configuration options.

Features:
- Modular tool organization
- JSON-safe data handling
- Configurable transport modes (stdio/HTTP)
- Built-in health monitoring
- Extensible architecture

Usage:
    python template_server.py --stdio    # For Cursor IDE
    python template_server.py            # HTTP mode (development)
    python template_server.py --help     # Show all options
"""

import asyncio
import json
import time
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# MCP Framework
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Template MCP Server")

# Global configuration
SERVER_VERSION = "1.0.0"
SERVER_BUILD_TIME = datetime.now().isoformat()

# Global state
server_stats = {
    "start_time": time.time(),
    "requests_handled": 0,
    "last_activity": time.time()
}

def make_json_safe(obj):
    """Convert objects to JSON-serializable format"""
    if hasattr(obj, '__dict__'):
        return {k: make_json_safe(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)

def update_activity():
    """Update server activity timestamp"""
    server_stats["last_activity"] = time.time()
    server_stats["requests_handled"] += 1

# ================================
# SERVER MANAGEMENT TOOLS
# ================================

@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """
    Get comprehensive server information and status.
    
    Returns:
        Server details including version, uptime, and statistics
    """
    update_activity()
    
    uptime = time.time() - server_stats["start_time"]
    uptime_hours = uptime / 3600
    
    return {
        "server_name": "Template MCP Server",
        "version": SERVER_VERSION,
        "build_time": SERVER_BUILD_TIME,
        "status": "running",
        "uptime_seconds": round(uptime, 2),
        "uptime_hours": round(uptime_hours, 2),
        "requests_handled": server_stats["requests_handled"],
        "last_activity": datetime.fromtimestamp(server_stats["last_activity"]).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "available_tools": len(mcp.list_tools())
    }

@mcp.tool()
def health_check() -> Dict[str, Any]:
    """
    Perform a health check of the server.
    
    Returns:
        Health status and basic system information
    """
    update_activity()
    
    try:
        # Basic health checks
        current_time = time.time()
        memory_usage = None
        
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pass
        
        return {
            "status": "healthy",
            "timestamp": datetime.fromtimestamp(current_time).isoformat(),
            "uptime_seconds": current_time - server_stats["start_time"],
            "memory_usage_mb": memory_usage,
            "requests_handled": server_stats["requests_handled"],
            "last_error": None
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ================================
# FILE SYSTEM TOOLS
# ================================

@mcp.tool()
def read_file(filepath: str) -> Dict[str, Any]:
    """
    Read contents of a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        File contents and metadata
    """
    update_activity()
    
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {filepath}"}
        
        if not file_path.is_file():
            return {"success": False, "error": f"Path is not a file: {filepath}"}
        
        # Get file stats
        stat_info = file_path.stat()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "filepath": str(file_path),
            "content": content,
            "size_bytes": stat_info.st_size,
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "lines": len(content.split('\n'))
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def write_file(filepath: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Write operation result
    """
    update_activity()
    
    try:
        file_path = Path(filepath)
        
        # Create parent directories if requested
        if create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        
        # Write file content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Get file stats after writing
        stat_info = file_path.stat()
        
        return {
            "success": True,
            "filepath": str(file_path),
            "size_bytes": stat_info.st_size,
            "lines_written": len(content.split('\n')),
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*", include_hidden: bool = False) -> Dict[str, Any]:
    """
    List files in a directory.
    
    Args:
        directory: Directory to list files from
        pattern: Glob pattern to match files
        include_hidden: Whether to include hidden files
        
    Returns:
        List of files and directories
    """
    update_activity()
    
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        if not dir_path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory}"}
        
        files = []
        dirs = []
        
        for item in dir_path.glob(pattern):
            if not include_hidden and item.name.startswith('.'):
                continue
                
            item_info = {
                "name": item.name,
                "path": str(item),
                "size_bytes": item.stat().st_size if item.is_file() else None,
                "modified_time": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            }
            
            if item.is_file():
                files.append(item_info)
            elif item.is_dir():
                dirs.append(item_info)
        
        return {
            "success": True,
            "directory": str(dir_path),
            "pattern": pattern,
            "files": files,
            "directories": dirs,
            "total_files": len(files),
            "total_directories": len(dirs)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# UTILITY TOOLS
# ================================

@mcp.tool()
def run_system_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a system command safely.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        
    Returns:
        Command execution result
    """
    update_activity()
    
    try:
        import subprocess
        
        # Security: Basic command validation
        dangerous_commands = ['rm -rf', 'del /f', 'format', 'shutdown', 'reboot']
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            return {"success": False, "error": "Dangerous command blocked for security"}
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": True,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": "< 1s"  # Placeholder
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout} seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_environment_info() -> Dict[str, Any]:
    """
    Get information about the current environment.
    
    Returns:
        Environment details and system information
    """
    update_activity()
    
    try:
        import platform
        
        env_vars = {}
        for key, value in os.environ.items():
            # Filter sensitive environment variables
            if not any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'TOKEN', 'KEY']):
                env_vars[key] = value
        
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable
            },
            "working_directory": os.getcwd(),
            "environment_variables": env_vars,
            "path_separator": os.pathsep,
            "line_separator": repr(os.linesep)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# TEMPLATE EXTENSION PLACEHOLDER
# ================================

@mcp.tool()
def template_example_tool(message: str = "Hello from Template Server!") -> Dict[str, Any]:
    """
    Example template tool - replace this with your custom functionality.
    
    Args:
        message: Message to echo back
        
    Returns:
        Example response with template information
    """
    update_activity()
    
    return {
        "success": True,
        "message": message,
        "server_name": "Template MCP Server",
        "timestamp": datetime.now().isoformat(),
        "template_info": {
            "description": "This is a template tool - replace with your custom functionality",
            "suggestions": [
                "Add your domain-specific tools here",
                "Organize tools into logical categories", 
                "Follow the JSON-safe pattern for return values",
                "Include proper error handling",
                "Update server documentation"
            ]
        }
    }

def setup_logging(debug_mode: bool, stdio_mode: bool):
    """Setup appropriate logging based on mode"""
    if debug_mode:
        # Debug mode: log to file with detailed info
        logging.basicConfig(
            level=logging.DEBUG,
            filename='/tmp/template_server_debug.log',
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    elif stdio_mode:
        # STDIO mode: minimal/no console logging to avoid JSON-RPC interference
        logging.basicConfig(
            level=logging.CRITICAL,
            stream=sys.stderr,
            format='%(message)s'
        )
    else:
        # HTTP mode: normal logging
        logging.basicConfig(
            level=logging.INFO,
            stream=sys.stderr,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(
        description="Template MCP Server - A modular foundation for new MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --stdio                    # STDIO mode (for Cursor IDE)
  %(prog)s --http --port 8000         # HTTP mode on port 8000
  %(prog)s --stdio --debug            # STDIO with debug logging
        """
    )
    
    # Transport mode arguments
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--stdio", 
        action="store_true", 
        help="Use STDIO transport (default, suitable for Cursor IDE)"
    )
    transport_group.add_argument(
        "--http", 
        action="store_true", 
        help="Use HTTP transport instead of STDIO"
    )
    
    # HTTP mode options
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host to bind to in HTTP mode (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind to in HTTP mode (default: 8000)"
    )
    
    # Debug options
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging to /tmp/template_server_debug.log"
    )
    
    args = parser.parse_args()
    
    # Determine transport mode (default to STDIO)
    transport_mode = "stdio"
    if args.http:
        transport_mode = "http"
    
    # Setup logging based on mode
    setup_logging(args.debug, transport_mode == "stdio")
    
    if args.debug:
        logging.info(f"Starting Template MCP Server v{SERVER_VERSION}")
        logging.info(f"Transport: {transport_mode}")
        if transport_mode == "http":
            logging.info(f"HTTP server: {args.host}:{args.port}")
    
    # Run server
    try:
        if transport_mode == "stdio":
            mcp.run()
        else:
            mcp.run(transport="http", host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        if args.debug:
            logging.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 