# Browser Automation Learning Agent: Architecture & Design

## Executive Summary

This project implements an intelligent agent system that learns to carry out browser-based tasks by observing, scripting, and refining automation procedures. Rather than directly executing browser actions through Playwright, the agent writes and tests JavaScript functions that it consolidates into a hierarchical structure of **Actions**, **Steps**, and **Sequences**—creating a maintainable library of reusable automation knowledge.

---

## Core Concepts

### The Three-Tier Hierarchy

```
SEQUENCE (Cross-context workflow)
    ↓
STEP (Same-context actions)
    ↓
ACTION (Atomic operation with preconditions)
```

#### **1. Actions**
**Atomic operations** that wait for their requirements to be met before executing.

**Characteristics:**
- Self-contained JavaScript functions
- Wait for preconditions (correct location, selectors present)
- Monitor for DOM mutations to settle
- Include error handling and validation
- Return structured results

**Example Action:**
```javascript
// Action: Click send button in Claude interface
async function clickSendButton() {
  // Wait for correct location
  if (!window.location.href.includes('claude.ai')) {
    throw new Error('Wrong domain');
  }
  
  // Wait for selector
  const selector = 'button[aria-label="Send message"]';
  await waitForSelector(selector, 5000);
  
  // Wait for DOM to settle
  await waitForDOMMutationsToSettle(100);
  
  // Execute action
  const button = document.querySelector(selector);
  button.click();
  
  return { success: true, timestamp: Date.now() };
}
```

#### **2. Steps**
**Series of actions** performed in the same context.

**Characteristics:**
- Multiple actions executed sequentially
- All actions share the same browser context (same page/iframe)
- No navigation or context changes
- Can include verification between actions

**Example Step:**
```javascript
// Step: Submit prompt to Claude
async function submitPromptToClaude(promptText) {
  const results = [];
  
  // Action 1: Find and focus input
  results.push(await focusClaudeInput());
  
  // Action 2: Type the prompt
  results.push(await typeIntoClaudeInput(promptText));
  
  // Action 3: Click send button
  results.push(await clickSendButton());
  
  // Action 4: Wait for response to start
  results.push(await waitForResponseStart());
  
  return { step: 'submitPromptToClaude', results };
}
```

#### **3. Sequences**
**Series of steps** performed across different contexts.

**Characteristics:**
- Multiple steps executed in order
- Context changes between steps (navigation, iframes, OS-level)
- Handles domain changes
- Coordinates between browser and OS operations

**Example Sequence:**
```javascript
// Sequence: Copy from Discord to Claude
[
  {
    context: 'discord.com',
    step: 'copyLatestMessage',
    tab: 'same'
  },
  {
    context: 'claude.ai', 
    step: 'submitPromptToClaude',
    tab: 'same'
  },
  {
    context: 'claude.ai',
    step: 'waitForAndCopyResponse', 
    tab: 'same'
  },
  {
    context: 'discord.com',
    step: 'pasteResponse',
    tab: 'same'
  }
]
```

---

## Context Management

### What Defines a Context?

A **context change** occurs when:

1. **Page navigation** - Moving to a different URL/domain
2. **Iframe transition** - Moving focus into/out of an iframe
3. **New frame/window** - Opening or switching to new browser windows
4. **Platform transition** - Switching from browser JavaScript to macOS osascript

### Current Implementation: `orchestrate_sequences`

The Plasmo MCP server's `orchestrate_sequences` tool currently:
- Takes a series of sequences with their contexts
- Executes them in order
- Assumes the **tab stays constant**
- Allows the **domain to change**
- Waits for domain pattern match before executing each sequence

**Current Limitations:**
- No iframe handling
- No multi-tab coordination
- No OS-level context switching
- Limited error recovery

---

## Learning & Development Process

### Phase 1: Discovery & Observation

The agent uses **Playwright MCP server** to:
1. Take page snapshots (accessibility tree, DOM structure)
2. Identify interactive elements
3. Observe DOM mutations during interactions
4. Monitor network activity
5. Capture console messages

**Tools Used:**
- `browser_snapshot` - Get page structure
- `browser_evaluate` - Execute exploratory JavaScript
- `browser_click` / `browser_type` - Test interactions
- DOM Observer patterns for monitoring changes

### Phase 2: Script Generation

The agent **writes JavaScript functions** rather than using Playwright commands directly:

