# 🔍 MCP Server Files Audit & Cleanup Plan

## 📊 Executive Summary

**Problem**: Multiple MCP server instances causing confusion and potential conflicts.
**Root Cause**: The correct MCP server is `/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_server.py` (4,336 lines), but there are several obsolete and duplicate files scattered throughout the project.

## 🎯 Critical Files Analysis

### ✅ **CORRECT/ACTIVE MCP SERVER**
- **📁 `/packages/mcp-server/mcp_server.py`** (4,336 lines)
  - **Purpose**: Main consolidated FastMCP server with comprehensive toolset
  - **Status**: ✅ Active, currently used
  - **Features**: Chrome debug, Firebase tools, agent management, file operations
  - **Recommendation**: ✅ **KEEP - This is the correct server**

---

## 🚨 **OBSOLETE/DUPLICATE FILES TO CLEAN UP**

### 🗑️ **Root Directory MCP Files (OBSOLETE)**

#### 1. ☑️ **`/mcp_server.py`** (756 lines) - **MIGRATE TOOLS FIRST, THEN DELETE**
- **Purpose**: Old Playwright-focused MCP server
- **Status**: 🚨 Modified but obsolete, BUT contains 3 unique tools
- **🔍 CRITICAL DISCOVERY**: Contains tools NOT in packages server:
  - ✅ `execute_command()` - Shell command execution with security checks
  - ✅ `run_instant_capture()` - Beautiful AI capture system launcher
  - ✅ `install_package()` - Python package installer via pip3
- **Issues**: 
  - Incomplete (calls undefined `main()` function)
  - Missing Firebase tools (user was confused about this)
  - Outdated FastMCP implementation
- **Recommendation**: ☑️ **MIGRATE TOOLS TO PACKAGES SERVER FIRST, THEN DELETE**

#### 2. ☑️ **`/mcp_server.py.backup.1756587233`** (624 lines) - **DELETE**
- **Purpose**: Backup of old root MCP server
- **Status**: 🗄️ Untracked backup file
- **Recommendation**: ☑️ **DELETE** - No longer needed

#### 3. ☑️ **`/mcp_server.py.backup.1756587213`** (624 lines) - **DELETE**
- **Purpose**: Backup of old root MCP server
- **Status**: 🗄️ Untracked backup file
- **Recommendation**: ☑️ **DELETE** - No longer needed

#### 4. ☑️ **`/mcp_server.py.backup.1756587205`** (624 lines) - **DELETE**
- **Purpose**: Backup of old root MCP server
- **Status**: 🗄️ Untracked backup file
- **Recommendation**: ☑️ **DELETE** - No longer needed

---

## 📦 **AUXILIARY MCP FILES**

### 🔒 **Security & Utilities**

#### 5. ☑️ **`/packages/mcp-server/mcp_server_secure.py`** (195 lines) - **COMMIT**
- **Purpose**: Security wrapper for external tunnel access
- **Status**: 🆕 Untracked, functional
- **Features**: API key auth, rate limiting, CORS
- **Recommendation**: ☑️ **COMMIT** - Useful for secure deployments

### 📝 **Documentation & Configuration**

#### 6. ☑️ **`/packages/mcp-server/MCP_SERVER_SIMPLIFICATION_RECOMMENDATIONS.md`** - **COMMIT**
- **Purpose**: Code organization recommendations
- **Status**: 🆕 Untracked documentation
- **Recommendation**: ☑️ **COMMIT** - Valuable project documentation

#### 7. ☑️ **`/packages/mcp-server/MCP_SERVER_DESIGN_REVIEW.md`** - **COMMIT**
- **Purpose**: Architecture design review
- **Status**: 🆕 Untracked documentation
- **Recommendation**: ☑️ **COMMIT** - Important design documentation

#### 8. ☑️ **`/docs/mcp/MCP_SERVER_REVIEW_SUMMARY.md`** - **COMMIT**
- **Purpose**: High-level review summary
- **Status**: 🆕 Untracked documentation
- **Recommendation**: ☑️ **COMMIT** - Move to packages/mcp-server/docs/

### 🛠️ **Development & Integration Tools**

#### 9. ☑️ **`/mcp_command_extension.py`** - **COMMIT**
- **Purpose**: Chrome extension integration
- **Status**: 🆕 Untracked, functional tool
- **Recommendation**: ☑️ **COMMIT** - Move to packages/mcp-server/tools/

#### 10. ☑️ **`/mcp_integration_instructions.py`** - **COMMIT**
- **Purpose**: Setup and integration helper
- **Status**: 🆕 Untracked, functional tool
- **Recommendation**: ☑️ **COMMIT** - Move to packages/mcp-server/tools/

