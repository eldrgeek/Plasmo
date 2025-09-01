# 🚀 **Native Tools System Implementation Plan**

## 📋 **Executive Summary**

This plan outlines the complete implementation of the Native Tools System for the Plasmo MCP server. The system will enable AI-powered tool discovery, execution, and management of all factored-out tools through a centralized registry and execution engine.

**Current Status**: ✅ Core MCP tools reduced from 44 to 19, all specialized tools factored out to modules  
**Goal**: Implement full native tools system to make all 25+ factored-out tools accessible via AI discovery

---

## 🏗️ **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (19 core tools)              │
├─────────────────────────────────────────────────────────────┤
│                Native Tools System                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   Registry  │ │  Executor   │ │  Validator  │         │
│  │             │ │             │ │             │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│              Factored-Out Tool Modules                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   Firebase  │ │    Agents   │ │  Services   │         │
│  │   (4 tools) │ │  (4 tools)  │ │ (8 tools)  │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
│  ┌─────────────┐ ┌─────────────┐                         │
│  │ Automation  │ │   Native    │                         │
│  │ (3 tools)   │ │ Tools (5)   │                         │
│  └─────────────┘ └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 **Current File Structure & Locations**

### **Core MCP Server**
- **Location**: `packages/mcp-server/mcp_server.py`
- **Status**: ✅ Cleaned up, 19 core tools remaining
- **Size**: Reduced from 4,336 lines to ~3,000 lines

### **Factored-Out Tool Modules**

#### **1. Firebase Tools Module**
- **Location**: `packages/mcp-server/firebase/`
- **Files**: 
  - `__init__.py` - Module initialization
  - `project_management.py` - 4 Firebase automation tools
- **Tools**: firebase_setup_new_project, firebase_configure_existing_project, firebase_project_status, firebase_batch_operations

#### **2. Agent Management Module**
- **Location**: `packages/mcp-server/agents/`
- **Files**:
  - `__init__.py` - Module initialization  
  - `claude_instances.py` - 4 Claude instance management tools
- **Tools**: launch_claude_instance, list_claude_instances, send_inter_instance_message, coordinate_claude_instances

#### **3. Service Orchestration Module**
- **Location**: `packages/mcp-server/services/`
- **Files**:
  - `__init__.py` - Module initialization
  - `orchestrator.py` - 8 service management tools
- **Tools**: service_status, start_service, stop_service, restart_service, start_all_services, stop_all_services, service_logs, service_health_check

#### **4. Automation Module**
- **Location**: `packages/mcp-server/automation/`
- **Files**:
  - `__init__.py` - Module initialization
  - `orchestration.py` - 1 multi-LLM coordination tool
  - `native_automation.py` - 2 native automation tools
- **Tools**: send_orchestration_command, inject_prompt_native, focus_and_type_native

### **Native Tools Configuration**
- **Location**: `packages/mcp-server/tools.yaml`
- **Status**: ✅ Complete with all 25+ factored-out tools registered
- **Content**: Tool definitions with parameters, use cases, and validation rules

---

## 🎯 **Implementation Phases**

### **Phase 1: Core Infrastructure (Priority 1)**
**Goal**: Build the foundation for tool discovery and execution

#### **1.1 Create Native Tools Module Structure**
```
packages/mcp-server/native_tools/
├── __init__.py              # Module initialization
├── registry.py              # Tool registry management
├── validator.py              # Tool validation system
├── executor.py              # Tool execution engine
├── watcher.py               # File watching for hot reload
└── exceptions.py            # Custom exception classes
```

#### **1.2 Implement Core Classes**

**ToolRegistry Class**:
- Load tools from `tools.yaml`
- Parse YAML with error handling
- Support hot reloading
- Tool categorization and search

**ToolValidator Class**:
- Validate tool configurations
- Check dependencies
- Verify module/function existence
- Test command execution

**ToolExecutor Class**:
- Execute tools dynamically
- Handle parameter validation
- Manage execution context
- Error handling and logging

**FileWatcher Class**:
- Monitor `tools.yaml` for changes
- Auto-reload registry on updates
- Debounced reloading
- Change notification system

### **Phase 2: Integration & Testing (Priority 2)**
**Goal**: Integrate with MCP server and ensure reliability

#### **2.1 MCP Server Integration**
- Import native tools system in main server
- Initialize registry on startup
- Handle tool discovery requests
- Manage tool execution lifecycle

