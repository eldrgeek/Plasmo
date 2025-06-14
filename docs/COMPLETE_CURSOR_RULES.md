# Complete Cursor Rules Documentation

This document contains the complete text of all cursor rules files that influence the Plasmo Chrome Extension with MCP Server repository.

## `.cursorrules` (Root Configuration)

```
# Cursor Rules for Plasmo Extension Development with MCP Server

## Project Context
This is a Plasmo browser extension project with an integrated MCP (Model Context Protocol) server for Chrome Debug Protocol integration. The MCP server enables real-time debugging and monitoring of the extension through AI assistance.

## Key Technologies
- **Plasmo**: Browser extension framework
- **TypeScript/React**: Extension UI and logic
- **Python FastMCP**: MCP server for Chrome debugging
- **Chrome Debug Protocol**: Browser automation and debugging
- **WebSocket**: Real-time communication with browser

## Development Guidelines

### MCP Server Development
- Always ensure return values from MCP tools are JSON-serializable (no complex objects)
- Use `make_json_safe()` helper for converting objects to basic types
- Handle Chrome Debug Protocol WebSocket connections carefully
- **CRITICAL: Chrome Debug Protocol requires INTEGER request IDs, not strings**
- Use `int(time.time() * 1000000) % 1000000` for Chrome Debug Protocol request IDs
- Test Chrome flag compatibility when adding new debugging features
- Remember that extension service worker IDs change on Chrome restart

### Chrome Debugging Setup
- Use `./launch-chrome-debug.sh` script for proper Chrome configuration
- Required flags: `--remote-debugging-port=9222 --remote-allow-origins=*`
- Extension debugging requires special WebSocket origin permissions
- Monitor console logs through MCP server tools, not direct WebSocket connections

### Code Organization
- Keep MCP server tools focused and single-purpose
- Document Chrome Debug Protocol interactions thoroughly
- Maintain separation between extension code and debugging infrastructure
- Use proper error handling for WebSocket connections

### File Management
- Never commit `__pycache__/`, `mcp_server.log`, or Chrome profile contents
- Keep `chrome-debug-profile/` directory structure but ignore contents
- Document any new MCP tools in relevant README files

### Extension Development
- Test extension functionality both standalone and through MCP debugging
- Verify auto-reload functionality works with file changes
- Use MCP server console monitoring for debugging extension logic
- Maintain compatibility between extension and debugging infrastructure

### Best Practices
- Test MCP server tools thoroughly before committing
- Handle serialization edge cases proactively
- Document Chrome version compatibility for debugging features
- Keep debugging tools separate from production extension code
- Use parallel tool calls when gathering multiple pieces of information

## Common Issues & Solutions
- **Serialization errors**: Convert objects to dict/list/string before returning
- **WebSocket 403 errors**: Ensure `--remote-allow-origins=*` flag is set
- **Chrome Debug Protocol "integer id" error**: Use integer request IDs, not strings
- **Extension not found**: Check service worker is running and ID is current
- **MCP tools not available**: Restart Cursor after server changes
```

---

## `.cursor/rules/core-architecture.mdc`

```

# Plasmo Chrome Extension Architecture Standards

## Project Structure Requirements
- Follow Plasmo framework conventions for file organization
- Use TypeScript for all source files
- Maintain clear separation between popup, background, content scripts, and options pages
- Keep MCP server components isolated in dedicated files

## Chrome Extension Patterns
- Use Manifest V3 standards and APIs
- Implement proper message passing between contexts (popup ↔ background ↔ content)
- Handle async Chrome API calls with proper error handling
- Use Chrome storage APIs for persistence, never localStorage in extension contexts

## React Integration
- Use functional components with hooks
- Implement proper state management for popup and options pages
- Follow React 18 patterns with concurrent features
- Use TypeScript interfaces for all props and state

## File Naming Conventions
```
popup.tsx          # Main popup component
options.tsx        # Extension options page
background.ts      # Service worker background script
contents/          # Content scripts directory
  main.ts          # Primary content script
assets/           # Static assets (icons, images)
```

## Import Standards
- Use relative imports for local modules
- Import types with `import type` syntax
- Group imports: React/external libraries first, then local imports
- Use destructuring for named imports

## Error Handling
- Wrap Chrome API calls in try-catch blocks
- Implement fallback behavior for missing permissions
- Log errors appropriately for debugging
- Use TypeScript strict mode for compile-time error prevention

```

