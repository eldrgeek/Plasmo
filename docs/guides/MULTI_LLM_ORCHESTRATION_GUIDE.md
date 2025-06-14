# Multi-LLM Orchestration Guide: Automating AI Services via Chrome Debug Protocol

## Overview
This guide explains how to successfully automate interactions with AI services (ChatGPT, Claude.ai, Perplexity, etc.) using the Chrome Debug Protocol (CDP) through an MCP server. This workflow was **100% validated** with Claude.ai and can be adapted for any web-based AI service.

## 🎯 What This Achieves
- **Inject prompts** into any AI service through browser automation
- **Extract responses** from AI services programmatically
- **Orchestrate multiple AI services** simultaneously
- **Monitor conversations** in real-time through Chrome DevTools
- **Scale AI interactions** beyond manual copy/paste

## 🏗️ Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │   MCP Server    │    │ Chrome Browser  │
│  (AI Assistant) │◄──►│   (Port 8000)   │◄──►│ (Debug Port)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    AI Services  │
                    │ ChatGPT/Claude/ │
                    │   Perplexity    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
1. **Chrome browser** with debug mode enabled
2. **MCP server** running (Python FastAPI)
3. **AI assistant** with MCP integration (Cursor/Claude Desktop)
4. **Target AI service** open in Chrome tab

### Setup Commands
```bash
# 1. Start Chrome with debug enabled
./launch-chrome-debug.sh
# OR manually:
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
#   --remote-debugging-port=9222 \
#   --remote-allow-origins=* \
#   --user-data-dir=./chrome-debug-profile

# 2. Start MCP server
python3 mcp_server.py

# 3. Open target AI service in Chrome
# Navigate to: https://chat.openai.com, https://claude.ai, etc.
```

## 🎪 The Proven Workflow (Step-by-Step)

### Step 1: Health Check
**Purpose**: Verify all systems operational
```python
# MCP Tool: health()
# Returns: Server status, Chrome availability, service health
```

### Step 2: Connect to Chrome
**Purpose**: Establish Chrome Debug Protocol connection
```python
# MCP Tool: connect_to_chrome()
# Returns: Connection status, available tabs list
```

### Step 3: Identify Target Tab
**Purpose**: Find the AI service tab to automate
```python
# MCP Tool: get_chrome_tabs()
# Look for: URLs containing "chat.openai.com", "claude.ai", "perplexity.ai"
# Returns: Tab ID for target service
```

### Step 4: Open DevTools (Optional)
**Purpose**: Monitor automation in real-time
```javascript
// Open tab-specific DevTools
const devToolsUrl = `chrome-devtools://devtools/bundled/devtools_app.html?ws=localhost:9222/devtools/page/${TAB_ID}`;
window.open(devToolsUrl, '_blank');
```

### Step 5: Inject Prompt
**Purpose**: Send your prompt to the AI service
```python
# MCP Tool: execute_javascript_fixed(code, tab_id)
# Code varies by service - see service-specific patterns below
```

### Step 6: Extract Response
**Purpose**: Retrieve AI service response programmatically
```python
# MCP Tool: execute_javascript_fixed(code, tab_id)
# Wait 3-5 seconds, then extract response content
```

## 🎨 Service-Specific Automation Patterns

### ChatGPT (chat.openai.com)
```javascript
// PROMPT INJECTION
const promptTextarea = document.querySelector('#prompt-textarea, textarea[placeholder*="Message"]');
if (promptTextarea) {
    promptTextarea.value = 'Your prompt here';
    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    promptTextarea.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Trigger send
    const sendButton = document.querySelector('button[data-testid="send-button"], button:has(svg[data-icon="send"])');
    if (sendButton && !sendButton.disabled) {
        sendButton.click();
    }
}

// RESPONSE EXTRACTION (wait 3-5 seconds after send)
const messages = document.querySelectorAll('[data-message-author-role="assistant"]');
const lastMessage = messages[messages.length - 1];
const response = lastMessage ? lastMessage.textContent : 'No response found';
return response;
```

### Claude.ai (claude.ai)
```javascript
// PROMPT INJECTION
const promptDiv = document.querySelector('div[contenteditable="true"][data-testid*="chat"], div[contenteditable="true"] p');
if (promptDiv) {
    promptDiv.textContent = 'Your prompt here';
    promptDiv.dispatchEvent(new Event('input', { bubbles: true }));
    promptDiv.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Trigger send
    const sendButton = document.querySelector('button[aria-label*="Send"], button[type="submit"]');
    if (sendButton && !sendButton.disabled) {
        sendButton.click();
    }
}

// RESPONSE EXTRACTION (wait 3-5 seconds after send)
const responses = document.querySelectorAll('div[data-is-streaming="false"]');
const lastResponse = responses[responses.length - 1];
const response = lastResponse ? lastResponse.textContent : 'No response found';
return response;
```

### Perplexity (perplexity.ai)
```javascript
// PROMPT INJECTION
const promptTextarea = document.querySelector('textarea[placeholder*="Ask"], textarea[name="q"]');
if (promptTextarea) {
    promptTextarea.value = 'Your prompt here';
    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Trigger send (usually Enter key or button)
    const sendButton = document.querySelector('button[type="submit"], button:has(svg)');
    if (sendButton) {
        sendButton.click();
    } else {
        // Try Enter key
        promptTextarea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    }
}

