# Agent Framework Exercise Plan

## Testing Status Analysis

**Current Test Coverage:**
- ✅ **Unit Tests**: `test_agent_modules.py` - Core agent management modules
- ✅ **Integration Tests**: `test_agent_tools_integration.py` - MCP server tool integration  
- ✅ **Basic Functionality**: Agent registration, messaging, notifications working
- ⚠️ **E2E Tests**: Limited - need comprehensive multi-agent workflows
- ❌ **Agent Spawning Tests**: No automated tests for agent_spawner.py
- ❌ **Cross-Agent Collaboration**: No tests for real multi-agent scenarios

**Existing Active Agents:**
- `product_manager_agent_DiscordPlus Project_1752261000` - Currently registered
- Multiple Claude instances registered: Claude Desktop, Green Plasmo, PersonalSidekick, etc.

## Comprehensive Exercise Plan

### Phase 1: Core System Validation ⚡ (15 minutes)

#### 1.1 MCP Server Health Check
```bash
# Verify MCP server is running and responsive
python -c "
import sys; sys.path.append('packages/mcp-server')
from mcp_server import health_check
print(health_check())
"
```

#### 1.2 Agent Module Tests
```bash
cd packages/mcp-server
python test_agent_modules.py
```

#### 1.3 MCP Tool Integration Tests  
```bash
cd packages/mcp-server
python test_agent_tools_integration.py --server-url http://127.0.0.1:8000
```

### Phase 2: Agent Registration & Discovery 🤖 (10 minutes)

#### 2.1 Register Test Agents
```python
# Via MCP tools
mcp__stdioserver__register_agent_with_name("TestCoordinator")
mcp__stdioserver__register_agent_with_name("TestDeveloper") 
mcp__stdioserver__register_agent_with_name("TestReviewer")
```

#### 2.2 Verify Agent Discovery
```python
# List all registered agents
result = mcp__stdioserver__messages("agents")
print("Registered agents:", result)

# Check agent-specific registrations
agents = ["TestCoordinator", "TestDeveloper", "TestReviewer"]
for agent in agents:
    info = mcp__stdioserver__get_agent_registration(agent)
    print(f"{agent}: {info}")
```

### Phase 3: Inter-Agent Messaging Workout 💬 (20 minutes)

#### 3.1 Basic Messaging Flow
```python
# TestCoordinator → TestDeveloper
result = mcp__stdioserver__messages("send", {
    "to": "TestDeveloper",
    "subject": "Task Assignment: Build User Authentication",
    "message": """
    Please implement user authentication with these requirements:
    - JWT-based authentication
    - Password strength validation
    - Rate limiting for login attempts
    - Email verification flow
    
    Estimated timeline: 3 days
    Priority: High
    """
})

# TestDeveloper → TestCoordinator  
result = mcp__stdioserver__messages("reply", {
    "reply_to": result["message_id"],
    "message": """
    Authentication task acknowledged. 
    
    Questions:
    1. Which JWT library should I use?
    2. Do you want 2FA support?
    3. OAuth integration required?
    
    Starting implementation now.
    """
})
```

#### 3.2 Code Review Workflow
```python
# TestDeveloper → TestReviewer
result = mcp__stdioserver__messages("send", {
    "to": "TestReviewer", 
    "subject": "Code Review Request: Auth Module",
    "message": """
    Please review the authentication module:
    
    Files changed:
    - src/auth/AuthService.ts (new)
    - src/auth/middleware.ts (new)
    - tests/auth.test.ts (new)
    - package.json (dependencies)
    
    Focus areas:
    - Security implementation
    - Error handling
    - Test coverage
    - Performance implications
    """
})

# TestReviewer → TestDeveloper
result = mcp__stdioserver__messages("reply", {
    "reply_to": result["message_id"],
    "message": """
    Code review completed. Overall: LGTM with minor suggestions.
    
    ISSUES FOUND:
    - AuthService.ts line 45: Use constant-time comparison
    - Missing rate limiting implementation
    - Test coverage at 85% - need edge cases
    
    SUGGESTIONS:
    - Consider using bcrypt for password hashing
    - Add logging for security events
    - Document API endpoints
    
    Status: Approved pending fixes
    """
})
```

#### 3.3 Message Threading & Search
```python
# Test message threading
thread_messages = mcp__stdioserver__messages("get", {
    "reply_to": original_message_id
})

# Test message search
search_results = mcp__stdioserver__messages("get", {
    "subject_contains": "authentication",
    "from": "TestDeveloper"
})

# Test message filtering
recent_messages = mcp__stdioserver__messages("get", {
    "after": "2025-09-01",
    "unread_only": True
})
```

### Phase 4: Real-Time Notification System ⚡ (15 minutes)