---

## `.cursor/rules/ai-assistant-instructions.mdc`

```
# AI Assistant Operating Instructions

## Rule System Integration
As an AI assistant with MCP access, I should actively reference and follow the established cursor rules:

### Core Workflow
1. **Read Current Rules**: Always check existing `.cursor/rules/*.mdc` files before providing advice
2. **Follow Established Patterns**: Adhere to patterns defined in the project's cursor rules
3. **Use MCP Capabilities**: Leverage MCP server tools for hands-on analysis and implementation
4. **Update Rules**: Suggest updates to rules based on discovered patterns or improvements

### Rule Categories to Reference
- **core-architecture.mdc**: Project structure and Chrome extension patterns
- **typescript-react-standards.mdc**: Code quality and React patterns
- **testing-strategy.mdc**: Testing approach and implementation
- **planning-methodology.mdc**: Project planning and agile practices
- **specification-standards.mdc**: Documentation and API standards
- **retrospectives-improvement.mdc**: Continuous improvement processes
- **mcp-server-standards.mdc**: MCP server development patterns
- **chrome-debug-integration.mdc**: Debug protocol usage patterns
- **ai-assisted-development.mdc**: AI-enhanced development workflows

## MCP Tool Usage Strategy

### Code Analysis Workflow
```typescript
// When analyzing code issues:
async function analyzeCodeIssue(issue: string) {
  // 1. Read project structure
  const structure = await get_project_structure();
  
  // 2. Search for related code
  const relatedFiles = await search_in_files(issue);
  
  // 3. Read relevant files
  const fileContents = await Promise.all(
    relatedFiles.map(file => read_file(file.path))
  );
  
  // 4. Analyze with cursor rules context
  const analysis = analyzeWithRulesContext(fileContents, issue);
  
  // 5. Use Chrome debug if needed
  if (requiresDebug(issue)) {
    await launchChromeDebug();
    const debugData = await performDebugAnalysis(issue);
    analysis.debugInsights = debugData;
  }
  
  return analysis;
}
```

### Development Assistance Pattern
```typescript
// When providing development assistance:
async function provideDevelopmentAssistance(request: string) {
  // 1. Understand current context
  const projectStructure = await get_project_structure();
  const currentFiles = await list_files(".", "*.{ts,tsx,js,jsx}", true);
  
  // 2. Reference applicable cursor rules
  const applicableRules = await identifyApplicableRules(request);
  
  // 3. Analyze existing patterns
  const codePatterns = await analyzeExistingPatterns(currentFiles);
  
  // 4. Generate contextual response
  const response = generateContextualResponse({
    request,
    projectStructure,
    rules: applicableRules,
    patterns: codePatterns
  });
  
  // 5. Provide implementation if requested
  if (request.includes("implement") || request.includes("create")) {
    const implementation = await generateImplementation(response);
    await write_file(implementation.path, implementation.content);
  }
  
  return response;
}
```

### Debug Session Management
```typescript
// When debugging is required:
async function manageDebugSession(issue: string) {
  try {
    // 1. Start debug session
    await launch_chrome_debug();
    const connection = await connect_to_chrome();
    
    // 2. Set up monitoring
    await start_console_monitoring(connection.tabs[0].id);
    
    // 3. Execute debug workflow
    const debugData = await executeDebugWorkflow(issue);
    
    // 4. Analyze results
    const analysis = await analyzeDebugResults(debugData);
    
    // 5. Generate actionable insights
    return generateDebugReport(analysis);
    
  } finally {
    // Always clean up
    await clear_console_logs();
  }
}
```

## Response Generation Guidelines

### Code Suggestions
When providing code suggestions:
1. **Check cursor rules** for established patterns
2. **Analyze existing code** to match style and architecture
3. **Consider Chrome extension context** (popup, background, content script)
4. **Include proper TypeScript types** following project standards
5. **Add appropriate tests** following testing strategy
6. **Consider performance implications** as outlined in rules

### Problem Solving Approach
1. **Understand the Problem**: Use MCP tools to analyze the current state
2. **Reference Standards**: Check cursor rules for applicable patterns
3. **Analyze Context**: Consider the broader codebase and architecture
4. **Propose Solutions**: Offer multiple approaches with trade-offs
5. **Implement if Requested**: Use MCP tools to make actual changes
6. **Validate Results**: Test and verify implementations

### Communication Style
- **Be Specific**: Reference exact files, line numbers, and functions
- **Explain Reasoning**: Connect suggestions to cursor rules and project patterns
- **Provide Context**: Explain how changes fit into the broader architecture
- **Offer Alternatives**: Present multiple solutions when applicable
- **Document Changes**: Explain what was changed and why

## Continuous Improvement
1. **Learn from Interactions**: Note successful patterns and common issues
2. **Update Rules**: Suggest improvements to cursor rules based on experience
3. **Refine Processes**: Optimize MCP tool usage based on outcomes
4. **Share Knowledge**: Document discoveries and improvements

## Error Handling and Recovery
```typescript
// Robust error handling for MCP operations:
async function robustMCPOperation<T>(operation: () => Promise<T>): Promise<T> {
  try {
    return await operation();
  } catch (error) {
    // Log error with context
    console.error(`MCP operation failed:`, error);
    
    // Attempt recovery based on error type
    if (error.message.includes('file not found')) {
      // Handle missing files
      const alternatives = await findAlternativeFiles();
      return await retryWithAlternatives(operation, alternatives);
    }
    
    if (error.message.includes('permission denied')) {
      // Handle permission issues
      await adjustPermissions();
      return await operation();
    }
    
    // If recovery fails, provide helpful error context
    throw new Error(`Operation failed: ${error.message}. Consider checking file paths and permissions.`);
  }
}
```

## Integration Checklist
Before providing any substantial code assistance:
- [ ] Read relevant cursor rule files
- [ ] Analyze current project structure
- [ ] Check existing code patterns
- [ ] Consider Chrome extension architecture
- [ ] Validate against TypeScript standards
- [ ] Ensure testing strategy compliance
- [ ] Use Chrome debug protocol if needed
- [ ] Document reasoning and trade-offs

## Success Metrics
- **Consistency**: Suggestions align with established patterns
- **Efficiency**: Use MCP tools to minimize manual work
- **Quality**: Generated code passes all checks and standards
- **Learning**: Continuously improve based on outcomes
- **Integration**: Changes fit seamlessly into existing codebase
```

---

## `.cursor/rules/typescript-react-standards.mdc`

```

# TypeScript & React Coding Standards

## TypeScript Configuration
- Use strict mode with all strictness flags enabled
- Prefer `interface` over `type` for object shapes
- Use proper generic constraints and utility types
- Implement discriminated unions for complex state

## React Patterns
```typescript
// Preferred component structure
interface ComponentProps {
  title: string;
  onAction?: (data: ActionData) => void;
}

export function ComponentName({ title, onAction }: ComponentProps) {
  const [state, setState] = useState<StateType>(initialState);
  
  // Event handlers
  const handleEvent = useCallback((data: ActionData) => {
    // Implementation
    onAction?.(data);
  }, [onAction]);
  
  // Effects
  useEffect(() => {
    // Setup and cleanup
    return () => {
      // Cleanup
    };
  }, [dependencies]);
  
  return (
    <div className="component-container">
      {/* JSX content */}
    </div>
  );
}
```

## Chrome API Integration
```typescript
// Proper Chrome API usage with error handling
const sendMessage = async (action: string, data?: unknown) => {
  try {
    const response = await chrome.runtime.sendMessage({ action, data });
    if (chrome.runtime.lastError) {
      throw new Error(chrome.runtime.lastError.message);
    }
    return response;
  } catch (error) {
    console.error('Message sending failed:', error);
    throw error;
  }
};
```

## State Management
- Use `useState` for local component state
- Use `useReducer` for complex state logic
- Implement custom hooks for shared logic
- Use React Query or SWR for async data fetching

## Code Organization
- One component per file
- Export components as named exports
- Use barrel exports (index.ts) for directories
- Group related functionality in custom hooks

## Performance
- Use `useCallback` and `useMemo` appropriately
- Implement proper dependency arrays
- Avoid inline object/function creation in render
- Use React.memo for expensive components

## CSS Integration
- Use CSS modules or styled-components
- Follow BEM naming convention for class names
- Implement responsive design patterns
- Use CSS custom properties for theming

```