#### 11. ☑️ **`/bolt_automation_mcp.py`** - **COMMIT**
- **Purpose**: Bolt.new automation via MCP
- **Status**: 🆕 Untracked, specialized tool
- **Recommendation**: ☑️ **COMMIT** - Move to packages/mcp-server/integrations/

---

## 📂 **SHARED SERVICES (SEPARATE CONCERN)**

#### 12. ☑️ **`/shared/python-common/services/mcp_service.py`** - **COMMIT**
- **Purpose**: Service orchestrator MCP integration
- **Status**: Part of shared service framework
- **Recommendation**: ☑️ **COMMIT** - Keep in shared services

#### 13. ☑️ **`/shared/python-common/services/mcp_tester_service.py`** - **COMMIT**
- **Purpose**: MCP testing service
- **Status**: Part of shared service framework
- **Recommendation**: ☑️ **COMMIT** - Keep in shared services

---

## 🧪 **TESTING INFRASTRUCTURE AUDIT**

### ✅ **EXCELLENT TESTING COVERAGE** 
The packages MCP server has **comprehensive testing infrastructure**:

**📊 Test Statistics:**
- **Total Test Files**: 11 test files (4,986 lines of test code)
- **MCP Tools Coverage**: 38/38 tools (100% comprehensive tests)
- **Test Categories**: Unit, Integration, Performance, Security
- **Test Runner**: Automated comprehensive test runner

**🎯 Key Test Files:**
- ☑️ `test_mcp_tools_comprehensive.py` (1,027 lines) - All 38 MCP tools
- ☑️ `test_agent_modules.py` (194 lines) - Agent management
- ☑️ `test_core_modules.py` (161 lines) - Core utilities
- ☑️ `run_comprehensive_tests.py` (439 lines) - Test orchestrator

### 🔍 **MISSING TESTS FOR MIGRATED TOOLS**

**🚨 Tests Needed for Root Server Tools:**
1. ☑️ **`execute_command()`** - No tests exist
   - **Security Testing**: Forbidden command detection
   - **Output Capture**: stdout/stderr handling  
   - **Error Handling**: Timeout, command failures
   - **Working Directory**: Path validation

2. ☑️ **`run_instant_capture()`** - No tests exist
   - **File Existence**: Script availability check
   - **Process Management**: Background execution
   - **Error Handling**: Missing dependencies

3. ☑️ **`install_package()`** - No tests exist
   - **Package Installation**: Valid package names
   - **Error Handling**: Invalid packages, network issues
   - **Security**: Package name validation

### 📋 **TEST CREATION PLAN**

#### **Phase 1: Create Missing Tests** ☑️
```python
# test_system_tools.py (NEW FILE)
def test_execute_command_basic()
def test_execute_command_security_checks()
def test_execute_command_forbidden_commands()
def test_execute_command_timeout()
def test_run_instant_capture_success()
def test_run_instant_capture_missing_script()
def test_install_package_success()
def test_install_package_invalid()
```

#### **Phase 2: Integration Testing** ☑️
```python
# test_migrated_tools_integration.py (NEW FILE)
def test_execute_command_with_working_dir()
def test_install_package_then_import()
def test_instant_capture_full_workflow()
```

---

## 🤖 **AUTOMATION SCRIPTS INTEGRATION ANALYSIS**

### 📊 **Discovered Automation Scripts** (15+ Files)

#### **🎯 AI Service Injectors** ☐
- ☐ **`cursor_ai_injector.py`** (642 lines) - Cross-platform Cursor AI chat automation
  - **Value**: HIGH - Direct Cursor integration, cross-platform
  - **Status**: Functional, well-documented
  - **Integration**: Register as "cursor_prompt_injector" tool
  
- ☐ **`gemini_native_injector.py`** (524 lines) - Gemini AI chat interface automation  
  - **Value**: HIGH - Google Gemini automation
  - **Status**: Native keyboard automation, cross-platform
  - **Integration**: Register as "gemini_prompt_injector" tool
  
- ☐ **`bolt_automation_playwright.py`** (305 lines) - Playwright-based Bolt.new automation
  - **Value**: MEDIUM - Code generation automation
  - **Status**: Needs testing, Playwright dependency
  - **Integration**: Register as "bolt_code_generator" tool

#### **📱 Web App Automation** ☐
- ☐ **`discord_export_automation.py`** (297 lines) - Discord channel export via MCP
  - **Value**: MEDIUM - Data extraction capability
  - **Status**: Uses MCP server integration
  - **Integration**: Register as "discord_channel_exporter" tool
  
