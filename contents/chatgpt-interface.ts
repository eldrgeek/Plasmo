/**
 * ChatGPT Interface for Content Scripts
 * ====================================
 * 
 * Automates interaction with ChatGPT web interface.
 */

import { AIInterfaceBase } from './ai-interface-base';

export class ChatGPTInterface extends AIInterfaceBase {
    private textareaSelector = 'textarea[placeholder*="Send a message"], textarea[data-id="root"]';
    private sendButtonSelector = 'button[data-testid="send-button"], button[data-testid="fruitjuice-send-button"]';
    private responseSelector = '[data-message-author-role="assistant"]';

    constructor() {
        super('ChatGPT');
    }

    /**
     * Detect if current page is ChatGPT
     */
    detectPage(): boolean {
        const url = window.location.href;
        const title = document.title.toLowerCase();

        return url.includes('chat.openai.com') ||
            url.includes('chatgpt.com') ||
            title.includes('chatgpt');
    }

    /**
     * Send message to ChatGPT
     */
    async sendMessage(message: string): Promise<void> {
        try {
            console.log('🔥 CHATGPT: Starting message injection...');
            console.log('🔥 CHATGPT: Message to send:', message);

            // Wait for textarea to be available
            const textarea = await this.waitForElement(this.textareaSelector) as HTMLTextAreaElement;
            if (!textarea) {
                console.log('🔥 CHATGPT: ❌ Textarea not found!');
                throw new Error('ChatGPT textarea not found');
            }

            console.log('🔥 CHATGPT: ✅ Textarea found, preparing to inject message...');

            // Clear existing content and set new message
            textarea.value = '';
            textarea.focus();

            console.log('🔥 CHATGPT: 📝 Typing message character by character...');

            // Type message character by character to trigger React events
            for (const char of message) {
                textarea.value += char;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                await this.sleep(10); // Small delay between characters
            }

            console.log('🔥 CHATGPT: ✅ Message typed successfully, waiting for UI update...');

            // Wait a moment for UI to update
            await this.sleep(500);

            // Find and click send button
            const sendButton = await this.waitForElement(this.sendButtonSelector) as HTMLButtonElement;
            if (!sendButton) {
                console.log('🔥 CHATGPT: ❌ Send button not found!');
                throw new Error('ChatGPT send button not found');
            }

            console.log('🔥 CHATGPT: 🔘 Clicking send button...');
            sendButton.click();
            console.log('🔥 CHATGPT: ✅ Message sent successfully! Waiting for response...');
            console.log(`✅ Message sent to ChatGPT: ${message.substring(0, 50)}...`);

        } catch (error) {
            console.error('🔥 CHATGPT: ❌ Failed to send message:', error);
            throw error;
        }
    }

    /**
     * Extract response from ChatGPT
     */
    async extractResponse(): Promise<string> {
        try {
            console.log('🔥 CHATGPT: 📥 Starting response extraction...');

            // Wait for response to appear (with longer timeout for AI generation)
            await this.sleep(2000); // Initial wait

            const responseElements = document.querySelectorAll(this.responseSelector);
            console.log(`🔥 CHATGPT: Found ${responseElements.length} response elements`);

            if (responseElements.length === 0) {
                console.log('🔥 CHATGPT: ❌ No response elements found!');
                throw new Error('No ChatGPT responses found');
            }

            // Get the latest response
            const latestResponse = responseElements[responseElements.length - 1];
            const responseText = latestResponse.textContent || latestResponse.innerHTML || '';

            console.log('🔥 CHATGPT: 📄 Raw response length:', responseText.length);
            console.log('🔥 CHATGPT: 📄 Response preview:', responseText.substring(0, 200) + '...');

            if (!responseText.trim()) {
                console.log('🔥 CHATGPT: ❌ Response is empty!');
                throw new Error('ChatGPT response is empty');
            }

            console.log('🔥 CHATGPT: ✅ Response extracted successfully!');
            console.log(`✅ Extracted ChatGPT response: ${responseText.substring(0, 100)}...`);
            return responseText.trim();

        } catch (error) {
            console.error('🔥 CHATGPT: ❌ Failed to extract response:', error);
            throw error;
        }
    }

    /**
     * Wait for ChatGPT to finish generating response
     */
    async waitForResponseComplete(timeout: number = 60000): Promise<boolean> {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            // Check if there's a "Stop generating" button (indicates ChatGPT is still generating)
            const stopButton = document.querySelector('button[aria-label*="Stop"]');
            if (!stopButton) {
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
            console.warn('ChatGPT response generation timed out');
        }

        return await this.extractResponse();
    }
} 