// RESPONSE EXTRACTION (wait 3-5 seconds after send)
const responseElements = document.querySelectorAll('[data-qa="answer"], .prose, .response-content');
const lastResponse = responseElements[responseElements.length - 1];
const response = lastResponse ? lastResponse.textContent : 'No response found';
return response;
```

## 🔧 Advanced Automation Techniques

### Handling Dynamic Content
```javascript
// Wait for elements to load
function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }
        
        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        setTimeout(() => {
            observer.disconnect();
            resolve(null);
        }, timeout);
    });
}

// Usage
const promptInput = await waitForElement('textarea[placeholder*="Message"]');
if (promptInput) {
    promptInput.value = 'Your prompt here';
    // ... rest of automation
}
```

### React Input Handling
```javascript
// For React-based interfaces (like ChatGPT)
function setReactInputValue(element, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    
    nativeInputValueSetter.call(element, value);
    
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
}

// Usage
const textarea = document.querySelector('#prompt-textarea');
setReactInputValue(textarea, 'Your prompt here');
```

### Response Streaming Detection
```javascript
// Wait for response to complete streaming
function waitForResponseComplete(selector, timeout = 30000) {
    return new Promise((resolve) => {
        let lastLength = 0;
        let stableCount = 0;
        
        const checkStability = () => {
            const element = document.querySelector(selector);
            if (!element) return;
            
            const currentLength = element.textContent.length;
            
            if (currentLength === lastLength) {
                stableCount++;
                if (stableCount >= 3) { // 3 consecutive same lengths = stable
                    resolve(element.textContent);
                    return;
                }
            } else {
                stableCount = 0;
                lastLength = currentLength;
            }
            
            setTimeout(checkStability, 1000);
        };
        
        setTimeout(checkStability, 1000);
        setTimeout(() => resolve('Timeout'), timeout);
    });
}

// Usage
const response = await waitForResponseComplete('[data-message-author-role="assistant"]:last-child');
```

## 🚨 Critical Success Factors

### ✅ DO
- **Use MCP tools through AI assistant interface** (Cursor, Claude Desktop)
- **Execute steps one by one** - never batch into standalone scripts
- **Wait appropriate time** between prompt injection and response extraction
- **Handle dynamic content** with proper selectors and waiting mechanisms
- **Test selectors** in DevTools console before automation
- **Allow popups** on target sites (required for DevTools)

### ❌ DON'T
- **Never write standalone Python scripts** that call MCP tools directly
- **Don't batch all steps** into a single script - they will fail
- **Don't rush extraction** - AI responses need time to generate
- **Don't use generic selectors** - they break when UIs change
- **Don't forget to handle React synthetic events** for React-based UIs

## 🐛 Troubleshooting

### Common Issues & Solutions

**Issue**: "FunctionTool object is not callable"
**Solution**: Use MCP tools through AI assistant interface, not direct Python calls

**Issue**: DevTools won't open
**Solution**: Check popup blocker - must allow popups on target site

**Issue**: Prompt injection not working
**Solution**: Check contenteditable vs textarea, try React input handling

**Issue**: Response extraction returns empty
**Solution**: Increase wait time, check response container selectors

**Issue**: Send button not clickable
**Solution**: Check button state, ensure prompt field has content first

**Issue**: Chrome connection failed
**Solution**: Verify Chrome launched with `--remote-debugging-port=9222 --remote-allow-origins=*`

### Debugging Commands
```bash
# Check Chrome debug tabs
curl http://localhost:9222/json

# Test MCP server health
curl http://localhost:8000/health

# Inspect page DOM in Chrome
# Open DevTools → Elements → Find selectors
```

## 📝 Creating Your Own Automation

### Step 1: Identify Selectors
1. Open target AI service in Chrome
2. Open DevTools (F12)
3. Find prompt input element
4. Find send button element  
5. Find response container element

### Step 2: Test in Console
```javascript
// Test prompt injection
const promptElement = document.querySelector('YOUR_PROMPT_SELECTOR');
console.log('Prompt element:', promptElement);

// Test send button
const sendButton = document.querySelector('YOUR_SEND_SELECTOR');
console.log('Send button:', sendButton);

