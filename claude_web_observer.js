/**
 * Claude Web DOM Observer
 * Monitors Claude.ai interface for prompt submission and response patterns
 */

class ClaudeWebObserver {
    constructor() {
        this.observers = [];
        this.interactions = [];
        this.currentInteraction = null;
        this.responseSelector = null;
        this.inputSelector = null;
        this.submitSelector = null;
        this.startTime = Date.now();
        
        console.log('🔍 Claude Web Observer initialized');
        this.init();
    }
    
    init() {
        // Find key elements
        this.discoverElements();
        
        // Set up observers
        this.setupMutationObserver();
        this.setupClickObserver();
        this.setupInputObserver();
        
        // Report status
        this.reportStatus();
    }
    
    discoverElements() {
        // Try common Claude.ai selectors
        const inputCandidates = [
            'div[contenteditable="true"]',
            'textarea[placeholder*="message"]',
            'textarea[placeholder*="Message"]', 
            'div[role="textbox"]',
            '[data-testid="chat-input"]',
            '.ProseMirror'
        ];
        
        const submitCandidates = [
            'button[aria-label*="Send"]',
            'button[type="submit"]',
            'button:has(svg)',
            '[data-testid="send-button"]',
            'button[aria-label*="submit"]'
        ];
        
        // Find input element
        for (const selector of inputCandidates) {
            const element = document.querySelector(selector);
            if (element) {
                this.inputSelector = selector;
                console.log(`✅ Found input: ${selector}`);
                break;
            }
        }
        
        // Find submit button
        for (const selector of submitCandidates) {
            const element = document.querySelector(selector);
            if (element) {
                this.submitSelector = selector;
                console.log(`✅ Found submit: ${selector}`);
                break;
            }
        }
        
        // Find response area (usually where messages appear)
        const responseCandidates = [
            '[data-testid="conversation"]',
            '.conversation',
            '[role="main"]',
            '.messages',
            '.chat-messages'
        ];
        
        for (const selector of responseCandidates) {
            const element = document.querySelector(selector);
            if (element) {
                this.responseSelector = selector;
                console.log(`✅ Found response area: ${selector}`);
                break;
            }
        }
    }
    
    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                this.handleMutation(mutation);
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true,
            attributeFilter: ['disabled', 'aria-disabled', 'class']
        });
        
        this.observers.push(observer);
        console.log('👁️ Mutation observer active');
    }
    
    setupClickObserver() {
        document.addEventListener('click', (e) => {
            if (this.submitSelector && e.target.matches(this.submitSelector)) {
                this.onSubmitClick(e);
            }
        }, true);
        
        console.log('👆 Click observer active');
    }
    
    setupInputObserver() {
        if (this.inputSelector) {
            document.addEventListener('input', (e) => {
                if (e.target.matches(this.inputSelector)) {
                    this.onInputChange(e);
                }
            }, true);
        }
        
        console.log('⌨️ Input observer active');
    }
    
    handleMutation(mutation) {
        const timestamp = Date.now();
        
        // Track button state changes
        if (mutation.type === 'attributes' && 
            (mutation.attributeName === 'disabled' || mutation.attributeName === 'aria-disabled')) {
            this.trackButtonState(mutation.target, timestamp);
        }
        
        // Track new content appearing
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            this.trackContentChanges(mutation, timestamp);
        }
        
        // Track text changes (streaming)
        if (mutation.type === 'characterData') {
            this.trackTextChanges(mutation, timestamp);
        }
    }
    
    trackButtonState(element, timestamp) {
        const isSubmitButton = this.submitSelector && element.matches(this.submitSelector);
        if (!isSubmitButton) return;
        
        const isDisabled = element.disabled || element.getAttribute('aria-disabled') === 'true';
        
        this.logEvent('button_state', {
            disabled: isDisabled,
            timestamp,
            element: this.getElementInfo(element)
        });
        
        if (this.currentInteraction) {
            if (isDisabled && !this.currentInteraction.submitTime) {
                this.currentInteraction.submitTime = timestamp;
                console.log('📤 Submit detected - button disabled');
            } else if (!isDisabled && this.currentInteraction.submitTime && !this.currentInteraction.completeTime) {
                this.currentInteraction.completeTime = timestamp;
                console.log('✅ Response complete - button enabled');
                this.finalizeInteraction();
            }
        }
    }
    
    trackContentChanges(mutation, timestamp) {
        const addedContent = Array.from(mutation.addedNodes)
            .filter(node => node.nodeType === Node.ELEMENT_NODE)
            .map(node => ({
                tagName: node.tagName,
                className: node.className,
                textContent: node.textContent?.substring(0, 100),
                selector: this.getElementSelector(node)
            }));
        
        if (addedContent.length > 0) {
            this.logEvent('content_added', {
                timestamp,
                addedContent,
                target: this.getElementInfo(mutation.target)
            });
        }
    }
    
    trackTextChanges(mutation, timestamp) {
        if (mutation.target.textContent) {
            this.logEvent('text_change', {
                timestamp,
                text: mutation.target.textContent.substring(0, 200),
                target: this.getElementInfo(mutation.target.parentElement)
            });
        }
    }
    
    onSubmitClick(event) {
        const timestamp = Date.now();
        
        // Start new interaction
        this.currentInteraction = {
            id: `interaction_${timestamp}`,
            startTime: timestamp,
            submitTime: null,
            completeTime: null,
            prompt: this.getCurrentPrompt(),
            events: []
        };
        
        console.log('🎯 New interaction started:', this.currentInteraction.id);
        this.logEvent('submit_click', { timestamp });
    }
    
    onInputChange(event) {
        this.logEvent('input_change', {
            timestamp: Date.now(),
            value: event.target.value || event.target.textContent
        });
    }
    
    getCurrentPrompt() {
        if (!this.inputSelector) return null;
        
        const inputElement = document.querySelector(this.inputSelector);
        return inputElement ? (inputElement.value || inputElement.textContent || '') : null;
    }
    
    finalizeInteraction() {
        if (!this.currentInteraction) return;
        
        this.currentInteraction.response = this.extractLatestResponse();
        this.currentInteraction.duration = this.currentInteraction.completeTime - this.currentInteraction.startTime;
        
        this.interactions.push(this.currentInteraction);
        console.log('📋 Interaction finalized:', {
            id: this.currentInteraction.id,
            duration: this.currentInteraction.duration,
            prompt: this.currentInteraction.prompt?.substring(0, 50),
            responseLength: this.currentInteraction.response?.length || 0
        });
        
        this.currentInteraction = null;
    }
    
    extractLatestResponse() {
        // Try to find the latest response message
        const messageCandidates = [
            '[data-testid="message"]',
            '.message',
            '[role="article"]',
            '.conversation > div:last-child',
            '.chat-message:last-child'
        ];
        
        for (const selector of messageCandidates) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                return lastElement.textContent || lastElement.innerText;
            }
        }
        
        return null;
    }
    
    logEvent(type, data) {
        const event = {
            type,
            timestamp: Date.now(),
            ...data
        };
        
        if (this.currentInteraction) {
            this.currentInteraction.events.push(event);
        }
        
        console.log(`📊 ${type}:`, data);
    }
    
    getElementInfo(element) {
        if (!element) return null;
        
        return {
            tagName: element.tagName,
            className: element.className,
            id: element.id,
            selector: this.getElementSelector(element)
        };
    }
    
    getElementSelector(element) {
        if (!element) return null;
        
        if (element.id) return `#${element.id}`;
        if (element.className) return `.${element.className.split(' ')[0]}`;
        return element.tagName.toLowerCase();
    }
    
    reportStatus() {
        const status = {
            initialized: true,
            inputSelector: this.inputSelector,
            submitSelector: this.submitSelector, 
            responseSelector: this.responseSelector,
            observersActive: this.observers.length,
            interactionsRecorded: this.interactions.length
        };
        
        console.log('📈 Observer Status:', status);
        
        // Make status globally accessible
        window.claudeObserverStatus = status;
        window.claudeObserverData = {
            interactions: this.interactions,
            currentInteraction: this.currentInteraction
        };
    }
    
    // Public methods for external control
    injectPrompt(text) {
        if (!this.inputSelector) {
            console.error('❌ No input element found');
            return false;
        }
        
        const inputElement = document.querySelector(this.inputSelector);
        if (!inputElement) {
            console.error('❌ Input element not accessible');
            return false;
        }
        
        // Clear existing content
        if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {
            inputElement.value = text;
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            // For contenteditable divs
            inputElement.textContent = text;
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        console.log('✏️ Prompt injected:', text.substring(0, 50));
        return true;
    }
    
    submitPrompt() {
        if (!this.submitSelector) {
            console.error('❌ No submit button found');
            return false;
        }
        
        const submitButton = document.querySelector(this.submitSelector);
        if (!submitButton) {
            console.error('❌ Submit button not accessible');
            return false;
        }
        
        if (submitButton.disabled) {
            console.error('❌ Submit button is disabled');
            return false;
        }
        
        submitButton.click();
        console.log('🚀 Prompt submitted');
        return true;
    }
    
    getInteractions() {
        return this.interactions;
    }
    
    getCurrentStatus() {
        return window.claudeObserverStatus;
    }
}

// Initialize the observer
window.claudeObserver = new ClaudeWebObserver();

// Export for external access
window.injectAndSubmit = (prompt) => {
    const observer = window.claudeObserver;
    if (observer.injectPrompt(prompt)) {
        setTimeout(() => observer.submitPrompt(), 100);
        return true;
    }
    return false;
};

console.log('🎉 Claude Web Observer loaded and ready!');