- ☐ **`auto_click_automation.py`** (192 lines) - Auto-click automation via Chrome Debug
  - **Value**: LOW - Simple click automation (replace with generic tool)
  - **Status**: Very specific use case
  - **Integration**: Absorb into general automation framework

#### **🎯 Capture & Monitoring** ☐
- ☐ **`instant_capture_beautiful.py`** - Beautiful AI capture system
  - **Value**: HIGH - Already referenced in root mcp_server.py
  - **Status**: Functional, beautiful UI
  - **Integration**: Already planned for native tools

- ☐ **`focus_monitor.py`** - Window focus monitoring
  - **Value**: MEDIUM - System monitoring capability
  - **Status**: Background monitoring tool
  - **Integration**: Register as "focus_monitor" tool

#### **🔧 Infrastructure Automation** ☐
- ☐ **`extension_manager.py`** - Extension management automation
  - **Value**: HIGH - Development workflow automation
  - **Status**: Chrome extension lifecycle management
  - **Integration**: Register as "extension_manager" tool

### 🎯 **Automation Script Integration Strategy**

#### **Phase A: High-Value Scripts (Priority 1)** ☐
```yaml
# High-impact automation tools for immediate integration
priority_scripts:
  cursor_ai_injector: {value: HIGH, effort: LOW}
  gemini_native_injector: {value: HIGH, effort: LOW}  
  instant_capture_beautiful: {value: HIGH, effort: LOW}
  extension_manager: {value: HIGH, effort: MEDIUM}
```

#### **Phase B: Specialized Tools (Priority 2)** ☐
```yaml
# Specialized automation for specific workflows
specialized_scripts:
  discord_export_automation: {value: MEDIUM, effort: MEDIUM}
  bolt_automation_playwright: {value: MEDIUM, effort: HIGH}
  focus_monitor: {value: MEDIUM, effort: LOW}
```

#### **Phase C: Consolidation (Priority 3)** ☐
```yaml
# Scripts to consolidate or replace
consolidation_candidates:
  auto_click_automation: {action: REPLACE, reason: "Too specific"}
  duplicate_discord_exporters: {action: MERGE, reason: "Overlapping functionality"}
```

---

## 🚀 **NATIVE TOOL SYSTEM IMPLEMENTATION PLAN**

### 📋 **Phase 1: Core Infrastructure** ☐

#### **1.1 Tool Registry System** ☐
- ☐ Create `packages/mcp-server/tools.yaml` with forgiving YAML parser
- ☐ Design ToolRegistryManager class with hot reload capability  
- ☐ Implement file watcher for automatic registry updates
- ☐ Add validation system for tool configs
- ☐ Create example tools (instant_capture, package_installer)

#### **1.2 Core MCP Tools** ☐
- ☐ `discover_tools_by_intent()` - AI-powered tool discovery
- ☐ `list_available_tools()` - Traditional tool listing
- ☐ `execute_native_tool()` - Tool execution engine
- ☐ `validate_registered_tool()` - Tool validation system
- ☐ `tool_status()` - Process status monitoring

#### **1.3 File Structure** ☐
```
packages/mcp-server/
├── tools.yaml                    ☐ Tool registry config
├── native_tools/                 ☐ Tool management module
│   ├── __init__.py              ☐
│   ├── registry.py              ☐ Registry management
│   ├── validator.py             ☐ Tool validation
│   ├── executor.py              ☐ Tool execution
│   └── watcher.py               ☐ File watching
└── tests/
    └── test_native_tools.py      ☐ Comprehensive tests
```

### 📋 **Phase 2: AI Integration** ☐

#### **2.1 Claude Code Specialist** ☐
- ☐ Design persistent Claude instance launcher
- ☐ Implement non-blocking message queue system
- ☐ Create intent analysis workflow
- ☐ Add tool combination suggestions
- ☐ Design new tool recommendation system

#### **2.2 Expert System Tools** ☐
- ☐ `get_expert_suggestions()` - Comprehensive AI recommendations
- ☐ `get_intent_analysis_result()` - Async result retrieval
- ☐ `request_tool_execution_approval()` - Review system for sensitive tools
- ☐ `check_approval_status()` - Approval status checking

#### **2.3 AI Specialist Integration** ☐
- ☐ Configure Claude instance with tool discovery expertise
- ☐ Implement message routing between main MCP and specialist
- ☐ Add confidence scoring for tool suggestions
- ☐ Create workflow for tool combination recommendations

### 📋 **Phase 3: Security & Validation** ☐

#### **3.1 Security Framework** ☐
- ☐ Implement `requires_review` system for sensitive tools
- ☐ Create approval workflow for dangerous operations
- ☐ Add tool execution sandboxing options
- ☐ Design audit logging for tool executions

