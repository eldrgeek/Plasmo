#!/bin/bash

# Platform Detection Utility for Plasmo Project
# =============================================
# This script detects the current platform and sets appropriate variables
# that can be used by other scripts for cross-platform compatibility.

# Detect the current platform
detect_platform() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
        PLATFORM_NAME="macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
        PLATFORM_NAME="Linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        PLATFORM="windows"
        PLATFORM_NAME="Windows"
    else
        PLATFORM="unknown"
        PLATFORM_NAME="Unknown ($OSTYPE)"
    fi
}

# Set platform-specific Chrome executable paths
set_chrome_paths() {
    case $PLATFORM in
        "macos")
            CHROME_EXECUTABLES=(
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            )
            CHROME_CONFIG_DIR="$HOME/Library/Application Support/Google/Chrome"
            CHROME_PREFS="$CHROME_CONFIG_DIR/Default/Preferences"
            NATIVE_MESSAGING_DIR="$CHROME_CONFIG_DIR/NativeMessagingHosts"
            ;;
        "linux")
            CHROME_EXECUTABLES=(
                "google-chrome"
                "google-chrome-stable"
                "chromium-browser"
                "chromium"
            )
            CHROME_CONFIG_DIR="$HOME/.config/google-chrome"
            CHROME_PREFS="$CHROME_CONFIG_DIR/Default/Preferences"
            NATIVE_MESSAGING_DIR="$CHROME_CONFIG_DIR/NativeMessagingHosts"
            ;;
        "windows")
            CHROME_EXECUTABLES=(
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                "chrome.exe"
            )
            CHROME_CONFIG_DIR="$HOME/AppData/Local/Google/Chrome/User Data"
            CHROME_PREFS="$CHROME_CONFIG_DIR/Default/Preferences"
            NATIVE_MESSAGING_DIR="$CHROME_CONFIG_DIR/NativeMessagingHosts"
            ;;
        *)
            CHROME_EXECUTABLES=("chrome" "chromium")
            CHROME_CONFIG_DIR="$HOME/.config/google-chrome"
            CHROME_PREFS="$CHROME_CONFIG_DIR/Default/Preferences"
            NATIVE_MESSAGING_DIR="$CHROME_CONFIG_DIR/NativeMessagingHosts"
            ;;
    esac
}

# Find the actual Chrome executable
find_chrome_executable() {
    CHROME_PATH=""
    
    for exe in "${CHROME_EXECUTABLES[@]}"; do
        if [[ -x "$exe" ]]; then
            CHROME_PATH="$exe"
            break
        elif command -v "$exe" &> /dev/null; then
            CHROME_PATH=$(command -v "$exe")
            break
        fi
    done
    
    if [[ -z "$CHROME_PATH" ]]; then
        echo "❌ Chrome executable not found. Tried:" >&2
        printf '   %s\n' "${CHROME_EXECUTABLES[@]}" >&2
        return 1
    fi
    
    return 0
}

# Set platform-specific process management commands
set_process_commands() {
    case $PLATFORM in
        "macos"|"linux")
            KILL_PROCESS_CMD="pkill -f"
            LIST_PROCESS_CMD="ps aux | grep"
            CHECK_PORT_CMD="lsof -i"
            ;;
        "windows")
            KILL_PROCESS_CMD="taskkill /F /IM"
            LIST_PROCESS_CMD="tasklist | findstr"
            CHECK_PORT_CMD="netstat -an | findstr"
            ;;
        *)
            KILL_PROCESS_CMD="pkill -f"
            LIST_PROCESS_CMD="ps aux | grep"
            CHECK_PORT_CMD="lsof -i"
            ;;
    esac
}

# Set platform-specific Cursor paths
set_cursor_paths() {
    case $PLATFORM in
        "macos")
            CURSOR_EXECUTABLES=(
                "/Applications/Cursor.app/Contents/MacOS/Cursor"
                "/usr/local/bin/cursor"
            )
            ;;
        "linux")
            CURSOR_EXECUTABLES=(
                "/usr/local/bin/cursor"
                "/opt/cursor/cursor"
                "/snap/bin/cursor"
                "cursor"
            )
            ;;
        "windows")
            CURSOR_EXECUTABLES=(
                "C:\\Users\\$USERNAME\\AppData\\Local\\Programs\\cursor\\Cursor.exe"
                "C:\\Program Files\\Cursor\\Cursor.exe"
                "cursor.exe"
            )
            ;;
        *)
            CURSOR_EXECUTABLES=("cursor")
            ;;
    esac
}

# Print platform information
print_platform_info() {
    echo "Platform Information:"
    echo "  System: $PLATFORM_NAME"
    echo "  Chrome Config: $CHROME_CONFIG_DIR"
    echo "  Native Messaging: $NATIVE_MESSAGING_DIR"
    echo "  Chrome Executable: ${CHROME_PATH:-'Not found'}"
}

# Initialize platform detection
init_platform() {
    detect_platform
    set_chrome_paths
    set_process_commands
    set_cursor_paths
    find_chrome_executable
}

# If script is run directly (not sourced), show platform info
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_platform
    print_platform_info
fi 