# 🐧 Linux Quick Start Guide

**For friends wanting to run the Plasmo project on Linux!**

## One-Command Setup (Recommended)

```bash
# Clone the repo and run the Linux setup
git clone <repo-url>
cd Plasmo
chmod +x linux_setup.sh && ./linux_setup.sh
```

That's it! The script will automatically:
- ✅ Detect your Linux distribution (Ubuntu, Fedora, Arch, etc.)
- ✅ Install all dependencies (Chrome, Node.js, Python, xdotool)
- ✅ Set up the Python virtual environment
- ✅ Configure Chrome paths for Linux
- ✅ Test everything is working

## Quick Start After Setup

```bash
# Start all services
./start_all_services.sh

# Build the extension
pnpm build

# Load extension in Chrome:
# 1. Open chrome://extensions/
# 2. Enable Developer mode
# 3. Click "Load unpacked"
# 4. Select: ./build/chrome-mv3-dev

# Configure the extension
./configure_extension_linux.sh
```

## What's Different from macOS?

| Component | macOS Path | Linux Path |
|-----------|------------|------------|
| Chrome Config | `~/Library/Application Support/Google/Chrome` | `~/.config/google-chrome` |
| Extensions | `~/Library/.../Extensions` | `~/.config/google-chrome/Default/Extensions` |
| Native Messaging | `~/Library/.../NativeMessagingHosts` | `~/.config/google-chrome/NativeMessagingHosts` |

## Linux-Specific Features

- **xdotool integration**: Automated keyboard/mouse control for Cursor IDE
- **Multiple package managers**: Supports apt (Ubuntu), dnf (Fedora), pacman (Arch)
- **Chrome/Chromium detection**: Automatically finds your browser installation
- **Distribution-aware setup**: Adapts to your Linux distribution

## Troubleshooting

If something goes wrong:

```bash
# Check what failed
./test_linux_compatibility.sh

# View logs
tail -f logs/mcp_server.log
tail -f logs/socketio_server.log

# Reset and try again
./stop_all_services.sh
rm -rf venv chrome-debug-profile
./linux_setup.sh
```

## Support Status

✅ **Fully Tested**: Ubuntu LTS, Fedora, Arch Linux  
✅ **Should Work**: Debian, CentOS, Manjaro, openSUSE  
⚠️  **May Need Manual Setup**: Other distributions  

## Dependencies Installed

- **Google Chrome** (or Chromium)
- **Node.js** + **pnpm**
- **Python 3** + **pip**
- **xdotool** (for Cursor automation)
- **Build tools** (gcc, make, etc.)

## Next Steps

Once setup is complete:
1. **Read the full guide**: `LINUX_SETUP_README.md`
2. **Test Chrome debugging**: `./launch-chrome-debug.sh`
3. **Start developing**: `pnpm dev`
4. **Join the fun**: Everything that works on macOS now works on Linux!

---

**Need help?** Check `LINUX_SETUP_README.md` for detailed troubleshooting and advanced setup options. 