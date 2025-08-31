# Agent Name Management Tool
# Add this as a new tool to your MCP server

# Global agent name override
_custom_agent_name = None

def set_custom_agent_name(name: str) -> None:
    """Set custom agent name to override directory-based naming."""
    global _custom_agent_name
    _custom_agent_name = name

def get_custom_agent_name() -> str:
    """Get agent name - custom name if set, otherwise current repo directory."""
    global _custom_agent_name
    if _custom_agent_name:
        return _custom_agent_name
    from pathlib import Path
    return Path.cwd().name

@mcp.tool()
def set_agent_name(agent_name: str) -> Dict[str, Any]:
    """
    Set a custom agent name for this MCP server instance.
    
    This allows multiple Claude instances running from the same directory
    to have distinct identities in the messaging system.
    
    Args:
        agent_name: Custom name for this agent (e.g., "ProductManager", "FrontendDev", "QAEngineer")
        
    Returns:
        Dict with success status and agent information
    """
    try:
        set_custom_agent_name(agent_name)
        
        # Re-register with new name
        from pathlib import Path
        from datetime import datetime
        import subprocess
        
        # Get repo information
        repo_path = str(Path.cwd().absolute())
        
        # Try to get GitHub remote URL
        github_url = None
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=5
            )
            if result.returncode == 0:
                github_url = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return {
            "success": True,
            "operation": "set_agent_name",
            "agent_name": agent_name,
            "previous_name": Path.cwd().name,
            "repo_path": repo_path,
            "github_url": github_url,
            "timestamp": datetime.now().isoformat(),
            "message": f"Agent name set to '{agent_name}'. Use messages(operation='register') to register with new name."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "operation": "set_agent_name",
            "timestamp": datetime.now().isoformat()
        }