#### **2.2 Testing Infrastructure**
- Unit tests for all components
- Integration tests with MCP server
- End-to-end tool execution tests
- Performance and reliability tests

### **Phase 3: AI-Powered Discovery (Priority 3)**
**Goal**: Enable intelligent tool discovery and recommendations

#### **3.1 Intent Analysis System**
- Parse user intent from natural language
- Match intent to available tools
- Confidence scoring for matches
- Tool combination suggestions

#### **3.2 Use Case Matching**
- Semantic search across tool descriptions
- Keyword-based matching
- Category-based filtering
- Tool relationship mapping

---

## 🔧 **Technical Implementation Details**

### **1. Tool Registry System**

#### **YAML Configuration Structure**
```yaml
# Example from current tools.yaml
firebase_setup_new_project:
  name: firebase_setup_new_project
  description: Create a complete new Firebase project with full automation
  category: cloud_services
  module: firebase.project_management
  function: firebase_setup_new_project
  supports_persistent: false
  requires_review: true
  keywords: [firebase, gcp, project, setup, automation, cloud]
  
  parameters:
    project_id:
      type: string
      required: true
      description: Unique project identifier
      
  validation:
    script_exists: true
    dependencies: [python3, firebase-cli]
    test_command: firebase --version
    
  use_cases:
    - I want to create a new Firebase project
    - Set up cloud infrastructure
    - Initialize Firebase services
```

#### **Registry Loading Process**
```python
class ToolRegistry:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.tools = {}
        self.categories = set()
        self.load_registry()
    
    def load_registry(self) -> bool:
        """Load tools from YAML configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for tool_name, tool_config in config.items():
                if tool_name != 'version':  # Skip metadata
                    self.register_tool(tool_name, tool_config)
            
            return True
        except Exception as e:
            logger.error(f"Failed to load tool registry: {e}")
            return False
```

### **2. Tool Validation System**

#### **Validation Checks**
```python
class ToolValidator:
    def validate_tool(self, tool_name: str, tool_config: dict) -> ValidationResult:
        """Comprehensive tool validation"""
        result = ValidationResult(tool_name)
        
        # Check module import
        if not self._validate_module(tool_config):
            result.add_error("Module import failed")
        
        # Check function existence
        if not self._validate_function(tool_config):
            result.add_error("Function not found")
        
        # Check dependencies
        if not self._validate_dependencies(tool_config):
            result.add_error("Dependencies not met")
        
        # Test execution (optional)
        if tool_config.get('validation', {}).get('test_command'):
            if not self._test_execution(tool_config):
                result.add_warning("Test execution failed")
        
        return result
```

### **3. Tool Execution Engine**

#### **Dynamic Execution**
```python
class ToolExecutor:
    def execute_tool(self, tool_name: str, tool_config: dict, 
                    parameters: dict, mode: str = "once") -> ExecutionResult:
        """Execute a tool dynamically"""
        try:
            # Import module dynamically
            module_name = tool_config['module']
            function_name = tool_config['function']
            
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            # Validate parameters
            validated_params = self._validate_parameters(tool_config, parameters)
            
            # Execute function
            if asyncio.iscoroutinefunction(function):
                result = await function(**validated_params)
                result = await function(**validated_params)
            else:
                result = function(**validated_params)
            
            return ExecutionResult(
                success=True,
                tool_name=tool_name,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                tool_name=tool_name,
                error=str(e),
                error_type=type(e).__name__
            )
```

---

## 🧪 **Testing Strategy**

### **Test Coverage Requirements**
- **Unit Tests**: 100% coverage for core classes
- **Integration Tests**: Tool execution end-to-end
- **Performance Tests**: Registry loading and tool discovery
- **Error Handling Tests**: Invalid configurations and failures

### **Test Files Structure**
```
packages/mcp-server/tests/
├── test_native_tools_registry.py
├── test_native_tools_validator.py
├── test_native_tools_executor.py
├── test_native_tools_watcher.py
├── test_native_tools_integration.py
└── test_native_tools_performance.py
```

---

## 🚀 **Deployment & Integration**

### **1. MCP Server Integration**
```python
# In mcp_server.py
try:
    from native_tools import ToolRegistry, ToolValidator, ToolExecutor, FileWatcher
    
    # Initialize native tools system
    tool_registry = ToolRegistry("tools.yaml")
    tool_validator = ToolValidator()
    tool_executor = ToolExecutor()
    
    # Start file watcher for hot reload
    file_watcher = FileWatcher("tools.yaml", tool_registry.load_registry)
    file_watcher.start_watching()
    
    logger.info("✅ Native tools system initialized")
    
except ImportError as e:
    logger.warning(f"⚠️ Native tools system not available: {e}")
    tool_registry = None
    tool_validator = None
    tool_executor = None
```

