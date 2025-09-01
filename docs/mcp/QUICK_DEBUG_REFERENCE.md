# 🚀 **QUICK DEBUG REFERENCE**
## Most Common Issues & Immediate Solutions

---

## 🔥 **CRITICAL: Immediate Fixes Needed**

### **1. Error Handling (19 instances to fix)**
```bash
# Find all generic exception handlers
grep -n "except Exception as e:" packages/mcp-server/mcp_server.py

# Replace with enhanced handling:
except Exception as e:
    return enhanced_handle_error("tool_name", e, {"param": value})
```

### **2. JSON Serialization (4+ duplicates)**
```bash
# Find all make_json_safe functions
find . -name "*.py" -exec grep -l "def make_json_safe" {} \;

# Use FastMCP's built-in tool_serializer instead
mcp = FastMCP(name="Server", tool_serializer=canonical_serializer)
```

### **3. MCP Server Cleanup**
```bash
# Check which server is running
ps aux | grep mcp_server

# Root server (757 lines) is artifact - active is packages/mcp-server/ (3113 lines)
```

---

## 🐛 **Common Error Patterns**

### **WebSocket Connection Issues**
```python
# Problem: Chrome Debug Protocol connection fails
# Solution: Use integer request IDs, not strings
request_id = int(time.time() * 1000000) % 1000000  # ✅ CORRECT
# request_id = str(uuid.uuid4())[:8]              # ❌ WRONG
```

### **Browser Automation Confusion**
```python
# Use Playwright for general automation (recommended)
await page.click('button')  # ✅ Higher-level, reliable

# Use CDP only for low-level debugging
cdp.execute_javascript('console.log("test")')  # ⚠️ Complex, error-prone
```

### **Service Orchestration Issues**
```bash
# Check service health
./check_services.sh
curl http://localhost:8000/health  # MCP Server
curl http://localhost:3001/api/status  # Socket.IO
```

---

## 🔧 **Quick Fixes**

### **Fix Error Handling**
```python
# Add to imports
from core.error_handling import enhanced_handle_error

# Replace generic handlers
except Exception as e:
    return enhanced_handle_error("tool_name", e, context)
```

### **Fix JSON Serialization**
```python
# Use FastMCP built-in
mcp = FastMCP(
    name="Server",
    tool_serializer=fastmcp_serializer  # From core/json_utils.py
)
```

### **Fix Browser Automation**
```python
# Prefer Playwright
from playwright.async_api import async_playwright

# Remove CDP if not needed
# CDP tools are redundant with Playwright
```

---

## 📋 **Priority Action Checklist**

### **HIGH PRIORITY (Fix Immediately)**
- [ ] Replace 19 generic exception handlers
- [ ] Consolidate JSON serialization functions
- [ ] Remove MCP server artifact (757-line root file)
- [ ] Choose browser automation approach (Playwright vs CDP)

### **MEDIUM PRIORITY (Fix Soon)**
- [ ] Validate native tools system with LLM
- [ ] Test service orchestration consistency
- [ ] Update all documentation references
- [ ] Clean up duplicate code

### **LOW PRIORITY (Ongoing)**
- [ ] Performance monitoring
- [ ] Error trend analysis
- [ ] Documentation consolidation
- [ ] Advanced debugging features

---

## 🎯 **Most Critical Issues**

1. **Error Handling Inconsistency** - 19 generic handlers need replacement
2. **JSON Serialization Redundancy** - 4+ duplicate functions
3. **MCP Server Artifact** - Confusing root-level server file
4. **Browser Automation Redundancy** - Playwright vs CDP overlap

---

## 📞 **When You Need Help**

### **Error Analysis**
```python
# Get detailed error information
from core.error_handling import get_last_errors
errors = get_last_errors("your_agent_name")
```

### **System Health**
```bash
# Comprehensive system check
./check_services.sh
python -m pytest packages/mcp-server/tests/ -v
```

### **Performance Issues**
```python
# Monitor tool execution times
import time
start = time.time()
result = tool_function()
duration = time.time() - start
```

---

## 🚨 **Emergency Fixes**

### **If MCP Server Won't Start**
```bash
# Kill any running instances
pkill -f mcp_server

# Start clean instance
cd packages/mcp-server
python mcp_server.py
```

### **If Chrome Debug Fails**
```bash
# Restart Chrome with proper flags
./launch-chrome-debug.sh

# Check connection
curl http://localhost:9222/json
```

### **If Services Conflict**
```bash
# Stop all services
./stop_all_services.sh

# Start in correct order
./start_all_services.sh
```

---

**📖 Full Documentation:** See `docs/mcp/MASTER_DEBUGGING_GUIDE.md` for complete analysis and detailed solutions.

**🎯 Start Here:** Focus on the 4 high-priority issues above, then move to medium-priority items.
