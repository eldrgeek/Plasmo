# Automatic Environment Setup

## 🚀 Zero-Configuration Development

The Plasmo Chrome extension project now features **automatic environment setup** that enables anyone to clone the repository and start developing immediately with a single command.

## ✨ What It Does

When you run `./start_all.sh` for the first time, it automatically:

1. **🔍 Verifies Project Structure**: Checks for essential files
2. **🐍 Python Environment**: Creates and configures virtual environment
3. **📦 Python Dependencies**: Installs all required packages from `requirements.txt`
4. **📋 Node.js Dependencies**: Installs TypeScript/React packages via `pnpm`
5. **🎯 Service Startup**: Launches all development services with monitoring

## 🛠️ First-Time Setup (Automatic)

### New Developer Experience
```bash
# 1. Clone the repository
git clone <repository-url>
cd Plasmo

# 2. One command to rule them all
./start_all.sh

# That's it! 🎉
```

### What Happens Behind the Scenes
```
🚀 Starting All Development Services
=====================================

🔧 Initial Environment Setup
============================
🔍 Verifying project requirements...
✅ All required files present

🐍 Setting up Python environment...
📦 Creating Python virtual environment...
✅ Virtual environment created
🔌 Activating virtual environment...
✅ Virtual environment activated
📋 Checking Python dependencies...
📦 Installing Python dependencies...
[... pip install output ...]
✅ Python dependencies installed

📦 Setting up Node.js environment...
✅ Node.js dependencies already installed
✅ Plasmo framework ready

🎯 Environment Setup Complete!
==============================
✅ Python virtual environment ready
✅ Python dependencies installed
✅ Node.js dependencies installed
✅ Project files verified

🚀 Starting development services...
```

## ⚡ Subsequent Runs (Fast)

After the first setup, `./start_all.sh` becomes lightning fast:

```
🚀 Starting All Development Services
=====================================

🔧 Initial Environment Setup
============================
🔍 Verifying project requirements...
✅ All required files present

🐍 Setting up Python environment...
✅ Virtual environment already exists
✅ Already in virtual environment
📋 Checking Python dependencies...
✅ Python dependencies already installed

📦 Setting up Node.js environment...
✅ Node.js dependencies already installed
✅ Plasmo framework ready

🎯 Environment Setup Complete!
==============================
[... services start immediately ...]
```

## 🎛️ Smart Detection

The setup system intelligently detects your environment state:

### Python Environment
- **Virtual Environment**: Auto-creates `venv/` if missing
- **Activation**: Automatically activates if not already active
- **Dependencies**: Quick import check before running pip install
- **Packages**: Installs from `requirements.txt` only if needed

### Node.js Environment
- **pnpm Check**: Verifies pnpm is installed with helpful error messages
- **Dependencies**: Checks `node_modules/` exists and has content
- **Plasmo Framework**: Validates extension framework is ready

### Project Structure
- **Essential Files**: Verifies `package.json`, `mcp_server.py`, startup scripts
- **Directory Context**: Ensures you're in the correct project directory
- **Error Recovery**: Provides helpful suggestions for missing components

## 📋 Prerequisites

### Automatic (Handled by Script)
- ✅ **Python Virtual Environment**: Created automatically
- ✅ **Python Packages**: Installed from `requirements.txt`
- ✅ **Node.js Packages**: Installed via `pnpm install`
- ✅ **Project Validation**: Verified automatically

### Manual (One-Time Setup)
- **Python 3**: `brew install python3` (macOS) or equivalent
- **pnpm**: `npm install -g pnpm`
- **Git**: For repository operations

## 🎯 Technology Stack

### Auto-Installed Python Dependencies
```
fastmcp>=2.6.1        # MCP server framework
websockets>=11.0.3     # WebSocket communication
aiohttp>=3.8.5         # Async HTTP client/server
pychrome>=0.2.3        # Chrome Debug Protocol
requests>=2.28.0       # HTTP library
```

### Auto-Installed Node.js Dependencies
```
plasmo                 # Chrome extension framework
react                  # UI library
typescript             # Type safety
socket.io              # Real-time communication
nodemon                # Auto-restart for development
```

## 🔄 Development Workflow

