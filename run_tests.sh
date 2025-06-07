#!/bin/bash

# MCP Server Test Runner
# ====================
# This script runs the comprehensive test suite for the MCP server

set -e  # Exit on any error

echo "🧪 MCP Server Test Runner"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if test file exists
if [ ! -f "test_mcp_server.py" ]; then
    print_error "test_mcp_server.py not found in current directory"
    exit 1
fi

# Check if MCP server file exists
if [ ! -f "mcp_server.py" ]; then
    print_error "mcp_server.py not found in current directory"
    exit 1
fi

print_status "Starting MCP server test suite..."

# Parse command line arguments
VERBOSE=false
OUTPUT_FILE=""
SAVE_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            SAVE_REPORT=true
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose     Enable verbose output"
            echo "  -o, --output FILE Save test report to file"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 --verbose          # Run with verbose output"
            echo "  $0 -o test_report.txt # Save report to file"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 test_mcp_server.py"

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

if [ "$SAVE_REPORT" = true ]; then
    CMD="$CMD --output $OUTPUT_FILE"
fi

print_status "Running command: $CMD"
echo ""

# Run the tests
if eval $CMD; then
    echo ""
    print_success "All tests completed successfully! ✅"
    
    if [ "$SAVE_REPORT" = true ]; then
        print_success "Test report saved to: $OUTPUT_FILE"
    fi
    
    exit 0
else
    echo ""
    print_error "Some tests failed! ❌"
    
    if [ "$SAVE_REPORT" = true ]; then
        print_warning "Test report saved to: $OUTPUT_FILE (check for details)"
    fi
    
    exit 1
fi 