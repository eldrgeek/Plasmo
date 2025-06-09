#!/usr/bin/env python3
"""
Test-Driven Development Suite for Multi-LLM Orchestration
========================================================

TDD test suite that integrates with continuous_test_runner.py for:
- Phase 1: MCP ↔ Socket.IO Bridge tests
- Phase 2: AI Service Content Scripts tests  
- Phase 3: End-to-End Integration tests
- Phase 4: Documentation & Refinement tests

Usage:
    python test_orchestration_tdd.py              # Run all tests
    python test_orchestration_tdd.py --phase 1    # Run specific phase
"""

import json
import os
import time
import unittest
from pathlib import Path
from typing import Dict, List, Any
import requests
import argparse
import sys
from datetime import datetime

class OrchestrationTDDTester:
    """TDD test suite for orchestration project."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.socketio_server = "http://localhost:3001"
        self.chrome_debug_port = 9222
        self.mcp_server_port = 8000
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        if self.verbose or level in ["ERROR", "FAIL", "PASS"]:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    # Phase 1: MCP ↔ Socket.IO Bridge Tests
    def test_phase1_prerequisites(self) -> Dict[str, Any]:
        """Test Phase 1 prerequisites."""
        self.log("🧪 Testing Phase 1 Prerequisites...")
        results = {}
        
        # Test MCP server is functional
        try:
            import mcp_server
            results["mcp_server_module"] = {"status": "PASS", "message": "MCP server module available"}
            self.log("  ✅ MCP server module: PASS", "PASS")
        except ImportError as e:
            results["mcp_server_module"] = {"status": "FAIL", "message": f"MCP server module missing: {e}"}
            self.log(f"  ❌ MCP server module: FAIL - {e}", "FAIL")
        
        # Test Socket.IO server accessibility
        try:
            response = requests.get(f"{self.socketio_server}/health", timeout=2)
            results["socketio_server"] = {"status": "PASS", "message": "Socket.IO server accessible"}
            self.log("  ✅ Socket.IO server: PASS", "PASS")
        except Exception as e:
            results["socketio_server"] = {"status": "FAIL", "message": f"Socket.IO server not accessible: {e}"}
            self.log(f"  ❌ Socket.IO server: FAIL - {e}", "FAIL")
        
        return results
    
    def test_phase1_socketio_integration(self) -> Dict[str, Any]:
        """Test Socket.IO client integration."""
        self.log("🧪 Testing Phase 1 Socket.IO Integration...")
        results = {}
        
        # Test Socket.IO dependency
        try:
            import socketio
            results["socketio_dependency"] = {"status": "PASS", "message": "python-socketio available"}
            self.log("  ✅ Socket.IO dependency: PASS", "PASS")
        except ImportError:
            results["socketio_dependency"] = {"status": "FAIL", "message": "python-socketio not installed"}
            self.log("  ❌ Socket.IO dependency: FAIL", "FAIL")
        
        # Test MCP server has orchestration command tool
        try:
            sys.path.append('.')
            import mcp_server
            
            if hasattr(mcp_server, 'send_orchestration_command'):
                results["orchestration_tool"] = {"status": "PASS", "message": "send_orchestration_command exists"}
                self.log("  ✅ Orchestration tool: PASS", "PASS")
            else:
                results["orchestration_tool"] = {"status": "FAIL", "message": "send_orchestration_command not implemented"}
                self.log("  ❌ Orchestration tool: FAIL (TDD - implement this!)", "FAIL")
        except Exception as e:
            results["orchestration_tool"] = {"status": "ERROR", "message": f"Error checking tool: {e}"}
            self.log(f"  ❌ Orchestration tool: ERROR - {e}", "ERROR")
        
        return results
    
    # Phase 2: AI Service Content Scripts Tests
    def test_phase2_file_structure(self) -> Dict[str, Any]:
        """Test Phase 2 file structure."""
        self.log("🧪 Testing Phase 2 File Structure...")
        results = {}
        
        required_files = [
            "contents/ai-interface-base.ts",
            "contents/chatgpt-interface.ts", 
            "contents/claude-interface.ts",
            "background/orchestration-handler.ts",
            "background/tab-manager.ts"
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            file_key = file_path.replace("/", "_").replace(".ts", "")
            
            if path.exists():
                results[file_key] = {"status": "PASS", "message": f"{file_path} exists"}
                self.log(f"  ✅ {file_path}: PASS", "PASS")
            else:
                results[file_key] = {"status": "FAIL", "message": f"{file_path} missing"}
                self.log(f"  ❌ {file_path}: FAIL (TDD - create this!)", "FAIL")
        
        return results
    
    # Phase 3: End-to-End Integration Tests
    def test_phase3_protocol_definition(self) -> Dict[str, Any]:
        """Test Phase 3 protocol definition."""
        self.log("🧪 Testing Phase 3 Protocol Definition...")
        results = {}
        
        # Test TypeScript types
        types_path = Path("types/orchestration.ts")
        if types_path.exists():
            results["orchestration_types"] = {"status": "PASS", "message": "Orchestration types defined"}
            self.log("  ✅ Orchestration types: PASS", "PASS")
        else:
            results["orchestration_types"] = {"status": "FAIL", "message": "Orchestration types missing"}
            self.log("  ❌ Orchestration types: FAIL (TDD - create this!)", "FAIL")
        
        return results
    
    # Phase 4: Documentation & Test Suite Tests
    def test_phase4_documentation(self) -> Dict[str, Any]:
        """Test Phase 4 documentation."""
        self.log("🧪 Testing Phase 4 Documentation...")
        results = {}
        
        # Test E2E test file
        e2e_path = Path("test-e2e-workflow.py")
        if e2e_path.exists():
            results["e2e_test_file"] = {"status": "PASS", "message": "E2E test file exists"}
            self.log("  ✅ E2E test file: PASS", "PASS")
        else:
            results["e2e_test_file"] = {"status": "FAIL", "message": "E2E test file missing"}
            self.log("  ❌ E2E test file: FAIL (TDD - create this!)", "FAIL")
        
        return results
    
    def run_phase_tests(self, phase: int) -> Dict[str, Any]:
        """Run tests for specific phase."""
        self.log(f"🚀 Running Phase {phase} Tests...")
        
        phase_results = {}
        
        if phase == 1:
            phase_results.update(self.test_phase1_prerequisites())
            phase_results.update(self.test_phase1_socketio_integration())
        elif phase == 2:
            phase_results.update(self.test_phase2_file_structure())
        elif phase == 3:
            phase_results.update(self.test_phase3_protocol_definition())
        elif phase == 4:
            phase_results.update(self.test_phase4_documentation())
        
        return phase_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all TDD tests."""
        self.log("🧪 Running All TDD Tests...")
        
        all_results = {}
        
        for phase in range(1, 5):
            self.log(f"\n{'='*50}")
            self.log(f"PHASE {phase} TESTS")
            self.log(f"{'='*50}")
            
            phase_results = self.run_phase_tests(phase)
            all_results[f"phase_{phase}"] = phase_results
        
        return all_results
    
    def generate_tdd_report(self, results: Dict[str, Any]) -> str:
        """Generate TDD test report."""
        report = []
        report.append("# Multi-LLM Orchestration TDD Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for phase_name, phase_results in results.items():
            phase_num = phase_name.split('_')[1]
            report.append(f"## Phase {phase_num} Results")
            report.append("")
            
            for test_name, test_result in phase_results.items():
                status = test_result.get('status', 'UNKNOWN')
                message = test_result.get('message', 'No message')
                
                total_tests += 1
                if status == 'PASS':
                    passed_tests += 1
                    icon = "✅"
                elif status == 'FAIL':
                    failed_tests += 1
                    icon = "❌"
                else:
                    failed_tests += 1
                    icon = "⚠️"
                
                report.append(f"- {icon} **{test_name}**: {message}")
            
            report.append("")
        
        # Summary
        report.append("## Summary")
        report.append("")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Passed**: {passed_tests}")
        report.append(f"- **Failed**: {failed_tests}")
        report.append("")
        
        if failed_tests == 0:
            report.append("🎉 **All tests passing! Implementation complete.**")
        else:
            report.append("🔧 **Tests failing - TDD implementation needed!**")
        
        return "\n".join(report)

def main():
    """Main TDD test runner."""
    parser = argparse.ArgumentParser(description="Multi-LLM Orchestration TDD Test Suite")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Run specific phase tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Save report to file")
    
    args = parser.parse_args()
    
    tester = OrchestrationTDDTester(verbose=args.verbose)
    
    try:
        if args.phase:
            results = {f"phase_{args.phase}": tester.run_phase_tests(args.phase)}
        else:
            results = tester.run_all_tests()
        
        # Generate report
        report = tester.generate_tdd_report(results)
        print("\n" + "="*60)
        print(report)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📝 Report saved to: {args.output}")
        
        # Return exit code based on test results
        all_passed = all(
            test_result.get('status') == 'PASS'
            for phase_results in results.values()
            for test_result in phase_results.values()
        )
        
        return 0 if all_passed else 1
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 