---

## `.cursor/rules/testing-strategy.mdc`

```

# Testing Standards for Plasmo Extension

## Testing Framework Setup
- Use Jest as the primary testing framework
- Implement React Testing Library for component testing
- Use MSW (Mock Service Worker) for API mocking
- Configure Chrome API mocks for extension testing

## Test Structure and Organization
```typescript
// Component test structure
describe('PopupComponent', () => {
  const mockOnAction = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('should render with correct props', () => {
    render(<PopupComponent title="Test" onAction={mockOnAction} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
  
  it('should handle user interactions', async () => {
    const user = userEvent.setup();
    render(<PopupComponent title="Test" onAction={mockOnAction} />);
    
    await user.click(screen.getByRole('button', { name: /action/i }));
    expect(mockOnAction).toHaveBeenCalledWith(expectedData);
  });
});
```

## Chrome Extension Testing
```typescript
// Mock Chrome APIs
const mockChrome = {
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
      removeListener: jest.fn(),
    },
  },
  storage: {
    sync: {
      get: jest.fn(),
      set: jest.fn(),
    },
  },
};

Object.assign(global, { chrome: mockChrome });
```

## Test Categories
1. **Unit Tests**: Individual functions and hooks
2. **Component Tests**: React component behavior
3. **Integration Tests**: Message passing between extension parts
4. **E2E Tests**: Full user workflows using Playwright

## Testing Patterns
- Test user behavior, not implementation details
- Use descriptive test names that explain scenarios
- Follow Given-When-Then structure
- Mock external dependencies appropriately

## Coverage Requirements
- Maintain minimum 80% code coverage
- Focus on critical path testing
- Test error conditions and edge cases
- Include accessibility testing with jest-axe

## Test Data Management
```typescript
// Test fixtures and factories
export const createMockExtensionData = (overrides = {}) => ({
  title: 'Test Extension',
  settings: {
    notifications: true,
    theme: 'light',
  },
  ...overrides,
});
```

## Continuous Testing
- Run tests on every commit (pre-commit hooks)
- Include tests in CI/CD pipeline
- Generate coverage reports
- Test against multiple Chrome versions

## Background Script Testing
```typescript
// Test background script functionality
describe('Background Script', () => {
  it('should handle installation events', () => {
    const installationHandler = chrome.runtime.onInstalled.addListener.mock.calls[0][0];
    
    installationHandler({ reason: 'install' });
    
    expect(chrome.storage.sync.set).toHaveBeenCalledWith({
      settings: expect.objectContaining({
        notifications: true,
      }),
    });
  });
});
```

## Content Script Testing
- Test DOM manipulation functions
- Mock browser APIs appropriately
- Test message handling between contexts
- Verify injection and cleanup behavior

```

---

## `.cursor/rules/planning-methodology.mdc`

```

# Project Planning & Development Methodology

## User Story Standards
Follow INVEST criteria for all user stories:
- **Independent**: Stories can be developed separately
- **Negotiable**: Details can be discussed and refined
- **Valuable**: Provides clear user value
- **Estimable**: Can be sized appropriately
- **Small**: Completed within one sprint
- **Testable**: Clear acceptance criteria

## Story Format
```markdown
## [Story ID] - [Brief Title]

**As a** [persona]  
**I want** [goal]  
**So that** [benefit]

### Acceptance Criteria
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

### Technical Notes
- API endpoints required
- Database changes needed
- Security considerations
- Performance requirements

### Definition of Done
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Accessibility verified
- [ ] Security review completed
```

## Sprint Planning Process
1. **Sprint Goal Definition**: Clear, measurable objective
2. **Capacity Planning**: Account for team availability
3. **Story Prioritization**: Value-driven backlog ordering
4. **Task Breakdown**: Stories decomposed to 4-8 hour tasks
5. **Risk Assessment**: Identify and mitigate blockers

## Chrome Extension Specific Planning
- Consider Chrome Web Store review cycles (7-14 days)
- Plan for Manifest V3 compliance updates
- Account for cross-browser compatibility testing
- Include security review for permissions

## Development Workflow
```
1. Feature Branch Creation
   ├── git checkout -b feature/STORY-ID-brief-description
   
2. Development Process
   ├── Implement feature following TDD
   ├── Write/update documentation
   ├── Add/update tests
   └── Manual testing in Chrome

3. Code Review
   ├── Create pull request with story context
   ├── Include screenshots/demo for UI changes
   ├── Verify all checks pass
   └── Address review feedback

4. Quality Assurance
   ├── Test in multiple Chrome versions
   ├── Verify extension permissions
   ├── Test installation/update flow
   └── Cross-platform validation

5. Release Planning
   ├── Version bump according to semver
   ├── Update changelog
   ├── Package for Chrome Web Store
   └── Plan rollback strategy
```

## Technical Debt Management
- Maintain technical debt backlog
- Allocate 20% of sprint capacity to debt reduction
- Regular architecture reviews
- Dependency update cycles

## Risk Management
- **High**: Chrome API deprecations, store policy changes
- **Medium**: Third-party dependency issues, performance degradation
- **Low**: Minor UI/UX improvements, non-critical features

## Stakeholder Communication
- Weekly progress updates with screenshots
- Monthly demo sessions
- Quarterly architecture reviews
- Regular user feedback collection

## Metrics and KPIs
- Sprint velocity and burndown
- Code coverage trends
- User adoption rates
- Store review ratings
- Performance metrics (load times, memory usage)

```

---

## `.cursor/rules/specification-standards.mdc`

```

# API Documentation & Technical Specifications

## API Documentation Structure
Follow OpenAPI/Swagger standards for all APIs including MCP server endpoints:

```yaml
# MCP Server API Specification
openapi: 3.0.3
info:
  title: Plasmo Extension MCP Server
  description: Model Context Protocol server for development tools
  version: 1.0.0
  contact:
    name: Development Team
    email: dev@example.com

servers:
  - url: http://localhost:8000
    description: Local development server

paths:
  /tools:
    get:
      summary: List available MCP tools
      description: Returns all available development tools
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Tool'
```

## Chrome Extension API Documentation
Document all Chrome API integrations:

```typescript
/**
 * Background Script Message Handler
 * 
 * @description Handles messages from popup and content scripts
 * @param request - Message request object
 * @param sender - Message sender information
 * @param sendResponse - Response callback function
 * 
 * @example
 * // From popup to background
 * chrome.runtime.sendMessage({
 *   action: 'getTabInfo'
 * }, (response) => {
 *   console.log('Current tab:', response.title);
 * });
 */
interface MessageRequest {
  action: 'getTabInfo' | 'showNotification' | string;
  data?: unknown;
}

interface MessageResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}
```

## Technical Specification Templates

### Feature Specification
```markdown
# Feature: [Feature Name]