#### 4.1 Notification Broadcasting
```python
# Send urgent notifications
result = mcp__stdioserver__notify("notify", 
    target_agent="TestDeveloper",
    message="Production issue: Authentication service down",
    sender="TestCoordinator"
)

result = mcp__stdioserver__notify("notify",
    target_agent="TestReviewer", 
    message="Emergency code review needed",
    sender="TestCoordinator"
)
```

#### 4.2 Notification Handling Workflow
```python
# TestDeveloper checks notifications
notifications = mcp__stdioserver__notify("check", agent_name="TestDeveloper")
print(f"TestDeveloper has {len(notifications)} pending notifications")

# TestReviewer waits for notifications (blocking)
result = mcp__stdioserver__notify("wait", agent_name="TestReviewer", timeout=30)
print(f"TestReviewer received: {result}")
```

### Phase 5: Agent Spawning & Lifecycle Management 🚀 (25 minutes)

#### 5.1 Spawn Specialized Agents
```bash
cd agents
python agent_spawner.py
```

Interactive spawning session:
```
Spawner> spawn
Agent role: ui_react_engineer
Specialization: component_library
Project context: Building reusable UI components for authentication
Target project directory: /Users/MikeWolf/Projects/Plasmo

Spawner> spawn  
Agent role: testing_specialist
Specialization: e2e_testing
Project context: Automated testing for authentication flow
```

#### 5.2 Monitor Agent Status
```bash
Spawner> list
📋 Active Agents:
  ui_react_engineer_component_library_1725394800: ui_react_engineer (active)
  testing_specialist_e2e_testing_1725394830: testing_specialist (active)

Spawner> status ui_react_engineer_component_library_1725394800
{
  "agent_id": "ui_react_engineer_component_library_1725394800",
  "role": "ui_react_engineer", 
  "status": "active",
  "current_tasks": [],
  "performance_score": 1.0
}
```

### Phase 6: Cross-Repository Collaboration 🔄 (20 minutes)

#### 6.1 File Access Between Projects
```python
# Read shared components from another project
content = mcp__stdioserver__messages("read_file", {
    "agent": "SharedComponents",
    "file_path": "src/components/Button.tsx"
})

# Share implementation with other projects
result = mcp__stdioserver__messages("send", {
    "to": "DiscordPlus",
    "subject": "Shared Component Available: AuthButton",
    "message": f"""
    New reusable authentication button component is ready:
    
    Location: src/components/AuthButton.tsx
    Features:
    - Loading states
    - Error handling  
    - Accessibility support
    - Theme integration
    
    Component source:
    {content['content'][:500]}...
    
    Ready to integrate into your project.
    """
})
```

### Phase 7: Chrome Debug Protocol Integration 🌐 (30 minutes)

#### 7.1 Browser Automation Setup
```python
# Connect to Chrome for E2E testing
result = mcp__stdioserver__connect_to_chrome()
print(f"Chrome connection: {result}")

# Get available tabs
tabs = mcp__stdioserver__get_chrome_tabs()
print(f"Available tabs: {len(tabs)}")
```

#### 7.2 Automated Testing Workflow
```python
# Agent coordinates E2E testing
result = mcp__stdioserver__messages("send", {
    "to": "testing_specialist_e2e_testing",
    "subject": "Execute E2E Test Suite",
    "message": """
    Please run the authentication E2E tests:
    
    Test scenarios:
    1. User registration flow
    2. Login/logout cycle  
    3. Password reset
    4. JWT token refresh
    5. Rate limiting verification
    
    Target URL: http://localhost:3000
    Report results via messaging system.
    """
})

# Execute JavaScript in browser context
test_result = mcp__stdioserver__execute_javascript(
    code="""
    // Simulate user authentication flow
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        const emailInput = loginForm.querySelector('input[type=email]');
        const passwordInput = loginForm.querySelector('input[type=password]');
        
        emailInput.value = 'test@example.com';
        passwordInput.value = 'TestPassword123!';
        
        loginForm.submit();
        return 'Login form submitted successfully';
    }
    return 'Login form not found';
    """,
    tab_id=tabs[0]['id']
)
```

### Phase 8: Multi-Agent Coordination Stress Test ⚖️ (45 minutes)

#### 8.1 Simulated Development Sprint
```python
# Sprint planning - Founder Agent coordinates
founder_plan = """
Sprint Goal: Implement complete user management system

Team assignments:
- ProductManager: Create detailed PRD
- UIReactEngineer: Build user interface components  
- TestingSpecialist: Develop test strategy
- ProjectSetup: Configure deployment pipeline
"""

# Broadcast sprint plan
for agent in ["ProductManager", "UIReactEngineer", "TestingSpecialist", "ProjectSetup"]:
    result = mcp__stdioserver__messages("send", {
        "to": agent,
        "subject": f"Sprint Assignment for {agent}",
        "message": founder_plan + f"\nYour specific role: Handle {agent} responsibilities"
    })
```