### For New Contributors
1. **Clone & Start**: One command gets everything running
2. **Develop**: Make changes - services auto-restart/reload
3. **Debug**: Use Chrome Debug Protocol via MCP server
4. **Test**: Continuous testing runs automatically

### For Regular Development
1. **Fast Start**: Skip setup, immediate service startup
2. **Consistent Environment**: Same virtual environment every time
3. **Zero Configuration**: No manual dependency management
4. **Full Visibility**: Real-time monitoring of all services

## 🎪 Service Architecture

After setup, the following services run with auto-restart:

- **🐍 MCP Server** (Port 8000): Chrome Debug Protocol + AI tools
- **🎯 Plasmo Dev Server**: Extension hot reload
- **🌐 SocketIO Server** (Port 3001): Real-time automation control
- **🧪 Test Runner**: Continuous quality assurance

## 🚨 Error Handling

### Common Setup Issues

**Python not found**:
```bash
❌ Failed to create virtual environment
💡 Make sure python3 is installed: brew install python3
```

**pnpm not available**:
```bash
❌ pnpm not found
💡 Install pnpm: npm install -g pnpm
```

**Missing project files**:
```bash
❌ Missing required files:
   • package.json
   • mcp_server.py
💡 Make sure you're in the correct Plasmo project directory
```

**Permission issues**:
```bash
# Make script executable
chmod +x start_all.sh
```

## 📁 Project Structure After Setup

```
Plasmo/
├── venv/                    # 🐍 Python virtual environment (auto-created)
│   ├── bin/activate         # Environment activation script
│   ├── lib/python3.11/      # Python packages
│   └── ...
├── node_modules/            # 📦 Node.js dependencies (auto-installed)
│   ├── plasmo/              # Extension framework
│   ├── react/               # UI library
│   └── ...
├── logs/                    # 📊 Service logs (auto-created)
│   ├── mcp_server.log       # MCP server output
│   ├── plasmo_dev.log       # Extension build logs
│   └── ...
├── requirements.txt         # 🐍 Python dependencies definition
├── package.json            # 📦 Node.js dependencies definition
├── start_all.sh            # 🚀 This magic startup script
└── ...                     # Your project files
```

## 🎊 Benefits

### For New Developers
- **⚡ Instant Productivity**: Clone and run in minutes
- **🎯 Zero Friction**: No manual dependency management
- **📚 Self-Documenting**: Clear error messages and suggestions
- **🛡️ Consistent Environment**: Same setup across all machines

### For Project Maintenance
- **🔄 Version Control**: Dependencies defined in files, not documentation
- **🧪 Reproducible Builds**: Identical environments every time
- **📈 Scalable Onboarding**: Works for teams of any size
- **🔧 Easy Updates**: Change files, everyone gets updates automatically

### For Development Experience
- **🚀 Fast Iteration**: Skip setup on subsequent runs
- **👁️ Full Visibility**: Real-time monitoring of all services
- **🧹 Clean Separation**: Virtual environment isolation
- **⚙️ Auto-Restart**: Services restart when files change

## 🎯 Use Cases

### New Team Member
```bash
# Day 1 - First time
git clone <repo>
cd Plasmo
./start_all.sh    # Full setup + start services

# Day 2+ - Regular development
./start_all.sh    # Instant start, skip setup
```

### CI/CD Pipeline
```bash
# Fresh environment every time
./start_all.sh    # Handles all setup automatically
npm test          # Run tests in consistent environment
```

### Docker/Container
```bash
# Container startup script
./start_all.sh    # Creates complete development environment
```

### Educational Workshops
```bash
# Students can start immediately
git clone <workshop-repo>
cd project
./start_all.sh    # Everything just works
```

## 🔮 Future Enhancements

- **Package Caching**: Speed up repeated setups
- **Environment Validation**: More comprehensive health checks
- **Update Detection**: Auto-update dependencies when files change
- **Platform Detection**: Windows/Linux specific optimizations
- **Development Profiles**: Different setups for different use cases

---

## 🎉 Summary

The automatic environment setup feature transforms the developer experience from:

**Before**: "Clone, read docs, install Python, create venv, activate, pip install, install pnpm, pnpm install, configure services..."

**After**: "Clone, `./start_all.sh`, start coding! 🚀"

This is developer experience engineering at its finest - removing friction and enabling focus on what matters: building great Chrome extensions! ✨ 