## Overview
Brief description of the feature and its purpose.

## Requirements
- Functional requirements
- Non-functional requirements (performance, security, etc.)
- Browser compatibility requirements

## Architecture
- Component diagrams
- Data flow diagrams
- Integration points

## API Design
- Endpoint specifications
- Message passing protocols
- Data schemas

## Security Considerations
- Permission requirements
- Data handling policies
- User privacy protections

## Testing Strategy
- Unit test requirements
- Integration test scenarios
- Manual testing procedures

## Performance Requirements
- Load time targets
- Memory usage limits
- Network efficiency goals

## Rollout Plan
- Development phases
- Testing milestones
- Release criteria
```

## Code Documentation Standards
Use JSDoc for all public APIs:

```typescript
/**
 * Highlights text on the current page
 * 
 * @param text - The text to highlight
 * @param color - Highlight color (default: yellow)
 * @returns Promise resolving to highlight count
 * 
 * @example
 * ```typescript
 * const count = await highlightText('search term', '#ffff00');
 * console.log(`Highlighted ${count} instances`);
 * ```
 * 
 * @throws {Error} When DOM access is restricted
 * @since 1.0.0
 */
async function highlightText(text: string, color: string = '#ffff00'): Promise<number> {
  // Implementation
}
```

## README Structure
```markdown
# Project Name

