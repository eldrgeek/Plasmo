# MCP Server Consolidation Plan

## Overview

Consolidate the root `mcp_server.py` and `packages/mcp-server/mcp_server.py` into a single, comprehensive MCP server in the packages directory, avoiding Playwright redundancy while preserving valuable features from both versions.

## Analysis Summary

### Root Version (`/mcp_server.py`)

- **Focus**: Playwright + Chrome Debug Protocol integration
- **Tools**: 20 total
- **Key Features**: Full browser automation, command execution, package management, instant capture
  Will be archived.

### Packages Version (`/packages/mcp-server/mcp_server.py`)

- **Focus**: Comprehensive MCP server with advanced features
- **Tools**: 17 total (more sophisticated)
- **Key Features**: Multi-agent communication, advanced file operations, error management, notification system

## Consolidation Strategy

### Base Architecture

- [x] Use packages version as foundation (more sophisticated architecture)
- [x] Preserve all multi-agent communication capabilities
- [x] Keep advanced file operations and error management
- [x] Maintain notification system and health monitoring

### Additions from Root Version

- [x] **Command Execution**: `execute_command` with security checks
- [ ] **Package Management**: `install_package` for pip operations
- [x] **Instant Capture**: `run_instant_capture` for AI capture system
- [ ] **Simple File Operations**: Basic `read_file`, `write_file`, `list_files` (complement existing advanced ones)

### Chrome Debug Protocol Enhancements

- [x] Merge improvements from root version's `execute_javascript_fixed`
- [x] Enhance WebSocket connection handling
- [x] Improve error reporting and timeout handling
- [x] Add better Chrome launch script integration

### Removals (Playwright Redundancy)

\*\*I think we don't need to do this. The root version will end up archived

- [x] Remove all Playwright browser automation tools (9 tools):
  - [x] `launch_browser`
  - [x] `navigate_to_url`
  - [x] `take_screenshot`
  - [x] `click_element`
  - [x] `fill_form_field`
  - [x] `execute_javascript` (Playwright version)
  - [x] `get_page_content`
  - [x] `wait_for_element`
  - [x] `close_browser`
- [x] Remove Playwright-specific imports and state management
- [x] Remove Playwright global variables and instances

## Implementation Steps

### Phase 1: Preparation

- [x] **Backup both existing files**
  - [x] Create backup of `/mcp_server.py` as `mcp_server_root_backup.py`
  - [x] Create backup of `/packages/mcp-server/mcp_server.py` as `mcp_server_packages_backup.py`
- [x] **Document current tool counts and capabilities**
- [x] **Identify all imports and dependencies**

### Phase 2: Core Consolidation

- [x] **Start with packages version as base**
  - [x] Copy packages version to new consolidated file
  - [x] Preserve all existing packages functionality
- [x] **Add non-Playwright tools from root version**
  - [x] Integrate `execute_command` with security checks
  - [ ] Add `install_package` functionality Not needed
  - [x] Include `run_instant_capture` system
  - [ ] Add simple file operations (`read_file`, `write_file`, `list_files`)
- [x] **Update imports and dependencies**
  - [x] Add `concurrent.futures` for command execution
        **Answer**: `concurrent.futures` is used in the root version's `execute_command` for running shell commands in separate threads to avoid blocking the MCP server. It allows async execution of blocking operations.
  - [x] Ensure all required modules are imported
  - [ ] Remove Playwright-specific imports
        **Answer**: Correct! Since we're archiving the root version, we don't need to remove Playwright imports from it.

### Phase 3: Chrome Debug Protocol Enhancement

- [x] **Merge Chrome Debug Protocol improvements**
  - [x] Integrate root version's `execute_javascript_fixed` improvements
  - [x] Enhance WebSocket connection management
  - [x] Improve error handling and timeout management
  - [x] Add better Chrome launch script integration
- [x] **Enhance existing Chrome tools**
  - [x] Improve `connect_to_chrome` with better error reporting
  - [x] Enhance `get_chrome_tabs` with filtering
  - [x] Upgrade `launch_chrome_debug` with script integration

### Phase 4: Testing and Validation

