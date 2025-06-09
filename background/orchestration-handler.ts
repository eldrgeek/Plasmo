/**
 * Orchestration Handler for Background Script
 * ==========================================
 * 
 * Handles orchestration commands from MCP server via Socket.IO
 * and coordinates with content scripts for AI service automation.
 */

import { io, Socket } from 'socket.io-client';

export interface OrchestrationCommand {
    id: string;
    type: string;
    prompt: string;
    targets: string[];
    timeout: number;
    priority?: string;
    timestamp: string;
    source: string;
}

export interface OrchestrationResponse {
    commandId: string;
    responses: AIServiceResponse[];
    success: boolean;
    timestamp: string;
}

export interface AIServiceResponse {
    service: string;
    content: string;
    success: boolean;
    error?: string;
    timestamp: string;
}

export class OrchestrationHandler {
    private socket: Socket | null = null;
    private isConnected: boolean = false;
    private activeCommands: Map<string, OrchestrationCommand> = new Map();

    constructor() {
        this.initializeSocketConnection();
    }

    /**
     * Initialize Socket.IO connection
     */
    private initializeSocketConnection(): void {
        try {
            this.socket = io('http://localhost:3001');

            this.socket.on('connect', () => {
                this.isConnected = true;
                console.log('✅ Background script connected to Socket.IO server');

                // Register extension with server
                this.socket?.emit('extension_register', {
                    extensionId: chrome.runtime.id,
                    timestamp: new Date().toISOString()
                });
            });

            this.socket.on('disconnect', () => {
                this.isConnected = false;
                console.log('❌ Background script disconnected from Socket.IO server');
            });

            this.socket.on('orchestration_command', (command: OrchestrationCommand) => {
                console.log('🔥 EXTENSION: Orchestration command received via Socket.IO!');
                console.log('🔥 EXTENSION: Command details:', JSON.stringify(command, null, 2));
                console.log('🔥 EXTENSION: Targets:', command.targets);
                console.log('🔥 EXTENSION: Prompt preview:', command.prompt.substring(0, 100) + '...');

                this.handleOrchestrationCommand(command);
            });

            this.socket.on('error', (error: any) => {
                console.error('Socket.IO error:', error);
            });

        } catch (error) {
            console.error('Failed to initialize Socket.IO connection:', error);
        }
    }

    /**
     * Handle incoming orchestration command
     */
    private async handleOrchestrationCommand(command: OrchestrationCommand): Promise<void> {
        try {
            // Store active command
            this.activeCommands.set(command.id, command);

            console.log(`🚀 Processing orchestration command ${command.id} for targets:`, command.targets);

            // Process each target AI service
            const responses: AIServiceResponse[] = [];

            for (const target of command.targets) {
                try {
                    const response = await this.processAIServiceTarget(command, target);
                    responses.push(response);
                } catch (error) {
                    console.error(`Failed to process target ${target}:`, error);
                    responses.push({
                        service: target,
                        content: '',
                        success: false,
                        error: error instanceof Error ? error.message : String(error),
                        timestamp: new Date().toISOString()
                    });
                }
            }

            // Send aggregated response back
            const orchestrationResponse: OrchestrationResponse = {
                commandId: command.id,
                responses,
                success: responses.some(r => r.success),
                timestamp: new Date().toISOString()
            };

            this.socket?.emit('orchestration_response', orchestrationResponse);
            console.log('🔥 EXTENSION: Sending orchestration response back to MCP server!');
            console.log('🔥 EXTENSION: Response summary:', {
                commandId: orchestrationResponse.commandId,
                success: orchestrationResponse.success,
                responseCount: responses.length,
                successfulResponses: responses.filter(r => r.success).length
            });
            console.log('🔥 EXTENSION: Full response data:', JSON.stringify(orchestrationResponse, null, 2));
            console.log(`✅ Completed orchestration command ${command.id}`);

            // Clean up
            this.activeCommands.delete(command.id);

        } catch (error) {
            console.error('Error handling orchestration command:', error);

            // Send error response
            this.socket?.emit('orchestration_response', {
                commandId: command.id,
                responses: [],
                success: false,
                error: error instanceof Error ? error.message : String(error),
                timestamp: new Date().toISOString()
            });
        }
    }