**Why JavaScript instead of Playwright?**
- **Reusability** - Functions can be stored and reused
- **Composability** - Small functions combine into larger workflows
- **Testing** - Can be tested independently
- **Performance** - Executes directly in browser context
- **Debugging** - Easier to inspect and modify

### Phase 3: Testing & Validation

The agent:
1. Executes generated JavaScript in browser
2. Observes results through DOM changes
3. Validates success criteria
4. Captures errors and exceptions
5. Iterates on failures

**Testing Strategies:**
- **Interactive testing** via Agent Bridge (human guidance)
- **Automated validation** for known patterns
- **Paranoid mode** with verification at each step

### Phase 4: Consolidation

Successful JavaScript functions are consolidated into:

1. **Action Library** - Individual tested operations
2. **Step Procedures** - Common multi-action workflows  
3. **Sequence Templates** - Complete automation workflows

**Storage Format:**
```python
"""
Action: Click Send Button in Claude Interface

Requirements:
- Domain: claude.ai
- Selector: button[aria-label="Send message"]
- DOM: Must be stable (no mutations for 100ms)

Returns:
- success: bool
- timestamp: float
- error: Optional[str]

Confidence: HIGH (validated 2025-09-30)
Last Tested: 2025-09-30
Success Rate: 95%
"""

async function clickClaudeSendButton():
    # JavaScript code here
```

---

## Tool Integration

### Playwright MCP Server

**Primary use:** Page inspection and interaction testing

**Key Tools:**
- `browser_snapshot` - Get page accessibility tree
- `browser_click` - Test clicking elements  
- `browser_type` - Test text input
- `browser_evaluate` - Execute JavaScript
- `browser_navigate` - Change pages
- `browser_wait_for` - Wait for conditions

### Plasmo MCP Server

**Primary use:** File operations, Chrome debug, agent coordination

**Key Tools:**
- `orchestrate_sequences` - Execute multi-step workflows
- `execute_javascript` - Run JS via Chrome Debug Protocol
- `smart_write_file` - Save learned procedures
- `smart_read_file` - Load existing procedures
- `messages` - Inter-agent communication

### DT-Server (Desktop Automation)

**Primary use:** OS-level mouse and keyboard control

**Key Tools:**
- `click_mouse` - Click at coordinates
- `type_text` - Type text via keyboard
- `press_key` - Press key combinations
- `take_screenshot` - Capture screen regions

### OSAscript (macOS Automation)

**Primary use:** Application control and system integration

**Key Tools:**
- Focus applications
- Switch desktop spaces
- Execute AppleScript commands
- System-level automation

---

## Knowledge Storage Architecture

### Directory Structure

```
procedures/
  general/
    clipboard_operations.py
    dom_waiting.py
    selector_helpers.py
  
  browser/
    claude_ai/
      submit_prompt.py
      wait_for_response.py
      copy_response.py
    discord/
      copy_message.py
      paste_message.py
      monitor_channel.py
    chatgpt/
      submit_prompt.py
      copy_response.py
  
  desktop/
    yabai_operations.py
    window_management.py
```

### Procedure Metadata Format

Each procedure file includes:

```python
"""
Procedure: Submit Prompt to Claude

Type: STEP
Context: claude.ai
Dependencies: 
  - focusClaudeInput (action)
  - typeIntoInput (action)
  - clickSendButton (action)

Preconditions:
  - Browser tab open to claude.ai/*
  - Input field visible and enabled
  - No pending operations

Input:
  - prompt_text: str

Output:
  - success: bool
  - message_id: Optional[str]
  - error: Optional[str]

Confidence: HIGH
Success Rate: 95% (over 100 executions)
Last Validated: 2025-09-30
Known Issues: None

Version: 2.1.0
Change Log:
  - 2.1.0: Added retry logic for button visibility
  - 2.0.0: Switched to aria-label selector (more stable)
  - 1.0.0: Initial implementation
"""

# JavaScript or Python code follows
```

---

## Execution Modes

### 1. Learning Mode (Step-by-Step)

**When:** Exploring unknown interfaces or uncertain procedures

**Process:**
1. Agent executes one action
2. Observes result via DOM changes  
3. Reports status via Agent Bridge
4. Waits for human confirmation if uncertain
5. Decides next action based on observations
6. Repeats until task complete