#### **3.2 Validation System** ☐
- ☐ Dependency checking (python3, pip3, etc.)
- ☐ Script existence validation
- ☐ Test command execution
- ☐ Automatic revalidation on file changes
- ☐ Health check reporting

#### **3.3 Process Management** ☐
- ☐ Persistent process tracking
- ☐ Process lifecycle management (start/stop/restart)
- ☐ Integration with existing service_manager.py
- ☐ Process health monitoring

### 📋 **Phase 4: Testing & Documentation** ☐

#### **4.1 Comprehensive Testing** ☐
- ☐ Unit tests for all native tool components
- ☐ Integration tests for AI specialist communication
- ☐ Security tests for approval system
- ☐ Performance tests for file watching
- ☐ End-to-end workflow tests

#### **4.2 Test Coverage** ☐
- ☐ Test tool registry loading and validation
- ☐ Test Claude specialist integration
- ☐ Test tool execution with various parameters
- ☐ Test error handling and recovery
- ☐ Test security and approval workflows

#### **4.3 Documentation** ☐
- ☐ Update MCP server documentation
- ☐ Create tool registry configuration guide
- ☐ Document AI specialist integration
- ☐ Create user guide for LLM interactions
- ☐ Add troubleshooting section

### 📋 **Phase 5: Migration & Integration** ☐

#### **5.1 Legacy Tool Migration** ☐
- ☐ Extract `execute_command()` logic to native tool framework
- ☐ Register `instant_capture` in tools.yaml
- ☐ Register `package_installer` in tools.yaml
- ☐ Add validation configs for migrated tools
- ☐ Test backward compatibility

#### **5.2 Service Integration** ☐
- ☐ Integrate with existing service_manager.py
- ☐ Add native tools to service health checks
- ☐ Update service orchestration documentation
- ☐ Test service coordination workflows

#### **5.3 Automation Scripts Integration** ☐
- ☐ **Audit & Catalog**: Review all 15+ automation scripts for functionality and value
- ☐ **Test & Validate**: Ensure scripts work correctly and identify dependencies
- ☐ **Categorize Scripts**: Group by function (AI injectors, web automation, capture, etc.)
- ☐ **Convert to Native Tools**: Register valuable scripts in tools.yaml
- ☐ **Security Review**: Mark sensitive automation scripts as requires_review: true
- ☐ **Remove Duplicates**: Consolidate overlapping functionality
- ☐ **Integration Testing**: Test scripts through native tool framework

#### **5.4 Example Tool Configurations** ☐
- ☐ Create comprehensive tools.yaml with all current project tools + automation scripts
- ☐ Add use case examples for AI discovery
- ☐ Document tool parameter validation  
- ☐ Create tool combination examples

---

## 🎯 **ORGANIZED COMMIT PLAN**

### **Commit 1: 🏗️ Core Native Tool Infrastructure**
```bash
# Phase 1: Core Infrastructure Implementation
git add packages/mcp-server/tools.yaml
git add packages/mcp-server/native_tools/
git add packages/mcp-server/tests/test_native_tools.py
```
**Files**: Tool registry, core modules, file watcher, basic tests
**Rationale**: Foundation for intelligent tool system

### **Commit 2: 🤖 AI Integration & Expert System**
```bash
# Phase 2: Claude Code Specialist Integration
git add packages/mcp-server/ai_specialist/
# Updated mcp_server.py with AI-powered tool discovery
```
**Files**: Claude specialist integration, intent analysis, expert suggestions
**Rationale**: AI-powered tool discovery and recommendations

### **Commit 3: 🛡️ Security & Validation Framework**
```bash
# Phase 3: Security and validation systems
# Updated native_tools with approval workflows
```
**Files**: Security framework, approval system, validation engine
**Rationale**: Safe execution of powerful native tools

### **Commit 4: 🧪 Comprehensive Testing Suite**
```bash
# Phase 4: Complete test coverage
git add packages/mcp-server/tests/test_ai_integration.py
git add packages/mcp-server/tests/test_security.py
```
**Files**: Full test suite for all native tool components  
**Rationale**: Maintain 100% test coverage for new system

### **Commit 5: 🔄 Legacy Migration & Integration**
```bash
# Phase 5: Migrate existing tools and integrate with services
# Remove obsolete root mcp_server.py after migration complete
git rm mcp_server.py
rm mcp_server.py.backup.*
```
**Files**: Migrated tools, service integration, cleanup
**Rationale**: Complete transition to new system

### **Commit 6: 📁 Organize MCP Tools**
```bash
mkdir -p packages/mcp-server/{tools,integrations,docs}
mv mcp_command_extension.py packages/mcp-server/tools/
mv mcp_integration_instructions.py packages/mcp-server/tools/
mv bolt_automation_mcp.py packages/mcp-server/integrations/
```
**Files**: Development and integration tools
**Rationale**: Centralize MCP-related utilities

