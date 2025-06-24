# Claude Instances → MCP Proxy Migration Plan

## 🎯 **Objective**
Migrate all Claude instances (Desktop + Code) to connect through the MCP Proxy instead of directly to the MCP server.

## 📊 **Current State**
- **MCP Server**: Port 8000 (HTTP) - PID 79718
- **MCP Proxy**: STDIO mode → backend http://localhost:8000/mcp - PID 69024  
- **Claude Desktop**: Direct STDIO connection to MCP server
- **Claude Code**: 3 instances running (PIDs: 6121, 85175, 10846)

## 🎯 **Target State**
- **All Claude instances** → MCP Proxy (STDIO) → MCP Server (HTTP)
- **Centralized management** through proxy
- **Enhanced monitoring** and debugging capabilities

## 📋 **Migration Steps**

### **Phase 1: Configuration Preparation**

1. **Create Proxy Configuration for Claude Desktop**
   ```json
   {
     "mcpServers": {
       "proxy-server": {
         "command": "python",
         "args": [
           "/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_proxy.py",
           "--stdio",
           "--backend-url",
           "http://localhost:8000/mcp"
         ],
         "cwd": "/Users/MikeWolf/Projects/Plasmo",
         "description": "Plasmo MCP Proxy - Central Hub"
       }
     }
   }
   ```

2. **Create Claude Code Configuration Scripts**
   - Script to configure each Claude Code instance
   - Shared proxy configuration template

### **Phase 2: Proxy Validation**

1. **Test Proxy Connectivity**
   - Verify proxy can reach MCP server
   - Test all 30 tools (28 backend + 3 proxy)
   - Validate Claude instance management tools

2. **Create Test Configuration**
   - Temporary proxy configuration for testing
   - Validation scripts for each connection

### **Phase 3: Sequential Migration**

1. **Kill and Reconfigure Claude Desktop**
   - Backup current config
   - Update config to proxy
   - Restart Claude Desktop
   - Verify connection

2. **Kill and Reconfigure Claude Code Instances**
   - Identify each instance configuration
   - Update configurations to proxy
   - Restart each instance individually
   - Verify each connection

### **Phase 4: Verification & Testing**

1. **Connection Testing**
   - Test all MCP tools through proxy
   - Verify Claude instance management
   - Test multi-agent coordination

2. **Performance Validation**
   - Response time comparison
   - Tool availability verification
   - Error handling testing

## 🔧 **Implementation Commands**

### **Backup Phase**
```bash
# Backup configurations
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ./backup/
cp claude_desktop_config.json ./backup/claude_desktop_local_backup.json
```

### **Kill Phase**
```bash
# Kill Claude Desktop
killall Claude

# Kill Claude Code instances 
kill 6121 85175 10846
```

### **Configuration Phase**
```bash
# Update Claude Desktop config
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "proxy-server": {
      "command": "python",
      "args": [
        "/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_proxy.py",
        "--stdio"
      ],
      "cwd": "/Users/MikeWolf/Projects/Plasmo"
    }
  }
}
EOF
```

### **Restart Phase**
```bash
# Restart Claude Desktop
open -a Claude

# Restart Claude Code instances (manual process)
# Each instance needs individual configuration
```

### **Verification Phase**
```bash
# Test proxy health
python -c "
import sys
sys.path.append('packages/mcp-server')
from mcp_proxy import create_enhanced_proxy
proxy = create_enhanced_proxy('http://localhost:8000/mcp', True)
print('✅ Proxy creation successful')
"

# Test tool availability
# Connect to Claude and run: 'What MCP tools are available?'
```

## ⚠️ **Risk Mitigation**

1. **Backup Strategy**
   - All configurations backed up before changes
   - Quick rollback procedure documented

2. **Service Dependencies**  
   - Ensure MCP server stays running during migration
   - Proxy service monitored throughout process

3. **Validation Steps**
   - Each instance tested before proceeding to next
   - Immediate rollback if issues detected

## 🎯 **Success Criteria**

- ✅ All Claude instances connect through proxy
- ✅ All 30 MCP tools accessible via proxy
- ✅ Claude instance management tools working
- ✅ No degradation in response times
- ✅ Enhanced debugging capabilities active

## 📊 **Expected Benefits**

1. **Centralized Management**
   - Single point of MCP server connection
   - Unified logging and monitoring

2. **Enhanced Debugging**
   - Proxy-level request/response logging
   - Better error tracking and diagnostics

3. **Scalability**
   - Easy addition of new Claude instances
   - Load balancing capabilities

4. **Service Reliability** 
   - Proxy can handle backend reconnections
   - Graceful failover handling 