**Characteristics:**
- Token-heavy (many LLM calls)
- Time-consuming
- Highly adaptable
- Good for debugging
- Human oversight available

### 2. Scripted Mode (Playwright Python)

**When:** Confident about approach or procedure is proven

**Process:**
1. Agent writes complete Python script upfront
2. Includes try/catch blocks and fallbacks
3. Executes entire procedure
4. Reports results

**Characteristics:**
- Token-efficient
- Fast execution
- Less adaptable
- Harder to debug failures
- Good for stable, known procedures

### 3. Paranoid Mode (Verified Execution)

**When:** Critical operations or untrusted environments

**Process:**
1. Execute action
2. Verify result explicitly
3. Check for error indicators
4. Confirm with human if issues detected
5. Proceed only on verification

**Characteristics:**
- Balanced token usage
- Moderate speed
- High reliability
- Good error detection
- Safety-first approach

---

## Agent Bridge (Human-AI Coordination)

### Purpose

Provides real-time communication between agent and human operator during automation development and execution.

### Capabilities

**Status Updates:**
```javascript
agentBridge.status("Finding Claude send button...", "info");
```

**Questions/Confirmations:**
```javascript
const response = await agentBridge.ask(
  "Found two possible send buttons. Should I use the one with aria-label?",
  ["Yes", "No", "Show me both"]
);
```

**Progress Tracking:**
```javascript
agentBridge.progress(45, "Tested 9 of 20 buttons");
```

**Interactive Testing:**
```javascript
await agentBridge.sendInteractiveStep(
  "Hover over the send button for 3 seconds",
  "button_hover_test",
  "test-001"
);
const result = await agentBridge.waitForResponse("test-001");
```

**Stop Button:**
- Always-visible "Stop" button during operations
- Allows human to interrupt if agent is on wrong track
- Agent checkpoint at logical boundaries

---

## DOM Observation Patterns

### Waiting for DOM Stability

Many web applications use dynamic rendering. Actions must wait for DOM to settle:

```javascript
async function waitForDOMMutationsToSettle(quietPeriodMs = 100) {
  return new Promise((resolve) => {
    let timeoutId;
    const observer = new MutationObserver(() => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        observer.disconnect();
        resolve();
      }, quietPeriodMs);
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true
    });
    
    // Start initial timeout
    timeoutId = setTimeout(() => {
      observer.disconnect();
      resolve();
    }, quietPeriodMs);
  });
}
```

### Button State Detection

Buttons often change state during interactions:

```javascript
const buttonObserver = {
  changes: [],
  startTime: Date.now(),
  
  observe(buttonSelector) {
    const button = document.querySelector(buttonSelector);
    
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes') {
          this.changes.push({
            type: 'attribute_change',
            attribute: mutation.attributeName,
            oldValue: mutation.oldValue,
            newValue: button.getAttribute(mutation.attributeName),
            timestamp: Date.now() - this.startTime
          });
        }
      });
    });
    
    observer.observe(button, {
      attributes: true,
      attributeOldValue: true,
      attributeFilter: ['disabled', 'aria-busy', 'class']
    });
    
    return observer;
  }
};
```

### Response Monitoring

Detecting when LLM responses complete:

```javascript
async function waitForResponseComplete(responseSelector, timeoutMs = 30000) {
  const startTime = Date.now();
  let lastContent = '';
  let stableCount = 0;
  
  while (Date.now() - startTime < timeoutMs) {
    const element = document.querySelector(responseSelector);
    const currentContent = element?.textContent || '';
    
    if (currentContent === lastContent) {
      stableCount++;
      if (stableCount >= 3) {
        // Content stable for 3 checks (1.5 seconds)
        return { complete: true, content: currentContent };
      }
    } else {
      stableCount = 0;
      lastContent = currentContent;
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  return { complete: false, content: lastContent, error: 'timeout' };
}
```

---

## Error Handling & Recovery

### Error Types

1. **Selector Not Found** - Element missing or changed
2. **DOM Not Stable** - Mutations continue beyond threshold
3. **Action Failed** - Click/type didn't produce expected result
4. **Context Mismatch** - Wrong domain or page state
5. **Timeout** - Operation took too long

### Recovery Strategies

**1. Retry with Backoff**
```python
async def retry_action(action_func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return await action_func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
```

