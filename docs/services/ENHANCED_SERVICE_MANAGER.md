# Enhanced Service Manager with File Watching & Validation

The enhanced service manager provides intelligent file watching and validation capabilities to ensure services are restarted safely when code changes.

## 🎯 Key Features

### ✨ Smart File Watching
- **Pattern-based watching**: Monitor specific files and patterns
- **Directory monitoring**: Watch entire directories with filtering
- **Debounced restarts**: Prevent rapid restarts from multiple file changes
- **Ignore patterns**: Exclude logs, caches, and build artifacts

### 🧪 Pre-validation
- **Configuration validation**: Check syntax before restarting
- **Alternate port testing**: Test services on validation ports
- **Build verification**: Run custom validation commands
- **Rollback prevention**: Don't restart if validation fails

### 🔄 Intelligent Restarts
- **Graceful shutdown**: Clean stop before restart
- **Health monitoring**: Wait for services to be ready
- **Restart delays**: Configurable delays between operations
- **Async operations**: Non-blocking service management

## 🚀 Quick Start

### Install Dependencies
```bash
# Install optional dependencies for full functionality
python service_manager.py install-deps
```

### Basic Usage
```bash
# Start all services with file watching enabled
python service_manager.py start-all

# Check status with file watching indicators
python service_manager.py status

# View file watching details
python service_manager.py watch-status
```

### Manual File Watching Control
```bash
# Enable file watching for a specific service
python service_manager.py enable-watch mcp

# Disable file watching
python service_manager.py disable-watch mcp

# Test validation without restarting
python service_manager.py validate mcp

# Restart with full validation
python service_manager.py restart-validated mcp
```

## 📁 Configuration

### Service Configuration Structure

Each service supports these file watching options:

```python
ServiceConfig(
    name="mcp",
    # ... basic config ...
    
    # File watching configuration
    watch_patterns=["mcp_server.py", "*.py"],           # Files to watch
    watch_dirs=["packages/mcp-server"],                 # Directories to monitor
    ignore_patterns=["*.log", "__pycache__/*"],         # Files to ignore
    validation_command=["python", "-m", "py_compile"],  # Pre-validation command
    validation_port=8001,                               # Test port
    restart_delay=4.0,                                  # Delay before restart
    debounce_delay=2.0                                  # Debounce file changes
)
```

### Current Service Configurations

#### MCP Server
- **Patterns**: `mcp_server.py`, `requirements.txt`, `*.py`
- **Directory**: `packages/mcp-server`
- **Validation**: Python syntax check + test on port 8001
- **Delays**: 4s restart, 2s debounce

#### Socket.IO Server (Python)
- **Patterns**: `socketio_server_python.py`, `cursor_ai_injector.py`
- **Directory**: `packages/socketio-server`  
- **Validation**: Python syntax check + test on port 3002
- **Delays**: 3s restart, 2s debounce

#### Socket.IO Server (JavaScript)
- **Patterns**: `socketio_server.js`, `package.json`
- **Directory**: `packages/socketio-server`
- **Validation**: Node.js syntax check + test on port 3002
- **Delays**: 2s restart, 1s debounce

#### Plasmo Dev Server
- **Patterns**: `package.json`, `tsconfig.json`, `plasmo.config.ts`
- **Directories**: `contents`, `popup.tsx`, `background.ts`
- **Validation**: TypeScript type checking
- **Delays**: 5s restart, 3s debounce

#### Dashboard Services
- **Patterns**: `dashboard_*.py`, `requirements.txt`
- **Directory**: `packages/dashboard-framework`
- **Validation**: Python syntax check + alternate ports
- **Delays**: 3s restart, 2s debounce

#### Continuous Tests
- **Patterns**: `continuous_test_runner.py`, `test_*.py`
- **Directory**: `tests`
- **Validation**: Python syntax check + test on port 8083
- **Delays**: 3s restart, 2s debounce

## 🔍 Status Indicators

### Service Status Display
```
✅ MCP SERVER: (python) 👁️ 🧪 - Port 8000 - PID 12345
   👁️  Watching: mcp_server.py, requirements.txt, *.py

❌ SOCKETIO: (python) ⚫ 🧪 - Port 3001
```

**Icons Meaning**:
- `✅/❌` Service running/stopped
- `👁️/⚫` File watching active/inactive  
- `🧪/⚫` Validation configured/not configured

### File Watching Status
```
👁️ MCP: WATCHING 🧪
   🎯 Patterns: mcp_server.py, requirements.txt, *.py
   📁 Directories: packages/mcp-server
   🧪 Validation: python -m py_compile packages/mcp-server/mcp_server.py

⚫ CHROME_DEBUG: NOT CONFIGURED
```