#### 8.2 Concurrent Task Execution
```python
# Multiple agents working simultaneously
tasks = [
    ("ProductManager", "Create PRD for user management"),
    ("UIReactEngineer", "Build LoginForm component"),
    ("TestingSpecialist", "Write integration tests"),
    ("ProjectSetup", "Configure CI/CD pipeline")
]

# Send tasks concurrently
for agent, task in tasks:
    mcp__stdioserver__notify("notify",
        target_agent=agent,
        message=f"URGENT: {task} - Sprint deadline in 2 hours",
        sender="FounderAgent"
    )
```

#### 8.3 Progress Reporting & Coordination
```python
# Agents report back to coordinator
reports = []
for agent in ["ProductManager", "UIReactEngineer", "TestingSpecialist"]:
    # Each agent sends progress update
    result = mcp__stdioserver__messages("send", {
        "to": "FounderAgent",
        "subject": f"Progress Update: {agent}",
        "message": f"""
        Task status: In Progress
        Completion: 75%
        Blockers: None
        ETA: 30 minutes
        Next steps: Finalizing implementation
        """
    })
    reports.append(result)

# Founder reviews all reports
all_messages = mcp__stdioserver__messages("get", {
    "to": "FounderAgent",
    "subject_contains": "Progress Update"
})
print(f"Received {len(all_messages)} progress reports")
```

## Expected Outcomes & Success Metrics

### Functional Verification ✅
- [ ] All agents register successfully
- [ ] Messages flow between agents without loss
- [ ] Notifications deliver in real-time
- [ ] Agent spawning creates functional instances
- [ ] Cross-repo file access works
- [ ] Chrome Debug Protocol integration functional

### Performance Metrics 📊
- [ ] Message latency < 100ms
- [ ] Agent registration < 5s  
- [ ] Chrome connection establishment < 10s
- [ ] Concurrent agent handling (5+ agents)
- [ ] Memory usage stable under load

### Collaboration Workflows ✨
- [ ] Code review workflow completed E2E
- [ ] Sprint planning coordination successful
- [ ] Cross-project component sharing works
- [ ] Automated testing pipeline functional
- [ ] Real-time problem resolution demonstrated

## Recovery & Cleanup Procedures 🧹

### After Testing
```bash
# Clean up test agents
python -c "
import sys; sys.path.append('packages/mcp-server')
from agents.agent_management import list_registered_agents, unregister_agent
agents = list_registered_agents()
for agent in agents:
    if agent['name'].startswith('Test'):
        unregister_agent(agent['name'])
        print(f'Unregistered {agent[\"name\"]}')
"

# Clear test messages
rm -rf messages/messages/test_*
rm -rf messages/notifications/pending/Test*

# Reset active agents registry
echo '[]' > agents/active_agents.json
```

### Backup Current State
```bash
# Backup current agent state before testing
cp -r messages/ messages_backup_$(date +%Y%m%d_%H%M%S)/
cp agents/active_agents.json agents/active_agents_backup.json
```

## Automated Test Execution Script

Create `run_agent_framework_tests.py`:
```python
#!/usr/bin/env python3
"""
Automated Agent Framework Exercise Runner
"""
import asyncio
import time
from datetime import datetime

async def run_complete_exercise():
    print("🚀 Starting Complete Agent Framework Exercise")
    print(f"📅 Started at: {datetime.now()}")
    
    phases = [
        ("Core System Validation", run_phase_1),
        ("Agent Registration", run_phase_2), 
        ("Inter-Agent Messaging", run_phase_3),
        ("Notification System", run_phase_4),
        ("Agent Spawning", run_phase_5),
        ("Cross-Repo Collaboration", run_phase_6),
        ("Chrome Debug Integration", run_phase_7),
        ("Multi-Agent Coordination", run_phase_8)
    ]
    
    results = {}
    
    for phase_name, phase_func in phases:
        print(f"\n📋 Starting: {phase_name}")
        start_time = time.time()
        
        try:
            result = await phase_func()
            duration = time.time() - start_time
            results[phase_name] = {
                "status": "success",
                "duration": duration,
                "result": result
            }
            print(f"✅ {phase_name} completed in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            results[phase_name] = {
                "status": "failed", 
                "duration": duration,
                "error": str(e)
            }
            print(f"❌ {phase_name} failed after {duration:.2f}s: {e}")
    
    # Final report
    print("\n" + "="*60)
    print("📊 AGENT FRAMEWORK EXERCISE RESULTS")
    print("="*60)
    
    total_duration = sum(r["duration"] for r in results.values())
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    print(f"✅ Successful Phases: {success_count}/{len(phases)}")
    print(f"❌ Failed Phases: {len(phases) - success_count}")
    
    if success_count == len(phases):
        print("\n🎉 ALL TESTS PASSED - Agent Framework is fully functional!")
    else:
        print(f"\n⚠️  {len(phases) - success_count} phases failed - Review errors above")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_complete_exercise())
```

This comprehensive exercise plan will thoroughly test all aspects of the agent framework, from basic functionality to complex multi-agent coordination scenarios.