### **Commit 7: 📚 Consolidate Documentation**
```bash
mv docs/mcp/MCP_SERVER_REVIEW_SUMMARY.md packages/mcp-server/docs/
git add packages/mcp-server/*.md
```
**Files**: All MCP documentation
**Rationale**: Keep documentation with relevant code

### **Commit 8: 🔒 Add Security Features**
```bash
git add packages/mcp-server/mcp_server_secure.py
```
**Files**: Security wrapper
**Rationale**: Enable secure external deployments

### **Commit 9: 🛠️ Commit Shared Services**
```bash
git add shared/python-common/services/mcp_*.py
```
**Files**: Service orchestrator integration
**Rationale**: Service framework components

---

## ⚠️ **CRITICAL ACTIONS NEEDED**

### 🚨 **Immediate (High Priority)**
1. ☑️ **DELETE** `/mcp_server.py` - This is causing the user confusion
2. ☑️ **UPDATE** service configs to point to correct server path
3. ☑️ **UPDATE** documentation to reference correct server location

### 🔄 **CRITICAL TOOL MIGRATION REQUIRED**
1. **BEFORE DELETION**: Migrate 3 unique tools from root server to packages server
   - `execute_command()` - Shell execution with security (lines 570-636)
   - `run_instant_capture()` - AI capture system launcher (lines 639-678)  
   - `install_package()` - Python package installer (lines 680-695)
2. **Create Tests**: Add comprehensive tests for migrated tools
3. **Validate**: Ensure 100% functionality preserved

### 🔧 **Configuration Updates Required**
1. **Service Manager**: Update paths to reference `/packages/mcp-server/mcp_server.py`
2. **Launch Scripts**: Update any scripts referencing root `mcp_server.py`
3. **Documentation**: Update README files with correct server location

### 📝 **Post-Cleanup Tasks**
1. **Test**: Verify correct MCP server still works after cleanup
2. **Update**: Cursor configuration to use correct server path
3. **Document**: Update project README with single source of truth

---

## 🎯 **SUCCESS METRICS**

### ✅ **After Cleanup**
- **Single MCP Server**: Only `/packages/mcp-server/mcp_server.py` exists
- **Organized Structure**: Tools and docs in appropriate subdirectories
- **Clear Documentation**: All MCP-related docs in one location
- **No Confusion**: No duplicate or obsolete server files

### 📊 **File Count Reduction**
- **Before**: 13+ MCP-related files scattered across project
- **After**: 8 organized files in proper structure
- **Reduction**: ~40% fewer files, 100% better organization

---

## 🚀 **Recommended Execution Order**

#### **🎯 Native Tool System Implementation** (Commits 1-5)
1. **🏗️ FOUNDATION**: Core infrastructure and registry system
2. **🤖 AI INTEGRATION**: Claude specialist and expert system  
3. **🛡️ SECURITY**: Validation and approval frameworks
4. **🧪 TESTING**: Comprehensive test coverage
5. **🔄 MIGRATION**: Legacy tools and cleanup

#### **📁 Organization & Documentation** (Commits 6-9)
6. **📁 ORGANIZE**: Centralize MCP utilities and tools
7. **📚 DOCUMENT**: Consolidate all documentation
8. **🔒 SECURE**: Add external security features
9. **🛠️ SERVICES**: Commit shared service components

### 📊 **Implementation Progress Tracking**

**Use the checkboxes above as your task list!** Each phase has detailed subtasks that can be completed incrementally.

**Total Tasks**: 54 checkboxes across 5 phases + automation integration
**Estimated Effort**: 3-4 weeks for full implementation including automation scripts
**Dependencies**: Claude specialist integration requires MCP messaging system

### 📄 **Example tools.yaml with Automation Scripts**

