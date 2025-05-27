#!/usr/bin/env python3
"""
Test runner script for UAC FastAPI project.

This script provides convenient ways to run different types of tests.
"""

import subprocess
import sys
import argparse


def run_command(command: list[str]) -> int:
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for UAC FastAPI project")
    parser.add_argument(
        "--type",
        choices=["all", "auth", "health", "integration", "slow"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--file",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add specific test selection
    if args.file:
        cmd.append(f"tests/{args.file}")
    elif args.type == "auth":
        cmd.extend(["-m", "auth"])
    elif args.type == "health":
        cmd.append("tests/test_health.py")
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "slow":
        cmd.extend(["-m", "slow"])
    else:  # all
        cmd.append("tests/")
    
    # Run the tests
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 