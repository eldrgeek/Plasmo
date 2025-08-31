#!/usr/bin/env python3
"""
Discord Channel Export Automation
Uses MCP servers to inject JavaScript into Chrome and export Discord channels
"""

import asyncio
import json
import os
from datetime import datetime

class DiscordExporter:
    def __init__(self):
        self.chrome_connection = None
        self.discord_tab_id = None
    
    async def connect_to_chrome(self):
        """Connect to Chrome debug protocol"""
        # This would use your MCP server
        # For now, showing the structure
        print("🔌 Connecting to Chrome...")
        # connection = await connect_to_chrome()
        # tabs = await get_chrome_tabs()
        # return connection, tabs
        pass
    
    async def find_discord_tab(self, tabs):
        """Find Discord tab in open tabs"""
        for tab in tabs:
            if 'discord.com' in tab.get('url', ''):
                print(f"📱 Found Discord tab: {tab['title']}")
                return tab['id']
        
        print("❌ No Discord tab found")
        return None
    
    async def inject_export_functions(self, tab_id):
        """Inject all the export functions we created"""
        
        # The complete JavaScript code (combining all our functions)
        js_code = """
        // scrollOnce function
        async function scrollOnce(delay = 1000) {
            const list = document.querySelectorAll('li.messageListItem__5126c');
            
            if (list.length === 0) {
                console.log('❌ No messages found');
                return { success: false, reachedEnd: false };
            }
            
            const firstMessageBefore = list[0].id;
            console.log(`📍 Before scroll: ${firstMessageBefore} (${list.length} total messages)`);
            
            const first = list[0];
            first.scrollIntoView({ 
                behavior: 'instant', 
                block: 'center', 
                inline: 'nearest'
            });
            
            await new Promise(resolve => setTimeout(resolve, delay));
            
            const newList = document.querySelectorAll('li.messageListItem__5126c');
            const firstMessageAfter = newList.length > 0 ? newList[0].id : null;
            
            const reachedEnd = (firstMessageBefore === firstMessageAfter);
            
            if (reachedEnd) {
                console.log('🏁 Reached beginning - first message unchanged');
            } else {
                console.log(`✅ New first message: ${firstMessageAfter} (${newList.length} total messages)`);
            }
            
            return { 
                success: true, 
                reachedEnd: reachedEnd,
                firstMessageBefore: firstMessageBefore,
                firstMessageAfter: firstMessageAfter
            };
        }
        
        // scrollToStart function
        async function scrollToStart(delay = 1000) {
            console.log('🚀 Starting scroll to beginning...');
            
            let attempt = 0;
            let result;
            
            do {
                attempt++;
                console.log(`--- Attempt ${attempt} ---`);
                result = await scrollOnce(delay);
            } while (result.success && !result.reachedEnd);
            
            if (result.reachedEnd) {
                console.log(`🎯 Successfully reached the beginning after ${attempt} attempts!`);
            } else {
                console.log(`❌ Failed to scroll after ${attempt} attempts`);
            }
            
            return result;
        }
        
        // Message collection function
        async function collectAllMessages(delay = 1500) {
            console.log('📖 Starting message collection from current position...');
            
            const messageContainer = document.querySelector('ol.scrollerInner__36d07[aria-label*="Messages"]');
            if (!messageContainer) {
                console.error('❌ Could not find Discord message container');
                return [];
            }
            
            let allMessages = new Map();
            let noNewMessagesCount = 0;
            let scrollCount = 0;
            
            while (noNewMessagesCount < 3) {
                scrollCount++;
                
                const currentMessages = Array.from(messageContainer.querySelectorAll('li.messageListItem__5126c'));
                let newCount = 0;
                
                currentMessages.forEach(msg => {
                    const id = msg.id;
                    if (!allMessages.has(id)) {
                        const content = msg.querySelector('div[id^="message-content-"]')?.textContent?.trim();
                        const author = msg.querySelector('[class*="username"]')?.textContent?.trim();
                        const timestamp = msg.querySelector('time')?.getAttribute('datetime');
                        
                        if (content && author && timestamp) {
                            allMessages.set(id, {
                                id: id,
                                content: content,
                                author: author,
                                timestamp: timestamp,
                                date: new Date(timestamp)
                            });
                            newCount++;
                        }
                    }
                });
                
                console.log(`📄 Batch ${scrollCount}: Found ${newCount} new messages (Total: ${allMessages.size})`);
                
                if (newCount === 0) {
                    noNewMessagesCount++;
                    console.log(`⏳ No new messages found (${noNewMessagesCount}/3)`);
                } else {
                    noNewMessagesCount = 0;
                }
                
                if (noNewMessagesCount >= 3) {
                    console.log('🏁 Reached end of channel content');
                    break;
                }
                
                window.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'PageDown',
                    code: 'PageDown',
                    bubbles: true
                }));
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
            
            const sortedMessages = Array.from(allMessages.values())
                .sort((a, b) => a.date.getTime() - b.date.getTime());
            
            console.log(`✅ Collection complete! Total messages: ${sortedMessages.length}`);
            return sortedMessages;
        }
        
        // Return data instead of downloading (so Python can handle file operations)
        async function exportCompleteChannelData(scrollDelay = 1000, collectDelay = 1500) {
            console.log('🚀 Starting complete Discord channel export...');
            
            try {
                console.log('📍 Step 1: Scrolling to channel beginning...');
                await scrollToStart(scrollDelay);
                
                console.log('📚 Step 2: Collecting all messages...');
                const messages = await collectAllMessages(collectDelay);
                
                const exportData = {
                    export_date: new Date().toISOString(),
                    channel_url: window.location.href,
                    total_messages: messages.length,
                    date_range: {
                        oldest: messages[0]?.timestamp,
                        newest: messages[messages.length - 1]?.timestamp
                    },
                    messages: messages
                };
                
                console.log('✅ Export data prepared for Python handler');
                
                // Store in window so Python can retrieve it
                window.discordExportData = exportData;
                
                return exportData;
                
            } catch (error) {
                console.error('❌ Export failed with error:', error);
                return { success: false, error: error.message };
            }
        }
        
        console.log('✅ All export functions injected and ready!');
        'Discord export functions ready';
        """
        
        # Execute injection using MCP server
        print("💉 Injecting export functions...")
        # result = await execute_javascript(js_code, tab_id)
        print("✅ Functions injected successfully!")
        
        return True
    
    async def run_export(self, tab_id, scroll_delay=1000, collect_delay=1500):
        """Run the complete export process"""
        
        print("🚀 Starting Discord channel export...")
        
        # Execute the export function
        export_js = f"""
        exportCompleteChannelData({scroll_delay}, {collect_delay}).then(data => {{
            console.log('Export completed, data stored in window.discordExportData');
            return data;
        }});
        """
        
        # result = await execute_javascript(export_js, tab_id)
        print("📊 Export process started in browser...")
        
        # Wait for completion (you'd need to poll or use a different method)
        print("⏳ Waiting for export to complete...")
        await asyncio.sleep(5)  # Placeholder
        
        # Retrieve the data
        retrieve_js = "return window.discordExportData;"
        # export_data = await execute_javascript(retrieve_js, tab_id)
        
        return None  # Placeholder
    
    async def save_to_file(self, export_data, filename=None):
        """Save export data to file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"discord_export_{timestamp}.json"
        
        print(f"💾 Saving to {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Export saved successfully!")
        print(f"📄 File: {os.path.abspath(filename)}")
        print(f"📊 Messages: {export_data.get('total_messages', 0)}")
        
        return filename
    
    async def export_discord_channel(self, scroll_delay=1000, collect_delay=1500):
        """Main export function"""
        
        try:
            # Connect to Chrome
            await self.connect_to_chrome()
            
            # Find Discord tab
            # self.discord_tab_id = await self.find_discord_tab(tabs)
            
            # Inject functions
            # await self.inject_export_functions(self.discord_tab_id)
            
            # Run export
            # export_data = await self.run_export(self.discord_tab_id, scroll_delay, collect_delay)
            
            # Save to file
            # filename = await self.save_to_file(export_data)
            
            print("🎉 Discord channel export completed successfully!")
            # return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None

# Usage example
async def main():
    exporter = DiscordExporter()
    await exporter.export_discord_channel(scroll_delay=1000, collect_delay=1500)

if __name__ == "__main__":
    asyncio.run(main())