- [x] **Test all consolidated tools**
  - [x] Verify multi-agent communication tools work
  - [x] Test advanced file operations
  - [x] Validate Chrome Debug Protocol tools
  - [x] Check command execution and security
  - [x] Test package management functionality
  - [x] Verify instant capture system
  - [x] Ensure that the execute sequence tool is working
        We will do this as follows:
        Once the mcp server has met all its requirements
        You and I will work together to build scripts
        For the YeshID auth flow, add it to the library and then test it
        If that part is unclear I can give you a converation that
        Will make it more relevant
- [x] **Validate tool registration**
  - [x] Ensure all tools are properly decorated with `@mcp.tool()`
  - [x] Add `@mcp.prompt()` for learning to do tasks
        **Answer**: Great idea! We'll add MCP prompts for the YeshID auth flow. Once the consolidated MCP server is ready, we'll work together to build scripts for the YeshID authentication flow, add it to the library, and test it. This will create reusable automation patterns.
  - [x] Verify tool parameter validation
  - [x] Check return value formatting
- [x] **Test error handling**
  - [x] Verify error management system works
  - [x] Test notification system
  - [x] Check health monitoring

### Phase 5: Documentation and Cleanup

- [x] **Update documentation**
  - [x] Update tool descriptions and docstrings
  - [x] Revise README with new tool list
  - [x] Update version changelog
- [x] **Clean up redundant files**
  - [x] Remove or archive root `mcp_server.py`
  - [x] Update any references to old file locations
- [x] **Update configuration**
  - [x] Update Cursor IDE configuration if needed
  - [x] Verify service manager integration
  - [x] Check auto-restart functionality

## Expected Final Tool Count: ~20 Tools

### Tool Categories:

- [x] **Multi-Agent Communication**: 3 tools
  - [x] `register_agent_with_name`
  - [x] `get_current_agent_name`
  - [x] `messages`
- [x] **Advanced File Operations**: 2 tools
  - [x] `get_project_structure` (from packages)
  - [x] `analyze_code` (from packages)
- [x] **Chrome Debug Protocol**: 5 tools
  - [x] `connect_to_chrome` (enhanced)
  - [x] `get_chrome_tabs` (enhanced)
  - [x] `launch_chrome_debug` (enhanced)
  - [x] `execute_javascript` (enhanced from root)
  - [x] `orchestrate_sequences` (from packages)
- [x] **System Operations**: 3 tools
  - [x] `get_system_info` (from packages)
  - [x] `server_info` (from packages)
  - [x] `health` (from packages)
- [x] **Command Execution**: 1 tool
  - [x] `execute_command` (from root)
- [x] **Error Management**: 1 tool
  - [x] `get_last_errors` (from packages)
- [x] **Notification System**: 1 tool
  - [x] `notify` (from packages)
- [x] **Special Features**: 1 tool
  - [x] `run_instant_capture` (from root, optional)

## Risk Mitigation

### Backup Strategy

- [x] **Full backup before any changes**
- [x] **Version control commit before consolidation**
- [x] **Test in isolated environment first**

### Rollback Plan

- [x] **Keep original files as backups**
- [x] **Document exact changes made**
- [x] **Have rollback procedure ready**

### Testing Strategy

- [x] **Test each tool individually**
- [x] **Verify integration with Cursor IDE**
- [x] **Check service manager compatibility**
- [x] **Validate Chrome Debug Protocol functionality**

## Success Criteria

- [x] **All tools from packages version preserved**
- [x] **Valuable non-Playwright tools from root version added**
- [x] **No Playwright redundancy**
- [x] **Enhanced Chrome Debug Protocol capabilities**
- [x] **Maintained multi-agent communication**
- [x] **Preserved error management and notifications**
- [x] **All tools properly tested and functional**
- [x] **Documentation updated**
- [x] **Service integration maintained**

## Comments Section

### User Feedback:

<!-- User can add comments here about specific preferences or concerns -->

### Implementation Notes:

<!-- Implementation team can add notes about specific challenges or decisions -->

### Testing Results:

<!-- Test results and validation notes can be added here -->

---

**Created**: $(date)
**Status**: Ready for Review
**Next Action**: User review and checkbox modification
