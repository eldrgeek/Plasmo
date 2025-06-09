/**
 * Base AI Interface for Content Scripts
 * ====================================
 * 
 * Abstract base class for AI service automation interfaces.
 * Provides common functionality for ChatGPT, Claude.ai, and other AI services.
 */

export abstract class AIInterfaceBase {
    protected serviceName: string;
    protected isInitialized: boolean = false;

    constructor(serviceName: string) {
        this.serviceName = serviceName;
    }

    /**
     * Detect if current page is the target AI service
     */
    abstract detectPage(): boolean;

    /**
     * Send message to AI service
     */
    abstract sendMessage(message: string): Promise<void>;

    /**
     * Extract response from AI service
     */
    abstract extractResponse(): Promise<string>;

    /**
     * Initialize the interface (detect page, set up listeners, etc.)
     */
    async initialize(): Promise<boolean> {
        try {
            if (this.detectPage()) {
                this.isInitialized = true;
                console.log(`✅ ${this.serviceName} interface initialized`);
                return true;
            } else {
                console.log(`❌ ${this.serviceName} page not detected`);
                return false;
            }
        } catch (error) {
            console.error(`Failed to initialize ${this.serviceName} interface:`, error);
            return false;
        }
    }

    /**
     * Wait for element to appear in DOM
     */
    protected waitForElement(selector: string, timeout: number = 10000): Promise<Element | null> {
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

            // Timeout fallback
            setTimeout(() => {
                observer.disconnect();
                resolve(null);
            }, timeout);
        });
    }

    /**
     * Wait for specified time
     */
    protected sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if interface is ready
     */
    isReady(): boolean {
        return this.isInitialized && this.detectPage();
    }

    /**
     * Get service name
     */
    getServiceName(): string {
        return this.serviceName;
    }
} 