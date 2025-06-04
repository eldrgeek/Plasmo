#!/usr/bin/env python3
"""
FastMCP HTTP Server for Cursor Integration
==========================================

This is a Model Context Protocol (MCP) server using fastMCP with HTTP transport.
It provides tools that can be used by AI assistants in Cursor IDE.

Setup Instructions:
1. Install dependencies: pip install fastmcp uvicorn
2. Run server: python mcp_server.py
3. Add to Cursor settings (see bottom of file for config)
4. Restart Cursor

Features:
- File operations (read, write, list)
- Code analysis tools
- Project structure analysis
- Git operations
- Database utilities
"""

import os
import json
import subprocess
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Cursor Development Assistant")

# Configuration
SERVER_PORT = 8000
SERVER_HOST = "127.0.0.1"

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success or error message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    List files in a directory.
    
    Args:
        directory: Directory path to list files from
        pattern: File pattern to match (e.g., "*.py", "*.js")
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    try:
        path = Path(directory)
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        return [f"Error listing files: {str(e)}"]

@mcp.tool()
def get_project_structure(directory: str = ".", max_depth: int = 3) -> Dict[str, Any]:
    """
    Get the structure of a project directory.
    
    Args:
        directory: Root directory to analyze
        max_depth: Maximum depth to traverse
        
    Returns:
        Dictionary representing the project structure
    """
    def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        if current_depth >= max_depth:
            return {}
        
        result = {}
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    result[item.name + "/"] = build_tree(item, current_depth + 1)
                else:
                    result[item.name] = {
                        "size": item.stat().st_size,
                        "type": "file"
                    }
        except PermissionError:
            result["<permission_denied>"] = {}
        
        return result
    
    try:
        return build_tree(Path(directory))
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_code(file_path: str) -> Dict[str, Any]:
    """
    Analyze a code file for basic metrics.
    
    Args:
        file_path: Path to the code file
        
    Returns:
        Dictionary with code analysis results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        analysis = {
            "file_path": file_path,
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0
        }
        
        # Basic analysis based on file extension
        ext = Path(file_path).suffix.lower()
        
        for line in lines:
            stripped = line.strip()
            
            if ext == '.py':
                if stripped.startswith('#'):
                    analysis["comment_lines"] += 1
                elif stripped.startswith('def '):
                    analysis["function_count"] += 1
                elif stripped.startswith('class '):
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'from ')):
                    analysis["import_count"] += 1
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                if stripped.startswith('//') or stripped.startswith('/*'):
                    analysis["comment_lines"] += 1
                elif 'function ' in stripped or '=>' in stripped:
                    analysis["function_count"] += 1
                elif 'class ' in stripped:
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'const ', 'require(')):
                    analysis["import_count"] += 1
        
        return analysis
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def run_git_command(command: str, directory: str = ".") -> str:
    """
    Run a git command and return the output.
    
    Args:
        command: Git command to run (without 'git' prefix)
        directory: Directory to run the command in
        
    Returns:
        Command output or error message
    """
    try:
        # Security: only allow safe git commands
        safe_commands = [
            'status', 'log', 'branch', 'diff', 'show',
            'ls-files', 'rev-parse', 'config --list'
        ]
        
        if not any(command.startswith(safe_cmd) for safe_cmd in safe_commands):
            return "Error: Only read-only git commands are allowed"
        
        result = subprocess.run(
            ['git'] + command.split(),
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Git error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error running git command: {str(e)}"

@mcp.tool()
def search_in_files(pattern: str, directory: str = ".", file_pattern: str = "*", case_sensitive: bool = False) -> List[Dict[str, Any]]:
    """
    Search for a pattern in files.
    
    Args:
        pattern: Text pattern to search for
        directory: Directory to search in
        file_pattern: File pattern to match (e.g., "*.py")
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        List of matches with file, line number, and content
    """
    try:
        matches = []
        path = Path(directory)
        
        for file_path in path.rglob(file_pattern):
            if not file_path.is_file():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        search_line = line if case_sensitive else line.lower()
                        search_pattern = pattern if case_sensitive else pattern.lower()
                        
                        if search_pattern in search_line:
                            matches.append({
                                "file": str(file_path),
                                "line_number": line_num,
                                "content": line.strip(),
                                "match": pattern
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return matches
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_sqlite_db(db_path: str, schema_sql: str) -> str:
    """
    Create a SQLite database with given schema.
    
    Args:
        db_path: Path for the database file
        schema_sql: SQL commands to create the schema
        
    Returns:
        Success or error message
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(schema_sql)
        
        conn.commit()
        conn.close()
        
        return f"Successfully created database at {db_path}"
    except Exception as e:
        return f"Error creating database: {str(e)}"

