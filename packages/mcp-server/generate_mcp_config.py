#!/usr/bin/env python3
"""
MCP Testing Configuration Generator
==================================

This script generates the correct configuration for Claude Desktop to use
the MCP Development Shim v2.0 (FastMCP Proxy Edition), eliminating the need 
to restart Claude Desktop during MCP server development.

Author: Claude AI Assistant
Version: 2.0.0 (FastMCP Edition)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

def get_claude_desktop_config_path() -> Path:
    """Get the Claude Desktop configuration file path for the current platform."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform.startswith("linux"):  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

def load_existing_config(config_path: Path) -> Dict[str, Any]:
    """Load existing Claude Desktop configuration."""
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not read existing config: {e}")
            return {}
    return {}

def create_shim_config(project_path: str) -> Dict[str, Any]:
    """Create the FastMCP proxy shim configuration for Claude Desktop."""
    shim_config = {
        "command": "python3",
        "args": [
            f"{project_path}/mcp_testing_shim.py",
            "--stdio"
        ],
        "cwd": project_path,
        "description": "FastMCP Development Proxy - Zero-downtime development"
    }
    
    return shim_config

def backup_config(config_path: Path) -> Path:
    """Create a backup of the existing configuration."""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        import shutil
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None

def generate_config(project_path: str = None, server_name: str = "mcp-development-shim") -> Dict[str, Any]:
    """Generate the complete Claude Desktop configuration."""
    
    if project_path is None:
        project_path = str(Path.cwd().absolute())
    
    config_path = get_claude_desktop_config_path()
    existing_config = load_existing_config(config_path)
    
    # Ensure mcpServers section exists
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Add or update the shim configuration
    shim_config = create_shim_config(project_path)
    existing_config["mcpServers"][server_name] = shim_config
    
    return existing_config, config_path

def save_config(config: Dict[str, Any], config_path: Path, create_backup: bool = True) -> bool:
    """Save the configuration to Claude Desktop config file."""
    try:
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if requested
        backup_path = None
        if create_backup:
            backup_path = backup_config(config_path)
        
        # Write new configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration saved to: {config_path}")
        if backup_path:
            print(f"📁 Backup created at: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def print_manual_instructions(config: Dict[str, Any], project_path: str):
    """Print manual configuration instructions."""
    print("\n📋 Manual Configuration Instructions:")
    print("=====================================")
    print("\n1. Open Claude Desktop")
    print("2. Go to Settings → Developer")
    print("3. Click 'Edit Config' or locate the configuration file:")
    print(f"   {get_claude_desktop_config_path()}")
    print("\n4. Add or merge this configuration:")
    print(json.dumps(config, indent=2))
    print("\n5. Save the file and restart Claude Desktop")
    print("\n6. Start your development workflow:")
    print(f"   cd {project_path}")
    print("   python3 mcp_server.py --stdio            # Start development server")
    print("   python3 mcp_testing_shim.py --stdio      # Start FastMCP proxy shim")
    print("\n📊 Benefits of FastMCP Proxy Shim v2.0:")
    print("   ✅ All development server tools automatically available")
    print("   ✅ Zero configuration - works out of the box")
    print("   ✅ Restart dev server without restarting Claude Desktop")
    print("   ✅ Built-in connection recovery and error handling")

def test_shim_setup(project_path: str) -> bool:
    """Test if the FastMCP proxy shim setup is correct."""
    shim_file = Path(project_path) / "mcp_testing_shim.py"
    dev_server_file = Path(project_path) / "mcp_server.py"
    
    issues = []
    
    if not shim_file.exists():
        issues.append(f"❌ FastMCP proxy shim not found: {shim_file}")
    
    if not dev_server_file.exists():
        issues.append(f"❌ Development server not found: {dev_server_file}")
    
    # Check if Python and dependencies are available
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-c", "import fastmcp"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("❌ FastMCP not installed (pip install fastmcp)")
    except Exception as e:
        issues.append(f"❌ Error checking FastMCP: {e}")
    
    if issues:
        print("\n⚠️  Setup Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 To install FastMCP: pip install fastmcp")
        return False
    
    print("\n✅ FastMCP proxy shim setup looks good!")
    return True

def main():
    """Main entry point for the configuration generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate FastMCP Development Proxy configuration")
    parser.add_argument("--project-path", "-p", 
                       help="Path to MCP project directory (default: current directory)")
    parser.add_argument("--server-name", "-n", default="mcp-development-shim",
                       help="Name for the MCP server in configuration")
    parser.add_argument("--manual", "-m", action="store_true",
                       help="Show manual configuration instructions only")
    parser.add_argument("--test", "-t", action="store_true",
                       help="Test the current setup without modifying configuration")
    parser.add_argument("--backup", "-b", action="store_true", default=True,
                       help="Create backup of existing configuration (default: true)")
    
    args = parser.parse_args()
    
    project_path = args.project_path or str(Path.cwd().absolute())
    
    print("🚀 FastMCP Development Proxy Configuration Generator v2.0")
    print("========================================================")
    print(f"📁 Project Path: {project_path}")
    print(f"🏷️  Server Name: {args.server_name}")
    print("🔧 FastMCP Proxy: Zero-downtime development with automatic tool discovery")
    
    # Test setup if requested
    if args.test:
        print("\n🧪 Testing FastMCP proxy setup...")
        test_shim_setup(project_path)
        return
    
    # Generate configuration
    config, config_path = generate_config(project_path, args.server_name)
    
    if args.manual:
        print_manual_instructions(config, project_path)
        return
    
    # Test setup before proceeding
    if not test_shim_setup(project_path):
        print("\n❌ Setup issues found. Please fix them before generating configuration.")
        print("💡 Run with --manual to see manual setup instructions.")
        return
    
    # Automatically save configuration
    print("\n💾 Saving Claude Desktop configuration...")
    if save_config(config, config_path, args.backup):
        print("\n🎉 Configuration complete!")
        print("\n📋 Next Steps:")
        print("1. Restart Claude Desktop to load the new configuration")
        print("2. Start your development server:")
        print(f"   cd {project_path}")
        print("   python3 mcp_server.py --stdio")
        print("3. Start the FastMCP proxy shim:")
        print("   python3 mcp_testing_shim.py --stdio")
        print("4. Claude Desktop will connect to the shim, which proxies to your dev server")
        print("\n✨ You can now restart your dev server anytime without breaking Claude Desktop!")
    else:
        print("\n❌ Failed to save configuration.")
        print("💡 Use --manual to see manual setup instructions.")

if __name__ == "__main__":
    main()
