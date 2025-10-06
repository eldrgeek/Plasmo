# Web Automation Agent Implementation Plan

## Project Overview

Build an agentic AI system that learns, executes, and refines web automation workflows by discovering procedures through Playwright exploration and executing them via JavaScript injection, storing learned procedures in a git-tracked library for reuse and continuous improvement.

> **📋 Related Document**: See [`automation-agent-architecture.md`](./automation-agent-architecture.md) for detailed architectural concepts, design patterns, and technical implementation details.

## Core Architecture Principles

### 1. Three-Tier Hierarchy

- **Sequence** (also called "procedure"): Cross-context workflows executed across different domains/contexts
- **Step**: Same-context actions performed in the same browser context
- **Action**: Atomic operations with preconditions (single browser interactions)

> **🔗 Architecture Details**: See [Three-Tier Hierarchy](./automation-agent-architecture.md#the-three-tier-hierarchy) in automation-agent-architecture.md for detailed examples and implementation patterns.

### 2. Tool Usage Strategy

- **Playwright**: Discovery and exploration ONLY (read-only page analysis)
- **JavaScript Execution**: ALL actions and interactions (via `orchestrate_sequences` and `execute_javascript`)
- **File Operations**: Procedure storage and retrieval (existing smart_read/write_file tools)

> **🔗 Tool Integration Details**: See [Tool Integration](./automation-agent-architecture.md#tool-integration) section for comprehensive tool usage patterns and limitations.

### 3. Separation of Concerns

- **Exploration**: Understand page structure, identify elements, generate selectors
- **Execution**: Run JavaScript that performs actual interactions
- **Learning**: Capture what works, store procedures with metadata
- **Healing**: Diagnose failures, regenerate improved code, update procedures

### 4. Core Design Patterns

- **Non-blocking Guards**: Use MutationObserver or Promise-based polling, never block render thread
- **Multi-Selector Strategy**: Multiple fallback selectors per element, ranked by robustness
- **Composability**: Procedures can call other procedures (dependency resolution)
- **Self-Healing**: Failures return diagnostic info for automated regeneration

> **🔗 Implementation Patterns**: See [DOM Observation Patterns](./automation-agent-architecture.md#dom-observation-patterns) and [Error Handling & Recovery](./automation-agent-architecture.md#error-handling--recovery) for detailed code examples and patterns.

---

## Directory Structure

```
~/procedures/
├── metadata.json                    # Global procedure index with search metadata
├── web/
│   ├── {domain}/
│   │   ├── auth/
│   │   │   ├── login.json
│   │   │   ├── logout.json
│   │   │   ├── ensure_logged_in.json
│   │   │   └── check_login_status.json
│   │   ├── {feature_area}/
│   │   │   └── {action}.json
│   │   └── ...
├── workflows/                       # Future: composed multi-procedure workflows
│   └── {workflow_name}.json
└── templates/
    ├── procedure_template.json
    └── workflow_template.json
```

> **🔗 Storage Architecture**: See [Knowledge Storage Architecture](./automation-agent-architecture.md#knowledge-storage-architecture) for detailed explanation of the JSON-based storage format and migration strategy.

---

## 📋 **PROJECT PLANNING HUB**

> **🎯 Use this section for task generation and project management**

### **Quick Reference Links**

- **Architecture Overview**: [`automation-agent-architecture.md`](./automation-agent-architecture.md)
- **Implementation Phases**: [Below](#implementation-phases)
- **Success Metrics**: [Success Metrics](#success-metrics)
- **Testing Protocol**: [Testing Protocol](#testing-protocol)

### **Phase Summary for Project Planning**

| Phase       | Duration  | Key Deliverables                                    | Dependencies |
| ----------- | --------- | --------------------------------------------------- | ------------ |
| **Phase 1** | 1 hour    | Directory structure, templates, metadata system     | None         |
| **Phase 2** | 2-3 hours | GitHub login/logout procedures, learning validation | Phase 1      |
| **Phase 3** | 3-4 hours | Composability system, dependency resolution         | Phase 2      |
| **Phase 4** | 4-5 hours | Self-healing mechanisms, diagnostic system          | Phase 3      |
| **Phase 5** | 2-3 hours | Non-blocking guards, timing profiles                | Phase 4      |
| **Phase 6** | 2-3 hours | Search system, metadata management                  | Phase 5      |

### **Critical Path Dependencies**

1. **Phase 1** → **Phase 2**: Infrastructure must be ready before learning
2. **Phase 2** → **Phase 3**: Need working procedures before composability
3. **Phase 3** → **Phase 4**: Composability enables complex failure scenarios
4. **Phase 4** → **Phase 5**: Recovery system needs robust guard patterns
5. **Phase 5** → **Phase 6**: Search system benefits from timing data

### **Resource Requirements**

- **Development Time**: 15-20 hours total
- **Testing Environment**: Chrome with debug protocol enabled
- **Tools**: Playwright MCP, Plasmo MCP, Chrome Debug Protocol
- **Storage**: `~/procedures/` directory with JSON files

---

## Procedure File Schema

```json
{
  "name": "github_login",
  "domain": "github.com",
  "description": "Log into GitHub account using OAuth or password manager",
  "version": "1.0.0",
  "created": "2025-10-01T11:30:00Z",
  "last_updated": "2025-10-01T11:30:00Z",
  "last_tested": "2025-10-01T11:30:00Z",

  "tags": ["auth", "github", "required_for_other_actions"],
  "dependencies": [],

  "sequences": [
    {
      "type": "execute",
      "domain_pattern": "github\\.com",
      "description": "Navigate to login page",
      "javascript": "document.querySelector('a[href=\"/login\"]').click()",
      "wait_for_element": "input[name='login']",
      "wait_timeout": 10000,
      "wait_config": {
        "method": "observer",
        "recommended_timeout": 5000,
        "success_history": [
          { "timestamp": "2025-10-01T10:00:00Z", "actual_wait_ms": 450 }
        ]
      }
    },
    {
      "type": "execute",
      "domain_pattern": "github\\.com/login",
      "description": "Wait for and submit login form",
      "javascript": "/* Multi-selector login code */",
      "selectors": [
        {
          "type": "aria-label",
          "value": "Sign in",
          "priority": 1,
          "last_verified": "2025-10-01"
        },
        {
          "type": "data-testid",
          "value": "login-button",
          "priority": 2
        },
        {
          "type": "css",
          "value": "button.btn-primary",
          "priority": 3,
          "notes": "Fragile: generic class"
        }
      ],
      "success_indicators": {
        "element_present": "img[alt*='avatar']",
        "url_pattern": "github\\.com$",
        "page_title_pattern": "GitHub"
      }
    }
  ],

  "execution_stats": {
    "total_executions": 15,
    "success_count": 14,
    "success_rate": 0.933,
    "avg_duration_ms": 2340,
    "last_failure": {
      "timestamp": "2025-09-28T14:20:00Z",
      "error": "selector_not_found",
      "resolution": "Updated to new selector",
      "fixed_in_version": "1.0.0"
    }
  },

  "timing_profile": {
    "sequence_1_wait": {
      "p50": 450,
      "p95": 620,
      "p99": 890,
      "recommended_timeout": 2000
    }
  },

  "recovery": {
    "common_failures": [
      {
        "error": "button_not_found",
        "likely_cause": "page redesign",
        "retry_strategy": "use_alternate_selector"
      }
    ]
  },

  "credentials": {
    "strategy": "browser_oauth_or_password_manager",
    "notes": "Relies on Google OAuth or browser password manager auto-fill"
  },

  "language_variations": {
    "tested_languages": ["en"],
    "selector_strategy": "prefer aria-labels and data attributes over text"
  }
}
```

---

## Implementation Phases

### Phase 1: Bootstrap Infrastructure

**Goal**: Create foundational structure and templates

**Tasks**:

1. Create directory structure in `~/procedures/`
2. Write `procedure_template.json` with full schema
3. Create empty `metadata.json` with index structure
4. Document procedure file format specification

**Success Criteria**:

- Directories exist and are git-tracked
- Template file validates against schema
- Documentation is clear and complete

**Estimated Time**: 1 hour

---

### Phase 2: First Learning Session

**Goal**: Manually walk through learning a complete procedure

**Example Task**: Learn GitHub login + logout

> **🔗 Execution Modes**: This phase uses [Learning Mode (Step-by-Step)](./automation-agent-architecture.md#1-learning-mode-step-by-step) from the architecture document. See [Execution Modes](./automation-agent-architecture.md#execution-modes) for detailed comparison of learning vs orchestrated approaches.

**Detailed Workflow**:

#### Step 2.1: Exploration Phase

```javascript
// Use Playwright to explore GitHub homepage
1. Navigate to github.com
2. Use playwright:browser_snapshot to get page structure
3. Identify login link/button with multiple selector strategies
4. Record all possible selectors (aria-label, data-testid, text, css)
```

#### Step 2.2: Code Generation Phase

```javascript
// Generate JavaScript with non-blocking guards
const loginCode = `
async function clickLogin() {
  // Multi-selector strategy with fallbacks
  const selectors = [
    'a[aria-label="Sign in"]',
    'a[href="/login"]',
    'a:contains("Sign in")'  // Note: might need custom implementation
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      element.click();
      return {
        success: true,
        selector_used: selector,
        action: 'clicked_login'
      };
    }
  }
  
  return {
    success: false,
    error: 'no_login_button',
    available_links: Array.from(document.querySelectorAll('a'))
      .map(a => ({href: a.href, text: a.textContent.trim()}))
  };
}

await clickLogin();
`;
```

#### Step 2.3: Execution Phase

```javascript
// Test with orchestrate_sequences
const result = await orchestrate_sequences(tabId, [
  {
    domain_pattern: "github\\.com$",
    javascript: loginCode,
    description: "Click login button",
  },
  {
    domain_pattern: "github\\.com/login",
    javascript: logoutCheckCode,
    description: "Verify we reached login page",
  },
]);
```

#### Step 2.4: Storage Phase

```javascript
// Store successful procedure
await smart_write_file(
  "~/procedures/web/github.com/auth/login.json",
  JSON.stringify(procedureObject, null, 2)
);

// Update metadata.json index
await updateMetadataIndex({
  domain: "github.com",
  procedure: "login",
  path: "web/github.com/auth/login.json",
  tags: ["auth", "github"],
});
```

**Success Criteria**:

- Login procedure successfully stored
- Logout procedure successfully stored
- Both procedures execute cleanly from storage
- Metadata index updated correctly

**Estimated Time**: 2-3 hours

---

### Phase 3: Composability Implementation

**Goal**: Enable procedures to call other procedures

> **🔗 Composability Patterns**: See [Composability](./automation-agent-architecture.md#composability) section for detailed examples of procedure dependencies and context passing between procedures.

**Tasks**:

1. **Create `ensure_logged_in` Helper Procedure**

```json
{
  "name": "github_ensure_logged_in",
  "sequences": [
    {
      "type": "call_procedure",
      "procedure": "web/github.com/auth/check_login_status.json",
      "required": false
    },
    {
      "type": "conditional",
      "condition": "previous_result.logged_in === false",
      "if_true": {
        "type": "call_procedure",
        "procedure": "web/github.com/auth/login.json",
        "required": true
      }
    }
  ]
}
```

2. **Implement Dependency Resolution in Agent**

```javascript
async function executeProcedure(procedurePath, context = {}) {
  const proc = await loadProcedure(procedurePath);

  for (const sequence of proc.sequences) {
    if (sequence.type === "call_procedure") {
      const subResult = await executeProcedure(sequence.procedure, context);

      if (!subResult.success && sequence.required) {
        return {
          success: false,
          error: `Dependency failed: ${sequence.procedure}`,
          sub_result: subResult,
        };
      }

      context.last_result = subResult;
    } else if (sequence.type === "execute") {
      const result = await executeSequence(sequence, context);

      if (!result.success) {
        // Trigger failure recovery
        return await diagnoseAndFix(sequence, result);
      }

      context.last_result = result;
    }
  }

  return { success: true, context };
}
```

3. **Create Dependent Procedure**

```json
{
  "name": "github_create_repo",
  "sequences": [
    {
      "type": "call_procedure",
      "procedure": "web/github.com/auth/ensure_logged_in.json",
      "required": true
    },
    {
      "type": "execute",
      "domain_pattern": "github\\.com",
      "javascript": "/* Navigate to new repo page */"
    }
  ]
}
```

**Success Criteria**:

- `ensure_logged_in` works as standalone procedure
- `create_repo` successfully calls `ensure_logged_in`
- Dependency failure propagates correctly
- Execution context passes between procedures

**Estimated Time**: 3-4 hours

---

### Phase 4: Failure Recovery System

**Goal**: Automatically diagnose and fix broken procedures

**Enhanced orchestrate_sequences Output**:

```json
{
  "success": false,
  "sequences_executed": [
    {
      "index": 3,
      "success": false,
      "error": "selector_not_found",
      "attempted_code": "document.querySelector('.old-class').click()",
      "diagnostics": {
        "page_url": "github.com/repo/new",
        "page_title": "Create a new repository",
        "similar_elements": [
          {
            "selector": "button[type='submit']",
            "text": "Create repository",
            "aria_label": "Create repository",
            "visible": true
          }
        ],
        "console_errors": [],
        "screenshot_available": false
      }
    }
  ]
}
```

**Agent Recovery Workflow**:

```
1. Receive failure with diagnostics
2. Parse error: "selector .old-class not found"
3. Analyze diagnostics.similar_elements
4. Use Playwright to verify correct element:
   - Navigate to same page
   - Take snapshot
   - Confirm button[type='submit'] is correct target
5. Generate updated JavaScript with multi-selector fallback
6. Test updated code via orchestrate_sequences
7. If successful:
   - Update procedure file
   - Add to changelog
   - Mark old selector as deprecated
8. Continue from failed step
```

**Self-Healing Code Pattern**:

```javascript
async function robustClick(selectorStrategies) {
  for (const strategy of selectorStrategies) {
    const element = document.querySelector(strategy.selector);
    if (element && element.offsetParent !== null) {
      element.click();
      return {
        success: true,
        selector_used: strategy.selector,
        strategy_type: strategy.type,
      };
    }
  }

  // If all strategies fail, return diagnostic info
  return {
    success: false,
    error: "no_matching_element",
    attempted_selectors: selectorStrategies.map((s) => s.selector),
    available_buttons: Array.from(document.querySelectorAll("button")).map(
      (btn) => ({
        text: btn.textContent.trim(),
        type: btn.type,
        classes: btn.className,
        aria_label: btn.getAttribute("aria-label"),
      })
    ),
  };
}
```

**Success Criteria**:

- Agent receives rich diagnostic info on failure
- Agent can re-explore page with Playwright
- Agent generates improved code with fallbacks
- Updated procedure passes validation
- Failure history tracked in procedure metadata

**Estimated Time**: 4-5 hours

---

### Phase 5: Non-Blocking Guard Patterns

**Goal**: Ensure all waiting is non-blocking

> **🔗 Guard Patterns**: See [DOM Observation Patterns](./automation-agent-architecture.md#dom-observation-patterns) for comprehensive examples of MutationObserver patterns, button state detection, and response monitoring.

**MutationObserver Pattern**:

```javascript
function waitForElement(selector, timeout = 10000) {
  return new Promise((resolve, reject) => {
    // Check if already present
    const existing = document.querySelector(selector);
    if (existing) {
      return resolve({
        element: existing,
        wait_time: 0,
      });
    }

    let timeoutId;
    const observer = new MutationObserver(() => {
      const element = document.querySelector(selector);
      if (element) {
        observer.disconnect();
        clearTimeout(timeoutId);
        resolve({
          element,
          wait_time: Date.now() - startTime,
        });
      }
    });

    const startTime = Date.now();
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    timeoutId = setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Element ${selector} not found within ${timeout}ms`));
    }, timeout);
  });
}

// Usage in procedure
try {
  const { element, wait_time } = await waitForElement(".login-btn", 10000);
  element.click();
  return { success: true, wait_time };
} catch (error) {
  return {
    success: false,
    error: "timeout_waiting_for_element",
    selector: ".login-btn",
    timeout: 10000,
  };
}
```

**Timing Profile Learning**:

```javascript
// After each successful execution, update timing profile
function updateTimingProfile(procedure, sequenceIndex, actualWaitTime) {
  const profile = procedure.timing_profile[`sequence_${sequenceIndex}_wait`];

  profile.measurements.push({
    timestamp: new Date().toISOString(),
    wait_ms: actualWaitTime,
  });

  // Calculate percentiles
  const sorted = profile.measurements.map((m) => m.wait_ms).sort();
  profile.p50 = percentile(sorted, 0.5);
  profile.p95 = percentile(sorted, 0.95);
  profile.p99 = percentile(sorted, 0.99);

  // Recommend timeout: p95 + 50% buffer, min 2000ms
  profile.recommended_timeout = Math.max(2000, Math.ceil(profile.p95 * 1.5));

  return profile;
}
```

**Success Criteria**:

- All guards use MutationObserver or Promise-based polling
- No synchronous blocking waits
- Timing profiles updated after successful executions
- Timeout recommendations adjust based on history

**Estimated Time**: 2-3 hours

---

### Phase 6: Metadata and Search System

**Goal**: Enable efficient procedure discovery

**Metadata Index Structure**:

```json
{
  "version": "1.0",
  "last_updated": "2025-10-01T15:00:00Z",
  "total_procedures": 25,

  "procedures": {
    "github.com": {
      "login": {
        "path": "web/github.com/auth/login.json",
        "tags": ["auth", "github", "required"],
        "dependencies": [],
        "dependents": ["github.com/create_repo", "github.com/fork"],
        "success_rate": 0.95,
        "last_tested": "2025-10-01T14:00:00Z"
      }
    }
  },

  "tags_index": {
    "auth": ["github.com/login", "linkedin.com/login"],
    "github": ["github.com/login", "github.com/create_repo", "github.com/fork"]
  },

  "dependency_graph": {
    "github.com/create_repo": ["github.com/login"],
    "github.com/fork": ["github.com/login"]
  }
}
```

**Fuzzy Search Implementation**:

```javascript
function searchProcedures(query) {
  const tokens = query.toLowerCase().split(/\s+/);
  const results = [];

  for (const [domain, procedures] of Object.entries(metadata.procedures)) {
    for (const [name, proc] of Object.entries(procedures)) {
      let score = 0;

      // Match against name
      if (name.includes(tokens.join("_"))) score += 10;

      // Match against domain
      if (tokens.some((t) => domain.includes(t))) score += 5;

      // Match against tags
      const matchingTags = proc.tags.filter((tag) =>
        tokens.some((t) => tag.includes(t))
      );
      score += matchingTags.length * 3;

      // Match against description
      const desc = loadProcedure(proc.path).description.toLowerCase();
      score += tokens.filter((t) => desc.includes(t)).length * 2;

      if (score > 0) {
        results.push({
          domain,
          name,
          path: proc.path,
          score,
          tags: proc.tags,
        });
      }
    }
  }

  return results.sort((a, b) => b.score - a.score);
}

// Usage
const matches = searchProcedures("github login");
// Returns: [{domain: "github.com", name: "login", score: 18, ...}]
```

**Success Criteria**:

- Metadata index stays in sync with procedures
- Search finds relevant procedures
- Tag-based filtering works
- Dependency graph is accurate

**Estimated Time**: 2-3 hours

---

## Testing Protocol

### Manual Validation Checklist

For each new procedure:

- [ ] **Clean State Test**: Clear cookies/cache, execute procedure
- [ ] **Rapid Repeat Test**: Execute 3 times in succession
- [ ] **Failure Injection Test**: Break selector, verify recovery
- [ ] **Composability Test**: Call from dependent procedure
- [ ] **Timing Test**: Verify non-blocking waits
- [ ] **Metadata Test**: Verify index updates correctly

### Automated Test Suite (Future)

```javascript
// Example test structure
describe("GitHub Login Procedure", () => {
  it("should execute successfully from clean state", async () => {
    await clearBrowserState();
    const result = await executeProcedure("github.com/login");
    expect(result.success).toBe(true);
  });

  it("should handle missing password manager gracefully", async () => {
    await disablePasswordManager();
    const result = await executeProcedure("github.com/login");
    expect(result.error).toContain("user_intervention_required");
  });
});
```

---

## Future Enhancements

### Phase 7: RAG-based Search (Future)

- Vector embeddings of procedure descriptions
- Semantic search over procedure library
- Context-aware suggestions based on browser history

### Phase 8: Specialist Agent (Future)

- Task decomposition into procedure chains
- Workflow composition and orchestration
- Error recovery strategies
- Learning from execution patterns

### Phase 9: Community Sharing (Future)

- Procedure validation and signing
- Community success metrics
- Version compatibility tracking
- Contribution guidelines

---

## Agent Instructions Template

Add to existing personal sidekick instructions:

```markdown
## WEB AUTOMATION CAPABILITIES

When asked to perform web tasks (login, create, submit, etc.):

### 1. CHECK LIBRARY FIRST

- Read ~/procedures/metadata.json
- Search for existing procedure matching task
- If found and recently tested (< 30 days), use it
- If found but old, consider re-validation

### 2. LEARNING NEW PROCEDURES

- Use Playwright (browser_snapshot) to explore pages - READ ONLY
- Identify elements using multiple selector strategies
- Generate JavaScript with non-blocking guards (MutationObserver)
- Test with orchestrate_sequences (NOT Playwright execution)
- Store in ~/procedures/web/{domain}/{category}/{action}.json
- Update metadata index

### 3. EXECUTION RULES

- NEVER use Playwright for actions, ONLY for discovery
- ALL actions via execute_javascript or orchestrate_sequences
- Return detailed execution info for learning
- Handle browser password managers and OAuth flows

### 4. HANDLING FAILURES

- Parse diagnostic info from orchestrate_sequences output
- Re-explore page with Playwright (snapshot only)
- Generate improved code with multi-selector fallbacks
- Update procedure file with learned improvements
- Mark deprecated selectors with timestamp

### 5. CODE PATTERNS

- Use MutationObserver for waiting (non-blocking)
- Multiple selector fallbacks ranked by robustness:
  1. aria-label (most robust)
  2. data-testid
  3. semantic HTML attributes
  4. CSS classes (least robust)
- Return detailed results for timing profile learning
- Handle both success and failure cases explicitly

### 6. COMPOSABILITY

- Procedures can call other procedures
- Check dependencies before execution
- Pass context between composed procedures
- Handle dependency failures gracefully

### 7. ASKING FOR HELP

When automation gets stuck:

- Password manager dropdown outside DOM
- CAPTCHA or 2FA challenge
- Unclear user intent
- Safety concerns (destructive actions)

Provide clear context and ask specific questions.
```

---

## Success Metrics

### Short-term (Phase 1-3)

- [ ] At least 3 procedures stored and working
- [ ] Composability demonstrated with dependent procedures
- [ ] Metadata index accurate and searchable

### Medium-term (Phase 4-6)

- [ ] Self-healing demonstrated on at least 2 broken procedures
- [ ] All guards are non-blocking
- [ ] Timing profiles improve timeout recommendations

### Long-term (Future Phases)

- [ ] 50+ procedures in library
- [ ] Community contributions integrated
- [ ] RAG search operational
- [ ] Specialist agent handles complex workflows

---

## Notes & Considerations

### Credentials Strategy

- **Preferred**: OAuth flows (browser handles)
- **Common**: Password manager auto-fill
- **Special**: Screenshot + click coordinates (future)
- **Fallback**: Ask user for help

### Timing Philosophy

- Start conservative (10s timeouts)
- Learn from execution history
- Adjust recommendations based on p95 + buffer
- Track timing profiles per sequence

### Error Recovery Decision Tree

1. Retry with same approach (if transient network error)
2. Try alternate selectors immediately (if element not found)
3. Re-explore with Playwright (if multiple failures)
4. Ask user for help (if stuck after exploration)

### Execution Context Requirements (Future)

- Browser capabilities (cookies, JavaScript, localStorage)
- Viewport requirements
- Iframe compatibility
- Mobile vs desktop

---

## Git Workflow

### Commit Conventions

- `feat(domain): add {action} procedure`
- `fix(domain/action): update selector for new UI`
- `test(domain/action): verify works with {condition}`
- `docs: update procedure schema`

### Branching Strategy

- `main`: Stable, tested procedures
- `feat/*`: New procedures under development
- `fix/*`: Updates to broken procedures

### Pull Request Template

```markdown
## Procedure Update

**Domain**: github.com
**Action**: login
**Change Type**: [new|fix|enhancement]

### Changes

- Updated login button selector
- Added aria-label fallback
- Improved error messages

### Testing

- [ ] Clean state test passed
- [ ] Rapid repeat test (3x) passed
- [ ] Composability test passed

### Metadata Updates

- [ ] Version bumped
- [ ] Changelog updated
- [ ] Success rate recalculated
```

---

## Contact & Maintenance

**Primary Maintainer**: Personal AI Sidekick Agent
**Repository**: ~/Projects/Plasmo/
**Documentation**: ~/Projects/Plasmo/docs/

**Review Schedule**:

- Weekly: Check for broken procedures (success_rate < 0.8)
- Monthly: Update timing profiles from execution history
- Quarterly: Audit dependency graph for circular dependencies
