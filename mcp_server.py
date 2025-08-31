#!/usr/bin/env python3
"""
Cursor IDE + Playwright Server Integration
==========================================

A comprehensive MCP (Model Context Protocol) server that provides browser automation
tools for Cursor IDE using Playwright and Chrome Debug Protocol.

Features:
- Natural language browser automation
- Chrome Debug Protocol integration  
- Screenshot capture and comparison
- Form automation and testing
- Console log monitoring
- JavaScript execution in browser context
- File operations and project analysis

Usage:
    python mcp_server.py --stdio    # For Cursor IDE
    python mcp_server.py            # HTTP mode (development)
"""

import asyncio
import json
import time
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# MCP and web automation imports
from fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, Page
import aiohttp
import websockets

# Initialize FastMCP server
mcp = FastMCP("Cursor Playwright Assistant")

# Global configuration
SERVER_VERSION = "1.0.0"
SERVER_BUILD_TIME = datetime.now().isoformat()
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_HOST = "localhost"

# Global state
playwright_instance = None
browser_instance = None
chrome_instances = {}
console_logs = []
active_pages = {}

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

# ================================
# PLAYWRIGHT BROWSER TOOLS
# ================================

@mcp.tool()
async def launch_browser(headless: bool = False, browser_type: str = "chromium") -> Dict[str, Any]:
    """
    Launch a Playwright browser instance for automation.
    
    Args:
        headless: Whether to run browser in headless mode
        browser_type: Browser type (chromium, firefox, webkit)
        
    Returns:
        Browser launch status and details
    """
    global playwright_instance, browser_instance
    
    try:
        if playwright_instance is None:
            playwright_instance = await async_playwright().start()
        
        # Launch browser based on type
        if browser_type == "chromium":
            browser_instance = await playwright_instance.chromium.launch(
                headless=headless,
                args=[
                    '--remote-debugging-port=9222',
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
        elif browser_type == "firefox":
            browser_instance = await playwright_instance.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser_instance = await playwright_instance.webkit.launch(headless=headless)
        else:
            return {"success": False, "error": f"Unsupported browser type: {browser_type}"}
        
        # Create a new page
        page = await browser_instance.new_page()
        page_id = f"page_{int(time.time())}"
        active_pages[page_id] = page
        
        return {
            "success": True,
            "browser_type": browser_type,
            "headless": headless,
            "page_id": page_id,
            "debug_port": 9222 if browser_type == "chromium" else None,
            "status": "Browser launched successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def navigate_to_url(url: str, page_id: str = None, wait_until: str = "networkidle") -> Dict[str, Any]:
    """
    Navigate to a specific URL.
    
    Args:
        url: URL to navigate to
        page_id: Page identifier (uses first page if not specified)
        wait_until: When to consider navigation finished
        
    Returns:
        Navigation result and page information
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available. Launch browser first."}
        
        # Navigate to URL
        response = await page.goto(url, wait_until=wait_until, timeout=30000)
        
        # Get page information
        title = await page.title()
        current_url = page.url
        
        return {
            "success": True,
            "page_id": page_id,
            "url": current_url,
            "title": title,
            "status_code": response.status if response else None,
            "status": "Navigation completed"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def take_screenshot(page_id: str = None, full_page: bool = False, filename: str = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page.
    
    Args:
        page_id: Page identifier
        full_page: Whether to capture full page or just viewport
        filename: Optional filename to save screenshot
        
    Returns:
        Screenshot capture result
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Take screenshot
        screenshot_path = await page.screenshot(
            path=filename,
            full_page=full_page
        )
        
        return {
            "success": True,
            "page_id": page_id,
            "filename": filename,
            "full_page": full_page,
            "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
            "status": "Screenshot captured successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def click_element(selector: str, page_id: str = None, wait_timeout: int = 10000) -> Dict[str, Any]:
    """
    Click on an element identified by CSS selector.
    
    Args:
        selector: CSS selector for the element
        page_id: Page identifier
        wait_timeout: Time to wait for element (milliseconds)
        
    Returns:
        Click operation result
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Wait for element and click
        await page.wait_for_selector(selector, timeout=wait_timeout)
        await page.click(selector)
        
        return {
            "success": True,
            "page_id": page_id,
            "selector": selector,
            "status": "Element clicked successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def fill_form_field(selector: str, text: str, page_id: str = None) -> Dict[str, Any]:
    """
    Fill a form field with text.
    
    Args:
        selector: CSS selector for the form field
        text: Text to fill
        page_id: Page identifier
        
    Returns:
        Fill operation result
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Fill the field
        await page.fill(selector, text)
        
        return {
            "success": True,
            "page_id": page_id,
            "selector": selector,
            "text_length": len(text),
            "status": "Form field filled successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def execute_javascript(code: str, page_id: str = None) -> Dict[str, Any]:
    """
    Execute JavaScript code in the browser page.
    
    Args:
        code: JavaScript code to execute
        page_id: Page identifier
        
    Returns:
        JavaScript execution result
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Execute JavaScript
        result = await page.evaluate(code)
        
        return {
            "success": True,
            "page_id": page_id,
            "code": code,
            "result": make_json_safe(result),
            "status": "JavaScript executed successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_page_content(page_id: str = None, content_type: str = "text") -> Dict[str, Any]:
    """
    Get page content in various formats.
    
    Args:
        page_id: Page identifier
        content_type: Type of content (text, html, title, url)
        
    Returns:
        Page content information
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Get requested content
        if content_type == "text":
            content = await page.inner_text("body")
        elif content_type == "html":
            content = await page.content()
        elif content_type == "title":
            content = await page.title()
        elif content_type == "url":
            content = page.url
        else:
            return {"success": False, "error": f"Unsupported content type: {content_type}"}
        
        return {
            "success": True,
            "page_id": page_id,
            "content_type": content_type,
            "content": content,
            "content_length": len(str(content)),
            "status": "Content retrieved successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def wait_for_element(selector: str, page_id: str = None, timeout: int = 30000) -> Dict[str, Any]:
    """
    Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector for the element
        page_id: Page identifier
        timeout: Maximum wait time in milliseconds
        
    Returns:
        Wait operation result
    """
    try:
        # Get page
        if page_id and page_id in active_pages:
            page = active_pages[page_id]
        elif active_pages:
            page = list(active_pages.values())[0]
            page_id = list(active_pages.keys())[0]
        else:
            return {"success": False, "error": "No browser page available"}
        
        # Wait for element
        element = await page.wait_for_selector(selector, timeout=timeout)
        
        # Get element information
        is_visible = await element.is_visible()
        is_enabled = await element.is_enabled()
        
        return {
            "success": True,
            "page_id": page_id,
            "selector": selector,
            "is_visible": is_visible,
            "is_enabled": is_enabled,
            "status": "Element found and ready"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# FILE OPERATIONS TOOLS
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
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "filepath": filepath,
            "content": content,
            "size": len(content),
            "lines": len(content.splitlines()),
            "status": "File read successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
        
    Returns:
        Write operation result
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "filepath": filepath,
            "size": len(content),
            "lines": len(content.splitlines()),
            "status": "File written successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*") -> Dict[str, Any]:
    """
    List files in a directory with optional pattern matching.
    
    Args:
        directory: Directory to list files from
        pattern: Glob pattern for file matching
        
    Returns:
        List of files and directories
    """
    try:
        from pathlib import Path
        
        path = Path(directory)
        if pattern == "*":
            files = list(path.iterdir())
        else:
            files = list(path.glob(pattern))
        
        file_list = []
        for file_path in files:
            file_info = {
                "name": file_path.name,
                "path": str(file_path),
                "is_directory": file_path.is_dir(),
                "size": file_path.stat().st_size if file_path.is_file() else 0
            }
            file_list.append(file_info)
        
        return {
            "success": True,
            "directory": directory,
            "pattern": pattern,
            "files": file_list,
            "count": len(file_list),
            "status": "Directory listed successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# SERVER INFORMATION
# ================================

@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """Get information about this MCP server."""
    tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
    
    return {
        "name": "Cursor Playwright Assistant",
        "version": SERVER_VERSION,
        "build_time": SERVER_BUILD_TIME,
        "description": "MCP server providing browser automation tools for Cursor IDE",
        "tools_count": len(tools_list),
        "available_tools": tools_list,
        "playwright_support": True,
        "chrome_debug_support": True,
        "status": "ready"
    }

@mcp.tool()
async def close_browser() -> Dict[str, Any]:
    """Close the browser and clean up resources."""
    global browser_instance, playwright_instance, active_pages
    
    try:
        # Close all pages
        for page_id in list(active_pages.keys()):
            page = active_pages[page_id]
            await page.close()
            del active_pages[page_id]
        
        # Close browser
        if browser_instance:
            await browser_instance.close()
            browser_instance = None
        
        # Stop playwright
        if playwright_instance:
            await playwright_instance.stop()
            playwright_instance = None
        
        return {
            "success": True,
            "status": "Browser closed and resources cleaned up"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# MAIN SERVER EXECUTION
# ================================

# ================================
# COMMAND EXECUTION TOOLS
# ================================

@mcp.tool()
def execute_command(command: str, working_dir: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute shell command safely with output capture and security checks."""
    
    if working_dir is None:
        working_dir = os.getcwd()
    
    # Security check - forbidden commands
    forbidden_commands = {
        'rm -rf', 'format', 'fdisk', 'dd', 'mkfs',
        'shutdown', 'reboot', 'halt', 'poweroff',
        'passwd', 'useradd', 'userdel', 'usermod'
    }
    
    command_lower = command.lower()
    for forbidden in forbidden_commands:
        if forbidden in command_lower:
            return {
                "success": False,
                "error": f"Forbidden command detected: {forbidden}",
                "command": command,
                "timestamp": time.time()
            }
    
    try:
        print(f"🚀 Executing: {command}")
        print(f"📁 Working directory: {working_dir}")
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        response = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "command": command,
            "working_directory": working_dir,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "timestamp": time.time()
        }
        
        # Log the execution
        status = "✅" if result.returncode == 0 else "❌"
        print(f"{status} Command completed with return code: {result.returncode}")
        
        return response
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "timestamp": time.time()
        }

@mcp.tool()
def run_instant_capture() -> Dict[str, Any]:
    """Start the beautiful instant AI capture system."""
    
    try:
        script_path = "instant_capture_beautiful.py"
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Instant capture script not found: {script_path}",
                "suggestion": "Run the setup script first: ./setup_beautiful_capture.sh"
            }
        
        # Launch the capture system in background
        command = f"python3 {script_path}"
        
        # For background execution, we'll start it and return immediately
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        return {
            "success": True,
            "command": command,
            "script_path": script_path,
            "status": "🎯 Instant AI Capture system started in background!",
            "usage": "Press Cmd+Shift+T anywhere to capture tasks",
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start instant capture: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def install_package(package_name: str) -> Dict[str, Any]:
    """Install Python package using pip3."""
    
    try:
        result = execute_command(f"pip3 install {package_name}", timeout=120)
        return {
            **result,
            "package_name": package_name,
            "operation": "package_installation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to install {package_name}: {str(e)}",
            "timestamp": time.time()
        }

def main():
    parser = argparse.ArgumentParser(description="Cursor Playwright MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Use STDIO transport for Cursor IDE")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (HTTP mode)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (HTTP mode)")
    args = parser.parse_args()
    
    # Print server information
    tools_count = len(mcp.tools) if hasattr(mcp, 'tools') else 13
    
    print(f"""
🚀 Cursor Playwright Assistant Starting
========================================
Version: {SERVER_VERSION}
Transport: {'STDIO (Cursor IDE)' if args.stdio else f'HTTP ({args.host}:{args.port})'}
Tools available: {tools_count}

🎭 Playwright Browser Automation Tools:
- launch_browser: Start browser for automation
- navigate_to_url: Navigate to web pages
- take_screenshot: Capture page screenshots
- click_element: Click on page elements
- fill_form_field: Fill form inputs
- execute_javascript: Run JavaScript in browser
- get_page_content: Extract page content
- wait_for_element: Wait for elements to appear
- close_browser: Clean up browser resources

📁 File Operation Tools:
- read_file: Read file contents
- write_file: Write file contents
- list_files: List directory contents

ℹ️  Server Information:
- get_server_info: Get server status and capabilities

🔧 Usage Examples (in Cursor chat):
- "Launch a browser and navigate to github.com"
- "Take a screenshot of the current page"
- "Click on the login button"
- "Fill the email field with test@example.com"
- "Execute JavaScript: document.title"
- "Wait for the loading spinner to disappear"

🎯 Ready for browser automation with natural language commands!
""")
    
    # Start server with appropriate transport
    if args.stdio:
        print("🎯 Server ready - listening on STDIO for Cursor IDE")
        mcp.run(transport="stdio")
    else:
        print(f"🎯 Server starting on http://{args.host}:{args.port}")
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port
        )

if __name__ == "__main__":
    main() 