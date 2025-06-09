/**
 * Claude.ai Interface for Content Scripts
 * ======================================
 * 
 * Automates interaction with Claude.ai web interface.
 */

import { AIInterfaceBase } from './ai-interface-base';

export class ClaudeInterface extends AIInterfaceBase {
    private textareaSelector = 'div[contenteditable="true"], textarea[placeholder*="Talk to Claude"]';
    private sendButtonSelector = 'button[aria-label*="Send"], button[data-testid="send-button"]';
    private responseSelector = '[data-is-streaming="false"]';

    constructor() {
        super('Claude.ai');
    }

    /**
     * Detect if current page is Claude.ai
     */
    detectPage(): boolean {
        const url = window.location.href;
        const title = document.title.toLowerCase();

        return url.includes('claude.ai') ||
            url.includes('anthropic.com') ||
            title.includes('claude');
    }

    /**
     * Send message to Claude.ai
     */
    async sendMessage(message: string): Promise<void> {
        try {
            console.log('🔥 CLAUDE: Starting message injection...');
            console.log('🔥 CLAUDE: Message to send:', message);

            // Wait for input field to be available
            const inputField = await this.waitForElement(this.textareaSelector);
            if (!inputField) {
                console.log('🔥 CLAUDE: ❌ Input field not found!');
                throw new Error('Claude.ai input field not found');
            }

            console.log('🔥 CLAUDE: ✅ Input field found, preparing injection...');

            // Focus on the input field
            (inputField as HTMLElement).focus();

            // For contenteditable div, set innerHTML; for textarea, set value
            if (inputField.tagName.toLowerCase() === 'textarea') {
                console.log('🔥 CLAUDE: 📝 Using textarea input method...');
                (inputField as HTMLTextAreaElement).value = message;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            } else {
                console.log('🔥 CLAUDE: 📝 Using contenteditable div method...');
                // For contenteditable div
                inputField.innerHTML = message;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }

            console.log('🔥 CLAUDE: ✅ Message injected, waiting for UI update...');

            // Wait a moment for UI to update
            await this.sleep(500);

            // Find and click send button
            const sendButton = await this.waitForElement(this.sendButtonSelector) as HTMLButtonElement;
            if (!sendButton) {
                console.log('🔥 CLAUDE: ❌ Send button not found!');
                throw new Error('Claude.ai send button not found');
            }

            console.log('🔥 CLAUDE: 🔘 Clicking send button...');
            sendButton.click();
            console.log('🔥 CLAUDE: ✅ Message sent successfully! Waiting for response...');
            console.log(`✅ Message sent to Claude.ai: ${message.substring(0, 50)}...`);

        } catch (error) {
            console.error('🔥 CLAUDE: ❌ Failed to send message:', error);
            throw error;
        }
    }

    /**
     * Extract response from Claude.ai
     */
    async extractResponse(): Promise<string> {
        try {
            // Wait for response to appear (with longer timeout for AI generation)
            await this.sleep(3000); // Initial wait for Claude to start responding

            // Wait for streaming to complete
            await this.waitForResponseComplete();

            // Find response elements
            const responseElements = document.querySelectorAll(this.responseSelector);
            if (responseElements.length === 0) {
                // Fallback: look for any message container
                const fallbackSelector = '[data-testid="message"], .message, .response';
                const fallbackElements = document.querySelectorAll(fallbackSelector);
                if (fallbackElements.length === 0) {
                    throw new Error('No Claude.ai responses found');
                }
            }

            // Get the latest response
            const allResponses = document.querySelectorAll('[data-testid="message"], .message, .response');
            const latestResponse = allResponses[allResponses.length - 1];
            const responseText = latestResponse?.textContent || latestResponse?.innerHTML || '';

            if (!responseText.trim()) {
                throw new Error('Claude.ai response is empty');
            }

            console.log('🔥 CLAUDE: ✅ Response extracted successfully!');
            console.log('🔥 CLAUDE: 📄 Response length:', responseText.length);
            console.log('🔥 CLAUDE: 📄 Response preview:', responseText.substring(0, 200) + '...');
            console.log(`✅ Extracted Claude.ai response: ${responseText.substring(0, 100)}...`);
            return responseText.trim();

        } catch (error) {
            console.error('Failed to extract Claude.ai response:', error);
            throw error;
        }
    }

    /**
     * Wait for Claude.ai to finish generating response
     */
    async waitForResponseComplete(timeout: number = 120000): Promise<boolean> {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            // Check for streaming indicators
            const streamingElements = document.querySelectorAll('[data-is-streaming="true"]');
            const thinkingIndicator = document.querySelector('.thinking, [aria-label*="thinking"]');
            const loadingIndicator = document.querySelector('.loading, [aria-label*="loading"]');

            if (streamingElements.length === 0 && !thinkingIndicator && !loadingIndicator) {
                await this.sleep(2000); // Extra wait to ensure completion
                return true; // Response is complete
            }

            await this.sleep(1000); // Check every second
        }

        return false; // Timeout
    }

    /**
     * Complete workflow: send message and wait for response
     */
    async sendAndGetResponse(message: string): Promise<string> {
        await this.sendMessage(message);

        // Wait for response generation to complete
        const isComplete = await this.waitForResponseComplete();
        if (!isComplete) {
            console.warn('Claude.ai response generation timed out');
        }

        return await this.extractResponse();
    }
} 