# 🐛 **MASTER DEBUGGING GUIDE**
## Plasmo Chrome Extension with MCP Server Integration

**Version:** 3.0.0 | **Last Updated:** 2025-01-27 | **Status:** ✅ **ANALYSIS COMPLETE + ACTION PLAN READY**

---

## 📋 **EXECUTIVE SUMMARY**

This guide provides a comprehensive root-cause analysis of the Plasmo MCP server debugging infrastructure, with detailed solutions for identified issues. The system has evolved through multiple iterations, creating complexity that requires systematic cleanup and consolidation.

### **Key Findings**
- **19 generic exception handlers** in main MCP server (should use enhanced error handling)
- **4+ duplicate `make_json_safe` functions** across codebase (needs consolidation)
- **Browser automation redundancy** (Playwright vs Chrome Debug Protocol overlap)
- **Multiple MCP server artifacts** (757-line root server vs 3,113-line package server)
- **Service orchestration complexity** with inconsistent error handling patterns
- **Native tools system** requires validation and LLM capability testing

---

## 🔍 **ROOT CAUSE ANALYSIS**

### **Issue 1: Error Handling Inconsistency** 🔴 **HIGH PRIORITY**

**Root Cause Identified:**
- **Main MCP Server (`packages/mcp-server/mcp_server.py`)**: 19 instances of `except Exception as e:` with basic error responses
- **Enhanced System (`packages/mcp-server/core/error_handling.py`)**: Sophisticated error handling with agent tracking, error IDs, and specific exception types
- **Gap**: Main server doesn't leverage the advanced error handling system already built

**Impact:**
- Inconsistent error responses across tools
- Missing error tracking and debugging capabilities
- Poor user experience with generic error messages

**Evidence:**
```python
# CURRENT: Basic error handling (19 instances)
except Exception as e:
    return {"success": False, "error": str(e)}

# SHOULD BE: Enhanced error handling
except Exception as e:
    return enhanced_handle_error("tool_name", e, context)
```

**Files Affected:**
- `packages/mcp-server/mcp_server.py` (main server)
- All 19 tool functions with generic exception handling

### **Issue 2: JSON Serialization Redundancy** 🔴 **HIGH PRIORITY**

**Root Cause Identified:**
- **4+ different `make_json_safe` implementations** scattered across files
- **Evolution Pattern**: Function evolved from simple to complex Unicode handling
- **Chrome Debug Protocol Objects**: pychrome objects contain non-serializable data
- **FastMCP Integration**: ✅ **FOUND!** FastMCP has built-in `tool_serializer` parameter

**Impact:**
- Code duplication and maintenance overhead
- Inconsistent Unicode handling approaches
- Manual serialization calls cluttering tool functions

**Evidence:**
```python
# Multiple implementations found in:
# - packages/mcp-server/mcp_server.py
# - template_server.py
# - dt_server.py
# - packages/mcp-server/core/json_utils.py (canonical version)

# FastMCP Solution Available:
mcp = FastMCP(
    name="Server",
    tool_serializer=fastmcp_serializer  # Built-in support!
)
```

### **Issue 3: Browser Automation Redundancy** 🟡 **MEDIUM PRIORITY**

**Root Cause Identified:**
- **Playwright Tools**: High-level browser automation with better APIs
- **Chrome Debug Protocol Tools**: Low-level WebSocket-based debugging
- **Overlap**: Both can launch browsers, navigate, execute JavaScript, take screenshots

**Analysis:**
- **Playwright Advantages**: Higher-level APIs, built-in waiting, better error handling, cross-browser support, built-in debugging tools
- **Chrome Debug Protocol Disadvantages**: Low-level complexity, manual waiting, Chrome-specific only, more prone to timing issues

**Recommendation:**
1. **Keep Playwright tools** (superior for most use cases)
2. **Remove Chrome Debug Protocol tools** from main MCP server
3. **Move CDP tools to separate server** if needed for specific debugging scenarios

