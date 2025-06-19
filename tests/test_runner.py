#!/usr/bin/env python3
"""
Test Runner
===========
Python replacement for run_tests.sh
Comprehensive test runner for the MCP server and related components.
"""

import os
import sys
import subprocess
import time
import click
from pathlib import Path
from typing import List, Optional, Dict, Any
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    # Graceful fallback if colorama not available
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = ""
    class Style:
        RESET_ALL = ""

class TestRunner:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def print_status(self, message: str, status_type: str = "info"):
        """Print colored status message"""
        color = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "header": Fore.MAGENTA
        }.get(status_type, "")
        
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def check_requirements(self) -> bool:
        """Check if required files and dependencies exist"""
        self.print_status("🔍 Checking test requirements...")
        
        # Check Python
        if not subprocess.run(["python3", "--version"], capture_output=True).returncode == 0:
            self.print_status("❌ Python 3 is required but not found", "error")
            return False
            
        # Check for test files
        test_files = [
            "test_mcp_server.py",
            "test_dual_mode.py", 
            "test_python_migration.py"
        ]
        
        missing_files = []
        for test_file in test_files:
            if not (self.base_dir / test_file).exists():
                missing_files.append(test_file)
                
        if missing_files:
            self.print_status("⚠️  Some test files not found:", "warning")
            for file in missing_files:
                self.print_status(f"   • {file}", "warning")
        else:
            self.print_status("✅ All test files found", "success")
            
        # Check for main files
        main_files = ["mcp_server.py", "service_manager.py"]
        missing_main = []
        for main_file in main_files:
            if not (self.base_dir / main_file).exists():
                missing_main.append(main_file)
                
        if missing_main:
            self.print_status("❌ Required main files not found:", "error")
            for file in missing_main:
                self.print_status(f"   • {file}", "error")
            return False
            
        self.print_status("✅ Requirements check passed", "success")
        return True
        
    def run_test_file(self, test_file: str, verbose: bool = False, output_file: Optional[str] = None) -> bool:
        """Run a specific test file"""
        test_path = self.base_dir / test_file
        
        if not test_path.exists():
            self.print_status(f"❌ Test file not found: {test_file}", "error")
            return False
            
        self.print_status(f"🧪 Running {test_file}...")
        
        # Build command
        cmd = ["python3", str(test_path)]
        
        if verbose:
            cmd.append("--verbose")
            
        if output_file:
            cmd.extend(["--output", output_file])
            
        try:
            # Run the test
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=not verbose,  # Show output if verbose
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.print_status(f"✅ {test_file} passed", "success")
                if not verbose and result.stdout:
                    # Show summary even in non-verbose mode
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        self.print_status(f"   {lines[-1]}")
                return True
            else:
                self.print_status(f"❌ {test_file} failed", "error")
                if result.stderr:
                    self.print_status(f"   Error: {result.stderr.strip()}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_status(f"⏰ {test_file} timed out after 5 minutes", "error")
            return False
        except Exception as e:
            self.print_status(f"❌ Error running {test_file}: {e}", "error")
            return False
            
    def run_all_tests(self, verbose: bool = False, output_file: Optional[str] = None) -> Dict[str, bool]:
        """Run all available test files"""
        self.print_status("🧪 MCP Server Test Suite", "header")
        self.print_status("=" * 25, "header")
        
        if not self.check_requirements():
            return {}
            
        # Find all test files
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(self.base_dir.glob(pattern))
            
        if not test_files:
            self.print_status("⚠️  No test files found", "warning")
            return {}
            
        self.print_status(f"Found {len(test_files)} test files")
        
        results = {}
        start_time = time.time()
        
        for test_file in sorted(test_files):
            test_name = test_file.name
            results[test_name] = self.run_test_file(test_name, verbose, output_file)
            
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.print_status("")
        self.print_status("📊 Test Summary", "header")
        self.print_status("=" * 15, "header")
        
        passed = sum(1 for result in results.values() if result)
        failed = len(results) - passed
        
        self.print_status(f"Total tests: {len(results)}")
        self.print_status(f"Passed: {passed}", "success" if passed > 0 else "info")
        self.print_status(f"Failed: {failed}", "error" if failed > 0 else "info")
        self.print_status(f"Duration: {duration:.2f} seconds")
        
        if output_file:
            self.print_status(f"Report saved to: {output_file}")
            
        return results
        
    def run_specific_tests(self, test_names: List[str], verbose: bool = False, output_file: Optional[str] = None) -> Dict[str, bool]:
        """Run specific test files by name"""
        self.print_status(f"🧪 Running {len(test_names)} specific tests", "header")
        
        if not self.check_requirements():
            return {}
            
        results = {}
        start_time = time.time()
        
        for test_name in test_names:
            # Add .py extension if not present
            if not test_name.endswith('.py'):
                test_name += '.py'
                
            results[test_name] = self.run_test_file(test_name, verbose, output_file)
            
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.print_status("")
        self.print_status("📊 Test Summary", "header")
        
        passed = sum(1 for result in results.values() if result)
        failed = len(results) - passed
        
        self.print_status(f"Passed: {passed}", "success" if passed > 0 else "info")
        self.print_status(f"Failed: {failed}", "error" if failed > 0 else "info")
        self.print_status(f"Duration: {duration:.2f} seconds")
        
        return results
        
    def list_available_tests(self):
        """List all available test files"""
        self.print_status("📋 Available Test Files", "header")
        
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(self.base_dir.glob(pattern))
            
        if not test_files:
            self.print_status("No test files found", "warning")
            return
            
        for test_file in sorted(test_files):
            # Try to get description from docstring
            description = "No description"
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '"""' in content:
                        start = content.find('"""') + 3
                        end = content.find('"""', start)
                        if end > start:
                            docstring = content[start:end].strip()
                            first_line = docstring.split('\n')[0].strip()
                            if first_line:
                                description = first_line
            except:
                pass
                
            self.print_status(f"  • {test_file.name} - {description}")

@click.group()
def cli():
    """Test Runner - Python replacement for run_tests.sh"""
    pass

@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', help='Save test report to file')
def all(verbose: bool, output: Optional[str]):
    """Run all available tests"""
    runner = TestRunner()
    results = runner.run_all_tests(verbose, output)
    
    # Exit with error code if any tests failed
    failed = sum(1 for result in results.values() if not result)
    sys.exit(1 if failed > 0 else 0)

@cli.command()
@click.argument('test_names', nargs=-1, required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', help='Save test report to file')
def run(test_names: List[str], verbose: bool, output: Optional[str]):
    """Run specific test files"""
    runner = TestRunner()
    results = runner.run_specific_tests(list(test_names), verbose, output)
    
    # Exit with error code if any tests failed
    failed = sum(1 for result in results.values() if not result)
    sys.exit(1 if failed > 0 else 0)

@cli.command()
def list():
    """List all available test files"""
    runner = TestRunner()
    runner.list_available_tests()

@cli.command()
@click.argument('test_file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', help='Save test report to file')
def single(test_file: str, verbose: bool, output: Optional[str]):
    """Run a single test file"""
    runner = TestRunner()
    
    if not runner.check_requirements():
        sys.exit(1)
        
    success = runner.run_test_file(test_file, verbose, output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    cli() 