```yaml
# tools.yaml - Comprehensive Native Tool Registry
version: 1.0
auto_reload: true
validation_on_change: true

tools:
  # AI Service Injectors
  cursor_prompt_injector:
    name: cursor_prompt_injector
    description: Cross-platform Cursor AI chat automation
    category: ai_automation
    script: cursor_ai_injector.py
    supports_persistent: false
    requires_review: false
    keywords: [cursor, ai, prompt, injection, automation]
    
    parameters:
      prompt:
        type: string
        required: true
        description: Prompt to inject into Cursor chat
      chat_type:
        type: string
        default: chat
        options: [chat, composer]
        
    validation:
      script_exists: true
      dependencies: [python3]
      test_command: python3 cursor_ai_injector.py --test
      
    use_cases:
      - I want to send a prompt to Cursor AI
      - Automate Cursor chat interaction
      - Inject code generation requests

  gemini_prompt_injector:
    name: gemini_prompt_injector  
    description: Gemini AI chat interface automation via native keyboard
    category: ai_automation
    script: gemini_native_injector.py
    supports_persistent: false
    requires_review: false
    keywords: [gemini, google, ai, prompt, native, automation]
    
    parameters:
      prompt:
        type: string
        required: true
      browser:
        type: string
        default: Chrome
        options: [Chrome, Safari, Firefox]
        
    use_cases:
      - I want to ask Gemini something
      - Automate Google AI interactions
      - Cross-platform AI automation

  # Web App Automation
  discord_channel_exporter:
    name: discord_channel_exporter
    description: Export Discord channel messages via Chrome Debug Protocol
    category: data_extraction
    script: discord_export_automation.py
    supports_persistent: false
    requires_review: true  # Data export needs review
    keywords: [discord, export, messages, data]
    
    parameters:
      channel_url:
        type: string
        required: true
      output_format:
        type: string
        default: json
        options: [json, csv, txt]
        
    validation:
      dependencies: [chrome, mcp_server]
      test_command: python3 discord_export_automation.py --test
      
    use_cases:
      - I need to export Discord conversations
      - Backup Discord channel data
      - Analyze Discord message history

  # Development Tools  
  extension_manager:
    name: extension_manager
    description: Chrome extension lifecycle management and automation
    category: development
    script: extension_manager.py
    supports_persistent: false
    requires_review: false
    keywords: [chrome, extension, development, reload]
    
    parameters:
      action:
        type: string
        required: true
        options: [reload, enable, disable, inspect]
      extension_id:
        type: string
        required: false
        
    use_cases:
      - I need to reload my extension
      - Manage Chrome extension development
      - Automate extension testing

  # System Tools (from legacy migration)
  instant_capture:
    name: instant_capture
    description: Beautiful AI capture system with floating UI
    category: capture
    script: instant_capture_beautiful.py
    supports_persistent: true
    requires_review: false
    keywords: [capture, ai, screenshot, ui, beautiful]
    
    parameters:
      theme:
        type: string
        default: dark
        options: [dark, light]
      position:
        type: string
        default: top-right
        
    use_cases:
      - I want to capture something
      - Take a screenshot with AI
      - Start the capture system
```

---

## 🚨 **COMPLETE UNCOMMITTED FILES AUDIT** (118 Total Files)

### 📊 **Files Status Overview**
- **Modified Files**: 8 files with changes
- **Untracked Files**: 110 new files  
- **🎯 Goal**: Zero uncommitted files

### 🗂️ **UNTRACKED FILES BY CATEGORY**

#### **📁 Configuration Files** ☐
- ☐ **`.skhdrc_simplified`** - COMMIT (simplified keyboard shortcuts config)
- ☐ **`.yabairc_no_sa`** - COMMIT (yabai config without scripting addition)

#### **📚 Documentation & Analysis** ☐
- ☐ **`CLAUDE.md`** - COMMIT (Claude integration documentation)
- ☐ **`SERVICE_ORCHESTRATION_README.md`** - COMMIT (service management docs)
- ☐ **`SIDEKICK_AUDIT_REPORT.md`** - COMMIT (sidekick analysis)
- ☐ **`MCP_FILES_AUDIT_AND_CLEANUP.md`** - COMMIT (this document)
- ☐ **`docs/Service_Orchestrator_Plan.md`** - COMMIT (orchestration planning)
- ☐ **`docs/mcp/fastmcp for LLMs.txt`** - COMMIT (FastMCP documentation)

#### **🤖 AI Chat Integration** ☐
- ☐ **`ai-chats/cursor_copy_messages_from_discord_to_go.md`** - COMMIT (workflow docs)
- ☐ **`claude_interface_investigation_report.md`** - COMMIT (investigation results)
- ☐ **`claude_interface_investigator.py`** - COMMIT (investigation automation)
- ☐ **`claude_dom_observer_results.json`** - COMMIT (DOM analysis data)
- ☐ **`claude_web_observer.js`** - COMMIT (web observer script)
- ☐ **`collaborative_hover_investigation_results.md`** - COMMIT (UI investigation)

#### **🔧 System Automation & Mapping** ☐
- ☐ **`yabai_mapper.py`** - COMMIT (window manager automation)
- ☐ **`macos_mapper.py`** - COMMIT (macOS system mapping)
- ☐ **`enhanced_macos_mapper.py`** - COMMIT (enhanced system mapping)
- ☐ **`complete_mapper.py`** - COMMIT (comprehensive mapping)
- ☐ **`compare_yabai_osascript.py`** - COMMIT (comparison analysis)
- ☐ **`focus_monitor.py`** - COMMIT (focus tracking automation)
- ☐ **`sidekick_notifications.py`** - COMMIT (notification system)
- ☐ **`morning_accountability.py`** - COMMIT (productivity automation)