## 🛠️ Validation Process

When a file changes, the service manager follows this validation workflow:

### 1. Configuration Validation
```python
# Example: Python syntax check
python -m py_compile mcp_server.py
```

### 2. Alternate Port Testing
- Start service on validation port (e.g., 8001)
- Test health endpoint
- Clean up test instance

### 3. Service Restart
- Stop current service gracefully
- Wait for restart delay
- Start service with health monitoring
- Resume file watching

### 4. Rollback Prevention
If validation fails:
- Current service keeps running
- Error logged with details
- No restart attempted
- File watching continues

## 🔧 Advanced Usage

### Custom Validation Commands

Add custom validation to service configs:

```python
# Syntax validation
validation_command=["python", "-m", "py_compile", "service.py"]

# Linting
validation_command=["pylint", "--errors-only", "service.py"]

# Type checking
validation_command=["mypy", "service.py"]

# Custom tests
validation_command=["python", "-m", "pytest", "test_service.py", "-x"]
```

### Multiple Watch Patterns

```python
watch_patterns=[
    "*.py",           # All Python files
    "config.yaml",    # Specific config file
    "requirements.*", # Requirements files
    "templates/*"     # Template directory
]
```

### Complex Ignore Patterns

```python
ignore_patterns=[
    "*.log",              # Log files
    "*.pyc",              # Compiled Python
    "__pycache__/*",      # Python cache
    "node_modules/*",     # Node dependencies
    "build/*",            # Build artifacts
    "dist/*",             # Distribution files
    ".git/*",             # Git files
    "chrome-debug-profile/*"  # Chrome profile
]
```

## 🚨 Error Handling

### Common Scenarios

#### Validation Timeout
```
⏰ Validation timeout for mcp
```
- Validation command took >30 seconds
- Service not restarted
- Check validation command complexity

#### Alternate Port Unavailable
```
❌ Validation port test failed for mcp
```
- Validation port already in use
- Network connectivity issues
- Service configuration problems

#### File Watching Unavailable
```
⚠️  Watchdog not available. Install with: pip install watchdog
```
- Missing `watchdog` dependency
- Run: `python service_manager.py install-deps`

## 📊 Performance Considerations

### Debouncing
- **Purpose**: Prevent restart storms from rapid file changes
- **Configuration**: `debounce_delay` in service config
- **Recommendation**: 1-3 seconds depending on service complexity

### Restart Delays
- **Purpose**: Allow proper cleanup between stop/start
- **Configuration**: `restart_delay` in service config
- **Recommendation**: 2-5 seconds depending on service startup time

### Validation Efficiency
- **Syntax checks**: Fast (0.1-0.5s)
- **Type checking**: Medium (1-3s)
- **Full tests**: Slow (5-30s)
- **Recommendation**: Use syntax checks for rapid feedback

## 🔗 Integration Examples

### VS Code Integration
Add to `.vscode/tasks.json`:

```json
{
    "label": "Restart Service with Validation",
    "type": "shell",
    "command": "python",
    "args": ["service_manager.py", "restart-validated", "${input:serviceName}"],
    "group": "build"
}
```

### Git Hooks
Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate all services before commit
python service_manager.py validate mcp
python service_manager.py validate socketio
```

### CI/CD Pipeline
```yaml
- name: Validate Service Configurations
  run: |
    python service_manager.py validate mcp
    python service_manager.py validate socketio
    python service_manager.py validate dashboard
```

## 📝 Troubleshooting

### File Changes Not Detected
1. Check if `watchdog` is installed: `pip install watchdog`
2. Verify watch patterns match your files
3. Check if files are in ignored patterns
4. Ensure watch directories exist

### Validation Always Fails
1. Test validation command manually
2. Check working directory and environment
3. Verify file paths in validation command
4. Check validation timeout (30s default)

### Services Not Restarting
1. Check service status: `python service_manager.py status`
2. Review logs in `logs/` directory
3. Test manual restart: `python service_manager.py restart service_name`
4. Verify process permissions

### High CPU Usage
1. Check debounce delays (may be too low)
2. Review ignore patterns (may be missing)
3. Limit watch directories scope
4. Consider excluding large directories

## 🔮 Future Enhancements

- **Dependency awareness**: Restart dependent services
- **Load balancing**: Zero-downtime restarts with multiple instances
- **Remote monitoring**: Web dashboard for file watching status
- **Smart validation**: Skip validation for trivial changes
- **Performance metrics**: Track restart frequency and validation times 