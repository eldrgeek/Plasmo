# Round Table Service Orchestration
*Centralized Service Management through MCP Server*

## 🎯 Overview

We've transformed the Round Table project from shell-script based service management to a sophisticated, centralized orchestration system managed through the MCP server. This provides:

- **Unified Control**: All services managed through one system
- **Real-time Monitoring**: Health checks, auto-restart, logging
- **Development Workflow**: Auto-restart on file changes
- **Cross-platform**: Python-based, works on Mac/Linux/Windows
- **Integration**: Direct access through Claude Desktop MCP tools

---

## 🚀 Quick Start

### 1. Bootstrap the System
```bash
# Make scripts executable
chmod +x bootstrap_services.py service_manager.py

# Initialize the new service orchestration
python bootstrap_services.py
```

### 2. Manage Services
```bash
# Check status of all services
python service_manager.py status

# Start all services
python service_manager.py start

# Start specific service
python service_manager.py start --service socketio_server

# Stop all services
python service_manager.py stop

# Restart a service
python service_manager.py restart mcp_server

# View logs
python service_manager.py logs mcp_server --lines 100

# Health check
python service_manager.py health
```

### 3. Use from Claude Desktop
```python
# Check service status
service_status()

# Start a service
start_service(service_name="socketio_server")

# Health check all services
service_health_check()

# View recent logs
service_logs(service_name="mcp_server", lines=50)
```

---

## 🏗️ Architecture

### Service Orchestrator (`packages/mcp-server/service_orchestrator.py`)
- **ServiceConfig**: Configuration for each service (commands, ports, dependencies, health checks)
- **ServiceStatus**: Real-time status tracking (PID, health, restart counts, logs)
- **ServiceOrchestrator**: Main orchestration class with monitoring thread

### MCP Tools (integrated into `mcp_server.py`)
- `service_status()` - Get status of one or all services
- `start_service()` - Start specific service
- `stop_service()` - Stop specific service  
- `restart_service()` - Restart specific service
- `start_all_services()` - Start all services in dependency order
- `stop_all_services()` - Stop all services
- `service_logs()` - Get recent log entries
- `service_health_check()` - Comprehensive health check

### Service Manager (`service_manager.py`)
- Command-line interface for service management
- Colored output and status indicators
- Integrates with MCP server tools via HTTP

---

## 📋 Managed Services

The system manages these Round Table services:

| Service | Description | Port | Dependencies |
|---------|-------------|------|--------------|
| **mcp_server** | Main MCP Server with tool orchestration | 8000 | None |
| **socketio_server** | SocketIO Server (Node.js) | 3001 | None |
| **socketio_server_python** | Python SocketIO Server alternative | 3002 | None |
| **plasmo_dev** | Chrome Extension Development Server | Auto | None |
| **dashboard** | Development Dashboard | 8080 | mcp_server |
| **collaboration_dashboard** | CollaborAItion Dashboard | 8081 | mcp_server |
| **dt_server** | Desktop Automation Server | 8082 | None |
| **continuous_testing** | Continuous Test Runner | None | mcp_server |

---

## 🔄 Development Workflow

### Auto-Restart on File Changes
Services automatically restart when their watched files change:

- **MCP Server**: `packages/mcp-server/*.py`
- **SocketIO Server**: `socketio_server.js`, `cursor_ai_injector.py`
- **Plasmo Dev**: `packages/chrome-extension/**/*`
- **Testing**: `tests/*.py`, `packages/**/*.py`, `*.py`

### Health Monitoring
- Automatic health checks every 5 seconds
- HTTP endpoint checks for web services
- Process monitoring for all services
- Auto-restart on failure (max 5 attempts)

### Logging
- Centralized logging in `logs/` directory
- Each service gets its own log file
- Real-time log viewing through tools
- Log rotation and management

---

## 🛠️ Migration from Old System

### Replaced Scripts
- ✅ `start_all_services.sh` → `python service_manager.py start`
- ✅ `stop_all_services.sh` → `python service_manager.py stop` 
- ✅ `check_services.py` → `python service_manager.py status`
- ✅ Shell-based monitoring → Integrated Python monitoring

### Benefits of New System
- **Single Source of Truth**: All service config in one place
- **Dependency Management**: Services start in correct order
- **Error Recovery**: Automatic restart with backoff
- **Real-time Status**: Live monitoring and health checks
- **Developer Experience**: Consistent interface across platforms
- **Integration**: Direct access from Claude Desktop

---

## 🔧 Configuration

### Adding New Services
Edit `packages/mcp-server/service_orchestrator.py`:

```python
ServiceConfig(
    name="my_new_service",
    description="My New Service", 
    command=["python3", "my_service.py"],
    working_dir=str(self.project_root),
    port=8090,
    health_check_url="http://localhost:8090/health",
    auto_restart_on_file_change=True,
    watch_files=["my_service.py"],
    dependencies=["mcp_server"]
)
```

### Environment Variables
Services inherit environment variables and can have custom ones:

```python
environment={"NODE_ENV": "development", "DEBUG": "true"}
```

### Health Checks
Services can have HTTP health check endpoints:

```python
health_check_url="http://localhost:8080/health"
```

---

## 📊 Monitoring & Debugging

### Real-time Status
```bash
# Detailed status with health info
python service_manager.py status

# Continuous health monitoring
watch -n 5 "python service_manager.py health"
```

### Log Analysis
```bash
# Recent logs for specific service
python service_manager.py logs mcp_server

# Follow logs in real-time
tail -f logs/mcp_server.log

# All service logs
ls logs/
```

### Health Dashboard
```python
# From Claude Desktop
service_health_check()
```

---

## 🚨 Troubleshooting

### Service Won't Start
1. Check dependencies: `python service_manager.py status`
2. Check logs: `python service_manager.py logs <service_name>`
3. Verify config in `service_orchestrator.py`
4. Check port conflicts: `netstat -an | grep <port>`

### Service Keeps Restarting
1. Check error logs for the service
2. Verify all dependencies are running
3. Check resource usage (CPU/memory)
4. Review auto-restart configuration

### MCP Server Issues
1. Restart: `python service_manager.py restart mcp_server`
2. Bootstrap: `python bootstrap_services.py`
3. Check proxy connection in Claude Desktop

---

## 🎉 Next Steps

With centralized service orchestration now in place:

1. **Round Table Development**: All services can be managed consistently
2. **Multi-Agent Coordination**: Services are monitored and auto-restart
3. **Development Velocity**: No more manual service management
4. **Production Ready**: Health monitoring and automatic recovery

The Round Table platform now has enterprise-grade service orchestration! 🚀

---

*Generated by Claude Desktop with Round Table Service Orchestration*