#### **🎯 Window Management & Testing** ☐
- ☐ **`test_yabai_direct.py`** - COMMIT (yabai testing)
- ☐ **`test_skhd_specific.py`** - COMMIT (keyboard shortcut testing)
- ☐ **`yabai_setup_check.py`** - COMMIT (yabai configuration validation)
- ☐ **`yabai_cli_tests.sh`** - COMMIT (CLI testing script)
- ☐ **`yabai_vs_osascript_examples.sh`** - COMMIT (comparison examples)

#### **🚀 Automation Scripts** (Already covered in automation section)
- ☐ **`discord_export_automation.py`** - COMMIT (Discord automation)
- ☐ **`discord_exporter_chrome_debug.py`** - COMMIT (Chrome debug exporter)
- ☐ **`instant_ai_capture.py`** - COMMIT (AI capture system)
- ☐ **`instant_capture_beautiful.py`** - COMMIT (beautiful capture system)
- ☐ **`hover_investigation_workflow.py`** - COMMIT (UI investigation)
- ☐ **`run_claude_investigation.py`** - COMMIT (Claude investigation runner)

#### **🔧 Setup & Infrastructure** ☐
- ☐ **`bootstrap_services.py`** - COMMIT (service bootstrapping)
- ☐ **`launch_sidekick.py`** - COMMIT (sidekick launcher)
- ☐ **`setup_beautiful_capture.sh`** - COMMIT (capture setup script)
- ☐ **`setup_instant_capture.sh`** - COMMIT (instant capture setup)
- ☐ **`install_scripting_addition.sh`** - COMMIT (yabai scripting setup)
- ☐ **`make_executable.sh`** - COMMIT (permission setup script)
- ☐ **`quick_capture.sh`** - COMMIT (quick capture utility)
- ☐ **`restart_skhd.sh`** - COMMIT (keyboard daemon restart)
- ☐ **`debug_float_toggle.sh`** - COMMIT (window float debugging)

#### **📊 Data & Configuration** ☐
- ☐ **`focus_log.json`** - COMMIT (focus tracking data)
- ☐ **`focus_prompts.json`** - COMMIT (focus prompt configurations)
- ☐ **`focus_rules.json`** - COMMIT (focus management rules)
- ☐ **`working_set.json`** - COMMIT (working set configuration)

#### **🗂️ Directories** ☐
- ☐ **`agents/`** - COMMIT (agent configurations and scripts)
- ☐ **`capture_ui/`** - COMMIT (capture user interface components)
- ☐ **`gtd/`** - COMMIT (Getting Things Done workflow tools)
- ☐ **`test_temp_mcp/`** - DELETE (temporary test directory)

#### **💬 Message System** ☐
- ☐ **`messages/agents/Claude Code One/`** - COMMIT (Claude agent messages)
- ☐ **`messages/agents/Claude Desktop/`** - COMMIT (Desktop agent messages)
- ☐ **`messages/agents/Green Plasmo/`** - COMMIT (Plasmo agent messages)
- ☐ **`messages/agents/Homey/`** - COMMIT (Homey agent messages)
- ☐ **`messages/agents/PersonalSidekick/`** - COMMIT (Sidekick agent messages)
- ☐ **`messages/notifications/pending/`** - COMMIT (pending notifications)

#### **🗑️ Backup Files** ☐
- ☐ **`focus_monitor.py.backup.1756495555`** - DELETE (backup file)
- ☐ **`working_set.json.backup.*`** - DELETE (backup files)
- ☐ **`yabai_mapper.py.backup.*`** - DELETE (backup files)
- ☐ **`simple_discord_export.py.backup.*`** - DELETE (backup files)
- ☐ **`mcp_server.py.backup.*`** - DELETE (already covered in MCP section)

#### **⚛️ React Components** ☐
- ☐ **`RoundTable.tsx`** - COMMIT (React component for discussions)

### 📋 **PACKAGES/MCP-SERVER UNTRACKED FILES** (All should be COMMITTED)

#### **📚 Documentation** ☐
- ☐ All `.md` files in packages/mcp-server/ - COMMIT (comprehensive documentation)

#### **🧪 Testing Infrastructure** ☐  
- ☐ All `test_*.py` files - COMMIT (complete test suite)
- ☐ `run_comprehensive_tests.py` - COMMIT (test runner)

