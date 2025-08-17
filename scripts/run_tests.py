#!/usr/bin/env python3
"""
Test Runner for Open WebUI

This script makes it easy to run tests for the Open WebUI project.
It provides options for running different types of tests, generating
coverage reports, and more.

Usage:
    python run_tests.py [OPTIONS]

Options:
    --unit           Run unit tests only
    --integration    Run integration tests only
    --all            Run all tests (default)
    --coverage       Generate coverage report
    --verbose        Run with verbose output
    --xml            Generate XML report for CI systems
    --component=NAME Run tests for a specific component (e.g., ai_core, backends)
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Terminal colors for better readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_section(text):
    """Print a formatted section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'-' * len(text)}{Colors.ENDC}\n")

def run_command(command, env=None):
    """Run a shell command and return its exit code."""
    start_time = time.time()
    print(f"{Colors.CYAN}Running: {' '.join(command)}{Colors.ENDC}")

    result = subprocess.run(command, env=env)

    elapsed_time = time.time() - start_time
    print(f"{Colors.CYAN}Completed in {elapsed_time:.2f}s with exit code {result.returncode}{Colors.ENDC}")

    return result.returncode

def run_tests(args):
    """Run the specified tests based on command-line arguments."""
    # Base pytest command
    pytest_cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")

    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])

    # Add XML report if requested
    if args.xml:
        pytest_cmd.append("--junitxml=test_results.xml")

    # Determine which tests to run
    if args.unit:
        pytest_cmd.append("tests/unit/")
    elif args.integration:
        pytest_cmd.append("tests/integration/")
    else:  # Run all tests
        pytest_cmd.append("tests/")

    # Filter by component if specified
    if args.component:
        pytest_cmd.append(f"-k {args.component}")

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.absolute())

    # Run the tests
    print_header("Running Open WebUI Tests")
    return run_command(pytest_cmd, env=env)

def generate_coverage_badge():
    """Generate a coverage badge for the README."""
    try:
        # This requires the coverage-badge package
        print_section("Generating Coverage Badge")
        run_command(["coverage-badge", "-o", "coverage-badge.svg"])
        print(f"{Colors.GREEN}Coverage badge generated at coverage-badge.svg{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Failed to generate coverage badge: {e}{Colors.ENDC}")

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for Open WebUI")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", action="store_true", help="Run with verbose output")
    parser.add_argument("--xml", action="store_true", help="Generate XML report for CI systems")
    parser.add_argument("--component", help="Run tests for a specific component")

    args = parser.parse_args()

    # If no test type is specified, run all tests
    if not (args.unit or args.integration or args.all):
        args.all = True

    # Run the tests
    exit_code = run_tests(args)

    # Generate coverage badge if coverage was requested
    if args.coverage:
        generate_coverage_badge()

    # Return the exit code from pytest
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
