# Linux Setup Guide for Plasmo Chrome Extension

This guide will help you set up the Plasmo Chrome Extension project with MCP server on Linux systems.

## Quick Start (Automated Setup)

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Plasmo
   ```

2. **Run the automated Linux setup**:
   ```bash
   chmod +x linux_setup.sh
   ./linux_setup.sh
   ```

3. **Start the development environment**:
   ```bash
   ./start_all_services.sh
   ```

That's it! The automated setup handles everything for you.

## Manual Setup (If Automated Setup Fails)

### Prerequisites

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y curl wget git python3 python3-pip python3-venv nodejs npm google-chrome-stable xdotool build-essential
```

#### Fedora/RHEL/CentOS:
```bash
sudo dnf install -y curl wget git python3 python3-pip nodejs npm google-chrome-stable xdotool gcc gcc-c++ make
```

#### Arch/Manjaro:
```bash
sudo pacman -S --noconfirm curl wget git python python-pip nodejs npm google-chrome xdotool base-devel
```

### Step-by-Step Manual Setup

1. **Install Node.js dependencies**:
   ```bash
   npm install -g pnpm
   pnpm install
   ```

2. **Setup Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   deactivate
   ```

3. **Test platform detection**:
   ```bash
   chmod +x platform_detect.sh
   ./platform_detect.sh
   ```

4. **Test Chrome debugging**:
   ```bash
   chmod +x launch-chrome-debug.sh
   ./launch-chrome-debug.sh
   ```

## Linux-Specific Differences

### File Paths
| Component | macOS | Linux |
|-----------|-------|-------|
| Chrome Config | `~/Library/Application Support/Google/Chrome` | `~/.config/google-chrome` |
| Chrome Preferences | `~/Library/.../Chrome/Default/Preferences` | `~/.config/google-chrome/Default/Preferences` |
| Native Messaging | `~/Library/.../Chrome/NativeMessagingHosts` | `~/.config/google-chrome/NativeMessagingHosts` |

### Chrome Executables
The system will automatically detect Chrome from these locations:
- `google-chrome`
- `google-chrome-stable`
- `chromium-browser`
- `chromium`

### Dependencies
- **xdotool**: Used for Cursor automation (keyboard/mouse input)
- **build-essential**: Required for some Python packages

## Project Structure (Linux-Specific Files)

```
Plasmo/
├── linux_setup.sh              # Automated Linux setup
├── platform_detect.sh          # Cross-platform detection utility
├── get_extension_id_linux.sh    # Linux Chrome extension ID finder
├── configure_extension_linux.sh # Linux extension configuration
└── LINUX_SETUP_README.md       # This file
```

## Usage

### 1. Start Development Environment
```bash
# Start all services (MCP server, Plasmo dev, SocketIO server)
./start_all_services.sh

# Or start individually:
./start_mcp.sh
pnpm dev
node socketio_server.js
```

### 2. Build and Load Extension
```bash
# Build the extension
pnpm build

# Load in Chrome:
# 1. Open chrome://extensions/
# 2. Enable Developer mode
# 3. Click "Load unpacked"
# 4. Select: ./build/chrome-mv3-dev
```

### 3. Configure Extension
```bash
# Auto-detect and configure
./configure_extension_linux.sh

# Or get extension ID manually
./get_extension_id_linux.sh
```

### 4. Test Chrome Debugging
```bash
# Launch Chrome with debugging enabled
./launch-chrome-debug.sh

# Test MCP server connection
python3 -c "
import requests
response = requests.get('http://localhost:9222/json')
print('Chrome Debug Protocol:', response.status_code)
"
```

## Troubleshooting

### Common Issues

#### 1. Chrome Not Found
```bash
# Check if Chrome is installed
which google-chrome || which chromium-browser

# Install Chrome on Ubuntu/Debian:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update && sudo apt-get install google-chrome-stable
```

#### 2. xdotool Missing
```bash
# Ubuntu/Debian:
sudo apt-get install xdotool

# Fedora:
sudo dnf install xdotool

# Arch:
sudo pacman -S xdotool
```

#### 3. Permission Denied
```bash
# Make scripts executable
chmod +x *.sh

# Check Python script permissions
chmod +x cursor_controller.py
```

#### 4. Port Already in Use
```bash
# Check what's using the ports
sudo lsof -i :8000  # MCP server
sudo lsof -i :3001  # SocketIO server
sudo lsof -i :9222  # Chrome debug

# Kill processes if needed
pkill -f mcp_server.py
pkill -f socketio_server.js
pkill -f "chrome.*9222"
```

#### 5. Chrome Profile Issues
```bash
# Reset Chrome debug profile
rm -rf chrome-debug-profile/
./launch-chrome-debug.sh
```

### Debug Information

#### Check Platform Detection
```bash
./platform_detect.sh
```

#### Check Services Status
```bash
./check_services.sh
```

#### View Logs
```bash
# MCP server logs
tail -f logs/mcp_server.log

# SocketIO server logs
tail -f logs/socketio_server.log

# Plasmo dev logs
tail -f logs/plasmo_dev.log
```

## Linux Distribution Notes

### Ubuntu LTS (20.04, 22.04, 24.04)
- Fully supported
- Use `apt-get` commands in the setup script
- Chrome installs cleanly from Google's repository

### Fedora (38+)
- Fully supported
- Use `dnf` commands
- May need to enable RPM Fusion repositories

### Arch Linux / Manjaro
- Fully supported
- Use `pacman` commands
- Chrome available in AUR

### Other Distributions
- Should work with manual dependency installation
- May need to adapt package manager commands
- Chrome must be installed manually if not in repositories

## Development Notes

### Auto-Reload Services
All services support auto-reload on Linux:
- **MCP Server**: Monitors Python files (if `watchdog` installed)
- **SocketIO Server**: Uses `nodemon` for auto-restart
- **Plasmo Dev**: Built-in hot reload
- **Test Runner**: Monitors all source files

### VS Code / Cursor Integration
Install Cursor IDE for Linux:
```bash
# Download from https://cursor.sh/
# Or use snap (if available):
sudo snap install cursor

# Make sure it's in PATH
which cursor
```

## Performance Tips

1. **Use SSD storage** for faster file watching
2. **Increase inotify limits** for large projects:
   ```bash
   echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```
3. **Close unnecessary Chrome tabs** to reduce memory usage
4. **Use Chrome's task manager** (Shift+Esc) to monitor extension performance

## Security Notes

- Chrome Debug Protocol (port 9222) is only accessible from localhost
- MCP server (port 8000) binds to 127.0.0.1 only
- Native messaging uses secure Chrome API
- All file operations are restricted to the project directory

## Contributing

When adding Linux-specific features:
1. Update `platform_detect.sh` for new platform detection
2. Test on multiple distributions (Ubuntu, Fedora, Arch)
3. Update this README with any new requirements
4. Ensure cross-platform compatibility is maintained 