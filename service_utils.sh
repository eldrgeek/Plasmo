#!/bin/bash

# Service Registry Utilities
# Shared functions for managing service information between start and check scripts

REGISTRY_FILE=".service_registry.json"

# Function to check if jq is available (for JSON parsing)
ensure_jq() {
    if ! command -v jq &> /dev/null; then
        echo "⚠️  jq not found, installing for JSON parsing..."
        if command -v brew &> /dev/null; then
            brew install jq
        elif command -v apt-get &> /dev/null; then
            sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        else
            echo "❌ Could not install jq. Please install manually."
            return 1
        fi
    fi
}

# Function to update service information in registry
update_service() {
    local service_name="$1"
    local pid="$2"
    local port="$3"
    local status="$4"
    
    ensure_jq || return 1
    
    local current_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create URL if port is provided
    local url="null"
    if [ ! -z "$port" ] && [ "$port" != "null" ]; then
        url="\"http://localhost:$port\""
    fi
    
    # Update the registry file
    jq --arg service "$service_name" \
       --arg pid "$pid" \
       --arg port "$port" \
       --arg status "$status" \
       --arg time "$current_time" \
       --arg url "$url" \
       '.services[$service].pid = ($pid | if . == "null" then null else . end) |
        .services[$service].port = ($port | if . == "null" then null else (. | tonumber) end) |
        .services[$service].status = $status |
        .services[$service].start_time = $time |
        .services[$service].url = ($url | if . == "null" then null else . end) |
        .last_updated = $time' "$REGISTRY_FILE" > "${REGISTRY_FILE}.tmp" && mv "${REGISTRY_FILE}.tmp" "$REGISTRY_FILE"
}

# Function to get service information from registry
get_service_info() {
    local service_name="$1"
    local field="$2"
    
    ensure_jq || return 1
    
    if [ ! -f "$REGISTRY_FILE" ]; then
        echo "null"
        return 1
    fi
    
    jq -r ".services[\"$service_name\"].$field // \"null\"" "$REGISTRY_FILE"
}

# Function to get all services status
get_all_services() {
    ensure_jq || return 1
    
    if [ ! -f "$REGISTRY_FILE" ]; then
        echo "{}"
        return 1
    fi
    
    jq '.services' "$REGISTRY_FILE"
}

# Function to detect actual port being used by a process
detect_process_port() {
    local pid="$1"
    local port_range="$2"  # Optional: comma-separated list of ports to check
    
    if [ -z "$pid" ]; then
        echo "null"
        return 1
    fi
    
    # Try lsof first (most reliable)
    if command -v lsof &> /dev/null; then
        local port=$(lsof -Pan -p "$pid" -i 2>/dev/null | grep LISTEN | head -1 | awk '{print $9}' | cut -d: -f2)
        if [ ! -z "$port" ]; then
            echo "$port"
            return 0
        fi
    fi
    
    # Fallback: check specific port range if provided
    if [ ! -z "$port_range" ]; then
        IFS=',' read -ra PORTS <<< "$port_range"
        for port in "${PORTS[@]}"; do
            if lsof -i ":$port" 2>/dev/null | grep -q "$pid"; then
                echo "$port"
                return 0
            fi
        done
    fi
    
    echo "null"
    return 1
}

# Function to check if service is actually running
is_service_running() {
    local service_name="$1"
    local pid=$(get_service_info "$service_name" "pid")
    
    if [ "$pid" = "null" ] || [ -z "$pid" ]; then
        return 1
    fi
    
    # Check if process is still running
    if kill -0 "$pid" 2>/dev/null; then
        return 0
    else
        # Process is dead, update registry
        update_service "$service_name" "null" "null" "stopped"
        return 1
    fi
}

# Function to detect Plasmo port dynamically
detect_plasmo_port() {
    local pid="$1"
    
    # Check common Plasmo ports
    for port in 1815 1816 1817 1818 1819 1820; do
        if lsof -i ":$port" 2>/dev/null | grep -q "$pid"; then
            echo "$port"
            return 0
        fi
    done
    
    echo "null"
    return 1
}

# Function to initialize registry if it doesn't exist
init_registry() {
    if [ ! -f "$REGISTRY_FILE" ]; then
        cat > "$REGISTRY_FILE" << 'EOF'
{
  "services": {
    "mcp_server": {
      "pid": null,
      "port": 8000,
      "url": "http://localhost:8000",
      "health_endpoint": "http://localhost:8000/health",
      "status": "stopped",
      "start_time": null,
      "log_file": "logs/mcp_server.log"
    },
    "socketio_server": {
      "pid": null,
      "port": 3001,
      "url": "http://localhost:3001",
      "health_endpoint": "http://localhost:3001/",
      "status": "stopped",
      "start_time": null,
      "log_file": "logs/socketio_server.log"
    },
    "plasmo_dev": {
      "pid": null,
      "port": null,
      "url": null,
      "health_endpoint": null,
      "status": "stopped",
      "start_time": null,
      "log_file": "logs/plasmo_dev.log",
      "port_range": [1815, 1816, 1817, 1818]
    },
    "test_runner": {
      "pid": null,
      "port": null,
      "url": null,
      "health_endpoint": null,
      "status": "stopped",
      "start_time": null,
      "log_file": "logs/continuous_testing.log"
    }
  },
  "last_updated": null,
  "script_version": "1.0"
}
EOF
    fi
}

# Function to clean up registry (remove dead processes)
cleanup_registry() {
    ensure_jq || return 1
    
    local services=("mcp_server" "socketio_server" "plasmo_dev" "test_runner")
    
    for service in "${services[@]}"; do
        if ! is_service_running "$service"; then
            update_service "$service" "null" "null" "stopped"
        fi
    done
}

# Export functions for use in other scripts
export -f update_service get_service_info get_all_services detect_process_port is_service_running detect_plasmo_port init_registry cleanup_registry ensure_jq 