**2. Fallback Selectors**
```javascript
async function findElementWithFallbacks(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      return { element, selector, confidence: 'high' };
    }
  }
  
  // Try fuzzy matching
  const fuzzyMatch = await fuzzyFindElement(selectors[0]);
  if (fuzzyMatch) {
    return { element: fuzzyMatch, selector: 'fuzzy', confidence: 'low' };
  }
  
  throw new Error('Element not found with any selector');
}
```

**3. Self-Correction**
- Procedure tracks success/failure rate
- Auto-triggers re-learning when success rate drops below threshold
- Updates selector strategies based on failures

**4. Human Escalation**
```javascript
if (confidence < THRESHOLD) {
  const guidance = await agentBridge.ask(
    "Procedure failing. Need guidance.",
    ["Retry with debugging", "Mark procedure as broken", "Help me fix it"]
  );
  
  if (guidance === "Help me fix it") {
    await enterInteractiveLearningMode();
  }
}
```

---

## Precondition Checking

### Environment Verification

Before executing procedures, verify preconditions:

**Browser Context:**
```javascript
function checkBrowserPreconditions(required) {
  const checks = {
    domain: window.location.hostname === required.domain,
    path: window.location.pathname.match(required.pathPattern),
    logged_in: document.querySelector('[data-logged-in="true"]') !== null,
    selector_present: document.querySelector(required.selector) !== null
  };
  
  return {
    satisfied: Object.values(checks).every(v => v),
    checks
  };
}
```

**Desktop Context (via yabai):**
```python
def check_desktop_preconditions(required):
    checks = {
        'desktop': get_current_desktop() == required['desktop'],
        'app_open': find_application(required['app']) is not None,
        'window_visible': is_window_visible(required['window'])
    }
    
    return {
        'satisfied': all(checks.values()),
        'checks': checks
    }
```

### Auto-Setup

If preconditions not met, agent can optionally set up environment:

```python
async def ensure_preconditions(procedure):
    pre = procedure.preconditions
    
    # Check current state
    state = check_all_preconditions(pre)
    
    if state['satisfied']:
        return True
    
    # Attempt auto-setup
    if pre.auto_setup_allowed:
        if not state['checks']['desktop']:
            switch_desktop(pre.required_desktop)
        
        if not state['checks']['app_open']:
            launch_application(pre.required_app)
        
        # Re-check
        state = check_all_preconditions(pre)
    
    if not state['satisfied']:
        # Ask human
        response = await agent_bridge.ask(
            f"Preconditions not met: {state['checks']}",
            ["Setup automatically", "Skip this procedure", "Manual setup"]
        )
        
        if response == "Setup automatically":
            await manual_setup_preconditions(pre)
    
    return state['satisfied']
```

---

## Future Enhancements

### 1. Multi-Tab Coordination

Extend `orchestrate_sequences` to handle:
- Opening new tabs
- Switching between tabs
- Coordinating actions across tabs
- Closing tabs when done

```javascript
{
  context: 'discord.com',
  step: 'copyMessage',
  tab: 'discord-main'
},
{
  context: 'claude.ai',
  step: 'submitPrompt',
  tab: 'new',  // Open new tab
  tab_name: 'claude-helper'
},
{
  context: 'claude.ai',
  step: 'copyResponse',
  tab: 'claude-helper'  // Reference by name
}
```

### 2. Iframe Handling

Support transitions into/out of iframes:

```javascript
{
  context: 'app.yeshid.com',
  step: 'navigateToSettings',
  iframe: null
},
{
  context: 'app.yeshid.com',
  step: 'toggleFeature',
  iframe: '#settings-frame'  // Enter iframe
}
```

### 3. Cross-Platform Actions

Seamless integration of browser and OS actions:

```javascript
{
  context: 'browser:claude.ai',
  step: 'copyResponse',
  tab: 'claude-main'
},
{
  context: 'os:macos',
  step: 'switchToDiscord',  // OSAscript
  desktop: 2
},
{
  context: 'browser:discord.com',
  step: 'pasteResponse',
  tab: 'discord-main'
}
```

### 4. Pattern Library

Build library of common UI patterns:
- Message input fields (contenteditable, textarea)
- Send buttons (icons, aria-labels, positions)
- Response streaming (DOM mutation patterns)
- Loading indicators
- Error messages

Agent learns patterns once, applies across applications.

### 5. Temporal Pattern Learning