### **Issue 4: MCP Server Artifact Cleanup** 🟡 **MEDIUM PRIORITY**

**Root Cause Identified:**
- **Root `mcp_server.py`**: 757-line artifact (NOT the active server)
- **`packages/mcp-server/mcp_server.py`**: 3,113-line active server with advanced features

**Impact:**
- Confusion about which server is active
- Documentation referencing wrong server
- Potential conflicts if both are running

**Evidence:**
```bash
# Root server (artifact):
# - 757 lines
# - Basic functionality
# - Generic error handling

# Package server (active):
# - 3,113 lines
# - Advanced features (agent management, service orchestration)
# - Enhanced error handling
# - Modular architecture
```

### **Issue 5: Service Orchestration Complexity** 🟡 **MEDIUM PRIORITY**

**Root Cause Identified:**
- **Multiple Services**: MCP server, Socket.IO server, Plasmo dev server, continuous testing
- **Inconsistent Error Handling**: Different services use different error patterns
- **Coordination Challenges**: Services may conflict or have dependency issues

**Impact:**
- Complex startup/shutdown procedures
- Potential service conflicts
- Difficult troubleshooting when issues occur

### **Issue 6: Native Tools System Validation** 🟡 **MEDIUM PRIORITY**

**Root Cause Identified:**
- **Native Tools Registry**: YAML-based configuration with 25+ tools
- **LLM Integration**: Designed for AI assistant interaction
- **Validation Gap**: System architecture complete but needs LLM capability testing

**Requirements:**
- Tool discovery testing (can LLM find appropriate tools?)
- Tool execution testing (can LLM execute tools correctly?)
- Tool combination testing (can LLM orchestrate multiple tools?)

---

## 🎯 **COMPREHENSIVE ACTION PLAN**

### **Phase 1: Immediate Fixes (High Priority)**

#### **1.1 Standardize Error Handling**
**Goal:** Replace all generic exception handlers with enhanced error handling

**Implementation Plan:**
```python
# Step 1: Import enhanced error handling
from core.error_handling import enhanced_handle_error

# Step 2: Replace all 19 instances in mcp_server.py
# BEFORE:
except Exception as e:
    return {"success": False, "error": str(e)}

# AFTER:
except Exception as e:
    return enhanced_handle_error("tool_name", e, {
        "param1": param1_value,
        "param2": param2_value
    })
```

**Files to Modify:**
- `packages/mcp-server/mcp_server.py` (19 replacements)
- Verify all tools use consistent error format

**Testing:**
- Test each tool with error conditions
- Verify error IDs are generated and retrievable
- Confirm agent-specific error tracking works

#### **1.2 Consolidate JSON Serialization**
**Goal:** Create single canonical serializer and remove duplicates

**Implementation Plan:**
```python
# Step 1: Create canonical serializer in core/json_utils.py
def fastmcp_serializer(obj: Any) -> str:
    """Canonical serializer for FastMCP integration."""
    # Handle Unicode, datetime, complex objects
    # Return JSON string that FastMCP can handle

# Step 2: Update FastMCP initialization
mcp = FastMCP(
    name="Cursor Development Assistant",
    tool_serializer=fastmcp_serializer
)

# Step 3: Remove manual serialization calls
# Remove @json_safe_response decorators
# Remove make_json_safe() calls from tool functions
```

**Files to Clean Up:**
- Remove `make_json_safe` from `packages/mcp-server/mcp_server.py`
- Remove `make_json_safe` from `template_server.py`
- Remove `make_json_safe` from `dt_server.py`
- Keep only canonical version in `core/json_utils.py`

### **Phase 2: Architecture Cleanup (Medium Priority)**

#### **2.1 Remove MCP Server Artifact**
**Goal:** Clean up root-level server artifact

