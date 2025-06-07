#!/usr/bin/env python3
"""
Playwright-based Bolt.new Automation
===================================

This script uses Playwright to launch a visible Chrome instance and automate Bolt.new.
Much more reliable than Chrome Debug Protocol and easier to debug.

Usage:
    python bolt_automation_playwright.py 'Create a simple React app'

Prerequisites:
    pip install playwright
    playwright install chromium
"""

import asyncio
import sys
import json
from playwright.async_api import async_playwright
from datetime import datetime

async def connect_to_existing_chrome():
    """Connect to existing Chrome debug instance."""
    playwright = await async_playwright().start()
    
    try:
        # Connect to existing Chrome instance via CDP
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        print("✅ Connected to existing Chrome instance")
        return playwright, browser
    except Exception as e:
        print(f"⚠️  Could not connect to existing Chrome: {e}")
        print("🔄 Falling back to launching new Chrome...")
        
        # Fallback: launch new Chrome
        browser = await playwright.chromium.launch(
            headless=False,
            args=['--start-maximized', '--no-first-run']
        )
        return playwright, browser

async def find_bolt_page(browser):
    """Find the existing bolt.new page."""
    print("🔍 Looking for existing bolt.new page...")
    
    try:
        # Get all contexts and pages
        contexts = browser.contexts
        
        for context in contexts:
            pages = context.pages
            for page in pages:
                try:
                    url = page.url
                    title = await page.title()
                    print(f"🔍 Found page: {title} - {url}")
                    
                    if "bolt.new" in url:
                        print(f"✅ Found bolt.new page: {title}")
                        await page.bring_to_front()
                        return page
                except Exception as e:
                    print(f"⚠️  Error checking page: {e}")
                    continue
        
        print("❌ No bolt.new page found in existing tabs")
        return None
        
    except Exception as e:
        print(f"⚠️  Error finding bolt page: {e}")
        return None

