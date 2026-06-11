#!/usr/bin/env python3
"""
Brahmakaal API Comprehensive Test Runner
Automated testing suite for all API endpoints with reporting and analysis
"""

import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path


class BrahmakaakTestRunner:
    """Comprehensive test runner for Brahmakaal API testing suite."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        
    def print_banner(self):
        """Print test runner banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧪 BRAHMAKAAL API TEST SUITE 🧪                          ║
║                                                                              ║
║  Comprehensive Automated Testing for 10 API Endpoints                       ║
║  • Core APIs: Panchang, Horoscope, Muhurta, Transits, Ayanamsha            ║
║  • Advanced APIs: Panchaka, Lagna, Complete Muhurta, Inauspicious, Calendar ║
║                                                                              ║
║  Test Categories: Unit, API, Accuracy, Performance, Integration             ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕐 Test execution started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def run_command(self, command, description):
        """Run a command and capture results."""
        print(f"\n🔄 {description}")
        print(f"   Command: {' '.join(command)}")
        
        start_time = time.time()
        
        # Set up environment with proper Python path
        env = os.environ.copy()
        current_dir = os.getcwd()
        env["PYTHONPATH"] = current_dir
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env=env
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            self.test_results[description] = {
                "success": success,
                "duration": duration,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                print(f"   ✅ {description} completed successfully ({duration:.2f}s)")
            else:
                print(f"   ❌ {description} failed ({duration:.2f}s)")
                print(f"   Error output: {result.stderr[:200]}...")
                
            return success
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {description} timed out after 10 minutes")
            self.test_results[description] = {
                "success": False,
                "duration": 600,
                "error": "Timeout"
            }
            return False
        except Exception as e:
            print(f"   💥 {description} failed with exception: {e}")
            self.test_results[description] = {
                "success": False,
                "duration": 0,
                "error": str(e)
            }
            return False
    
    def install_dependencies(self):
        """Install required test dependencies."""
        dependencies = [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-timeout>=2.1.0",
            "pytest-xdist>=3.0.0",  # For parallel execution
            "httpx>=0.24.0",
            "coverage>=7.0.0"
        ]
        
        print(f"\n📦 Installing test dependencies...")
        for dep in dependencies:
            command = [sys.executable, "-m", "pip", "install", dep]
            success = self.run_command(command, f"Installing {dep}")
            if not success:
                print(f"   ⚠️  Warning: Failed to install {dep}")
    
    def run_test_suite(self, test_type="all"):
        """Run the comprehensive test suite."""
        
        # 1. Quick API Health Check
        print(f"\n🏥 PHASE 1: API Health Check")
        success = self.run_command([
            "python", "-m", "pytest", 
            "tests/integration/test_end_to_end.py::TestEndToEndIntegration::test_system_health_endpoints",
            "-v", "--tb=short"
        ], "API Health Check")
        
        if not success:
            print("   ⚠️  API health check failed - continuing with other tests")
        
        # 2. Unit Tests (if they exist)
        if Path("tests/unit").exists():
            print(f"\n🔧 PHASE 2: Unit Tests")
            self.run_command([
                "python", "-m", "pytest", "tests/unit/", 
                "-v", "--tb=short", "-m", "not slow"
            ], "Unit Tests")
        
        # 3. API Endpoint Tests
        print(f"\n🌐 PHASE 3: API Endpoint Tests")
        api_tests = [
            ("Core Panchang API", "tests/api/test_panchang_api.py"),
            ("Enhanced Panchaka API", "tests/api/test_panchaka_api.py"),
        ]
        
        for test_name, test_path in api_tests:
            if Path(test_path).exists():
                self.run_command([
                    "python", "-m", "pytest", test_path, 
                    "-v", "--tb=short", "-m", "not slow"
                ], test_name)
        
        # 4. Accuracy Validation Tests
        if test_type in ["all", "accuracy"]:
            print(f"\n🎯 PHASE 4: Accuracy Validation Tests")
            self.run_command([
                "python", "-m", "pytest", "tests/accuracy/", 
                "-v", "--tb=short", "-m", "accuracy"
            ], "Accuracy Validation Tests")
        
        # 5. Performance Tests
        if test_type in ["all", "performance"]:
            print(f"\n⚡ PHASE 5: Performance Tests")
            self.run_command([
                "python", "-m", "pytest", "tests/performance/", 
                "-v", "--tb=short", "-m", "performance and not slow"
            ], "Performance Tests")
        
        # 6. Integration Tests
        if test_type in ["all", "integration"]:
            print(f"\n🔗 PHASE 6: Integration Tests")
            self.run_command([
                "python", "-m", "pytest", "tests/integration/", 
                "-v", "--tb=short", "-m", "integration and not slow"
            ], "Integration Tests")
        
        # 7. Extended Tests (optional)
        if test_type == "extended":
            print(f"\n🔄 PHASE 7: Extended Tests (Slow)")
            self.run_command([
                "python", "-m", "pytest", "tests/", 
                "-v", "--tb=short", "-m", "slow"
            ], "Extended Slow Tests")
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print(f"\n📊 Generating Coverage Report...")
        
        # Generate HTML coverage report
        self.run_command([
            "python", "-m", "coverage", "html", "--directory", "htmlcov"
        ], "HTML Coverage Report")
        
        # Generate terminal coverage report
        self.run_command([
            "python", "-m", "coverage", "report", "--show-missing"
        ], "Terminal Coverage Report")
    
    def print_summary(self):
        """Print test execution summary."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📋 TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 Overall Statistics:")
        print(f"   • Total Test Phases: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   • Total Duration: {total_duration:.2f} seconds")
        
        print(f"\n🔍 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result.get("duration", 0)
            print(f"   {status} {test_name} ({duration:.2f}s)")
        
        if failed_tests > 0:
            print(f"\n⚠️  Failed Tests Details:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    error_info = result.get("stderr", result.get("error", "Unknown error"))
                    print(f"   ❌ {test_name}: {error_info[:100]}...")
        
        print(f"\n🕐 Test execution completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return exit code
        return 0 if failed_tests == 0 else 1
    
    def run_quick_test(self):
        """Run quick smoke tests only."""
        print("\n🚀 QUICK TEST MODE - Running Essential Tests Only")
        
        quick_tests = [
            ("API Health Check", [
                "python", "-m", "pytest", 
                "tests/integration/test_end_to_end.py::TestEndToEndIntegration::test_system_health_endpoints",
                "-v"
            ]),
            ("Core Panchang Test", [
                "python", "-m", "pytest", 
                "tests/api/test_panchang_api.py::TestPanchangAPI::test_panchang_basic_functionality",
                "-v"
            ]),
            ("Basic Integration Test", [
                "python", "-m", "pytest", 
                "tests/integration/test_end_to_end.py::TestEndToEndIntegration::test_complete_api_workflow",
                "-v"
            ])
        ]
        
        for test_name, command in quick_tests:
            self.run_command(command, test_name)
    
    def run_accuracy_only(self):
        """Run accuracy validation tests only."""
        print("\n🎯 ACCURACY VALIDATION MODE")
        
        accuracy_tests = [
            ("Drik Panchang Validation", [
                "python", "-m", "pytest", "tests/accuracy/", 
                "-v", "-m", "accuracy"
            ])
        ]
        
        for test_name, command in accuracy_tests:
            self.run_command(command, test_name)


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Brahmakaal API Test Runner")
    parser.add_argument("--type", choices=["all", "quick", "accuracy", "performance", "integration", "extended"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    runner = BrahmakaakTestRunner()
    runner.print_banner()
    
    # Install dependencies if requested
    if args.install_deps:
        runner.install_dependencies()
    
    # Run tests based on type
    if args.type == "quick":
        runner.run_quick_test()
    elif args.type == "accuracy":
        runner.run_accuracy_only()
    else:
        runner.run_test_suite(args.type)
    
    # Generate coverage report if requested
    if args.coverage:
        runner.generate_coverage_report()
    
    # Print summary and exit
    exit_code = runner.print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 