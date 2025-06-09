# Complete Development Environment Startup

## Overview

The `start_all.sh` script provides a comprehensive, zero-configuration way to start all development services with automatic dependency installation and real-time monitoring.

## 🚀 One-Command Setup

```bash
./start_all.sh
```

**For first-time users**: The script automatically handles all setup requirements!

## 🔧 Automatic Environment Setup

### First Run (New Clone)
When you first run the script on a fresh clone, it will automatically:

1. **Verify Requirements**: Check for essential project files
2. **Python Environment**: 
   - Create virtual environment (`venv/`) if needed
   - Activate virtual environment
   - Install Python dependencies from `requirements.txt`
3. **Node.js Environment**:
   - Verify `pnpm` is available
   - Install TypeScript/Node dependencies with `pnpm install`
   - Verify Plasmo framework is ready
4. **Start Services**: Launch all development services with monitoring

### Subsequent Runs
On subsequent runs, the script will:
- ✅ **Skip setup** if dependencies are already installed
- ✅ **Auto-activate** the virtual environment
- ✅ **Start services** immediately

## 📋 Prerequisites

The script handles most setup automatically, but you need:

- **Python 3**: `brew install python3` (macOS) or equivalent
- **pnpm**: `npm install -g pnpm`
- **Git**: For cloning the repository

Everything else is installed automatically!

## 🎯 Services Started

### 1. **MCP Server** (Port 8000)
- **Auto-restart**: Monitors `*.py` files via `start_mcp_auto_restart.sh`
- **Endpoint**: `http://localhost:8000/mcp`
- **Purpose**: Chrome Debug Protocol integration and "Tell Bolt to..." functionality

### 2. **Plasmo Dev Server** 
- **Auto-reload**: Built-in hot reload for extension files
- **Purpose**: Chrome extension development with live updates
- **Watches**: `*.ts`, `*.tsx`, extension manifest, popup files

### 3. **SocketIO Server** (Port 3001)
- **Auto-restart**: Monitors `socketio_server.js` and `cursor_ai_injector.py` via nodemon
- **Endpoint**: `http://localhost:3001`
- **Purpose**: Real-time communication and automation control

### 4. **Continuous Test Runner**
- **Auto-restart**: Monitors test files and source code changes
- **Purpose**: Automated testing and validation
- **Watches**: `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.html`, `*.css`, `*.py`

## 🎭 Real-Time Monitoring Features

- **Color-Coded Output**: Each service has its own color for easy identification
- **Timestamped Logs**: Every message shows the exact time
- **Restart Notifications**: Automatically detects and announces service restarts
- **Live Log Streaming**: Shows real-time output from all services in one terminal

## 💻 Development Workflow

### For New Contributors
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd Plasmo
   ```

2. **One command to start everything**
   ```bash
   ./start_all.sh
   ```
   
3. **The script automatically**:
   - Creates Python virtual environment
   - Installs all Python dependencies
   - Installs all Node.js dependencies
   - Starts all services with monitoring
   - Shows real-time logs with restart detection

### For Regular Development
1. **Start**: `./start_all.sh` - Skips setup, starts services immediately
2. **Develop**: Make changes to any files - services auto-restart/reload
3. **Debug**: Use Chrome Debug Protocol tools via MCP server
4. **Test**: Continuous testing runs automatically
5. **Stop**: Ctrl+C stops everything gracefully

## 🔍 Environment Detection

The script intelligently detects your environment:

- **Virtual Environment**: Auto-creates and activates `venv/`
- **Dependencies**: Checks if packages are installed before installing
- **Project Structure**: Verifies you're in the correct directory
- **Service State**: Cleans up existing processes before starting

## 📁 Project Structure

After setup, your project will have:
```
Plasmo/
├── venv/                    # Python virtual environment (auto-created)
├── node_modules/            # Node.js dependencies (auto-installed)
├── logs/                    # Service logs (auto-created)
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── start_all.sh            # This startup script
└── ...                     # Project files
```

## 🚨 Troubleshooting

### Common Issues
- **Python not found**: Install Python 3 (`brew install python3`)
- **pnpm not found**: Install pnpm (`npm install -g pnpm`)
- **Permission denied**: Make script executable (`chmod +x start_all.sh`)
- **Port conflicts**: Script automatically cleans up existing instances

### Error Messages
The script provides helpful error messages and suggestions for resolving issues.

## ✨ Benefits

- **Zero Configuration**: Works out of the box for new contributors
- **Intelligent Setup**: Only installs what's needed
- **Full Visibility**: Real-time monitoring of all services
- **Clean Environment**: Proper virtual environment isolation
- **Fast Iteration**: Skip setup on subsequent runs
- **Error Prevention**: Validates environment before starting

This comprehensive setup enables anyone to clone the repository and have a fully functional development environment running within minutes! 🎯 