Brief description and key features.

## Installation
Step-by-step setup instructions.

## Usage
Common use cases with examples.

## API Reference
Link to detailed API documentation.

## Development
- Setup instructions
- Build process
- Testing guidelines
- Contributing guidelines

## Architecture
High-level system overview.

## Security
Security considerations and best practices.

## Changelog
Link to detailed changelog.

## License
License information.
```

## Living Documentation Principles
- Keep documentation close to code
- Update docs with every feature change
- Include interactive examples where possible
- Maintain versioned documentation
- Use automated documentation generation

## Quality Checklist
- [ ] Clear, jargon-free language
- [ ] Comprehensive examples
- [ ] Up-to-date screenshots
- [ ] Working code samples
- [ ] Error scenarios documented
- [ ] Performance characteristics noted
- [ ] Security implications covered
- [ ] Browser compatibility noted

## Documentation Review Process
1. Technical accuracy review
2. Clarity and completeness check
3. Example validation
4. Link verification
5. Accessibility compliance
6. Multi-audience validation (developers, stakeholders, end-users)

```

---

## `.cursor/rules/retrospectives-improvement.mdc`

```

# Retrospectives & Continuous Improvement

## Sprint Retrospective Format
Conduct retrospectives using the "Start, Stop, Continue" framework with additional elements:

```markdown
# Sprint [Number] Retrospective
**Date**: [Date]  
**Participants**: [Team Members]  
**Sprint Goal**: [Original Goal]  
**Goal Achievement**: [Met/Partially Met/Not Met]

