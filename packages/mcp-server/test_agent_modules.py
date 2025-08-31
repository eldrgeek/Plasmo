#!/usr/bin/env python3
"""
Test script for the new agent management modules.

This script tests the functionality of the modular agent management system
to ensure all components work correctly.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the agent modules
from agents.agent_management import (
    get_agent_name, register_agent, set_custom_agent_name, get_custom_agent_name,
    get_agent_registration, list_registered_agents, get_agent_stats
)
from agents.messaging import (
    create_message, get_messages, mark_message_read, delete_message,
    list_message_summaries, get_message_by_id, search_messages,
    get_message_thread, get_message_stats
)
from agents.notifications import (
    send_notification, get_pending_notifications, clear_notifications,
    set_cancel_flag, check_cancel_flag, clear_cancel_flag,
    get_notification_stats
)
from agents.claude_instances import (
    launch_claude_instance, list_claude_instances, coordinate_claude_instances,
    get_instance_stats
)


def test_agent_management():
    """Test agent management functionality."""
    print("Testing Agent Management...")
    
    # Test basic agent name functionality
    original_name = get_agent_name()
    print(f"  Original agent name: {original_name}")
    
    # Test custom name
    set_custom_agent_name("TestAgent")
    custom_name = get_agent_name()
    print(f"  Custom agent name: {custom_name}")
    assert custom_name == "TestAgent"
    
    # Test registration
    registration = register_agent()
    print(f"  Registration successful: {registration['name']}")
    assert registration['name'] == "TestAgent"
    
    # Test listing agents
    agents = list_registered_agents()
    print(f"  Registered agents: {len(agents)}")
    assert len(agents) >= 1
    
    # Test agent stats
    stats = get_agent_stats()
    print(f"  Agent stats: {stats}")
    
    print("  ✅ Agent management tests passed!")


def test_messaging():
    """Test messaging functionality."""
    print("\nTesting Messaging...")
    
    # Create a test message
    message = create_message(
        to="TestAgent",
        subject="Test Message",
        message="This is a test message"
    )
    print(f"  Created message: {message['id']}")
    
    # Get messages
    messages = get_messages("TestAgent")
    print(f"  Retrieved {len(messages)} messages")
    assert len(messages) >= 1
    
    # Test message by ID
    retrieved_message = get_message_by_id(message['id'])
    print(f"  Retrieved message by ID: {retrieved_message['subject']}")
    assert retrieved_message['subject'] == "Test Message"
    
    # Test message summaries
    summaries = list_message_summaries("TestAgent")
    print(f"  Message summaries: {len(summaries)}")
    
    # Test search
    search_results = search_messages("TestAgent", "test")
    print(f"  Search results: {len(search_results)}")
    
    # Test message stats
    stats = get_message_stats("TestAgent")
    print(f"  Message stats: {stats}")
    
    print("  ✅ Messaging tests passed!")


def test_notifications():
    """Test notification functionality."""
    print("\nTesting Notifications...")
    
    # Send a notification
    notification = send_notification("TestAgent", "Test notification")
    print(f"  Sent notification: {notification['id']}")
    
    # Get pending notifications
    notifications = get_pending_notifications("TestAgent")
    print(f"  Pending notifications: {len(notifications)}")
    assert len(notifications) >= 1
    
    # Test cancel flags
    set_cancel_flag("TestAgent")
    has_flag = check_cancel_flag("TestAgent")
    print(f"  Cancel flag set: {has_flag}")
    assert has_flag is True
    
    clear_cancel_flag("TestAgent")
    has_flag = check_cancel_flag("TestAgent")
    print(f"  Cancel flag cleared: {not has_flag}")
    assert has_flag is False
    
    # Test notification stats
    stats = get_notification_stats("TestAgent")
    print(f"  Notification stats: {stats}")
    
    # Clear notifications
    cleared_count = clear_notifications("TestAgent")
    print(f"  Cleared {cleared_count} notifications")
    
    print("  ✅ Notification tests passed!")


def test_claude_instances():
    """Test Claude instance management."""
    print("\nTesting Claude Instances...")
    
    # Test instance stats (should work even without implementation)
    stats = get_instance_stats()
    print(f"  Instance stats: {stats}")
    
    # Test listing instances
    instances = list_claude_instances()
    print(f"  List instances result: {instances.get('success', False)}")
    
    # Test launching (will likely fail without implementation)
    launch_result = launch_claude_instance("tester")
    print(f"  Launch result: {launch_result.get('success', False)}")
    
    # Test coordination
    coord_result = coordinate_claude_instances("Test task")
    print(f"  Coordination result: {coord_result.get('success', False)}")
    
    print("  ✅ Claude instance tests completed!")


def run_all_tests():
    """Run all tests."""
    print("🧪 Running Agent Module Tests")
    print("=" * 50)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Set up test environment
        os.environ['MESSAGES_ROOT'] = str(temp_path / "messages")
        
        try:
            test_agent_management()
            test_messaging()
            test_notifications()
            test_claude_instances()
            
            print("\n" + "=" * 50)
            print("🎉 All tests completed!")
            print("✅ Agent management modules are working correctly!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    run_all_tests()