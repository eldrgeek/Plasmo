#!/usr/bin/env python3
"""
MCP Server Test Automation
==========================

This script demonstrates advanced testing capabilities using the MCP server
for Chrome Debug Protocol automation.
"""

import requests
import json
import time
from datetime import datetime

class MCPTestAutomation:
    def __init__(self, mcp_base_url="http://127.0.0.1:8000"):
        self.mcp_base_url = mcp_base_url
        self.connection_id = "localhost:9222"
        self.tab_id = None
        
    def call_mcp_tool(self, tool_name, **params):
        """Call an MCP server tool"""
        url = f"{self.mcp_base_url}/tools/{tool_name}"
        try:
            response = requests.post(url, json=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ MCP Tool Error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ MCP Connection Error: {e}")
            return {"success": False, "error": str(e)}
    
    def step_1_get_tabs(self):
        """Step 1: Get available Chrome tabs"""
        print("📋 Step 1: Getting Chrome tabs...")
        result = self.call_mcp_tool("get_chrome_tabs", connection_id=self.connection_id)
        
        if result.get("success"):
            tabs = result.get("tabs", [])
            print(f"✅ Found {len(tabs)} debuggable tabs")
            for tab in tabs:
                print(f"  📄 {tab['title'][:50]}... - {tab['url'][:60]}")
                if "test_page.html" in tab['url']:
                    self.tab_id = tab['id']
                    print(f"  🎯 Using tab ID: {self.tab_id}")
            return True
        else:
            print(f"❌ Failed to get tabs: {result.get('error')}")
            return False
    
    def step_2_basic_javascript(self):
        """Step 2: Execute basic JavaScript tests"""
        print("\n📋 Step 2: Running basic JavaScript tests...")
        
        tests = [
            ("Math test", "2 + 2 === 4"),
            ("String test", "'hello'.toUpperCase() === 'HELLO'"),
            ("Array test", "[1,2,3].length === 3"),
            ("Date test", "new Date().getFullYear() > 2020"),
            ("DOM test", "document.getElementById('results') !== null")
        ]
        
        passed = 0
        for test_name, expression in tests:
            result = self.call_mcp_tool(
                "execute_javascript_fixed",
                code=f"({expression}) ? 'PASS' : 'FAIL'",
                tab_id=self.tab_id,
                connection_id=self.connection_id
            )
            
            if result.get("success"):
                test_result = result.get("value", "UNKNOWN")
                if test_result == "PASS":
                    print(f"  ✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"  ❌ {test_name}: FAILED")
            else:
                print(f"  ❌ {test_name}: ERROR - {result.get('error')}")
        
        print(f"📊 Basic tests: {passed}/{len(tests)} passed")
        return passed == len(tests)
    
    def step_3_test_framework_integration(self):
        """Step 3: Use the built-in test framework"""
        print("\n📋 Step 3: Running test framework integration...")
        
        # First, check if test framework is available
        result = self.call_mcp_tool(
            "execute_javascript_fixed",
            code="typeof window.testRunner",
            tab_id=self.tab_id,
            connection_id=self.connection_id
        )
        
        if result.get("value") != "object":
            print("❌ Test framework not available")
            return False
        
        # Run the full test suite
        result = self.call_mcp_tool(
            "execute_javascript_fixed",
            code="""
            (async () => {
                const results = await window.testRunner.run();
                return {
                    total: results.length,
                    passed: results.filter(r => r.status === 'PASS').length,
                    failed: results.filter(r => r.status === 'FAIL').length,
                    details: results.map(r => ({name: r.name, status: r.status, error: r.error}))
                };
            })()
            """,
            tab_id=self.tab_id,
            connection_id=self.connection_id
        )
        
        if result.get("success"):
            test_data = result.get("value", {})
            if isinstance(test_data, dict):
                print(f"✅ Test suite completed:")
                print(f"  📊 Total: {test_data.get('total', 0)}")
                print(f"  ✅ Passed: {test_data.get('passed', 0)}")
                print(f"  ❌ Failed: {test_data.get('failed', 0)}")
                
                for detail in test_data.get('details', []):
                    status_icon = "✅" if detail['status'] == 'PASS' else "❌"
                    error_info = f" - {detail.get('error', '')}" if detail.get('error') else ""
                    print(f"    {status_icon} {detail['name']}{error_info}")
                
                return test_data.get('failed', 1) == 0
            else:
                print(f"✅ Test suite result: {test_data}")
                return True
        else:
            print(f"❌ Test framework execution failed: {result.get('error')}")
            return False
    
    def step_4_performance_monitoring(self):
        """Step 4: Monitor page performance"""
        print("\n📋 Step 4: Monitoring page performance...")
        
        # Get page performance metrics
        result = self.call_mcp_tool(
            "execute_javascript_fixed",
            code="""
            {
                memory: performance.memory ? {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                } : null,
                timing: {
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domReady: performance.timing.domComplete - performance.timing.navigationStart
                },
                navigation: {
                    type: performance.navigation.type,
                    redirectCount: performance.navigation.redirectCount
                }
            }
            """,
            tab_id=self.tab_id,
            connection_id=self.connection_id
        )
        
        if result.get("success"):
            perf_data = result.get("value", {})
            print("✅ Performance metrics collected:")
            
            if perf_data.get("memory"):
                mem = perf_data["memory"]
                print(f"  🧠 Memory: {mem['used']:,} / {mem['total']:,} bytes")
            
            timing = perf_data.get("timing", {})
            print(f"  ⏱️  DOM Content Loaded: {timing.get('domContentLoaded', 0)}ms")
            print(f"  ⏱️  Load Complete: {timing.get('loadComplete', 0)}ms")
            
            return True
        else:
            print(f"❌ Performance monitoring failed: {result.get('error')}")
            return False
    
    def step_5_error_simulation(self):
        """Step 5: Test error handling"""
        print("\n📋 Step 5: Testing error handling...")
        
        # Simulate an error and check console
        result = self.call_mcp_tool(
            "execute_javascript_fixed",
            code="""
            try {
                // Intentionally cause an error
                console.error('🧪 Simulated error for testing');
                throw new Error('Test error from MCP automation');
            } catch(e) {
                console.log('✅ Error caught successfully:', e.message);
                return 'Error handling works: ' + e.message;
            }
            """,
            tab_id=self.tab_id,
            connection_id=self.connection_id
        )
        
        if result.get("success"):
            error_result = result.get("value", "")
            if "Error handling works" in str(error_result):
                print("✅ Error simulation and handling successful")
                return True
            else:
                print(f"❌ Unexpected error result: {error_result}")
                return False
        else:
            print(f"❌ Error simulation failed: {result.get('error')}")
            return False
    
    def step_6_final_report(self):
        """Step 6: Generate final test report"""
        print("\n📋 Step 6: Generating final test report...")
        
        # Get final page state
        result = self.call_mcp_tool(
            "execute_javascript_fixed",
            code="""
            {
                title: document.title,
                url: window.location.href,
                elements: document.querySelectorAll('*').length,
                scripts: document.querySelectorAll('script').length,
                timestamp: new Date().toISOString(),
                testFrameworkAvailable: typeof window.testRunner !== 'undefined',
                consoleErrors: console.memory ? 'Console API available' : 'Console limited'
            }
            """,
            tab_id=self.tab_id,
            connection_id=self.connection_id
        )
        
        if result.get("success"):
            report = result.get("value", {})
            print("📊 Final Test Report:")
            print(f"  📄 Page: {report.get('title', 'Unknown')}")
            print(f"  🌐 URL: {report.get('url', 'Unknown')}")
            print(f"  🏗️  DOM Elements: {report.get('elements', 0)}")
            print(f"  📜 Scripts: {report.get('scripts', 0)}")
            print(f"  🧪 Test Framework: {'✅ Available' if report.get('testFrameworkAvailable') else '❌ Not found'}")
            print(f"  ⏰ Timestamp: {report.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"❌ Report generation failed: {result.get('error')}")
            return False
    
    def run_full_automation_suite(self):
        """Run the complete test automation suite"""
        print("🚀 MCP Server Test Automation Suite Starting")
        print("=" * 60)
        
        start_time = time.time()
        results = []
        
        # Run all test steps
        steps = [
            ("Get Chrome Tabs", self.step_1_get_tabs),
            ("Basic JavaScript Tests", self.step_2_basic_javascript),
            ("Test Framework Integration", self.step_3_test_framework_integration),
            ("Performance Monitoring", self.step_4_performance_monitoring),
            ("Error Handling", self.step_5_error_simulation),
            ("Final Report", self.step_6_final_report)
        ]
        
        for step_name, step_func in steps:
            print(f"\n⭐ Executing: {step_name}")
            try:
                success = step_func()
                results.append((step_name, success))
                print(f"{'✅' if success else '❌'} {step_name}: {'PASSED' if success else 'FAILED'}")
            except Exception as e:
                print(f"❌ {step_name}: EXCEPTION - {e}")
                results.append((step_name, False))
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print("\n🎉 MCP Server Test Automation Complete!")
        print("=" * 60)
        print(f"📊 Results: {passed}/{total} steps passed")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for step_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {step_name}")
        
        return passed == total

if __name__ == "__main__":
    automation = MCPTestAutomation()
    success = automation.run_full_automation_suite()
    exit(0 if success else 1)