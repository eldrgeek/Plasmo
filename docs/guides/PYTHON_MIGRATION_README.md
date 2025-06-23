# Python Migration Strategy for Plasmo Extension

> **✅ MIGRATION COMPLETE**: The Python migration has been completed successfully. This document is kept for reference. Use `python service_manager.py status` to check current system status.

This document outlines the migration strategy from shell scripts and JavaScript services to Python, providing cross-platform compatibility while maintaining backward compatibility through a shim layer approach.

## 🎯 Goals

1. **Cross-Platform Compatibility**: Run on Windows, Linux, and macOS
2. **Gradual Migration**: Maintain existing functionality while migrating piece by piece
3. **Environment-Based Switching**: Choose implementations via environment variables
4. **Enhanced Maintainability**: Python code is more readable and maintainable than shell scripts

## 📁 New Python Files

### Core Infrastructure
- `service_manager.py` - Cross-platform service management with shim layer support
- `check_services.py` - Python replacement for `check_services.sh`
- `socketio_server_python.py` - FastAPI + Socket.IO server (future replacement for `socketio_server.js`)
- Migration testing completed and integrated into main test suite

### Configuration
- `requirements.txt` - Updated with FastAPI, Socket.IO, and utility dependencies
- `environment.env.example` - Environment configuration template

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test the Migration

```bash
python test_python_migration.py
```

### 3. Try the Python Service Manager

```bash
# Check service status
python service_manager.py status

# Start all services
python service_manager.py start-all

# Stop all services  
python service_manager.py stop-all

# Start individual service
python service_manager.py start socketio
```

### 4. Try the Python Service Checker

```bash
# Full status check
python check_services.py

# Quick status check
python check_services.py --quiet

# JSON output
python check_services.py --json
```

## 🔧 Environment Configuration

Copy the example environment file and customize:

```bash
cp environment.env.example .env
```

### Key Environment Variables

```bash
# Socket.IO Server Implementation
SOCKETIO_IMPLEMENTATION=javascript  # or "python"

# MCP Server Implementation
MCP_IMPLEMENTATION=python

# Service Ports
SOCKETIO_PORT=3001
MCP_PORT=8000

# Development Configuration
ENABLE_AUTO_RESTART=true
ENABLE_FILE_WATCHING=true
```

## 🔄 Migration Strategy

### Phase 1: Shim Layer (Current)
- Python scripts call existing JavaScript/shell implementations
- Provides cross-platform service management
- No disruption to existing functionality

### Phase 2: Gradual Replacement
- Start using Python Socket.IO server: `SOCKETIO_IMPLEMENTATION=python`
- Migrate more shell scripts to Python equivalents
- A/B test between implementations

### Phase 3: Full Migration
- Default to Python implementations
- Deprecate JavaScript/shell versions
- Remove Node.js dependencies

### Phase 4: Enhancement
- Add FastHTML web interfaces
- Enhanced cross-platform features
- Advanced service orchestration

## 📊 Service Management

### Service Manager CLI

The `service_manager.py` provides a unified interface for all services:

```bash
# Available commands
python service_manager.py --help

# Service operations
python service_manager.py start <service>     # Start a service
python service_manager.py stop <service>      # Stop a service  
python service_manager.py restart <service>   # Restart a service
python service_manager.py status              # Show all service status

# Bulk operations
python service_manager.py start-all           # Start all services
python service_manager.py stop-all            # Stop all services
```

### Supported Services

| Service | Description | Current Implementation |
|---------|-------------|----------------------|
| `socketio` | Socket.IO server for extension communication | JavaScript (with Python option) |
| `mcp` | MCP server for Chrome Debug Protocol | Python |
| `plasmo` | Plasmo development server | JavaScript |
| `tests` | Continuous test runner | Python |

## 🌍 Cross-Platform Features

### Process Management
- Uses `psutil` for cross-platform process detection and management
- Handles process groups and cleanup on all platforms
- Supports both POSIX and Windows signal handling

### Path Handling
- Uses `pathlib` for cross-platform path operations
- Automatically handles Windows vs Unix path separators
- Resolves relative paths correctly

