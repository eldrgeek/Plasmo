#!/bin/bash
# cursor_collab.sh - Terminal interface for messaging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   Cursor Collaboration Tool    ${NC}"
    echo -e "${BLUE}================================${NC}"
}

send_message() {
    echo -e "${YELLOW}=== Send Message ===${NC}"
    read -p "To: " to
    read -p "Subject: " subject
    echo "Message (end with Ctrl+D or empty line):"
    message=""
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            break
        fi
        message="${message}${line}\n"
    done
    
    if [[ -z "$to" || -z "$subject" || -z "$message" ]]; then
        echo -e "${RED}❌ All fields required${NC}"
        return 1
    fi
    
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d "{
            \"operation\": \"send\",
            \"payload\": {
                \"to\": \"$to\",
                \"subject\": \"$subject\",
                \"message\": \"$message\"
            }
        }" | jq -r '
        if .success then
            "✅ Message sent! ID: \(.message_id)"
        else
            "❌ Failed: \(.error // "Unknown error")"
        end
    '
}

check_messages() {
    echo -e "${YELLOW}=== Checking Messages ===${NC}"
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d '{"operation": "list"}' | jq -r '
        if .success then
            "📬 Inbox (\(.message_summaries | length) messages, \(.unread_count) unread)",
            "=" * 50,
            (.message_summaries[] | 
                (if .read then "✅" else "🔴" end) + 
                " #\(.id) From: \(.from) | \(.subject)"
            )
        else
            "❌ Failed: \(.error // "Unknown error")"
        end
    '
}

read_message() {
    echo -e "${YELLOW}=== Read Message ===${NC}"
    read -p "Message ID: " id
    
    if [[ -z "$id" ]]; then
        echo -e "${RED}❌ Message ID required${NC}"
        return 1
    fi
    
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d "{
            \"operation\": \"get\",
            \"payload\": {\"id\": $id}
        }" | jq -r '
        if .success and (.messages | length > 0) then
            .messages[0] | 
            "📖 Message #\(.id)",
            "=" * 50,
            "From: \(.from)",
            "To: \(.to)", 
            "Subject: \(.subject)",
            "Date: \(.timestamp)",
            "",
            .message
        else
            "❌ Message not found or error: \(.error // "Unknown error")"
        end
    '
}

reply_message() {
    echo -e "${YELLOW}=== Reply to Message ===${NC}"
    read -p "Reply to message ID: " reply_id
    
    if [[ -z "$reply_id" ]]; then
        echo -e "${RED}❌ Message ID required${NC}"
        return 1
    fi
    
    echo "Reply message (end with Ctrl+D or empty line):"
    message=""
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            break
        fi
        message="${message}${line}\n"
    done
    
    if [[ -z "$message" ]]; then
        echo -e "${RED}❌ Message content required${NC}"
        return 1
    fi
    
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d "{
            \"operation\": \"reply\",
            \"payload\": {
                \"reply_to\": $reply_id,
                \"message\": \"$message\"
            }
        }" | jq -r '
        if .success then
            "✅ Reply sent! ID: \(.message_id)"
        else
            "❌ Failed: \(.error // "Unknown error")"
        end
    '
}

list_agents() {
    echo -e "${YELLOW}=== Registered Agents ===${NC}"
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d '{"operation": "agents"}' | jq -r '
        if .success then
            "👥 Agents (\(.agents | length) registered)",
            "=" * 40,
            (.agents[] | 
                "🤖 \(.agent_name)",
                "   Path: \(.repo_path)",
                (if .github_url then "   GitHub: \(.github_url)" else "" end),
                "   Registered: \(.registration_timestamp)",
                ""
            )
        else
            "❌ Failed: \(.error // "Unknown error")"
        end
    '
}

register_agent() {
    echo -e "${YELLOW}=== Register Agent ===${NC}"
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d '{"operation": "register"}' | jq -r '
        if .success then
            "✅ Agent registered: \(.agent.agent_name)",
            "   Path: \(.agent.repo_path)",
            (if .agent.github_url then "   GitHub: \(.agent.github_url)" else "" end)
        else
            "❌ Failed: \(.error // "Unknown error")"
        end
    '
}

status_check() {
    echo -e "${YELLOW}=== System Status ===${NC}"
    
    # Check MCP server
    curl -s -X POST "$MCP_SERVER/mcp/tools/server_info" \
        -H "Content-Type: application/json" \
        -d '{}' | jq -r '
        if .success then
            "✅ MCP Server: Running",
            "   Version: \(.version // "Unknown")",
            "   Host: \(.host // "Unknown"):\(.port // "Unknown")"
        else
            "❌ MCP Server: Error"
        end
    '
    
    echo ""
    
    # Check messaging system
    curl -s -X POST "$MCP_SERVER/mcp/tools/messages" \
        -H "Content-Type: application/json" \
        -d '{"operation": "agents"}' | jq -r '
        if .success then
            "✅ Messaging: Active",
            "   Agents: \(.agents | length)"
        else
            "❌ Messaging: Error"
        end
    '
}

show_menu() {
    echo ""
    echo -e "${GREEN}Available commands:${NC}"
    echo "  send     - Send a new message"
    echo "  check    - List message summaries"
    echo "  read     - Read a specific message"
    echo "  reply    - Reply to a message"
    echo "  agents   - List registered agents"
    echo "  register - Register this agent"
    echo "  status   - Check system status"
    echo "  help     - Show this menu"
    echo "  quit     - Exit"
    echo ""
}

interactive_mode() {
    print_header
    echo -e "${GREEN}Welcome to Cursor Collaboration!${NC}"
    show_menu
    
    while true; do
        read -p "cursor-collab> " command
        
        case "$command" in
            send) send_message ;;
            check) check_messages ;;
            read) read_message ;;
            reply) reply_message ;;
            agents) list_agents ;;
            register) register_agent ;;
            status) status_check ;;
            help) show_menu ;;
            quit|exit) 
                echo -e "${GREEN}👋 Goodbye!${NC}"
                break 
                ;;
            *)
                echo -e "${RED}❌ Unknown command: $command${NC}"
                echo "Type 'help' for available commands"
                ;;
        esac
        echo ""
    done
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ Error: jq is required but not installed${NC}"
    echo "Install jq: brew install jq (macOS) or apt-get install jq (Ubuntu)"
    exit 1
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ Error: curl is required but not installed${NC}"
    exit 1
fi

# Handle command line arguments
case "${1:-interactive}" in
    send) send_message ;;
    check) check_messages ;;
    read) read_message ;;
    reply) reply_message ;;
    agents) list_agents ;;
    register) register_agent ;;
    status) status_check ;;
    interactive) interactive_mode ;;
    help|--help)
        print_header
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  send      - Send a new message"
        echo "  check     - List message summaries"
        echo "  read      - Read a specific message"
        echo "  reply     - Reply to a message"
        echo "  agents    - List registered agents"
        echo "  register  - Register this agent"
        echo "  status    - Check system status"
        echo "  interactive - Start interactive mode (default)"
        echo ""
        echo "Examples:"
        echo "  $0 send           # Send a message"
        echo "  $0 check          # Check for messages"
        echo "  $0 agents         # List all agents"
        echo "  $0                # Start interactive mode"
        ;;
    *) 
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 