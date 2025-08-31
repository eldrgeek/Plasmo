#!/usr/bin/env python3
"""
Discord Channel Export with Playwright - Chrome Debug Connection
Connects to existing Chrome instance with debugging enabled
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class DiscordChannelExporter:
    def __init__(self, debug_port=9222):
        self.browser = None
        self.page = None
        self.debug_port = debug_port
        self.playwright = None
    
    async def connect_to_chrome(self):
        """Connect to existing Chrome instance with debugging"""
        print(f"🔌 Connecting to Chrome debug instance on port {self.debug_port}...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Connect to existing Chrome instance
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            
            # Get existing contexts and pages
            contexts = self.browser.contexts
            if contexts:
                context = contexts[0]  # Use first context
                pages = context.pages
                
                # Find Discord page or use first available page
                discord_page = None
                for page in pages:
                    url = page.url
                    if 'discord.com' in url:
                        discord_page = page
                        break
                
                if discord_page:
                    self.page = discord_page
                    print(f"✅ Connected to existing Discord page: {self.page.url}")
                else:
                    # Use first available page
                    if pages:
                        self.page = pages[0]
                        print(f"✅ Connected to page: {self.page.url}")
                        print("⚠️  Not a Discord page - you may need to navigate to Discord first")
                    else:
                        # Create new page if none exist
                        self.page = await context.new_page()
                        print("✅ Created new page in existing browser")
            else:
                print("❌ No browser contexts found")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Chrome: {e}")
            print("💡 Make sure Chrome is running with: --remote-debugging-port=9222")
            return False
    
    async def navigate_to_discord(self, channel_url=None):
        """Navigate to Discord channel or check current page"""
        if channel_url:
            print(f"🔗 Navigating to: {channel_url}")
            await self.page.goto(channel_url)
        else:
            current_url = self.page.url
            print(f"📍 Using current page: {current_url}")
            
            if 'discord.com' not in current_url:
                print("⚠️  Current page is not Discord. Please navigate to a Discord channel first.")
                return False
        
        # Wait for Discord to load
        try:
            await self.page.wait_for_selector('ol.scrollerInner__36d07', timeout=10000)
            print("✅ Discord channel detected and loaded")
            return True
        except Exception as e:
            print(f"❌ Discord channel not found: {e}")
            print("💡 Make sure you're on a Discord channel page")
            return False
    
    async def inject_export_functions(self):
        """Inject all the JavaScript export functions"""
        print("💉 Injecting JavaScript functions...")
        
        js_functions = '''
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
                
                // Safety limit for very large channels
                if (attempt > 200) {
                    console.log('⚠️ Safety limit reached (200 attempts)');
                    break;
                }
            } while (result.success && !result.reachedEnd);
            
            if (result.reachedEnd) {
                console.log(`🎯 Successfully reached the beginning after ${attempt} attempts!`);
            } else {
                console.log(`❌ Failed to scroll after ${attempt} attempts`);
            }
            
            return result;
        }
        
        // collectAllMessages function
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
                                timestamp: timestamp
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
                
                // Safety limit for extremely large channels
                if (scrollCount > 1000) {
                    console.log('⚠️ Safety limit reached (1000 scroll batches)');
                    break;
                }
                
                // Scroll down (Page Down)
                window.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'PageDown',
                    code: 'PageDown',
                    bubbles: true
                }));
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
            
            // Sort messages chronologically
            const sortedMessages = Array.from(allMessages.values())
                .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
            
            console.log(`✅ Collection complete! Total messages: ${sortedMessages.length}`);
            return sortedMessages;
        }
        
        // Export function that returns data for Python
        async function exportChannelData(scrollDelay = 1000, collectDelay = 1500) {
            console.log('🚀 Starting Discord channel export...');
            
            try {
                console.log('📍 Step 1: Scrolling to beginning...');
                const scrollResult = await scrollToStart(scrollDelay);
                
                if (!scrollResult.success) {
                    throw new Error('Failed to scroll to beginning');
                }
                
                console.log('📚 Step 2: Collecting messages...');
                const messages = await collectAllMessages(collectDelay);
                
                const exportData = {
                    export_date: new Date().toISOString(),
                    channel_url: window.location.href,
                    total_messages: messages.length,
                    date_range: {
                        oldest: messages[0]?.timestamp || null,
                        newest: messages[messages.length - 1]?.timestamp || null
                    },
                    messages: messages
                };
                
                console.log('✅ Export data prepared');
                console.log(`📊 Total messages collected: ${messages.length}`);
                
                return exportData;
                
            } catch (error) {
                console.error('❌ Export failed:', error);
                return { success: false, error: error.message };
            }
        }
        
        // Make functions globally available
        window.exportChannelData = exportChannelData;
        window.scrollToStart = scrollToStart;
        window.collectAllMessages = collectAllMessages;
        
        console.log('✅ Export functions injected successfully!');
        return 'Functions injected';
        '''
        
        try:
            result = await self.page.evaluate(js_functions)
            print(f"✅ JavaScript injection successful: {result}")
            return True
        except Exception as e:
            print(f"❌ JavaScript injection failed: {e}")
            return False
    
    async def run_export(self, scroll_delay=1000, collect_delay=1500):
        """Execute the export process and return data"""
        print(f"🚀 Starting export process...")
        print(f"⏱️  Timing: {scroll_delay}ms scroll delay, {collect_delay}ms collect delay")
        
        try:
            # Execute the export function
            export_data = await self.page.evaluate(f"""
                exportChannelData({scroll_delay}, {collect_delay})
            """)
            
            if export_data and not export_data.get('error'):
                print(f"✅ Export completed successfully!")
                print(f"📊 Messages collected: {export_data.get('total_messages', 0)}")
                return export_data
            else:
                print(f"❌ Export failed: {export_data}")
                return None
                
        except Exception as e:
            print(f"❌ Export execution failed: {e}")
            return None
    
    async def save_export_data(self, export_data, filename=None):
        """Save export data to JSON file"""
        if not export_data:
            print("❌ No data to save")
            return None
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Extract channel info from URL
            url = export_data.get('channel_url', '')
            channel_id = url.split('/')[-1] if url else 'unknown'
            filename = f"discord_export_{channel_id}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            file_path = os.path.abspath(filename)
            file_size = os.path.getsize(filename)
            
            print(f"💾 Export saved successfully!")
            print(f"📁 File: {file_path}")
            print(f"📊 Messages: {export_data.get('total_messages', 0)}")
            print(f"💽 Size: {file_size:,} bytes")
            
            if export_data.get('date_range'):
                print(f"📅 Date range: {export_data['date_range']['oldest']} to {export_data['date_range']['newest']}")
            
            return file_path
            
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
            return None
    
    async def close(self):
        """Clean up resources (but don't close the browser)"""
        # Note: We don't close the browser since it's the user's existing instance
        if self.playwright:
            await self.playwright.stop()
        print("🧹 Disconnected from browser (browser remains open)")
    
    async def export_current_channel(self, scroll_delay=1000, collect_delay=1500):
        """Export the currently open Discord channel"""
        try:
            # Connect to existing Chrome
            if not await self.connect_to_chrome():
                return {'success': False, 'error': 'Failed to connect to Chrome'}
            
            # Check current page is Discord
            if not await self.navigate_to_discord():
                return {'success': False, 'error': 'Not on a Discord channel page'}
            
            # Inject export functions
            if not await self.inject_export_functions():
                return {'success': False, 'error': 'Failed to inject JavaScript functions'}
            
            # Wait a moment for everything to be ready
            await asyncio.sleep(2)
            
            # Run export
            export_data = await self.run_export(scroll_delay, collect_delay)
            
            if export_data:
                # Save to file
                file_path = await self.save_export_data(export_data)
                
                if file_path:
                    return {
                        'success': True,
                        'file_path': file_path,
                        'message_count': export_data.get('total_messages', 0),
                        'channel_url': export_data.get('channel_url', '')
                    }
                else:
                    return {'success': False, 'error': 'Failed to save export file'}
            else:
                return {'success': False, 'error': 'Export process failed'}
                
        except Exception as e:
            print(f"❌ Export failed with exception: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            await self.close()

# Convenience functions
async def export_current_discord_channel(scroll_delay=1000, collect_delay=1500, debug_port=9222):
    """Export the currently open Discord channel from existing Chrome instance"""
    exporter = DiscordChannelExporter(debug_port=debug_port)
    return await exporter.export_current_channel(scroll_delay, collect_delay)

async def test_connection():
    """Test connection to Chrome debug instance"""
    print("🧪 Testing connection to Chrome debug instance...")
    exporter = DiscordChannelExporter()
    
    try:
        if await exporter.connect_to_chrome():
            print(f"✅ Successfully connected!")
            print(f"📍 Current page: {exporter.page.url}")
            
            # Check if it's Discord
            is_discord = 'discord.com' in exporter.page.url
            print(f"🔍 Is Discord page: {is_discord}")
            
            return True
        else:
            print("❌ Connection failed")
            return False
    finally:
        await exporter.close()

async def main():
    """Main function to run the export"""
    print("🎬 Discord Channel Export Tool")
    print("=" * 50)
    
    # Test connection first
    print("\n1️⃣ Testing Chrome connection...")
    if not await test_connection():
        print("\n💡 Make sure Chrome is running with debugging enabled:")
        print("   chrome --remote-debugging-port=9222")
        return
    
    print("\n2️⃣ Starting export of current Discord channel...")
    print("⚠️  Make sure you're on the Discord channel you want to export!")
    
    # Run export with custom timing for large channels
    result = await export_current_discord_channel(
        scroll_delay=1200,    # 1.2 seconds between scrolls to beginning
        collect_delay=1800,   # 1.8 seconds between collection scrolls
        debug_port=9222       # Chrome debug port
    )
    
    if result['success']:
        print(f"\n🎉 Export completed successfully!")
        print(f"📁 File: {result['file_path']}")
        print(f"📊 Messages: {result['message_count']:,}")
        print(f"🔗 Channel: {result['channel_url']}")
    else:
        print(f"\n❌ Export failed: {result['error']}")

if __name__ == "__main__":
    print("Starting Discord export...")
    asyncio.run(main())
