#!/usr/bin/env python3
"""
Round Table Service Manager
===========================

Modern Python replacement for shell scripts.
Uses MCP Server's service orchestration tools for centralized management.
"""

import sys
import time
import argparse
from pathlib import Path

def make_mcp_request(tool_name: str, **params):
    """Make a request to the MCP server"""
    import requests
    try:
        response = requests.post(
            f"http://localhost:8000/mcp/tools/{tool_name}",
            json=params,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def print_status(message: str, level: str = "info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[0;34m",     # Blue
        "success": "\033[0;32m",  # Green  
        "warning": "\033[1;33m",  # Yellow
        "error": "\033[0;31m",    # Red
        "reset": "\033[0m"        # Reset
    }
    
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    
    color = colors.get(level, colors["info"])
    icon = icons.get(level, "•")
    
    print(f"{color}{icon} {message}{colors['reset']}")

def wait_for_mcp_server(timeout: int = 30):
    """Wait for MCP server to be available"""
    print_status("Waiting for MCP server to be available...", "info")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print_status("MCP server is ready!", "success")
                return True
        except:
            pass
        time.sleep(2)
    
    print_status("MCP server is not responding", "error")
    return False

def cmd_status(args):
    """Show status of all services"""
    print_status("Checking service status...", "info")
    
    result = make_mcp_request("service_status")
    
    if not result.get("success"):
        print_status(f"Failed to get status: {result.get('error')}", "error")
        return 1
    
    services = result.get("services", {})
    summary = result.get("summary", {})
    
    print(f"\n🎯 Round Table Service Status")
    print("=" * 50)
    print(f"Total Services: {summary.get('total_services', 0)}")
    print(f"Running: {summary.get('running', 0)} | Stopped: {summary.get('stopped', 0)} | Failed: {summary.get('failed', 0)}")
    print()
    
    for name, service in services.items():
        status = service.get("status", "unknown")
        pid = service.get("pid")
        port = service.get("port")
        health = service.get("health_status", "unknown")
        
        # Status icon
        status_icon = {
            "running": "🟢",
            "stopped": "⚪", 
            "failed": "🔴",
            "starting": "🟡",
            "restarting": "🟠"
        }.get(status, "❓")
        
        # Health icon  
        health_icon = {
            "healthy": "💚",
            "unhealthy": "💔",
            "unknown": "❓"
        }.get(health, "❓")
        
        line = f"{status_icon} {name:<20} {status:<12}"
        if pid:
            line += f" PID:{pid:<8}"
        if port:
            line += f" Port:{port}"
        line += f" {health_icon}"
        
        print(line)
    
    return 0

def cmd_start(args):
    """Start services"""
    if args.service:
        print_status(f"Starting service: {args.service}", "info")
        result = make_mcp_request("start_service", service_name=args.service)
    else:
        print_status("Starting all services...", "info")
        exclude = args.exclude.split(",") if args.exclude else []
        result = make_mcp_request("start_all_services", exclude=exclude)
    
    if result.get("success"):
        print_status("Start operation completed successfully!", "success")
        if "started_services" in result:
            for service in result["started_services"]:
                print_status(f"Started: {service}", "success")
    else:
        print_status(f"Start failed: {result.get('error')}", "error")
        return 1
    
    return 0

def cmd_stop(args):
    """Stop services"""
    if args.service:
        print_status(f"Stopping service: {args.service}", "info")
        result = make_mcp_request("stop_service", service_name=args.service, force=args.force)
    else:
        print_status("Stopping all services...", "info")
        result = make_mcp_request("stop_all_services", force=args.force)
    
    if result.get("success"):
        print_status("Stop operation completed successfully!", "success")
        if "stopped_services" in result:
            for service in result["stopped_services"]:
                print_status(f"Stopped: {service}", "success")
    else:
        print_status(f"Stop failed: {result.get('error')}", "error")
        return 1
    
    return 0

def cmd_restart(args):
    """Restart a service"""
    if not args.service:
        print_status("Service name required for restart", "error")
        return 1
    
    print_status(f"Restarting service: {args.service}", "info")
    result = make_mcp_request("restart_service", service_name=args.service)
    
    if result.get("success"):
        print_status(f"Successfully restarted {args.service}!", "success")
    else:
        print_status(f"Restart failed: {result.get('error')}", "error")
        return 1
    
    return 0

def cmd_logs(args):
    """Show service logs"""
    if not args.service:
        print_status("Service name required for logs", "error")
        return 1
    
    print_status(f"Getting logs for: {args.service}", "info")
    result = make_mcp_request("service_logs", service_name=args.service, lines=args.lines)
    
    if result.get("success"):
        logs = result.get("logs", [])
        print(f"\n📋 Recent logs for {args.service} ({len(logs)} lines):")
        print("=" * 60)
        for line in logs:
            print(line.rstrip())
    else:
        print_status(f"Failed to get logs: {result.get('error')}", "error")
        return 1
    
    return 0

def cmd_health(args):
    """Check service health"""
    print_status("Performing health checks...", "info")
    result = make_mcp_request("service_health_check")
    
    if not result.get("success"):
        print_status(f"Health check failed: {result.get('error')}", "error")
        return 1
    
    overall = result.get("overall_health", "unknown")
    summary = result.get("summary", {})
    recommendations = result.get("recommendations", [])
    
    health_icon = {
        "healthy": "💚",
        "unhealthy": "💔", 
        "degraded": "⚠️"
    }.get(overall, "❓")
    
    print(f"\n{health_icon} Overall Health: {overall.upper()}")
    print("=" * 40)
    
    if summary.get("healthy"):
        print(f"✅ Healthy ({len(summary['healthy'])}): {', '.join(summary['healthy'])}")
    
    if summary.get("unhealthy"):
        print(f"❌ Unhealthy ({len(summary['unhealthy'])}): {', '.join(summary['unhealthy'])}")
    
    if summary.get("not_running"):
        print(f"⚪ Not Running ({len(summary['not_running'])}): {', '.join(summary['not_running'])}")
    
    if summary.get("unknown"):
        print(f"❓ Unknown ({len(summary['unknown'])}): {', '.join(summary['unknown'])}")
    
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
    
    return 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Round Table Service Manager - Centralized service orchestration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start services")
    start_parser.add_argument("--service", "-s", help="Specific service to start")
    start_parser.add_argument("--exclude", "-e", help="Comma-separated list of services to exclude")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop services") 
    stop_parser.add_argument("--service", "-s", help="Specific service to stop")
    stop_parser.add_argument("--force", "-f", action="store_true", help="Force stop services")
    
    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart a service")
    restart_parser.add_argument("service", help="Service to restart")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show service logs")
    logs_parser.add_argument("service", help="Service to show logs for")
    logs_parser.add_argument("--lines", "-n", type=int, default=50, help="Number of log lines")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Check if MCP server is running (except for starting it)
    if args.command != "start" or (args.command == "start" and args.service != "mcp_server"):
        if not wait_for_mcp_server():
            print_status("MCP server must be running first. Start it with: python start_service_manager.py start --service mcp_server", "error")
            return 1
    
    # Route to command handlers
    commands = {
        "status": cmd_status,
        "start": cmd_start, 
        "stop": cmd_stop,
        "restart": cmd_restart,
        "logs": cmd_logs,
        "health": cmd_health
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print_status(f"Unknown command: {args.command}", "error")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_status("\nOperation cancelled by user", "warning")
        sys.exit(130)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        sys.exit(1)
