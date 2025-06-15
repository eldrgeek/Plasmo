# Roundtable Development Documentation Enhancements

This document outlines enhancements to the Roundtable project documentation, including:

- A backend testing plan
- A frontend implementation plan with Bolt.new integration
- A UI testing plan with self-driven automation
- A reusable Bolt.new workflow guide

---

## 1. Backend Testing Plan

To ensure the reliability of the backend, implement a testing pyramid strategy:

### Unit Testing
- **Goal**: Test isolated functions and classes
- **Tools**:
  - Python: `pytest`
  - JavaScript/Node: `jest`, `mocha`, or `uvu`
- **Practices**:
  - Mock dependencies
  - Fast execution
  - Run with: `pytest tests/unit/`

### Integration Testing
- **Goal**: Verify communication between modules (e.g., MCP server ↔ socket.io)
- **Tools**:
  - Python: `pytest` with `pytest-asyncio`
  - TypeScript: `jest` or `vitest` with in-memory socket mocks
- **Practices**:
  - Use test fixtures to set up environments
  - Test socket message flow and Chrome protocol calls
  - Run with: `pytest tests/integration/`

### End-to-End Testing
- **Goal**: Validate full-stack user scenarios
- **Tools**:
  - `Playwright` or `Cypress` (headless browser automation)
- **Practices**:
  - Run the full stack in a test environment
  - Simulate user interactions and LLM responses
  - Run with: `npx playwright test` or `npx cypress run`

---

## 2. Frontend Implementation Plan with Bolt.new

This project uses **bolt.new**, an AI coding agent, to automate stepwise frontend development.

### Workflow Summary
- Provide Bolt.new with an implementation spec
- Bolt breaks the spec into separate tasks
- Tasks are saved as `.md` files in `plans/todo/`
- Each task file points to the next one
- A file `plans/head` points to the current task
- Completed tasks are moved to `plans/done/`

### Directory Layout
```
plans/
├── head                # contains filename of current task
├── todo/
│   ├── 01_create_ui.md
│   ├── 02_connect_socket.md
│   └── ...
└── done/
    └── 01_create_ui.md
```

### Example Task File (`plans/todo/01_create_ui.md`)
```markdown
## Task: Create the extension popup UI
- Create a React component `Popup.tsx`
- Include a button to trigger a message to the background script

### Next:
02_connect_socket.md
```

### Execution Loop
1. Bolt reads the file referenced in `plans/head`
2. Executes task (e.g., writes code)
3. Moves file to `plans/done/`
4. Updates `plans/head` to the `Next:` file
5. Repeats until `plans/todo/` is empty

### Benefits
- Stepwise execution reduces context overload
- Tasks can be reviewed or revised individually
- Highly compatible with AI flow programming principles

---

## 3. UI Testing Plan with Self-Driven Automation

### Component Testing
- **Tool**: `jest` with `@testing-library/react`
- **Scope**: UI components (`.tsx`)
- **Examples**:
  - Render tests: `expect(getByText("Send")).toBeInTheDocument()`
  - Event handling: `fireEvent.click(button)`

### End-to-End UI Testing
- **Tool**: `Playwright` (preferred) or `Cypress`
- **Examples**:
  - Load extension popup via `chrome-extension://<id>/popup.html`
  - Simulate click and verify DOM change
- **Commands**:
  - `npx playwright test`
  - `npx playwright codegen` (to record tests)

### CI Integration
- Add to `.github/workflows/test.yml`:
```yaml
- name: Run Playwright Tests
  run: npx playwright install && npx playwright test
```
- Trigger on UI-related file changes:
```yaml
on:
  push:
    paths:
      - 'src/**.tsx'
      - 'src/**.css'
```

---

## 4. Bolt.new Agent Workflow Guide

### Purpose
A reusable methodology for using AI coding agents to develop software projects incrementally.

---

### 🔁 Bolt.new Task Queue Structure

**Directories:**
- `plans/todo/`: contains Markdown task files
- `plans/done/`: completed task files
- `plans/head`: points to the current task filename

**Task File Format:**
```markdown
## Task Summary
Instructions for one logical change

### Next:
<next-task-filename>
```

---

### 🚀 Workflow Steps

1. **Write a spec** for the project or feature
2. **Use Bolt.new** to split it into file-scoped tasks saved to `plans/todo/`
3. **Point `plans/head`** to the first task
4. **Run Bolt** on the file in `plans/head`
5. **After execution**:
   - Move the file to `plans/done/`
   - Update `plans/head` to `Next:` in the task
6. **Repeat** until all tasks are completed

---

### ✅ Best Practices

- Keep each task **small and focused**
- Use human-readable filenames (e.g., `03_fix_popup_layout.md`)
- Allow manual edits of task files if needed
- Run tests after each task completion
- Version control the `plans/` directory to preserve history

---

### 🛠 Tooling Suggestions

- Bolt.new
- Cursor (for integrating agent execution)
- Playwright (to run tests after each task)
- Git pre-commit hook to lint or validate changed files

---

### 📦 Example Project Setup
```bash
mkdir plans/todo plans/done
echo "01_setup_env.md" > plans/head
# Use your orchestrator to feed each task to Bolt
```

---

### 🤖 Why This Works
- Aligns with AI's strengths in single-responsibility tasks
- Avoids context dilution from multi-file prompts
- Encourages iterative review and testing
- Scales to multi-agent systems with coordination queues

---

This guide is reusable for any agent that:
- Accepts a spec
- Writes code
- Accepts file-level prompts
- Can update a local file system

---

End of document.