    /**
     * Process individual AI service target
     */
    private async processAIServiceTarget(command: OrchestrationCommand, target: string): Promise<AIServiceResponse> {
        console.log(`🎯 Processing target: ${target}`);

        // Find or create tab for the target AI service
        const tab = await this.getOrCreateAIServiceTab(target);
        if (!tab || !tab.id) {
            throw new Error(`Failed to get tab for ${target}`);
        }

        // Inject content script if needed
        await this.ensureContentScriptInjected(tab.id, target);

        // Send command to content script
        const response = await this.sendCommandToContentScript(tab.id, command, target);

        return {
            service: target,
            content: response.content || '',
            success: response.success,
            error: response.error,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Get or create tab for AI service
     */
    private async getOrCreateAIServiceTab(service: string): Promise<chrome.tabs.Tab> {
        const serviceUrls: { [key: string]: string } = {
            'chatgpt': 'https://chat.openai.com',
            'claude': 'https://claude.ai',
            'perplexity': 'https://perplexity.ai'
        };

        const targetUrl = serviceUrls[service];
        if (!targetUrl) {
            throw new Error(`Unknown AI service: ${service}`);
        }

        // Look for existing tab
        const tabs = await chrome.tabs.query({ url: `*://${new URL(targetUrl).hostname}/*` });

        if (tabs.length > 0 && tabs[0]) {
            // Use existing tab
            await chrome.tabs.update(tabs[0].id!, { active: true });
            return tabs[0];
        } else {
            // Create new tab
            return await chrome.tabs.create({ url: targetUrl, active: false });
        }
    }

    /**
     * Ensure content script is injected
     */
    private async ensureContentScriptInjected(tabId: number, service: string): Promise<void> {
        try {
            // Test if content script is already injected
            await chrome.tabs.sendMessage(tabId, { type: 'ping' });
        } catch {
            // Content script not injected, inject it
            const scriptFiles = ['contents/ai-interface-base.js'];

            if (service === 'chatgpt') {
                scriptFiles.push('contents/chatgpt-interface.js');
            } else if (service === 'claude') {
                scriptFiles.push('contents/claude-interface.js');
            }

            for (const file of scriptFiles) {
                try {
                    await chrome.scripting.executeScript({
                        target: { tabId },
                        files: [file]
                    });
                } catch (error) {
                    console.warn(`Failed to inject ${file}:`, error);
                }
            }
        }
    }

    /**
     * Send command to content script
     */
    private async sendCommandToContentScript(
        tabId: number,
        command: OrchestrationCommand,
        service: string
    ): Promise<{ success: boolean; content?: string; error?: string }> {
        return new Promise((resolve) => {
            const timeout = setTimeout(() => {
                resolve({
                    success: false,
                    error: `Timeout waiting for ${service} response`
                });
            }, command.timeout * 1000);

            chrome.tabs.sendMessage(tabId, {
                type: 'orchestration_command',
                service,
                prompt: command.prompt,
                commandId: command.id
            }, (response) => {
                clearTimeout(timeout);

                if (chrome.runtime.lastError) {
                    resolve({
                        success: false,
                        error: chrome.runtime.lastError.message
                    });
                } else {
                    resolve(response || {
                        success: false,
                        error: 'No response from content script'
                    });
                }
            });
        });
    }

    /**
     * Get connection status
     */
    isSocketConnected(): boolean {
        return this.isConnected;
    }

    /**
     * Get active commands count
     */
    getActiveCommandsCount(): number {
        return this.activeCommands.size;
    }
}

// Initialize orchestration handler when background script loads
const orchestrationHandler = new OrchestrationHandler();

// Export for testing
export default orchestrationHandler; 