**Implementation Plan:**
```bash
# Step 1: Backup and remove artifact
cp mcp_server.py mcp_server_artifact_backup.py
rm mcp_server.py

# Step 2: Update documentation references
# Update all docs to reference packages/mcp-server/mcp_server.py

# Step 3: Update any configuration files
# Ensure all scripts point to the correct server location
```

**Documentation Updates:**
- Update `docs/mcp/MCP_README.md`
- Update `docs/plasmo/CHROME_DEBUG_README.md`
- Update any configuration files

#### **2.2 Browser Automation Consolidation**
**Goal:** Choose primary browser automation approach

**Implementation Plan:**
```python
# Option A: Keep Playwright as primary (RECOMMENDED)
# Remove CDP tools from main server:
# - launch_chrome_debug()
# - connect_to_chrome()
# - execute_javascript_fixed()
# - start_console_monitoring()
# - get_console_logs()
# - clear_console_logs()
# - get_chrome_debug_info()

# Option B: Create separate CDP server
# Move CDP tools to dedicated server for specific debugging scenarios
```

**Migration Strategy:**
1. Keep Playwright tools (superior APIs)
2. Remove CDP tools from main MCP server
3. Update documentation to reflect Playwright focus
4. Move CDP tools to separate server if needed

### **Phase 3: System Validation (Ongoing)**

#### **3.1 Native Tools System Validation**
**Goal:** Ensure LLM can effectively use the native tools system

**Validation Checklist:**
- [ ] Tool Discovery: Can LLM find appropriate tools for given tasks?
- [ ] Tool Execution: Can LLM execute tools with correct parameters?
- [ ] Tool Combination: Can LLM orchestrate multiple tools for complex tasks?
- [ ] Error Recovery: Does system handle errors gracefully?

**Testing Approach:**
```python
# Test scenarios:
test_scenarios = [
    "I need to install a Python package",
    "Show me the current project structure",
    "Take a beautiful screenshot with AI",
    "Inject a prompt into Cursor AI chat",
    "Monitor console logs in Chrome"
]
```

#### **3.2 Service Orchestration Validation**
**Goal:** Ensure all services work together reliably

**Service Health Checks:**
```bash
# Automated health verification
./check_services.sh
curl http://localhost:8000/health  # MCP Server
curl http://localhost:3001/api/status  # Socket.IO Server
# Verify Plasmo dev server status
```

### **Phase 4: Documentation Consolidation**

#### **4.1 Create Unified Debugging Guide**
**Goal:** Single source of truth for debugging information

**Structure:**
1. **Quick Start**: Common debugging scenarios with solutions
2. **Architecture Overview**: How components work together
3. **Troubleshooting Guide**: Common issues and fixes
4. **Advanced Debugging**: Deep-dive analysis techniques
5. **API Reference**: Complete tool and function reference

#### **4.2 Update All References**
**Goal:** Ensure all documentation points to correct files and servers

**Files to Update:**
- Consolidate multiple debugging guides into single master guide
- Update all MCP server references to point to active server
- Remove references to deprecated tools and functions

---

## 🛠️ **IMMEDIATE ACTION ITEMS**

### **Priority 1: Error Handling Standardization**
```bash
# 1. Review current error handling patterns
grep -n "except Exception as e:" packages/mcp-server/mcp_server.py

# 2. Apply enhanced error handling to all 19 instances
# 3. Test error scenarios for each tool
# 4. Verify error tracking and retrieval works
```

### **Priority 2: JSON Serialization Cleanup**
```bash
# 1. Identify all make_json_safe implementations
find . -name "*.py" -exec grep -l "def make_json_safe" {} \;

# 2. Create canonical version in core/json_utils.py
# 3. Update FastMCP initialization to use tool_serializer
# 4. Remove duplicate implementations
```

### **Priority 3: MCP Server Cleanup**
```bash
# 1. Verify which server is actually active
ps aux | grep mcp_server

# 2. Backup and remove artifact if confirmed inactive
# 3. Update all documentation references
# 4. Test that system still works after cleanup
```

