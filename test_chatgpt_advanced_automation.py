#!/usr/bin/env python3
"""
Test script for Advanced ChatGPT automation using the same technique as Bolt.new
"""

import asyncio
import sys
sys.path.append('.')
import mcp_server

async def test_advanced_chatgpt_automation():
    """Test the advanced ChatGPT automation with React bypass technique"""
    print("🚀 Testing Advanced ChatGPT Automation")
    print("=" * 50)
    
    # Test 1: Check Chrome tabs
    print("\n1️⃣ Checking Chrome tabs...")
    tabs_result = mcp_server.get_chrome_tabs()
    
    if not tabs_result.get("success"):
        print(f"❌ Failed to get Chrome tabs: {tabs_result.get('error')}")
        return False
    
    print(f"✅ Found {len(tabs_result.get('tabs', []))} Chrome tabs")
    
    # Test 2: Check for ChatGPT tab
    print("\n2️⃣ Looking for ChatGPT tab...")
    chatgpt_tabs = []
    for tab in tabs_result.get("tabs", []):
        url = tab.get("url", "")
        if 'chat.openai.com' in url or 'chatgpt.com' in url:
            chatgpt_tabs.append(tab)
    
    if not chatgpt_tabs:
        print("❌ No ChatGPT tab found. Please:")
        print("   - Open https://chat.openai.com/ or https://chatgpt.com/")
        print("   - Make sure you're logged in")
        return False
    
    print(f"✅ Found {len(chatgpt_tabs)} ChatGPT tab(s)")
    for tab in chatgpt_tabs:
        print(f"   • {tab.get('title', 'Unknown')} - {tab.get('url', '')[:50]}...")
    
    # Test 3: Test prompt injection using advanced technique
    print("\n3️⃣ Testing advanced prompt injection...")
    test_prompt = "Please respond with exactly: 'Advanced ChatGPT automation test successful!'"
    
    automation_result = mcp_server.tell_chatgpt_to(test_prompt)
    
    if automation_result.get("success"):
        print("✅ Advanced automation successful!")
        print(f"   Message: {automation_result.get('message')}")
    else:
        print(f"❌ Automation failed: {automation_result.get('error')}")
        return False
    
    # Test 4: Wait and extract response
    print("\n4️⃣ Waiting for ChatGPT response...")
    print("   (Waiting 5 seconds for response generation...)")
    await asyncio.sleep(5)
    
    response_result = mcp_server.get_chatgpt_response()
    
    if response_result.get("success"):
        response_text = response_result.get("response", "")
        print("✅ Response extracted successfully!")
        print(f"   Length: {response_result.get('length')} characters")
        print(f"   Preview: {response_result.get('preview')}")
        
        # Check if response contains expected phrase
        expected_phrase = "Advanced ChatGPT automation test successful!"
        if expected_phrase.lower() in response_text.lower():
            print("🎯 Response contains expected test phrase!")
        else:
            print("⚠️ Response doesn't contain expected phrase (this is normal)")
            print("   This might be due to ChatGPT's response variation")
    else:
        print(f"❌ Failed to extract response: {response_result.get('error')}")
        return False
    
    print("\n🎉 Advanced ChatGPT Automation Test Complete!")
    return True

async def demo_advanced_conversation():
    """Demonstrate the advanced ChatGPT automation with a multi-turn conversation"""
    print("\n🎭 Advanced ChatGPT Conversation Demo")
    print("=" * 40)
    
    conversation_prompts = [
        "Hello! What is the capital of France?",
        "What's the population of that city?",
        "Tell me one interesting fact about it."
    ]
    
    for i, prompt in enumerate(conversation_prompts, 1):
        print(f"\n💬 Turn {i}: Sending prompt...")
        print(f"   Prompt: {prompt}")
        
        # Send prompt using advanced automation
        result = mcp_server.tell_chatgpt_to(prompt)
        
        if result.get("success"):
            print("✅ Prompt sent successfully")
        else:
            print(f"❌ Failed to send prompt: {result.get('error')}")
            continue
        
        # Wait for response
        print("   ⏳ Waiting for response...")
        await asyncio.sleep(4)
        
        # Extract response
        response_result = mcp_server.get_chatgpt_response()
        
        if response_result.get("success"):
            print(f"📖 Response: {response_result.get('preview')}")
        else:
            print(f"❌ Failed to get response: {response_result.get('error')}")
        
        # Brief pause between turns
        if i < len(conversation_prompts):
            await asyncio.sleep(2)
    
    print("\n🎭 Advanced Conversation Demo Complete!")

async def main():
    print("🧪 Advanced ChatGPT Automation Test Suite")
    print("Using the same React bypass technique as Bolt.new")
    print("=" * 60)
    
    # Run basic test
    print("\n🔧 BASIC AUTOMATION TEST")
    basic_success = await test_advanced_chatgpt_automation()
    
    if basic_success:
        print("\n🎯 CONVERSATION DEMO")
        await demo_advanced_conversation()
    else:
        print("\n❌ Basic test failed - skipping conversation demo")
        print("\nTroubleshooting:")
        print("1. Ensure ChatGPT tab is open and logged in")
        print("2. Refresh the ChatGPT page to load the content script")
        print("3. Check browser console for any errors")
        print("4. Verify the MCP server is running")

if __name__ == "__main__":
    asyncio.run(main()) 