## Metrics Review
- **Velocity**: [Points completed vs planned]
- **Quality**: [Bugs found, test coverage, code review feedback]
- **Chrome Extension**: [Store ratings, user feedback, performance metrics]
- **Technical Debt**: [Items addressed vs added]

## What Went Well (Continue)
- [Specific positive outcomes]
- [Effective practices to maintain]
- [Successful collaborations]

## What Didn't Go Well (Stop)
- [Issues that hindered progress]
- [Ineffective practices to eliminate]
- [Communication breakdowns]

## What We Should Try (Start)
- [New practices to experiment with]
- [Tools or processes to adopt]
- [Skills to develop]

## Action Items
- [ ] [Specific action] - Owner: [Name] - Due: [Date]
- [ ] [Process improvement] - Owner: [Name] - Due: [Date]
- [ ] [Technical change] - Owner: [Name] - Due: [Date]

## Chrome Extension Specific Insights
- Store review feedback analysis
- User support ticket patterns
- Performance monitoring results
- Security audit findings

## Team Health Assessment
Rate 1-5 (5 = excellent):
- **Collaboration**: [Score] - [Notes]
- **Learning**: [Score] - [Notes]
- **Fun**: [Score] - [Notes]
- **Delivering Value**: [Score] - [Notes]
```

## Retrospective Facilitation Guidelines
1. **Psychological Safety**: Focus on systems, not individuals
2. **Data-Driven**: Use metrics to support observations
3. **Actionable Outcomes**: Every insight should lead to specific actions
4. **Time-boxed**: 90 minutes maximum for 2-week sprints
5. **Rotating Facilitation**: Different team member each sprint

## Post-Mortem Process
For significant issues or outages:

```markdown
# Post-Mortem: [Incident Title]
**Date**: [Incident Date]  
**Duration**: [How long issue persisted]  
**Impact**: [Users affected, functionality lost]  
**Severity**: [Critical/High/Medium/Low]

## Timeline
- **[Time]**: [Event description]
- **[Time]**: [Event description]
- **[Time]**: [Resolution achieved]

## Root Cause Analysis
- **Immediate Cause**: [What directly caused the issue]
- **Contributing Factors**: [What made this possible]
- **Root Cause**: [Underlying system/process issue]

## What Went Well
- [Effective response actions]
- [Good monitoring/alerting]
- [Successful communication]

## What Could Be Improved
- [Response time issues]
- [Missing monitoring]
- [Communication gaps]

## Action Items
- [ ] [Immediate fix] - Owner: [Name] - Due: [Date]
- [ ] [Process improvement] - Owner: [Name] - Due: [Date]
- [ ] [Monitoring enhancement] - Owner: [Name] - Due: [Date]
- [ ] [Documentation update] - Owner: [Name] - Due: [Date]