### **Priority 4: Browser Automation Decision**
```python
# Analyze usage patterns
playwright_usage = count_playwright_tool_calls()
cdp_usage = count_cdp_tool_calls()

# Make decision based on usage and capabilities
if playwright_usage > cdp_usage:
    # Remove CDP tools from main server
    remove_cdp_tools_from_main_server()
else:
    # Keep both but document clearly when to use each
    document_browser_automation_strategy()
```

---

## 🔬 **ADVANCED DEBUGGING TECHNIQUES**

### **WebSocket Message Analysis**
```python
# Monitor Chrome Debug Protocol messages
def analyze_websocket_messages():
    """Analyze WebSocket message patterns for debugging."""
    # Filter extension noise
    # Monitor command/response correlation
    # Identify timing issues
```

### **LLM Tool Discovery Testing**
```python
def test_llm_tool_discovery():
    """Test LLM ability to discover and use tools."""
    test_prompts = [
        "I need to see the project structure",
        "Install numpy package",
        "Take a screenshot",
        "Monitor browser console"
    ]
    # Test each prompt against native tools registry
```

### **Service Orchestration Debugging**
```python
def debug_service_orchestration():
    """Debug multi-service coordination issues."""
    # Check service health
    # Verify message passing
    # Test error propagation
    # Monitor resource usage
```

---

## 📊 **SUCCESS METRICS**

### **Phase 1 Success Criteria**
- [ ] All 19 generic exception handlers replaced with enhanced handling
- [ ] Error IDs generated and retrievable for all tools
- [ ] Agent-specific error tracking working
- [ ] Error suggestions provided for common issues

### **Phase 2 Success Criteria**
- [ ] Single canonical JSON serializer implemented
- [ ] FastMCP tool_serializer parameter utilized
- [ ] No duplicate make_json_safe implementations
- [ ] All tools use automatic serialization

### **Phase 3 Success Criteria**
- [ ] MCP server artifact removed
- [ ] All documentation updated
- [ ] No references to deprecated server
- [ ] System functionality verified after cleanup

### **Phase 4 Success Criteria**
- [ ] Browser automation strategy decided and documented
- [ ] Redundant tools removed or properly separated
- [ ] Clear guidance on when to use each automation approach

---

## 🚨 **MONITORING & MAINTENANCE**

### **Automated Health Checks**
```bash
# Daily health verification
#!/bin/bash
check_mcp_server_health
check_service_orchestration
check_error_handling_consistency
check_json_serialization
```

### **Error Tracking Dashboard**
- Monitor error rates by tool
- Track error resolution times
- Identify common failure patterns
- Generate error trend reports

### **Performance Monitoring**
- Tool execution times
- Memory usage patterns
- WebSocket connection stability
- Service response times

---

## 📚 **REFERENCES & RESOURCES**

### **Key Files**
- `packages/mcp-server/mcp_server.py` - Main active server
- `packages/mcp-server/core/error_handling.py` - Enhanced error system
- `packages/mcp-server/tools.yaml` - Native tools registry
- `service_manager.py` - Service orchestration

### **Related Documentation**
- `docs/mcp/MCP_README.md` - MCP server setup
- `docs/plasmo/CHROME_DEBUG_README.md` - Chrome debugging
- `CURRENT_STATUS.md` - Current system status
- `docs/mcp/INTERACTIVE_MCP_TUTORIAL_GUIDE.md` - Tutorial walkthrough

### **External Resources**
- [FastMCP Documentation](https://gofastmcp.com/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Plasmo Framework](https://docs.plasmo.com/)

---

**🎯 Next Steps:**
1. **Start with Phase 1** - Error handling standardization
2. **Test thoroughly** after each change
3. **Update documentation** as changes are made
4. **Validate system** after each phase completion

**📞 Support:** If issues arise during implementation, reference this guide's troubleshooting section or check the error logs for specific guidance.

---

**✅ Analysis Complete | Action Plan Ready | Ready for Implementation**