#### **🏗️ Core Modules** ☐
- ☐ `agents/`, `core/`, `files/` directories - COMMIT (modular architecture)
- ☐ `agent_messaging.py`, `agent_name_tool.py` - COMMIT (agent tools)
- ☐ `chrome_debug_client.py` - COMMIT (Chrome integration)
- ☐ `service_orchestrator.py` - COMMIT (service management)

### 🎯 **MODIFIED FILES THAT NEED DECISIONS** ☐

#### **🔧 Configuration Changes** ☐
- ☐ **`.vscode/settings.json`** - COMMIT (IDE configuration)
- ☐ **`requirements.txt`** - COMMIT (dependency updates)

#### **🛠️ Service Changes** ☐
- ☐ **`service_manager.py`** - COMMIT (service management updates)
- ☐ **`packages/mcp-server/mcp_server.py`** - COMMIT (main server updates)
- ☐ **`packages/mcp-server/claude_instance_launcher.py`** - COMMIT (launcher updates)
- ☐ **`packages/mcp-server/mcp_proxy.py`** - COMMIT (proxy updates)

#### **📁 Agent Configuration** ☐
- ☐ **`messages/agents/Plasmo/info.json`** - COMMIT (agent metadata)

#### **⚠️ Legacy File** ☐
- ☐ **`mcp_server.py`** - DELETE AFTER MIGRATION (obsolete root server)

---

## 🎯 **ZERO UNCOMMITTED FILES PLAN**

### **Batch Commit 1: 🗑️ Clean Backups & Temp Files**
```bash
rm -f *.backup.*
rm -rf test_temp_mcp/
rm focus_monitor.py.backup.1756495555
rm working_set.json.backup.*
rm yabai_mapper.py.backup.*
rm simple_discord_export.py.backup.*
```
**Result**: -15 files

### **Batch Commit 2: 📚 Documentation & Analysis**
```bash
git add *.md docs/ ai-chats/ claude_*
git add collaborative_hover_investigation_results.md
git add SERVICE_ORCHESTRATION_README.md SIDEKICK_AUDIT_REPORT.md
```
**Result**: -10 files

### **Batch Commit 3: 🤖 Automation & Scripts**
```bash
git add *automation*.py *capture*.py *investigation*.py
git add *mapper*.py focus_monitor.py sidekick_notifications.py
git add morning_accountability.py launch_sidekick.py
git add setup_*.sh install_*.sh make_executable.sh
git add quick_capture.sh restart_skhd.sh debug_float_toggle.sh
```
**Result**: -25 files

### **Batch Commit 4: 🧪 Testing & Validation**
```bash
git add test_*.py *test*.sh yabai_setup_check.py
git add yabai_cli_tests.sh yabai_vs_osascript_examples.sh
```
**Result**: -8 files

### **Batch Commit 5: 📊 Configuration & Data**
```bash
git add .skhdrc_simplified .yabairc_no_sa
git add *.json focus_*.json working_set.json
git add bootstrap_services.py RoundTable.tsx
```
**Result**: -8 files

### **Batch Commit 6: 🗂️ Directories & Message System**
```bash
git add agents/ capture_ui/ gtd/
git add messages/agents/ messages/notifications/
```
**Result**: -6 directories

### **Batch Commit 7: 📦 MCP Server Complete Integration**
```bash
git add packages/mcp-server/
git add mcp_command_extension.py mcp_integration_instructions.py
```
**Result**: -40+ files

### **Batch Commit 8: 🔧 Service & Configuration Updates**
```bash
git add .vscode/settings.json requirements.txt service_manager.py
git add messages/agents/Plasmo/info.json
```
**Result**: -4 files

### **Final Cleanup: 🗑️ Remove Legacy**
```bash
git rm mcp_server.py  # After migration complete
```
**Result**: -1 file

**🎯 FINAL RESULT: 0 uncommitted files!**

---

---

## ⚠️ **CRITICAL MCP SERVER RESTART REQUIREMENT**

**🔴 MANDATORY AFTER ANY MCP CHANGES:**
```
After modifying ANY MCP server files, you MUST:
1. 🛑 Stop MCP server in Cursor (disconnect/disable)
2. 🔄 Restart MCP server in Cursor (reconnect/enable)  
3. ✅ Verify tools are available before proceeding

Files requiring restart:
- packages/mcp-server/mcp_server.py (main server)
- packages/mcp-server/tools.yaml (tool registry)
- Any native tool modules
- MCP configuration changes
```

**💡 Pro Tip**: Test MCP tools after each batch of changes to ensure nothing breaks!

---

**Generated**: January 29, 2025  
**Purpose**: Resolve MCP server file confusion and establish single source of truth  
**Priority**: 🚨 HIGH - User is confused about which server is correct
