#!/usr/bin/env python3
"""
Cursor Collaboration Assistant
============================

A practical script to enable collaboration between Cursor instances through the MCP messaging system.

Usage:
    python cursor_collaboration_assistant.py poll          # Start polling for messages
    python cursor_collaboration_assistant.py send         # Send a message interactively
    python cursor_collaboration_assistant.py inbox        # View message inbox
    python cursor_collaboration_assistant.py agents       # List available agents
    python cursor_collaboration_assistant.py status       # Check system status
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
MCP_SERVER_URL = "http://localhost:8000"
POLL_INTERVAL = 30  # seconds
AUTO_RESPOND = True

class CursorCollaborationAssistant:
    def __init__(self, server_url: str = MCP_SERVER_URL):
        self.server_url = server_url
        self.session = requests.Session()
        self.running = False
        
    def call_mcp_tool(self, tool: str, operation: str = None, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an MCP tool via HTTP."""
        url = f"{self.server_url}/mcp/tools/{tool}"
        
        if tool == "messages":
            data = {"operation": operation}
            if payload:
                data["payload"] = payload
        else:
            data = payload or {}
            
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {e}"}
    
    def register_agent(self) -> bool:
        """Register this agent in the messaging system."""
        result = self.call_mcp_tool("messages", "register")
        if result.get("success"):
            agent_info = result["agent"]
            print(f"✅ Registered agent: {agent_info['agent_name']}")
            print(f"   Repo path: {agent_info['repo_path']}")
            if agent_info.get("github_url"):
                print(f"   GitHub: {agent_info['github_url']}")
            return True
        else:
            print(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
            return False
    
    def send_message_interactive(self):
        """Send a message with interactive prompts."""
        # First, list available agents
        agents_result = self.call_mcp_tool("messages", "agents")
        if agents_result.get("success") and agents_result.get("agents"):
            print("\n📋 Available agents:")
            for agent in agents_result["agents"]:
                print(f"   • {agent['agent_name']} ({agent.get('github_url', 'local')})")
        else:
            print("⚠️  No other agents found. Make sure other instances are registered.")
        
        print("\n✉️  Send Message")
        print("=" * 40)
        
        to = input("To (agent name): ").strip()
        if not to:
            print("❌ Recipient required")
            return
            
        subject = input("Subject: ").strip()
        if not subject:
            print("❌ Subject required")
            return
            
        print("Message (press Enter twice to finish):")
        message_lines = []
        while True:
            line = input()
            if line == "" and len(message_lines) > 0 and message_lines[-1] == "":
                break
            message_lines.append(line)
        
        # Remove trailing empty line
        if message_lines and message_lines[-1] == "":
            message_lines.pop()
            
        message = "\n".join(message_lines)
        if not message:
            print("❌ Message content required")
            return
        
        # Send the message
        result = self.call_mcp_tool("messages", "send", {
            "to": to,
            "subject": subject,
            "message": message
        })
        
        if result.get("success"):
            print(f"✅ Message sent! ID: {result['message_id']}")
        else:
            print(f"❌ Failed to send: {result.get('error', 'Unknown error')}")
    
    def view_inbox(self):
        """View message inbox with interactive options."""
        result = self.call_mcp_tool("messages", "list")
        
        if not result.get("success"):
            print(f"❌ Failed to load inbox: {result.get('error', 'Unknown error')}")
            return
        
        messages = result.get("message_summaries", [])
        unread_count = result.get("unread_count", 0)
        
        print(f"\n📬 Inbox ({len(messages)} messages, {unread_count} unread)")
        print("=" * 50)
        
        if not messages:
            print("   No messages found.")
            return
        
        for i, msg in enumerate(messages, 1):
            status = "🔴" if not msg["read"] else "✅"
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%m/%d %H:%M")
            print(f"{i:2d}. {status} From: {msg['from']:<15} | {timestamp} | {msg['subject']}")
        
        print("\nOptions:")
        print("  r <num> - Read message")
        print("  reply <num> - Reply to message")
        print("  delete <num> - Delete message")
        print("  q - Quit")
        
        while True:
            choice = input("\n> ").strip().lower()
            
            if choice == "q":
                break
            elif choice.startswith("r "):
                try:
                    msg_num = int(choice.split()[1])
                    if 1 <= msg_num <= len(messages):
                        self.read_message(messages[msg_num - 1]["id"])
                except (ValueError, IndexError):
                    print("❌ Invalid message number")
            elif choice.startswith("reply "):
                try:
                    msg_num = int(choice.split()[1])
                    if 1 <= msg_num <= len(messages):
                        self.reply_to_message(messages[msg_num - 1]["id"])
                except (ValueError, IndexError):
                    print("❌ Invalid message number")
            elif choice.startswith("delete "):
                try:
                    msg_num = int(choice.split()[1])
                    if 1 <= msg_num <= len(messages):
                        self.delete_message(messages[msg_num - 1]["id"])
                except (ValueError, IndexError):
                    print("❌ Invalid message number")
            else:
                print("❌ Unknown command")
    
    def read_message(self, message_id: int):
        """Read a specific message."""
        result = self.call_mcp_tool("messages", "get", {"id": message_id})
        
        if not result.get("success") or not result.get("messages"):
            print(f"❌ Failed to read message: {result.get('error', 'Message not found')}")
            return
        
        msg = result["messages"][0]
        
        print(f"\n📖 Message #{msg['id']}")
        print("=" * 50)
        print(f"From: {msg['from']}")
        print(f"To: {msg['to']}")
        print(f"Subject: {msg['subject']}")
        print(f"Date: {datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        if msg.get("reply_to"):
            print(f"Reply to: #{msg['reply_to']}")
        print()
        print(msg['message'])
        print()
    
    def reply_to_message(self, message_id: int):
        """Reply to a message."""
        print(f"\n💬 Reply to message #{message_id}")
        print("Message (press Enter twice to finish):")
        
        message_lines = []
        while True:
            line = input()
            if line == "" and len(message_lines) > 0 and message_lines[-1] == "":
                break
            message_lines.append(line)
        
        # Remove trailing empty line
        if message_lines and message_lines[-1] == "":
            message_lines.pop()
            
        message = "\n".join(message_lines)
        if not message:
            print("❌ Message content required")
            return
        
        result = self.call_mcp_tool("messages", "reply", {
            "reply_to": message_id,
            "message": message
        })
        
        if result.get("success"):
            print(f"✅ Reply sent! ID: {result['message_id']}")
        else:
            print(f"❌ Failed to reply: {result.get('error', 'Unknown error')}")
    
    def delete_message(self, message_id: int):
        """Delete a message."""
        confirm = input(f"Delete message #{message_id}? (y/N): ").strip().lower()
        if confirm == "y":
            result = self.call_mcp_tool("messages", "delete", {"id": message_id})
            if result.get("success"):
                print("✅ Message deleted")
            else:
                print(f"❌ Failed to delete: {result.get('error', 'Unknown error')}")
    
    def list_agents(self):
        """List all registered agents."""
        result = self.call_mcp_tool("messages", "agents")
        
        if not result.get("success"):
            print(f"❌ Failed to list agents: {result.get('error', 'Unknown error')}")
            return
        
        agents = result.get("agents", [])
        
        print(f"\n👥 Registered Agents ({len(agents)})")
        print("=" * 50)
        
        if not agents:
            print("   No agents registered.")
            return
        
        for agent in agents:
            print(f"🤖 {agent['agent_name']}")
            print(f"   Path: {agent['repo_path']}")
            if agent.get('github_url'):
                print(f"   GitHub: {agent['github_url']}")
            reg_time = datetime.fromisoformat(agent['registration_timestamp']).strftime('%Y-%m-%d %H:%M')
            print(f"   Registered: {reg_time}")
            if agent.get('last_active'):
                active_time = datetime.fromisoformat(agent['last_active']).strftime('%Y-%m-%d %H:%M')
                print(f"   Last active: {active_time}")
            print()
    
    def check_status(self):
        """Check system status."""
        print("🔍 System Status Check")
        print("=" * 30)
        
        # Check MCP server
        try:
            result = self.call_mcp_tool("server_info")
            if result.get("success"):
                print("✅ MCP Server: Running")
                print(f"   Version: {result.get('version', 'Unknown')}")
                print(f"   Uptime: {result.get('uptime', 'Unknown')}")
            else:
                print("❌ MCP Server: Error")
                print(f"   {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ MCP Server: Connection failed ({e})")
            return
        
        # Check messaging system
        try:
            agents_result = self.call_mcp_tool("messages", "agents")
            messages_result = self.call_mcp_tool("messages", "list")
            
            if agents_result.get("success") and messages_result.get("success"):
                agent_count = len(agents_result.get("agents", []))
                message_count = len(messages_result.get("message_summaries", []))
                unread_count = messages_result.get("unread_count", 0)
                
                print("✅ Messaging System: Active")
                print(f"   Agents: {agent_count}")
                print(f"   Messages: {message_count}")
                print(f"   Unread: {unread_count}")
            else:
                print("❌ Messaging System: Error")
        except Exception as e:
            print(f"❌ Messaging System: Failed ({e})")
    
    def poll_for_messages(self):
        """Poll for new messages continuously."""
        print(f"🔄 Starting message polling (interval: {POLL_INTERVAL}s)")
        print("Press Ctrl+C to stop")
        
        # Register agent first
        if not self.register_agent():
            return
        
        self.running = True
        last_check = None
        
        try:
            while self.running:
                # Check for new messages
                result = self.call_mcp_tool("messages", "get", {"unread_only": True})
                
                if result.get("success"):
                    messages = result.get("messages", [])
                    
                    if messages:
                        print(f"\n🔔 {len(messages)} new message(s) received!")
                        
                        for msg in messages:
                            print(f"\n📩 New message from {msg['from']}")
                            print(f"   Subject: {msg['subject']}")
                            print(f"   Preview: {msg['message'][:100]}...")
                            
                            # Auto-respond to certain message types
                            if AUTO_RESPOND:
                                self.auto_respond(msg)
                    
                    last_check = datetime.now()
                
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping message polling")
            self.running = False
    
    def auto_respond(self, message: Dict[str, Any]):
        """Auto-respond to certain types of messages."""
        subject = message["subject"].lower()
        content = message["message"].lower()
        
        # Auto-acknowledge certain message types
        if any(keyword in subject for keyword in ["urgent", "help", "emergency"]):
            reply = "I've received your urgent message and will prioritize it. Working on it now!"
            
            result = self.call_mcp_tool("messages", "reply", {
                "reply_to": message["id"],
                "message": reply
            })
            
            if result.get("success"):
                print(f"   🤖 Auto-replied to urgent message")
        
        elif "status" in subject or "ping" in content:
            reply = "System status: Online and ready for collaboration!"
            
            result = self.call_mcp_tool("messages", "reply", {
                "reply_to": message["id"],
                "message": reply
            })
            
            if result.get("success"):
                print(f"   🤖 Auto-replied to status check")

def main():
    parser = argparse.ArgumentParser(description="Cursor Collaboration Assistant")
    parser.add_argument("command", choices=["poll", "send", "inbox", "agents", "status"], 
                       help="Command to execute")
    parser.add_argument("--server", default=MCP_SERVER_URL, 
                       help="MCP server URL")
    
    args = parser.parse_args()
    
    assistant = CursorCollaborationAssistant(args.server)
    
    if args.command == "poll":
        assistant.poll_for_messages()
    elif args.command == "send":
        assistant.register_agent()
        assistant.send_message_interactive()
    elif args.command == "inbox":
        assistant.register_agent()
        assistant.view_inbox()
    elif args.command == "agents":
        assistant.list_agents()
    elif args.command == "status":
        assistant.check_status()

if __name__ == "__main__":
    main() 