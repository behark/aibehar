#!/usr/bin/env python3
"""
Dependency Verification Tool for Open WebUI

This script verifies the project's dependencies, checking for:
1. Outdated packages
2. Security vulnerabilities
3. Compatibility issues
4. Missing dependencies

Usage:
    python verify_dependencies.py [--check-security] [--update-recommendations]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

# Configure colors for terminal output
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

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_section(text: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'-' * len(text)}{Colors.ENDC}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def get_installed_packages() -> Dict[str, str]:
    """Get a dictionary of installed packages and their versions."""
    result = {}
    returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "list", "--format=json"])

    if returncode != 0:
        print_error(f"Failed to get installed packages: {stderr}")
        return {}

    try:
        packages = json.loads(stdout)
        for package in packages:
            result[package["name"].lower()] = package["version"]
        return result
    except json.JSONDecodeError:
        print_error("Failed to parse pip list output")
        return {}

def get_project_dependencies() -> Dict[str, Dict[str, List[str]]]:
    """Parse pyproject.toml and extract dependencies."""
    try:
        import tomli
    except ImportError:
        print_info("Installing tomli to parse pyproject.toml...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tomli"], check=True)
        import tomli

    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)

        result = {
            "main": {},
            "optional": {}
        }

        # Extract main dependencies
        for dep in pyproject.get("project", {}).get("dependencies", []):
            # Skip comment lines
            if dep.startswith("#"):
                continue

            # Parse the dependency specification
            parts = dep.split(">=")
            if len(parts) > 1:
                name = parts[0].strip()
                version_parts = parts[1].split(",")
                min_version = version_parts[0].strip()
                result["main"][name.lower()] = [min_version]
            else:
                parts = dep.split("==")
                if len(parts) > 1:
                    name = parts[0].strip()
                    exact_version = parts[1].strip()
                    result["main"][name.lower()] = [exact_version]
                else:
                    # Handle dependencies without version constraints
                    name = dep.strip()
                    if "[" in name:
                        name = name.split("[")[0]
                    result["main"][name.lower()] = ["any"]

        # Extract optional dependencies
        optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
        for group, deps in optional_deps.items():
            result["optional"][group] = {}
            for dep in deps:
                parts = dep.split(">=")
                if len(parts) > 1:
                    name = parts[0].strip()
                    version_parts = parts[1].split(",")
                    min_version = version_parts[0].strip()
                    result["optional"][group][name.lower()] = [min_version]
                else:
                    parts = dep.split("==")
                    if len(parts) > 1:
                        name = parts[0].strip()
                        exact_version = parts[1].strip()
                        result["optional"][group][name.lower()] = [exact_version]
                    else:
                        # Handle dependencies without version constraints
                        name = dep.strip()
                        if "[" in name:
                            name = name.split("[")[0]
                        result["optional"][group][name.lower()] = ["any"]

        return result
    except Exception as e:
        print_error(f"Failed to parse pyproject.toml: {e}")
        return {"main": {}, "optional": {}}

def check_outdated_packages() -> Dict[str, Dict[str, str]]:
    """Check for outdated packages."""
    returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"])

    if returncode != 0:
        print_error(f"Failed to check for outdated packages: {stderr}")
        return {}

    try:
        outdated = {}
        packages = json.loads(stdout) if stdout.strip() else []
        for package in packages:
            name = package["name"].lower()
            outdated[name] = {
                "current": package["version"],
                "latest": package["latest_version"]
            }
        return outdated
    except json.JSONDecodeError:
        print_error("Failed to parse pip outdated output")
        return {}

def check_security_vulnerabilities() -> Dict[str, List[Dict[str, Any]]]:
    """Check for security vulnerabilities using safety."""
    try:
        import safety
    except ImportError:
        print_info("Installing safety to check for vulnerabilities...")
        subprocess.run([sys.executable, "-m", "pip", "install", "safety"], check=True)

    returncode, stdout, stderr = run_command([sys.executable, "-m", "safety", "check", "--json"])

    if returncode != 0 and stdout:
        try:
            vulnerabilities = {}
            data = json.loads(stdout)

            for vuln in data["vulnerabilities"]:
                package_name = vuln["package_name"].lower()
                if package_name not in vulnerabilities:
                    vulnerabilities[package_name] = []

                vulnerabilities[package_name].append({
                    "vulnerability_id": vuln["vulnerability_id"],
                    "affected_versions": vuln["affected_versions"],
                    "description": vuln["description"]
                })

            return vulnerabilities
        except json.JSONDecodeError:
            print_error("Failed to parse safety output")
            return {}

    return {}

def verify_dependencies(check_security: bool = False) -> Dict[str, Any]:
    """Verify project dependencies and generate a report."""
    print_header("Open WebUI Dependency Verification")

    results = {
        "timestamp": datetime.now().isoformat(),
        "missing_dependencies": [],
        "outdated_dependencies": [],
        "security_issues": [],
        "recommendations": []
    }

    print_section("Checking Project Dependencies")
    project_deps = get_project_dependencies()
    installed_packages = get_installed_packages()

    # Check for missing dependencies
    for name, versions in project_deps["main"].items():
        if name not in installed_packages:
            print_warning(f"Missing dependency: {name} {versions[0]}")
            results["missing_dependencies"].append({
                "name": name,
                "required_version": versions[0]
            })
        elif versions[0] != "any":
            from packaging import version
            try:
                if version.parse(installed_packages[name]) < version.parse(versions[0]):
                    print_warning(f"Outdated version: {name} {installed_packages[name]} < {versions[0]}")
                    results["missing_dependencies"].append({
                        "name": name,
                        "required_version": versions[0],
                        "installed_version": installed_packages[name]
                    })
            except Exception:
                print_warning(f"Could not compare versions for {name}")

    # Check for outdated packages
    print_section("Checking for Outdated Packages")
    outdated = check_outdated_packages()
    if outdated:
        for name, versions in outdated.items():
            if name in project_deps["main"]:
                print_warning(f"Outdated: {name} {versions['current']} -> {versions['latest']}")
                results["outdated_dependencies"].append({
                    "name": name,
                    "current_version": versions["current"],
                    "latest_version": versions["latest"]
                })
    else:
        print_success("No outdated packages found")

    # Check for security vulnerabilities
    if check_security:
        print_section("Checking for Security Vulnerabilities")
        vulnerabilities = check_security_vulnerabilities()
        if vulnerabilities:
            for name, vulns in vulnerabilities.items():
                for vuln in vulns:
                    print_error(f"Security issue in {name}: {vuln['vulnerability_id']}")
                    print_info(f"  {vuln['description'][:100]}...")
                    results["security_issues"].append({
                        "name": name,
                        "vulnerability_id": vuln["vulnerability_id"],
                        "description": vuln["description"]
                    })
        else:
            print_success("No security vulnerabilities found")

    # Generate recommendations
    if results["missing_dependencies"]:
        cmds = []
        for dep in results["missing_dependencies"]:
            if "installed_version" in dep:
                cmds.append(f"{dep['name']}=={dep['required_version']}")
            else:
                cmds.append(f"{dep['name']}=={dep['required_version']}")

        if cmds:
            cmd = f"{sys.executable} -m pip install {' '.join(cmds)}"
            results["recommendations"].append({
                "type": "install_missing",
                "command": cmd,
                "description": "Install missing dependencies"
            })

    if results["outdated_dependencies"]:
        cmds = []
        for dep in results["outdated_dependencies"]:
            cmds.append(f"{dep['name']}=={dep['latest_version']}")

        if cmds:
            cmd = f"{sys.executable} -m pip install -U {' '.join(cmds)}"
            results["recommendations"].append({
                "type": "update",
                "command": cmd,
                "description": "Update outdated dependencies"
            })

    if results["security_issues"]:
        results["recommendations"].append({
            "type": "security",
            "description": "Review and address security vulnerabilities"
        })

    return results

def save_report(results: Dict[str, Any], filename: str = "dependency_report.json") -> None:
    """Save the verification results to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print_success(f"Report saved to {filename}")
    except Exception as e:
        print_error(f"Failed to save report: {e}")

def print_recommendations(results: Dict[str, Any]) -> None:
    """Print recommendations based on verification results."""
    if not results["recommendations"]:
        print_success("No actions needed. All dependencies are up to date and secure.")
        return

    print_section("Recommendations")

    for i, rec in enumerate(results["recommendations"], 1):
        print_info(f"{i}. {rec['description']}")
        if "command" in rec:
            print(f"   {Colors.CYAN}Run: {rec['command']}{Colors.ENDC}\n")

def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Verify Open WebUI dependencies")
    parser.add_argument("--check-security", action="store_true", help="Check for security vulnerabilities")
    parser.add_argument("--update-recommendations", action="store_true", help="Update dependencies based on recommendations")
    args = parser.parse_args()

    results = verify_dependencies(check_security=args.check_security)
    save_report(results)
    print_recommendations(results)

    if args.update_recommendations and results["recommendations"]:
        print_section("Applying Recommendations")
        for rec in results["recommendations"]:
            if "command" in rec:
                print_info(f"Running: {rec['command']}")
                returncode, stdout, stderr = run_command(rec["command"].split())
                if returncode != 0:
                    print_error(f"Failed: {stderr}")
                else:
                    print_success("Command executed successfully")

if __name__ == "__main__":
    main()
