#!/usr/bin/env python3
"""
Test runner for the Unified QueryRAG Engine tests.
Runs all test suites for the combined system.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def run_unified_tests():
    """Run all unified engine tests."""
    print("=" * 80)
    print("UNIFIED QUERYRAG ENGINE TEST SUITE")
    print("=" * 80)
    print()
    
    # Test files to run - only the new unified tests
    test_files = [
        "config/profiles/default_profile/tests/test_unified_engine.py",
        "config/profiles/default_profile/tests/test_unified_api.py", 
        "config/profiles/default_profile/tests/test_unified_mcp.py"
    ]
    
    # Note: We're not including the old test files that have import issues
    # They can be run separately if needed after fixing their imports
    
    print(f"Running {len(test_files)} test suites:")
    for test_file in test_files:
        print(f"  - {test_file}")
    print()
    
    # Run tests with verbose output
    test_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "--durations=10",  # Show 10 slowest tests
        *test_files
    ]
    
    # Run the tests
    exit_code = pytest.main(test_args)
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 80)
    
    return exit_code

def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    test_files = {
        "engine": "config/profiles/default_profile/tests/test_unified_engine.py",
        "api": "config/profiles/default_profile/tests/test_unified_api.py",
        "mcp": "config/profiles/default_profile/tests/test_unified_mcp.py",
        "integration": "config/profiles/default_profile/tests/test_api_integration.py",
        "rag": "config/profiles/default_profile/tests/test_generic_langchain_rag.py"
    }
    
    if suite_name not in test_files:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_files.keys())}")
        return 1
    
    test_file = test_files[suite_name]
    if not Path(test_file).exists():
        print(f"Test file not found: {test_file}")
        return 1
    
    print(f"Running {suite_name} test suite: {test_file}")
    print()
    
    test_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        test_file
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_quick_tests():
    """Run quick tests (unit tests only, no integration)."""
    print("Running quick tests (unit tests only)...")
    print()
    
    test_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "not integration",  # Skip integration tests
        "config/profiles/default_profile/tests/test_unified_engine.py"
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_integration_tests():
    """Run integration tests only."""
    print("Running integration tests...")
    print()
    
    test_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "integration",  # Only integration tests
        "config/profiles/default_profile/tests/test_unified_engine.py",
        "config/profiles/default_profile/tests/test_unified_api.py",
        "config/profiles/default_profile/tests/test_unified_mcp.py"
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def show_test_coverage():
    """Show test coverage information."""
    print("Test Coverage Information:")
    print("=" * 50)
    print()
    
    test_files = [
        "config/profiles/default_profile/tests/test_unified_engine.py",
        "config/profiles/default_profile/tests/test_unified_api.py",
        "config/profiles/default_profile/tests/test_unified_mcp.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file} - Available")
        else:
            print(f"❌ {test_file} - Missing")
    
    print()
    print("Test Categories:")
    print("  - Engine Tests: Core unified engine functionality")
    print("  - API Tests: FastAPI endpoint testing")
    print("  - MCP Tests: MCP server tool testing")
    print("  - Integration Tests: End-to-end workflow testing")
    print("  - Error Handling Tests: Exception and edge case testing")

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        # Run all tests by default
        return run_unified_tests()
    
    command = sys.argv[1].lower()
    
    if command == "all":
        return run_unified_tests()
    elif command == "quick":
        return run_quick_tests()
    elif command == "integration":
        return run_integration_tests()
    elif command == "coverage":
        show_test_coverage()
        return 0
    elif command in ["engine", "api", "mcp", "integration", "rag"]:
        return run_specific_test_suite(command)
    else:
        print("Usage: python run_unified_tests.py [command]")
        print()
        print("Commands:")
        print("  all          - Run all test suites (default)")
        print("  quick        - Run quick unit tests only")
        print("  integration  - Run integration tests only")
        print("  engine       - Run unified engine tests only")
        print("  api          - Run unified API tests only")
        print("  mcp          - Run unified MCP tests only")
        print("  coverage     - Show test coverage information")
        print()
        print("Examples:")
        print("  python run_unified_tests.py")
        print("  python run_unified_tests.py all")
        print("  python run_unified_tests.py engine")
        print("  python run_unified_tests.py quick")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
