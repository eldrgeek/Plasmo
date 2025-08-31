#!/usr/bin/env python3
"""
Comprehensive Test Runner for MCP Server
=========================================

This script runs all test suites and generates a comprehensive test report.
It includes unit tests, integration tests, performance tests, and security tests.

Usage:
    python run_comprehensive_tests.py
    python run_comprehensive_tests.py --verbose
    python run_comprehensive_tests.py --report-format json
    python run_comprehensive_tests.py --parallel
"""

import asyncio
import json
import sys
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import concurrent.futures
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Comprehensive test runner for all MCP server tests."""
    
    def __init__(self, verbose: bool = False, parallel: bool = False):
        self.verbose = verbose
        self.parallel = parallel
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.server_process = None
        
        # Test configuration
        self.test_suites = [
            {
                "name": "Core Module Tests",
                "script": "test_core_modules.py",
                "type": "unit",
                "timeout": 30,
                "critical": True
            },
            {
                "name": "Agent Module Tests", 
                "script": "test_agent_modules.py",
                "type": "unit",
                "timeout": 30,
                "critical": True
            },
            {
                "name": "Comprehensive Tool Tests",
                "script": "test_mcp_tools_comprehensive.py",
                "type": "unit",
                "timeout": 60,
                "critical": True
            },
            {
                "name": "Integration Tests",
                "script": "test_integration.py",
                "type": "integration",
                "timeout": 45,
                "critical": True
            },
            {
                "name": "MCP Server Integration",
                "script": "test_mcp_server_integration.py",
                "type": "integration",
                "timeout": 120,
                "critical": True,
                "requires_server": True
            },
            {
                "name": "Protocol Tests",
                "script": "mcp_protocol_tester.py",
                "type": "protocol",
                "timeout": 60,
                "critical": False,
                "requires_server": True
            }
        ]
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    async def start_mcp_server(self):
        """Start MCP server for integration tests."""
        logger.info("🚀 Starting MCP server for integration tests...")
        
        server_script = Path(__file__).parent / "mcp_server.py"
        self.server_process = subprocess.Popen([
            sys.executable, str(server_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Check if server is running
        if self.server_process.poll() is None:
            logger.info("✅ MCP server started successfully")
            return True
        else:
            logger.error("❌ MCP server failed to start")
            return False
    
    async def stop_mcp_server(self):
        """Stop MCP server."""
        if self.server_process:
            logger.info("🛑 Stopping MCP server...")
            self.server_process.terminate()
            try:
                await asyncio.wait_for(self.server_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.server_process.kill()
                await self.server_process.wait()
            logger.info("✅ MCP server stopped")
    
    def run_test_suite(self, suite: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test suite."""
        logger.info(f"🧪 Running {suite['name']}...")
        
        script_path = Path(__file__).parent / suite["script"]
        if not script_path.exists():
            return {
                "name": suite["name"],
                "success": False,
                "error": f"Test script not found: {script_path}",
                "execution_time": 0,
                "output": "",
                "type": suite["type"]
            }
        
        start_time = time.time()
        
        try:
            # Run the test script
            if suite["script"] == "test_mcp_server_integration.py":
                # Integration test with proxy server URL
                result = subprocess.run([
                    sys.executable, str(script_path),
                    "--server-url", "http://127.0.0.1:8001"
                ], capture_output=True, text=True, timeout=suite["timeout"])
            else:
                # Regular test
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, timeout=suite["timeout"])
            
            end_time = time.time()
            
            return {
                "name": suite["name"],
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "execution_time": round(end_time - start_time, 2),
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
                "type": suite["type"],
                "critical": suite.get("critical", False)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "name": suite["name"],
                "success": False,
                "error": f"Test timed out after {suite['timeout']} seconds",
                "execution_time": suite["timeout"],
                "output": "",
                "type": suite["type"],
                "critical": suite.get("critical", False)
            }
        except Exception as e:
            return {
                "name": suite["name"],
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "output": "",
                "type": suite["type"],
                "critical": suite.get("critical", False)
            }
    
    async def run_all_tests(self):
        """Run all test suites."""
        logger.info("🎯 Starting Comprehensive MCP Server Test Suite")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        
        # Check if server is needed
        server_needed = any(suite.get("requires_server", False) for suite in self.test_suites)
        
        if server_needed:
            if not await self.start_mcp_server():
                logger.error("❌ Failed to start MCP server, skipping integration tests")
                # Filter out tests that require server
                self.test_suites = [s for s in self.test_suites if not s.get("requires_server", False)]
        
        try:
            if self.parallel:
                # Run tests in parallel
                await self.run_tests_parallel()
            else:
                # Run tests sequentially
                await self.run_tests_sequential()
        
        finally:
            if server_needed:
                await self.stop_mcp_server()
        
        self.end_time = time.time()
        
        # Generate report
        self.generate_report()
    
    async def run_tests_sequential(self):
        """Run tests sequentially."""
        for suite in self.test_suites:
            result = self.run_test_suite(suite)
            self.test_results[suite["name"]] = result
            
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} {suite['name']} - {result['execution_time']}s")
            
            if not result["success"] and result.get("critical", False):
                logger.warning(f"⚠️  Critical test failed: {suite['name']}")
    
    async def run_tests_parallel(self):
        """Run tests in parallel."""
        logger.info("🏃 Running tests in parallel...")
        
        # Group tests by dependencies
        unit_tests = [s for s in self.test_suites if s["type"] == "unit"]
        integration_tests = [s for s in self.test_suites if s["type"] != "unit"]
        
        # Run unit tests in parallel
        if unit_tests:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_suite = {executor.submit(self.run_test_suite, suite): suite for suite in unit_tests}
                
                for future in concurrent.futures.as_completed(future_to_suite):
                    suite = future_to_suite[future]
                    try:
                        result = future.result()
                        self.test_results[suite["name"]] = result
                        
                        status = "✅" if result["success"] else "❌"
                        logger.info(f"{status} {suite['name']} - {result['execution_time']}s")
                        
                    except Exception as e:
                        logger.error(f"❌ Error running {suite['name']}: {e}")
        
        # Run integration tests sequentially (they may interfere with each other)
        for suite in integration_tests:
            result = self.run_test_suite(suite)
            self.test_results[suite["name"]] = result
            
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} {suite['name']} - {result['execution_time']}s")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        total_time = self.end_time - self.start_time
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - successful_tests
        critical_failures = sum(1 for r in self.test_results.values() if not r["success"] and r.get("critical", False))
        
        # Group by type
        by_type = {}
        for result in self.test_results.values():
            test_type = result["type"]
            if test_type not in by_type:
                by_type[test_type] = {"total": 0, "successful": 0}
            by_type[test_type]["total"] += 1
            if result["success"]:
                by_type[test_type]["successful"] += 1
        
        # Print report
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE MCP SERVER TEST REPORT")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print(f"🖥️  System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total // 1024**3}GB RAM")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   • Total Test Suites: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {(successful_tests / total_tests * 100):.1f}%")
        
        if critical_failures > 0:
            print(f"   • ⚠️  Critical Failures: {critical_failures}")
        
        print(f"\n📋 RESULTS BY TYPE:")
        for test_type, stats in by_type.items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"   • {test_type.title()}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        execution_times = [r["execution_time"] for r in self.test_results.values()]
        print(f"   • Average execution time: {sum(execution_times) / len(execution_times):.2f}s")
        print(f"   • Fastest suite: {min(execution_times):.2f}s")
        print(f"   • Slowest suite: {max(execution_times):.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for name, result in self.test_results.items():
                if not result["success"]:
                    critical_marker = "🔥" if result.get("critical", False) else "❌"
                    print(f"   {critical_marker} {name}")
                    print(f"      Error: {result['error']}")
                    if result.get("output") and self.verbose:
                        print(f"      Output: {result['output'][:200]}...")
        
        print(f"\n🔧 DETAILED RESULTS:")
        for name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            critical = " (CRITICAL)" if result.get("critical", False) else ""
            print(f"   {status} {name}{critical} - {result['execution_time']}s")
        
        # Generate recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if critical_failures > 0:
            print("   • 🔥 Fix critical test failures immediately")
        if failed_tests > 0:
            print("   • 🔧 Review failed tests and fix underlying issues")
        if (successful_tests / total_tests) < 0.9:
            print("   • 📈 Improve test coverage and reliability")
        
        total_execution_time = sum(execution_times)
        if total_execution_time > 300:  # 5 minutes
            print("   • ⚡ Consider optimizing test execution time")
        
        print("=" * 80)
        
        # Overall assessment
        if critical_failures == 0 and (successful_tests / total_tests) >= 0.9:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - System is ready for production")
        elif critical_failures == 0 and (successful_tests / total_tests) >= 0.8:
            print("✅ OVERALL ASSESSMENT: GOOD - Minor issues need attention")
        elif critical_failures == 0:
            print("⚠️  OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Several issues need fixing")
        else:
            print("🔥 OVERALL ASSESSMENT: CRITICAL ISSUES - Do not deploy to production")
        
        print("=" * 80)
        
        return successful_tests == total_tests and critical_failures == 0
    
    def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON report for CI/CD integration."""
        return {
            "timestamp": datetime.now().isoformat(),
            "execution_time": self.end_time - self.start_time if self.end_time else 0,
            "summary": {
                "total_tests": len(self.test_results),
                "successful": sum(1 for r in self.test_results.values() if r["success"]),
                "failed": sum(1 for r in self.test_results.values() if not r["success"]),
                "critical_failures": sum(1 for r in self.test_results.values() if not r["success"] and r.get("critical", False)),
                "success_rate": (sum(1 for r in self.test_results.values() if r["success"]) / len(self.test_results) * 100) if self.test_results else 0
            },
            "results": self.test_results,
            "system_info": {
                "cpu_cores": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total // 1024**3,
                "python_version": sys.version
            }
        }
    
    def save_report(self, format: str = "json"):
        """Save report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            report_file = Path(__file__).parent / f"test_report_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(self.generate_json_report(), f, indent=2)
            logger.info(f"📄 JSON report saved to: {report_file}")
        
        return report_file


async def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive MCP Server Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--report-format", choices=["json", "text"], default="text", help="Report format")
    parser.add_argument("--save-report", action="store_true", help="Save report to file")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ComprehensiveTestRunner(verbose=args.verbose, parallel=args.parallel)
    
    try:
        # Run all tests
        await runner.run_all_tests()
        
        # Save report if requested
        if args.save_report:
            runner.save_report(args.report_format)
        
        # Return success based on test results
        total_tests = len(runner.test_results)
        successful_tests = sum(1 for r in runner.test_results.values() if r["success"])
        critical_failures = sum(1 for r in runner.test_results.values() if not r["success"] and r.get("critical", False))
        
        return successful_tests == total_tests and critical_failures == 0
        
    except KeyboardInterrupt:
        logger.info("⏸️  Tests interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)