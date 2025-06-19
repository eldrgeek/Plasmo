/**
 * Tab Manager for Background Script
 * ================================
 * 
 * Manages Chrome tabs for AI service automation.
 * Handles tab creation, lifecycle, and cleanup.
 */

export interface TabInfo {
    id: number;
    url: string;
    service: string;
    active: boolean;
    lastAccessed: number;
}

export class TabManager {
    private managedTabs: Map<string, TabInfo> = new Map();
    private cleanupInterval: number | null = null;

    constructor() {
        this.initializeCleanup();
        this.setupTabListeners();
    }

    /**
     * Get or create tab for AI service
     */
    async getOrCreateServiceTab(service: string): Promise<chrome.tabs.Tab> {
        const existingTab = this.managedTabs.get(service);

        // Check if existing tab is still valid
        if (existingTab) {
            try {
                const tab = await chrome.tabs.get(existingTab.id);
                if (tab && tab.url && tab.id) {
                    // Update last accessed time
                    existingTab.lastAccessed = Date.now();
                    await chrome.tabs.update(tab.id, { active: true });
                    return tab;
                }
            } catch {
                // Tab no longer exists, remove from tracking
                this.managedTabs.delete(service);
            }
        }

        // Create new tab
        const serviceUrls: { [key: string]: string } = {
            'chatgpt': 'https://chat.openai.com',
            'claude': 'https://claude.ai',
            'perplexity': 'https://perplexity.ai',
            'gemini': 'https://gemini.google.com',
            'copilot': 'https://copilot.microsoft.com'
        };

        const url = serviceUrls[service];
        if (!url) {
            throw new Error(`Unknown AI service: ${service}`);
        }

        const tab = await chrome.tabs.create({ url, active: false });

        if (tab.id) {
            // Track the new tab
            this.managedTabs.set(service, {
                id: tab.id,
                url,
                service,
                active: true,
                lastAccessed: Date.now()
            });
        }

        return tab;
    }

    /**
     * Close tab for specific service
     */
    async closeServiceTab(service: string): Promise<boolean> {
        const tabInfo = this.managedTabs.get(service);
        if (tabInfo) {
            try {
                await chrome.tabs.remove(tabInfo.id);
                this.managedTabs.delete(service);
                return true;
            } catch (error) {
                console.error(`Failed to close tab for ${service}:`, error);
                this.managedTabs.delete(service); // Remove from tracking anyway
                return false;
            }
        }
        return false;
    }

    /**
     * Close all managed tabs
     */
    async closeAllServiceTabs(): Promise<void> {
        const tabIds = Array.from(this.managedTabs.values()).map(tab => tab.id);

        if (tabIds.length > 0) {
            try {
                await chrome.tabs.remove(tabIds);
            } catch (error) {
                console.error('Failed to close some tabs:', error);
            }
        }

        this.managedTabs.clear();
    }

    /**
     * Get tab info for service
     */
    getServiceTabInfo(service: string): TabInfo | undefined {
        return this.managedTabs.get(service);
    }

    /**
     * Get all managed tabs
     */
    getAllManagedTabs(): TabInfo[] {
        return Array.from(this.managedTabs.values());
    }

    /**
     * Update tab activity
     */
    updateTabActivity(tabId: number): void {
        for (const [service, tabInfo] of this.managedTabs.entries()) {
            if (tabInfo.id === tabId) {
                tabInfo.lastAccessed = Date.now();
                tabInfo.active = true;
                break;
            }
        }
    }

    /**
     * Setup tab event listeners
     */
    private setupTabListeners(): void {
        // Listen for tab closure
        chrome.tabs.onRemoved.addListener((tabId) => {
            for (const [service, tabInfo] of this.managedTabs.entries()) {
                if (tabInfo.id === tabId) {
                    this.managedTabs.delete(service);
                    console.log(`🗑️ Removed tracking for ${service} tab (closed)`);
                    break;
                }
            }
        });

        // Listen for tab updates
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete') {
                this.updateTabActivity(tabId);
            }
        });

        // Listen for tab activation
        chrome.tabs.onActivated.addListener(({ tabId }) => {
            this.updateTabActivity(tabId);
        });
    }

    /**
     * Initialize cleanup routine
     */
    private initializeCleanup(): void {
        // Clean up inactive tabs every 30 minutes
        this.cleanupInterval = setInterval(() => {
            this.cleanupInactiveTabs();
        }, 30 * 60 * 1000) as unknown as number;
    }

    /**
     * Clean up tabs that haven't been accessed recently
     */
    private async cleanupInactiveTabs(): Promise<void> {
        const maxInactiveTime = 2 * 60 * 60 * 1000; // 2 hours
        const now = Date.now();
        const toRemove: string[] = [];

        for (const [service, tabInfo] of this.managedTabs.entries()) {
            if (now - tabInfo.lastAccessed > maxInactiveTime) {
                try {
                    await chrome.tabs.remove(tabInfo.id);
                    toRemove.push(service);
                    console.log(`🧹 Cleaned up inactive ${service} tab`);
                } catch {
                    // Tab already closed, just remove from tracking
                    toRemove.push(service);
                }
            }
        }

        toRemove.forEach(service => this.managedTabs.delete(service));
    }

    /**
     * Get statistics about managed tabs
     */
    getStats(): {
        totalTabs: number;
        activeServices: string[];
        oldestTab: { service: string; age: number } | null;
    } {
        const tabs = this.getAllManagedTabs();
        const now = Date.now();

        let oldestTab: { service: string; age: number } | null = null;

        for (const [service, tabInfo] of this.managedTabs.entries()) {
            const age = now - tabInfo.lastAccessed;
            if (!oldestTab || age > oldestTab.age) {
                oldestTab = { service, age };
            }
        }

        return {
            totalTabs: tabs.length,
            activeServices: Array.from(this.managedTabs.keys()),
            oldestTab
        };
    }

    /**
     * Destroy tab manager (cleanup)
     */
    destroy(): void {
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
        }
    }
}

// Export singleton instance
export const tabManager = new TabManager(); 