@mcp.tool()
def query_sqlite_db(db_path: str, query: str) -> List[Dict[str, Any]]:
    """
    Query a SQLite database.
    
    Args:
        db_path: Path to the database file
        query: SQL query to execute
        
    Returns:
        Query results as list of dictionaries
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """
    Get system information useful for development.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": dict(os.environ),
        "path_separator": os.pathsep,
        "file_separator": os.sep
    }

# Add server info endpoint
@mcp.tool()
def server_info() -> Dict[str, str]:
    """Get information about this MCP server."""
    # Get tools by calling the list_tools method
    tools_list = []
    try:
        # Get all tool names from the server
        tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
    except:
        tools_list = []
    
    return {
        "name": "Cursor Development Assistant",
        "version": "1.0.0",
        "description": "MCP server providing development tools for Cursor IDE",
        "transport": "HTTP",
        "tools_count": str(len(tools_list)),
        "available_tools": tools_list
    }

if __name__ == "__main__":
    # Get tools count for display
    tools_count = 0
    tools_list = []
    try:
        tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
        tools_count = len(tools_list)
    except:
        # Fallback - count the decorated functions
        tools_count = 11  # Hardcoded count of tools we defined
        tools_list = [
            "read_file", "write_file", "list_files", "get_project_structure",
            "analyze_code", "run_git_command", "search_in_files", 
            "create_sqlite_db", "query_sqlite_db", "get_system_info", "server_info"
        ]
    
    print(f"""
🚀 FastMCP Server Starting
========================
Server: http://{SERVER_HOST}:{SERVER_PORT}
Transport: HTTP
Tools available: {tools_count}

To integrate with Cursor:
1. Open Cursor settings (Cmd/Ctrl + ,)
2. Search for "mcp" or "Model Context Protocol"
3. Add this configuration:

{{
  "mcpServers": {{
    "cursor-dev-assistant": {{
      "url": "http://{SERVER_HOST}:{SERVER_PORT}"
    }}
  }}
}}

4. Restart Cursor
5. The tools will be available in AI conversations

Available Tools:
""")
    
    for tool_name in tools_list:
        print(f"  • {tool_name}")
    
    print("\n" + "="*50)
    
    # Start the server using FastMCP 2.x API
    mcp.run(
        transport="streamable-http",
        host=SERVER_HOST, 
        port=SERVER_PORT
    )

"""
CURSOR INTEGRATION INSTRUCTIONS:
===============================

1. Save this file as 'mcp_server.py'

2. Install dependencies:
   pip install fastmcp uvicorn

3. Run the server:
   python mcp_server.py

4. Configure Cursor:
   - Open Cursor settings (Cmd/Ctrl + ,)
   - Search for "mcp" 
   - Add this to your settings.json:

{
  "mcpServers": {
    "cursor-dev-assistant": {
      "url": "http://127.0.0.1:8000"
    }
  }
}

5. Restart Cursor

6. Test by asking the AI: "What tools are available from the MCP server?"

AVAILABLE TOOLS:
- read_file: Read file contents
- write_file: Write to files
- list_files: List directory contents
- get_project_structure: Analyze project layout
- analyze_code: Get code metrics
- run_git_command: Safe git operations
- search_in_files: Text search across files
- create_sqlite_db: Create databases
- query_sqlite_db: Query databases
- get_system_info: System information
- server_info: MCP server details

EXAMPLE PROMPTS:
- "Read the package.json file in my project"
- "Show me the project structure"
- "Search for 'TODO' comments in Python files"
- "What's the git status of this repository?"
- "Analyze the code in src/main.py"
""" 