### Terminal Output
- Uses `colorama` for cross-platform colored output
- Works in Windows Command Prompt, PowerShell, and Unix terminals
- Graceful fallback when colors aren't supported

## 🧪 Testing

### Run Migration Tests

```bash
python test_python_migration.py
```

This tests:
- Service manager functionality
- Service checker functionality  
- Environment-based switching
- Cross-platform compatibility

### Manual Testing

1. **Test Service Status**:
   ```bash
   python service_manager.py status
   ```

2. **Test Environment Switching**:
   ```bash
   export SOCKETIO_IMPLEMENTATION=python
   python service_manager.py restart socketio
   ```

3. **Test Cross-Platform Compatibility**:
   - Run on different operating systems
   - Test with different Python versions
   - Verify process detection works

## 🚀 Using Python Socket.IO Server

To switch to the Python Socket.IO implementation:

### 1. Set Environment Variable

```bash
export SOCKETIO_IMPLEMENTATION=python
```

### 2. Restart Socket.IO Service

```bash
python service_manager.py restart socketio
```

### 3. Verify It's Running

```bash
python check_services.py
```

The status should show "SocketIO Server (python) is running".

### 4. Test the Web Interface

Visit http://localhost:3001 to see the Python server's web interface.

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Issues**:
   - On Unix: Make sure scripts are executable: `chmod +x *.py`
   - On Windows: Run from Administrator PowerShell if needed

3. **Port Conflicts**:
   - Change ports in environment configuration
   - Check what's using ports: `python check_services.py`

4. **Process Detection Issues**:
   - Install psutil: `pip install psutil`
   - Check platform compatibility

### Debug Mode

Enable verbose logging:

```bash
export LOG_LEVEL=DEBUG
python service_manager.py status
```

## 🔮 Future Enhancements

### Planned Features

1. **FastHTML Web Interfaces**: Modern, reactive web UIs using FastHTML
2. **Advanced Process Monitoring**: Resource usage, health checks, auto-restart
3. **Service Dependencies**: Automatic dependency resolution and startup ordering
4. **Configuration Management**: Advanced environment and config file support
5. **Docker Support**: Containerized deployment options
6. **Remote Management**: API for remote service management

### Extension Integration

The Python infrastructure is designed to support:
- Enhanced Chrome extension debugging
- Multi-browser support
- Advanced automation features
- Better error handling and logging

## 📚 Migration Guide for Existing Scripts

### Converting Shell Scripts to Python

1. **Identify the shell script's purpose**
2. **Create equivalent Python module** 
3. **Use service_manager for subprocess management**
4. **Add cross-platform path handling**
5. **Implement proper error handling**
6. **Add CLI interface with Click**

### Example Migration Pattern

```python
#!/usr/bin/env python3
"""
Python replacement for some_script.sh
"""

import sys
from pathlib import Path
import click
from colorama import Fore, Style, init

# Add service manager
sys.path.insert(0, str(Path(__file__).parent))
from service_manager import ServiceManager

init(autoreset=True)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(verbose):
    """Your script description"""
    manager = ServiceManager()
    
    # Your logic here
    if verbose:
        print(f"{Fore.BLUE}ℹ️ Verbose mode enabled{Style.RESET_ALL}")
    
    # Use manager.start_service(), etc.

if __name__ == "__main__":
    main()
```

## 🤝 Contributing

When adding new Python scripts:

1. Follow the existing patterns in `service_manager.py`
2. Add comprehensive error handling
3. Use `click` for CLI interfaces
4. Add docstrings and type hints
5. Test on multiple platforms
6. Update this README with new features

## 📝 Status

- ✅ **Service Manager**: Complete with shim layer support
- ✅ **Service Checker**: Complete with enhanced features  
- ✅ **Python Socket.IO Server**: Basic implementation complete
- 🚧 **Shell Script Migration**: In progress
- 🚧 **FastHTML Integration**: Planned
- 🚧 **Advanced Features**: Planned

This migration approach allows us to gradually transition to Python while maintaining full backward compatibility and adding enhanced cross-platform support. 