## Prevention Measures
- [System changes to prevent recurrence]
- [Process improvements]
- [Training or knowledge sharing needed]
```

## Continuous Improvement Framework

### Monthly Technical Health Review
- Code quality metrics analysis
- Performance monitoring review
- Security audit results
- Dependency update status
- Technical debt assessment

### Quarterly Architecture Review
- Design pattern effectiveness
- Technology stack evaluation
- Scalability assessment
- Integration point analysis
- Future technology planning

### Learning and Development Tracking
```markdown
## Team Learning Goals - Q[Quarter] [Year]

### Individual Development Plans
- **[Team Member]**: [Skills to develop] - [Learning resources] - [Timeline]
- **[Team Member]**: [Skills to develop] - [Learning resources] - [Timeline]

### Team-wide Learning Initiatives
- [ ] [Technology workshop] - [Date] - [Facilitator]
- [ ] [Best practices sharing] - [Date] - [Topic]
- [ ] [External conference/training] - [Event] - [Attendees]

### Knowledge Sharing Sessions
- **Brown Bag Lunches**: [Schedule and topics]
- **Code Reviews**: [Focus areas for learning]
- **Pair Programming**: [Rotation schedule]
```

## Metrics for Continuous Improvement

### Development Metrics
- Sprint velocity trends
- Code review feedback patterns
- Bug discovery timing (dev vs production)
- Test coverage evolution
- Build/deployment success rates

### Extension-Specific Metrics
- Chrome Web Store ratings and reviews
- User adoption and retention rates
- Extension performance (load times, memory usage)
- Permission usage analytics
- Update success rates

### Team Health Metrics
- Retrospective action item completion rate
- Team satisfaction surveys
- Knowledge sharing frequency
- Cross-training effectiveness
- Innovation time usage

## Improvement Experiment Framework
```markdown
## Improvement Experiment: [Title]
**Hypothesis**: [What we believe will improve]  
**Success Criteria**: [How we'll measure success]  
**Duration**: [Experiment timeline]  
**Participants**: [Who's involved]

### Implementation Plan
- [Step 1 with timeline]
- [Step 2 with timeline]
- [Step 3 with timeline]

### Measurements
- **Baseline**: [Current state metrics]
- **Target**: [Desired improvement]
- **Measurement Method**: [How we'll track progress]

### Results
- [Actual outcomes vs targets]
- [Unexpected effects]
- [Lessons learned]

### Decision
- [ ] Adopt permanently
- [ ] Modify and continue
- [ ] Discontinue
```

## Communication and Follow-up
- Share retrospective summaries with stakeholders
- Update team charter and working agreements
- Track action item completion in next retrospectives
- Celebrate improvements and learning achievements
- Document successful practices for future teams

```

---

## Large Files (Full Content)

Due to the size of the remaining cursor rules files, here are the key sections and complete content references:

### `.cursor/rules/chrome-debug-integration.mdc` (23KB, 814 lines)
**Full content includes:**
- Automated debugging workflows with Chrome Debug Protocol
- Intelligent breakpoint management patterns
- Console monitoring and analysis
- Extension-specific debug patterns
- Performance debugging automation
- Critical WebSocket message filtering patterns
- DevTools interference prevention
- Service coordination patterns
- Error recovery and resilience patterns

### `.cursor/rules/ai-assisted-development.mdc` (12KB, 369 lines)
**Full content includes:**
- MCP Server Knowledge Injection requirements
- Enhanced MCP tool usage patterns
- Chrome debugging workflow v2.0
- Error-aware development assistance
- Context-aware problem solving
- Solution implementation with MCP integration
- Knowledge transfer and learning patterns
- Continuous improvement integration

### `.cursor/rules/mcp-server-standards.mdc` (12KB, 330 lines)
**Full content includes:**
- Server consolidation and architecture (v2.0)
- Development workflow constraints
- Enhanced error handling standards
- Security best practices v2.0
- Chrome Debug Protocol integration patterns
- Tool categories and organization
- Performance and monitoring standards
- Migration guide from legacy servers
- Knowledge injection requirements

All complete files are available in the repository at their respective paths in `.cursor/rules/` directory. 