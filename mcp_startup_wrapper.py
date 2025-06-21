#!/usr/bin/env python3
"""
MCP Server Startup Wrapper
==========================
This wrapper ensures the MCP server starts with the correct working directory
and environment, regardless of how Claude Desktop launches it.
"""

import os
import sys
from pathlib import Path

def main():
    # Force working directory to project root
    script_path = Path(__file__).absolute()
    project_root = script_path.parent
    
    print(f"🚀 MCP Wrapper: Setting working directory to {project_root}", file=sys.stderr)
    os.chdir(project_root)
    
    # Ensure messages directory exists
    messages_dir = project_root / "messages"
    messages_dir.mkdir(exist_ok=True)
    (messages_dir / "agents").mkdir(exist_ok=True)
    (messages_dir / "messages").mkdir(exist_ok=True)
    (messages_dir / "deleted").mkdir(exist_ok=True)
    (messages_dir / "notifications").mkdir(exist_ok=True)
    
    # Create sequence file if it doesn't exist
    sequence_file = messages_dir / "sequence.txt"
    if not sequence_file.exists():
        sequence_file.write_text("0")
    
    print(f"✅ MCP Wrapper: Messages directory ready at {messages_dir}", file=sys.stderr)
    print(f"🎯 MCP Wrapper: Starting server from {os.getcwd()}", file=sys.stderr)
    
    # Import and run the actual server
    mcp_server_path = project_root / "packages" / "mcp-server" / "mcp_server.py"
    
    # Add the server directory to Python path
    sys.path.insert(0, str(mcp_server_path.parent))
    
    print(f"🔧 MCP Wrapper: Loading server from {mcp_server_path}", file=sys.stderr)
    print(f"📝 MCP Wrapper: Command line args: {sys.argv}", file=sys.stderr)
    
    # Execute the server with proper module loading
    import subprocess
    import sys
    
    # Replace current process with the actual server
    os.execv(sys.executable, [sys.executable, str(mcp_server_path)] + sys.argv[1:])

if __name__ == "__main__":
    main() 