async def inject_prompt_and_submit(page, prompt_text):
    """Inject prompt into Bolt.new and submit."""
    print(f"🎯 Injecting prompt: {prompt_text}")
    
    try:
        # Wait for the page to be fully loaded
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Extra wait for any dynamic content
        
        # Multiple selectors to find the textarea - more specific for Bolt.new
        textarea_selectors = [
            'textarea[placeholder*="How can Bolt help" i]',
            'textarea[placeholder*="prompt" i]',
            'textarea[placeholder*="describe" i]', 
            'textarea[placeholder*="build" i]',
            'textarea[placeholder*="help" i]',
            'textarea:not([style*="display: none"])',
            '.prompt-input textarea',
            '[data-testid*="prompt"] textarea',
            'textarea.w-full',  # Common Tailwind class in Bolt
            'textarea',
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    textarea = element
                    print(f"✅ Found textarea with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not textarea:
            # Try to take a screenshot for debugging
            await page.screenshot(path="bolt_debug.png")
            print("❌ Could not find textarea. Screenshot saved as bolt_debug.png")
            return False
        
        # Focus and clear the textarea
        await textarea.click()
        await page.keyboard.press('Control+a')  # Select all
        await page.keyboard.press('Delete')     # Delete selection
        
        # Type the prompt
        await textarea.type(prompt_text, delay=50)  # Small delay between keystrokes
        
        print("✅ Prompt injected successfully")
        
        # Wait a moment for any reactive updates
        await page.wait_for_timeout(1500)
        
        # Find and click submit button - more specific for Bolt.new
        submit_selectors = [
            'button[type="submit"]',
            'button:has(svg):near(textarea)',  # Button with icon near textarea
            'button[aria-label*="submit" i]',
            'button[aria-label*="send" i]',
            'button:has-text("Send")',
            'button:has-text("Submit")',
            'button:has-text("Generate")',
            'button:has-text("Create")',
            'button.bg-',  # Styled button (likely using Tailwind)
            'button[class*="primary"]',
            'form button',  # Button inside a form
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible() and await button.is_enabled():
                    submit_button = button
                    print(f"✅ Found submit button with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not submit_button:
            # Try to find any button near the textarea
            try:
                submit_button = page.locator('button').filter(has_text=lambda text: any(word in text.lower() for word in ['send', 'submit', 'generate', 'create'])).first
                if await submit_button.is_visible():
                    print("✅ Found submit button by text content")
                else:
                    submit_button = None
            except Exception:
                pass
        
        if not submit_button:
            await page.screenshot(path="bolt_no_button.png")
            print("❌ Could not find submit button. Screenshot saved as bolt_no_button.png")
            return False
        
        # Click the submit button
        await submit_button.click()
        print("✅ Submit button clicked")
        
        # Wait for response to start loading
        await page.wait_for_timeout(3000)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        await page.screenshot(path="bolt_error.png")
        print("Screenshot saved as bolt_error.png")
        return False

async def monitor_response(page, timeout_seconds=60):
    """Monitor for Bolt's response."""
    print("🔍 Monitoring for Bolt's response...")
    
    start_time = datetime.now()
    
    # Look for signs that Bolt is generating a response
    response_indicators = [
        '[data-testid*="response"]',
        '[class*="response"]',
        '[class*="generating"]',
        '[class*="loading"]',
        'pre code',  # Code blocks that Bolt generates
        '.markdown',  # Markdown content
        '.prose',    # Prose styling
        '[class*="message"]',
        '.chat-message',
        '[role="article"]',  # Semantic content
    ]
    
    last_content_length = 0
    
    while (datetime.now() - start_time).seconds < timeout_seconds:
        try:
            # Check for response content
            found_content = False
            for selector in response_indicators:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    
                    if count > 0:
                        for i in range(count):
                            element = elements.nth(i)
                            if await element.is_visible():
                                content = await element.text_content()
                                if content and len(content.strip()) > 20:
                                    if len(content) > last_content_length:
                                        last_content_length = len(content)
                                        clean_content = content[:100].replace('\n', ' ')
                                        print(f"✅ Response growing: {len(content)} chars - {clean_content}...")
                                        found_content = True
                except Exception:
                    continue
            
            # Check for any text content that looks like a response
            if not found_content:
                # Look for any significant text content that wasn't there before
                body_text = await page.locator('body').text_content()
                if len(body_text) > last_content_length + 100:  # Significant content increase
                    print(f"✅ Page content increased significantly: {len(body_text)} chars")
                    return True
            
            # Check page title for changes
            title = await page.title()
            if any(word in title.lower() for word in ['generating', 'creating', 'building']):
                print(f"🔄 Bolt is working: {title}")
            
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"⚠️  Monitoring error: {e}")
            await page.wait_for_timeout(2000)
    
    print("⏰ Response monitoring timed out")
    return False

async def main():
    if len(sys.argv) != 2:
        print("Usage: python bolt_automation_playwright.py '<prompt>'")
        print("Example: python bolt_automation_playwright.py 'Create a simple React todo app'")
        sys.exit(1)
    
    prompt_text = sys.argv[1]
    print(f"🚀 Starting Playwright Bolt.new automation...")
    print(f"🎯 Prompt: {prompt_text}")
    
    playwright = None
    browser = None
    
    try:
        # Connect to existing Chrome
        playwright, browser = await connect_to_existing_chrome()
        
        # Find existing bolt.new page
        page = await find_bolt_page(browser)
        if not page:
            print("❌ Could not find bolt.new page")
            return
        
        # Inject prompt and submit
        success = await inject_prompt_and_submit(page, prompt_text)
        if not success:
            print("❌ Failed to inject prompt and submit")
            return
        
        # Monitor for response
        response_detected = await monitor_response(page)
        
        if response_detected:
            print("🎉 Automation completed successfully!")
            print("✅ Bolt is generating your response")
        else:
            print("⚠️  Automation completed but no clear response detected")
            print("💡 Check the browser window manually")
        
        # Keep the browser open for user to see results
        print("🌐 Browser will remain open for you to view the results")
        print("Press Enter to close the browser...")
        input()
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        
    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

if __name__ == "__main__":
    asyncio.run(main()) 