Capture timing information:
- How fast do responses stream?
- How long do loading states last?
- When do buttons become enabled?

Use timing patterns to optimize waiting strategies.

---

## Questions for Clarification

### Architecture

1. **Context transitions**: Should `orchestrate_sequences` be extended to handle iframes and new tabs, or should that be a separate tool?

2. **Error recovery**: When a sequence fails mid-execution, should it:
   - Retry the failed step?
   - Restart the entire sequence?
   - Ask human for guidance?
   - Mark procedure as broken and exit?

3. **State management**: How should the agent track state across steps in a sequence? Should there be a shared context object passed between steps?

### Learning Process

4. **Confidence thresholds**: What success rate qualifies a procedure as:
   - HIGH confidence (always use)
   - MEDIUM confidence (use with verification)
   - LOW confidence (re-learn)

5. **Version control**: Should procedures be versioned automatically, or should the agent decide when to create new versions?

6. **Testing frequency**: How often should stable procedures be re-tested to ensure they still work?

### Tool Selection

7. **Playwright vs JavaScript**: When should the agent prefer Playwright commands over writing JavaScript? For example, is navigation always Playwright?

8. **DT-Server usage**: Should desktop automation be reserved for cases where browser automation isn't possible, or used proactively for certain task types?

9. **OSAscript integration**: Should osascript be wrapped in Python helpers, or should the agent write raw AppleScript when needed?

### Knowledge Storage

10. **Procedure granularity**: What's the right level of granularity for stored procedures? Should "click button" be separate from "click send button in Claude"?

11. **Search vs organization**: Should procedures be found by:
    - Directory structure (claude_ai/submit_prompt.py)?
    - Semantic search (vector embeddings)?
    - Both?

12. **Metadata format**: Is the proposed metadata format sufficient, or are there other fields needed for procedure management?

### Agent Bridge

13. **Notification frequency**: How often should the agent report status? Only on major milestones, or for every action?

14. **Stop vs Pause**: Should there be separate "Stop" (abort) and "Pause" (continue later) buttons?

15. **Interactive mode**: Should interactive testing mode be a separate mode, or should it be callable at any time during execution?

---

## Implementation Priorities

### Phase 1: Core Infrastructure
- ✅ Basic action execution via JavaScript
- ✅ Current `orchestrate_sequences` implementation  
- ⏳ Enhanced DOM observation patterns
- ⏳ Agent Bridge for human coordination

### Phase 2: Learning System
- ⏳ Interactive learning mode
- ⏳ Procedure generation from observations
- ⏳ Testing and validation framework
- ⏳ Knowledge storage system

### Phase 3: Advanced Features
- ⏳ Multi-tab coordination
- ⏳ Iframe handling
- ⏳ Cross-platform actions (browser + OS)
- ⏳ Pattern library and reuse

### Phase 4: Intelligence
- ⏳ Self-correction and auto-relearning
- ⏳ Confidence-based execution modes
- ⏳ Temporal pattern recognition
- ⏳ Semantic procedure search

---

## Success Metrics

**Learning Effectiveness:**
- Time to learn new procedure (from exploration to stable)
- Success rate of learned procedures
- Number of procedures that remain stable over time

**Execution Reliability:**
- Procedure success rate across different environments
- Error recovery success rate
- Time to detect and adapt to interface changes

**Knowledge Quality:**
- Procedure reusability across similar contexts
- False positive rate (procedures that seem to work but don't)
- Human intervention frequency

**Developer Experience:**
- Time saved vs manual scripting
- Confidence in agent's decisions
- Ease of debugging failed procedures

---

## Conclusion

This browser automation learning agent represents a shift from traditional scripting to **intelligent, adaptive automation**. By observing, learning, testing, and consolidating browser interactions into a structured knowledge base, the agent can:

- **Learn once, reuse everywhere** - Patterns learned from one interface can accelerate learning others
- **Adapt to changes** - Self-correct when interfaces evolve
- **Scale gracefully** - From simple single-page actions to complex multi-application workflows
- **Collaborate with humans** - Leverage human expertise where needed while automating repetitive patterns

The three-tier hierarchy of Actions → Steps → Sequences provides a natural way to organize automation knowledge at appropriate levels of abstraction, while the integration of multiple tool servers (Playwright, Plasmo, DT-Server, OSAscript) enables comprehensive automation across browser and desktop environments.