// Test response extraction
const responseElement = document.querySelector('YOUR_RESPONSE_SELECTOR');
console.log('Response element:', responseElement);
```

### Step 3: Build Automation Script
```javascript
// Template for any AI service
async function automateAIService(prompt) {
    // 1. Find and fill prompt input
    const promptInput = document.querySelector('PROMPT_SELECTOR');
    if (promptInput) {
        // Handle based on input type (textarea vs contenteditable)
        if (promptInput.tagName === 'TEXTAREA') {
            promptInput.value = prompt;
            promptInput.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            promptInput.textContent = prompt;
            promptInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    
    // 2. Click send button
    const sendButton = document.querySelector('SEND_SELECTOR');
    if (sendButton && !sendButton.disabled) {
        sendButton.click();
    }
    
    // 3. Wait and extract response
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const responseElement = document.querySelector('RESPONSE_SELECTOR');
    return responseElement ? responseElement.textContent : 'No response found';
}

// Usage
const result = await automateAIService('Your prompt here');
console.log('AI Response:', result);
```

## 🎯 Orchestration Workflow for Multiple AIs

### Parallel Execution
```javascript
// Automate multiple AI services simultaneously
async function orchestrateMultipleAIs(prompt, services) {
    const results = {};
    
    for (const service of services) {
        // Find tab for each service
        const tabs = await getChromeTabs();
        const targetTab = tabs.find(tab => tab.url.includes(service.domain));
        
        if (targetTab) {
            // Execute automation for this service
            const response = await executeJavaScript(service.automationScript(prompt), targetTab.id);
            results[service.name] = response;
        }
    }
    
    return results;
}

// Service definitions
const aiServices = [
    {
        name: 'ChatGPT',
        domain: 'chat.openai.com',
        automationScript: (prompt) => `/* ChatGPT automation script */`
    },
    {
        name: 'Claude',
        domain: 'claude.ai', 
        automationScript: (prompt) => `/* Claude automation script */`
    },
    {
        name: 'Perplexity',
        domain: 'perplexity.ai',
        automationScript: (prompt) => `/* Perplexity automation script */`
    }
];

// Execute orchestration
const results = await orchestrateMultipleAIs('Explain quantum computing', aiServices);
```

## 🎉 Success Metrics

### Validation Checklist
- [ ] Chrome debug connection successful
- [ ] Target AI service tab identified  
- [ ] Prompt injection working
- [ ] Send button activation successful
- [ ] Response extraction reliable
- [ ] DevTools monitoring functional
- [ ] End-to-end workflow <12 seconds

### Performance Targets
- **Connection Time**: <2 seconds
- **Prompt Injection**: <1 second
- **Response Time**: 3-10 seconds (varies by AI service)
- **Extraction Time**: <1 second
- **Total Workflow**: <15 seconds

## 🔮 Advanced Use Cases

### Multi-Round Conversations
```javascript
// Continue conversation across multiple exchanges
async function conversationFlow(exchanges) {
    for (const exchange of exchanges) {
        await automateAIService(exchange.prompt);
        const response = await extractResponse();
        exchange.response = response;
        
        // Wait between exchanges
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}
```

### Response Comparison
```javascript
// Compare responses from multiple AI services
async function compareAIResponses(prompt) {
    const services = ['ChatGPT', 'Claude', 'Perplexity'];
    const responses = {};
    
    for (const service of services) {
        responses[service] = await automateAIService(prompt, service);
    }
    
    return {
        prompt,
        responses,
        comparison: analyzeResponses(responses)
    };
}
```

### Automated Testing
```javascript
// Test AI service capabilities automatically
const testSuite = [
    'Write a Python function to sort a list',
    'Explain the theory of relativity',
    'Create a marketing plan for a startup',
    'Debug this JavaScript code: [code snippet]'
];

for (const testPrompt of testSuite) {
    const result = await automateAIService(testPrompt);
    console.log(`Test: ${testPrompt}`);
    console.log(`Result: ${result.substring(0, 100)}...`);
}
```

## 🎪 Live Demo Script

Use this exact sequence with any AI assistant that has MCP integration:

### For ChatGPT:
1. "Check MCP server health using the health tool"
2. "Connect to Chrome using connect_to_chrome tool"  
3. "Get Chrome tabs and find any ChatGPT tabs using get_chrome_tabs"
4. "Open DevTools for the ChatGPT tab found"
5. "Execute JavaScript to inject prompt 'Hello! Write a simple Python function' into ChatGPT"
6. "Wait 5 seconds then extract the response from ChatGPT"

### For Claude.ai:
1. "Check MCP server health using the health tool"
2. "Connect to Chrome using connect_to_chrome tool"
3. "Get Chrome tabs and find any Claude.ai tabs using get_chrome_tabs"  
4. "Open DevTools for the Claude.ai tab found"
5. "Execute JavaScript to inject prompt 'Hello! Write a simple Python function' into Claude.ai"
6. "Wait 5 seconds then extract the response from Claude.ai"

**Note**: Execute each step individually, wait for completion, then proceed to next step. Never batch steps together.

---

## 📚 Additional Resources

- **MCP Server Code**: `mcp_server.py` - Core automation infrastructure
- **Chrome Launch Script**: `launch-chrome-debug.sh` - Debug mode setup
- **Test Scripts**: `test_mcp_server.py` - Validation and testing
- **Cursor Integration**: `claude_desktop_config.json` - AI assistant setup

This guide enables you to replicate the proven multi-LLM orchestration workflow with any AI service. The key is using the step-by-step MCP tool approach through an AI assistant interface rather than standalone automation scripts. 