### **2. MCP Tool Registration**
```python
@mcp.tool()
def list_available_tools(category: str = "all", include_status: bool = False) -> Dict[str, Any]:
    """List all available native tools in the registry"""
    if not tool_registry:
        return {"success": False, "error": "Native tools system not available"}
    
    tools = tool_registry.list_tools(category, include_status)
    return {"success": True, "tools": tools}

@mcp.tool()
def discover_tools_by_intent(intent: str, max_suggestions: int = 3) -> Dict[str, Any]:
    """AI-powered tool discovery based on user intent"""
    if not tool_registry:
        return {"success": False, "error": "Native tools system not available"}
    
    suggestions = tool_registry.search_by_intent(intent, max_suggestions)
    return {"success": True, "suggestions": suggestions}

@mcp.tool()
def execute_native_tool(tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a native tool from the registry"""
    if not tool_registry or not tool_executor:
        return {"success": False, "error": "Native tools system not available"}
    
    tool_config = tool_registry.get_tool(tool_name)
    if not tool_config:
        return {"success": False, "error": f"Tool '{tool_name}' not found"}
    
    result = tool_executor.execute_tool(tool_name, tool_config, parameters or {})
    return result
```

---

## 📊 **Success Metrics & Validation**

### **Functional Requirements**
- ✅ All 25+ factored-out tools discoverable via native tools system
- ✅ Tool execution works reliably for all tool types
- ✅ Hot reloading works when `tools.yaml` changes
- ✅ Error handling provides clear feedback
- ✅ Performance meets MCP server requirements

### **Performance Requirements**
- Registry loading: < 1 second
- Tool discovery: < 100ms
- Tool execution: < 5 seconds (excluding tool runtime)
- Memory usage: < 50MB additional

### **User Experience Requirements**
- AI assistants can discover tools by intent
- Clear error messages for failed operations
- Tool documentation accessible through discovery
- Seamless integration with existing MCP tools

---

## 🔍 **Key Implementation Challenges**

### **1. Dynamic Module Importing**
- **Challenge**: Importing modules dynamically at runtime
- **Solution**: Use `importlib.import_module()` with proper error handling
- **Fallback**: Graceful degradation when modules unavailable

### **2. Parameter Validation**
- **Challenge**: Validating parameters against tool configurations
- **Solution**: Type checking and parameter schema validation
- **Fallback**: Clear error messages for invalid parameters

### **3. Error Handling & Recovery**
- **Challenge**: Managing failures in tool execution
- **Solution**: Comprehensive error categorization and recovery
- **Fallback**: Graceful degradation and user feedback

### **4. Performance Optimization**
- **Challenge**: Maintaining fast tool discovery and execution
- **Solution**: Caching, lazy loading, and efficient data structures
- **Fallback**: Progressive enhancement for complex operations

---

## 📚 **Resources & Dependencies**

### **Required Python Packages**
```python
# Add to requirements.txt
pyyaml>=6.0          # YAML parsing
watchdog>=3.0         # File watching
importlib-metadata    # Module metadata (Python < 3.8)
```

### **Documentation References**
- **Current tools.yaml**: Complete tool registry configuration
- **MCP Server**: Main server implementation and tool decorators
- **Factored Modules**: Tool implementations in dedicated modules
- **FastMCP Documentation**: Framework-specific implementation details

---

## 🎯 **Next Steps for New Conversation**

### **Immediate Actions**
1. **Review this plan** and understand the current state
2. **Examine the existing code** in the specified locations
3. **Start with Phase 1** - Core Infrastructure implementation
4. **Build incrementally** with testing at each step

### **Key Files to Examine**
- `packages/mcp-server/tools.yaml` - Complete tool registry
- `packages/mcp-server/mcp_server.py` - Current MCP server state
- `packages/mcp-server/firebase/`, `agents/`, `services/`, `automation/` - Factored modules

### **Success Criteria**
- Native tools system loads and initializes successfully
- All 25+ factored-out tools are discoverable
- Tool execution works reliably
- Integration with MCP server is seamless

This plan provides a complete roadmap for implementing the Native Tools System. The foundation is already in place with the factored-out modules and YAML configuration. The next conversation should focus on building the core infrastructure to bring this system to life! 🚀
