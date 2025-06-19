#!/usr/bin/env python3
"""
Test script for Python migration approach.
Verifies that the service manager can handle both JavaScript and Python implementations.
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from service_manager import ServiceManager
from check_services import ServiceChecker

def test_service_manager():
    """Test the service manager functionality"""
    print("🧪 Testing Python Service Manager")
    print("=" * 50)
    
    # Initialize service manager
    manager = ServiceManager()
    
    # Test status checking
    print("\n📊 Current Service Status:")
    manager.print_service_status()
    
    # Test environment switching
    print(f"\n🔄 Current Socket.IO Implementation: {os.getenv('SOCKETIO_IMPLEMENTATION', 'javascript')}")
    
    return True

def test_service_checker():
    """Test the service checker functionality"""
    print("\n🔍 Testing Service Checker")
    print("=" * 30)
    
    checker = ServiceChecker()
    
    # Test quick status
    status = checker.service_manager.get_service_status()
    all_running = all(info["running"] for info in status.values())
    
    if all_running:
        checker.print_status("All services running", "success")
    else:
        checker.print_status("Some services not running", "warning")
        for name, info in status.items():
            if not info["running"]:
                checker.print_status(f"{name} is not running", "error")
    
    return True

def test_environment_switching():
    """Test environment-based implementation switching"""
    print("\n🔀 Testing Environment Switching")
    print("=" * 40)
    
    # Show current environment
    print("Current Environment Variables:")
    print(f"  SOCKETIO_IMPLEMENTATION: {os.getenv('SOCKETIO_IMPLEMENTATION', 'javascript')}")
    print(f"  MCP_IMPLEMENTATION: {os.getenv('MCP_IMPLEMENTATION', 'python')}")
    print(f"  SOCKETIO_PORT: {os.getenv('SOCKETIO_PORT', '3001')}")
    
    # Test service configuration loading
    manager = ServiceManager()
    socketio_config = manager.service_configs.get("socketio")
    
    if socketio_config:
        print(f"\nSocket.IO Configuration:")
        print(f"  Implementation: {socketio_config.implementation.value}")
        print(f"  Command: {' '.join(socketio_config.command)}")
        print(f"  Port: {socketio_config.port}")
        print(f"  Log File: {socketio_config.log_file}")
    
    return True

def test_cross_platform_compatibility():
    """Test cross-platform features"""
    print("\n🌍 Testing Cross-Platform Compatibility")
    print("=" * 45)
    
    import platform
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Test path handling
    from pathlib import Path
    test_path = Path.cwd() / "logs"
    print(f"Logs directory: {test_path}")
    print(f"Logs directory exists: {test_path.exists()}")
    
    # Test process detection (cross-platform)
    try:
        import psutil
        print(f"psutil available: {psutil.__version__}")
        
        # Test process listing
        python_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                          if 'python' in p.info['name'].lower()]
        print(f"Python processes found: {len(python_processes)}")
        
    except ImportError:
        print("psutil not available - install with: pip install psutil")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Python Migration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Service Manager", test_service_manager),
        ("Service Checker", test_service_checker), 
        ("Environment Switching", test_environment_switching),
        ("Cross-Platform Compatibility", test_cross_platform_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result, None))
            print(f"✅ {test_name}: PASSED")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ {test_name}: FAILED - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"    Error: {error}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Python migration approach is working.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test service manager: python service_manager.py status")
        print("3. Test service checker: python check_services.py")
        print("4. Switch to Python Socket.IO: export SOCKETIO_IMPLEMENTATION=python")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 