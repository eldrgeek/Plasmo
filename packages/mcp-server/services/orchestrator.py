"""
Service orchestration tools.

This module contains service management tools that were factored out from the main
MCP server to reduce complexity and provide specialized service orchestration functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

import sys
import os
from typing import Dict, Any, List

# Import service orchestrator
try:
    from service_orchestrator import get_orchestrator
    SERVICE_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    SERVICE_ORCHESTRATOR_AVAILABLE = False


def service_status(service_name: str = None) -> Dict[str, Any]:
    """
    Get status of one or all services managed by the orchestrator.
    
    Args:
        service_name: Specific service name, or None for all services
        
    Returns:
        Service status information including PID, health, logs, etc.
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        
        if service_name:
            return {
                "success": True,
                "service": orchestrator.get_service_status(service_name)
            }
        else:
            return {
                "success": True, 
                "services": orchestrator.list_all_services(),
                "summary": {
                    "total_services": len(orchestrator.services_config),
                    "running": sum(1 for s in orchestrator.services_status.values() if s.status == "running"),
                    "stopped": sum(1 for s in orchestrator.services_status.values() if s.status == "stopped"),
                    "failed": sum(1 for s in orchestrator.services_status.values() if s.status == "failed")
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Service status check failed: {str(e)}",
            "service_name": service_name
        }


def start_service(service_name: str, wait_for_health: bool = True) -> Dict[str, Any]:
    """
    Start a specific service.
    
    Args:
        service_name: Name of the service to start
        wait_for_health: Whether to wait for health check before returning
        
    Returns:
        Start operation result with PID and status
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available" 
            }
        
        orchestrator = get_orchestrator()
        result = orchestrator.start_service(service_name, wait_for_health)
        
        return {
            "success": result["success"],
            "operation": "start_service",
            "service_name": service_name,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start service: {str(e)}",
            "service_name": service_name,
            "wait_for_health": wait_for_health
        }


def stop_service(service_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Stop a specific service.
    
    Args:
        service_name: Name of the service to stop
        force: Whether to force kill the service
        
    Returns:
        Stop operation result
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        result = orchestrator.stop_service(service_name, force)
        
        return {
            "success": result["success"],
            "operation": "stop_service", 
            "service_name": service_name,
            "force": force,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stop service: {str(e)}",
            "service_name": service_name,
            "force": force
        }


def restart_service(service_name: str) -> Dict[str, Any]:
    """
    Restart a specific service.
    
    Args:
        service_name: Name of the service to restart
        
    Returns:
        Restart operation result
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        result = orchestrator.restart_service(service_name)
        
        return {
            "success": result["success"],
            "operation": "restart_service",
            "service_name": service_name,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to restart service: {str(e)}",
            "service_name": service_name
        }


def start_all_services(exclude: List[str] = None) -> Dict[str, Any]:
    """
    Start all services in dependency order.
    
    Args:
        exclude: List of service names to exclude from startup
        
    Returns:
        Bulk start operation result with individual service results
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        result = orchestrator.start_all_services(exclude or [])
        
        return {
            "success": result["success"],
            "operation": "start_all_services",
            "excluded": exclude or [],
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start all services: {str(e)}",
            "exclude": exclude
        }


def stop_all_services(force: bool = False) -> Dict[str, Any]:
    """
    Stop all running services.
    
    Args:
        force: Whether to force kill all services
        
    Returns:
        Bulk stop operation result
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        result = orchestrator.stop_all_services(force)
        
        return {
            "success": result["success"],
            "operation": "stop_all_services",
            "force": force,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stop all services: {str(e)}",
            "force": force
        }


def service_logs(service_name: str, lines: int = 50) -> Dict[str, Any]:
    """
    Get recent log entries for a service.
    
    Args:
        service_name: Name of the service
        lines: Number of recent log lines to retrieve
        
    Returns:
        Recent log entries and log file information
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        
        # Get service status which includes recent logs
        status = orchestrator.get_service_status(service_name)
        
        if "error" in status:
            return {"success": False, **status}
        
        # Try to read more lines from log file
        from pathlib import Path
        log_file = Path(status["log_file"])
        recent_logs = []
        
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    recent_logs = all_lines[-lines:] if len(all_lines) > lines else all_lines
            except Exception as e:
                recent_logs = status.get("recent_logs", [])
        
        return {
            "success": True,
            "operation": "service_logs",
            "service_name": service_name,
            "log_file": str(log_file),
            "lines_requested": lines,
            "lines_returned": len(recent_logs),
            "logs": recent_logs,
            "log_file_exists": log_file.exists()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get service logs: {str(e)}",
            "service_name": service_name,
            "lines": lines
        }


def service_health_check() -> Dict[str, Any]:
    """
    Perform health checks on all services and return comprehensive status.
    
    Returns:
        Health check results for all services
    """
    try:
        if not SERVICE_ORCHESTRATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Service Orchestrator not available"
            }
        
        orchestrator = get_orchestrator()
        
        # Get all service statuses
        all_services = orchestrator.list_all_services()
        
        health_summary = {
            "healthy": [],
            "unhealthy": [],
            "unknown": [],
            "not_running": []
        }
        
        for service_name, service_data in all_services.items():
            if service_data["status"] != "running":
                health_summary["not_running"].append(service_name)
            elif service_data["health_status"] == "healthy":
                health_summary["healthy"].append(service_name)
            elif service_data["health_status"] == "unhealthy":
                health_summary["unhealthy"].append(service_name)
            else:
                health_summary["unknown"].append(service_name)
        
        overall_health = "healthy"
        if health_summary["unhealthy"]:
            overall_health = "unhealthy" 
        elif health_summary["unknown"] or health_summary["not_running"]:
            overall_health = "degraded"
        
        return {
            "success": True,
            "operation": "service_health_check",
            "overall_health": overall_health,
            "summary": health_summary,
            "details": all_services,
            "recommendations": _get_health_recommendations(health_summary)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Service health check failed: {str(e)}"
        }


def _get_health_recommendations(health_summary: Dict[str, List[str]]) -> List[str]:
    """Generate health recommendations based on service status"""
    recommendations = []
    
    if health_summary["unhealthy"]:
        recommendations.append(f"🔴 Restart unhealthy services: {', '.join(health_summary['unhealthy'])}")
    
    if health_summary["not_running"]:
        recommendations.append(f"▶️ Start stopped services: {', '.join(health_summary['not_running'])}")
    
    if health_summary["unknown"]:
        recommendations.append(f"❓ Check services with unknown health: {', '.join(health_summary['unknown'])}")
    
    if not recommendations:
        recommendations.append("✅ All services are healthy!")
    
    return recommendations
