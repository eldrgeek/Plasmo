#!/bin/bash

# Test Linux Compatibility for Plasmo Project
# ===========================================
# This script validates that the Linux setup files are correct

echo "🧪 Testing Linux Compatibility for Plasmo Project"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

print_test() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((test_passed++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((test_failed++))
    fi
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# Test 1: Check if Linux setup script exists and is executable
echo ""
echo "🔍 Testing Setup Scripts"
echo "------------------------"

if [ -f "linux_setup.sh" ] && [ -x "linux_setup.sh" ]; then
    print_test 0 "linux_setup.sh exists and is executable"
else
    print_test 1 "linux_setup.sh missing or not executable"
fi

if [ -f "platform_detect.sh" ] && [ -x "platform_detect.sh" ]; then
    print_test 0 "platform_detect.sh exists and is executable"
else
    print_test 1 "platform_detect.sh missing or not executable"
fi

if [ -f "get_extension_id_linux.sh" ] && [ -x "get_extension_id_linux.sh" ]; then
    print_test 0 "get_extension_id_linux.sh exists and is executable"
else
    print_test 1 "get_extension_id_linux.sh missing or not executable"
fi

if [ -f "configure_extension_linux.sh" ] && [ -x "configure_extension_linux.sh" ]; then
    print_test 0 "configure_extension_linux.sh exists and is executable"
else
    print_test 1 "configure_extension_linux.sh missing or not executable"
fi

# Test 2: Validate platform detection logic
echo ""
echo "🔍 Testing Platform Detection"
echo "-----------------------------"

# Test platform detection script
if [ -f "platform_detect.sh" ]; then
    # Source the script and test function existence
    source platform_detect.sh 2>/dev/null
    
    if type detect_platform &>/dev/null; then
        print_test 0 "detect_platform function exists"
    else
        print_test 1 "detect_platform function missing"
    fi
    
    if type set_chrome_paths &>/dev/null; then
        print_test 0 "set_chrome_paths function exists"
    else
        print_test 1 "set_chrome_paths function missing"
    fi
    
    if type find_chrome_executable &>/dev/null; then
        print_test 0 "find_chrome_executable function exists"
    else
        print_test 1 "find_chrome_executable function missing"
    fi
else
    print_test 1 "platform_detect.sh not found for testing"
fi

# Test 3: Check Linux-specific path patterns
echo ""
echo "🔍 Testing Linux Path Patterns"
echo "------------------------------"

# Check if Linux setup script contains correct paths
if grep -q "\.config/google-chrome" linux_setup.sh 2>/dev/null; then
    print_test 0 "Linux Chrome config path found in setup script"
else
    print_test 1 "Linux Chrome config path missing in setup script"
fi

if grep -q "apt-get\|dnf\|pacman" linux_setup.sh 2>/dev/null; then
    print_test 0 "Linux package managers detected in setup script"
else
    print_test 1 "Linux package managers missing in setup script"
fi

if grep -q "xdotool" linux_setup.sh 2>/dev/null; then
    print_test 0 "xdotool dependency found in setup script"
else
    print_test 1 "xdotool dependency missing in setup script"
fi

# Test 4: Check if Chrome Debug Protocol paths are updated
echo ""
echo "🔍 Testing Chrome Launch Script Updates"
echo "---------------------------------------"

if grep -q "platform_detect.sh" launch-chrome-debug.sh 2>/dev/null; then
    print_test 0 "launch-chrome-debug.sh uses platform detection"
else
    print_test 1 "launch-chrome-debug.sh not updated for cross-platform"
fi

# Test 5: Check MCP server Python compatibility
echo ""
echo "🔍 Testing MCP Server Compatibility"
echo "-----------------------------------"

if grep -q '"linux".*google-chrome' mcp_server.py 2>/dev/null; then
    print_test 0 "MCP server has Linux Chrome executable paths"
else
    print_test 1 "MCP server missing Linux Chrome paths"
fi

# Test 6: Check required files exist
echo ""
echo "🔍 Testing Required Files"
echo "-------------------------"

required_files=(
    "package.json"
    "requirements.txt"
    "mcp_server.py"
    "socketio_server.js"
    "start_all_services.sh"
    "cursor_ai_injector.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_test 0 "Required file exists: $file"
    else
        print_test 1 "Required file missing: $file"
    fi
done

# Test 7: Check if cursor_ai_injector has Linux support
echo ""
echo "🔍 Testing Cursor AI Injector Linux Support"
echo "--------------------------------------------"

if grep -q "'linux'" cursor_ai_injector.py 2>/dev/null; then
    print_test 0 "cursor_ai_injector.py has Linux support"
else
    print_test 1 "cursor_ai_injector.py missing Linux support"
fi

if grep -q "xdotool" cursor_ai_injector.py 2>/dev/null; then
    print_test 0 "cursor_ai_injector.py uses xdotool for Linux"
else
    print_test 1 "cursor_ai_injector.py missing xdotool integration"
fi

# Test 8: Validate Linux documentation
echo ""
echo "🔍 Testing Documentation"
echo "------------------------"

if [ -f "LINUX_SETUP_README.md" ]; then
    print_test 0 "Linux setup documentation exists"
    
    if grep -q "Ubuntu\|Fedora\|Arch" LINUX_SETUP_README.md 2>/dev/null; then
        print_test 0 "Documentation covers major Linux distributions"
    else
        print_test 1 "Documentation missing Linux distribution coverage"
    fi
else
    print_test 1 "Linux setup documentation missing"
fi

# Test 9: Check script syntax
echo ""
echo "🔍 Testing Script Syntax"
echo "------------------------"

for script in linux_setup.sh platform_detect.sh get_extension_id_linux.sh configure_extension_linux.sh; do
    if [ -f "$script" ]; then
        if bash -n "$script" 2>/dev/null; then
            print_test 0 "Script syntax valid: $script"
        else
            print_test 1 "Script syntax error: $script"
        fi
    fi
done

# Test 10: Validate Linux Chrome paths are different from macOS
echo ""
echo "🔍 Testing Platform Path Differences"
echo "------------------------------------"

if grep -q "Library/Application Support" get_extension_id_linux.sh 2>/dev/null; then
    print_test 1 "Linux script still contains macOS paths"
else
    print_test 0 "Linux scripts use correct Linux paths"
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "${GREEN}Tests Passed: $test_passed${NC}"
echo -e "${RED}Tests Failed: $test_failed${NC}"

total_tests=$((test_passed + test_failed))
if [ $total_tests -gt 0 ]; then
    success_rate=$((test_passed * 100 / total_tests))
    echo "Success Rate: $success_rate%"
fi

echo ""
if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Linux compatibility is ready.${NC}"
    echo ""
    echo "Next steps for Linux users:"
    echo "1. Run: chmod +x linux_setup.sh && ./linux_setup.sh"
    echo "2. Start services: ./start_all_services.sh"
    echo "3. Configure extension: ./configure_extension_linux.sh"
else
    echo -e "${RED}❌ Some tests failed. Please fix the issues above.${NC}"
    exit 1
fi 