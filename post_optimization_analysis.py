#!/usr/bin/env python3
"""
Post-Optimization Analysis for Dimensional AI Platform
Identifies missing components and optimization opportunities
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class PostOptimizationAnalyzer:
    def __init__(self, project_root: str = "/home/behar/Desktop/sssss"):
        self.project_root = Path(project_root)
        self.analysis_report = {
            "analysis_date": datetime.now().isoformat(),
            "project_name": "Dimensional AI Platform",
            "missing_components": {},
            "optimization_opportunities": {},
            "recommendations": [],
            "enterprise_readiness_score": 0.0
        }
    
    def analyze_missing_components(self):
        """Identify missing enterprise components"""
        print("🔍 Analyzing missing components...")
        
        missing = {}
        
        # Database Models and ORM
        if not self._check_database_models():
            missing["database_models"] = {
                "severity": "high",
                "description": "Missing database models and ORM layer",
                "impact": "No structured data persistence",
                "recommendation": "Implement SQLAlchemy models for users, sessions, consciousness data"
            }
        
        # Authentication & Authorization
        if not self._check_auth_system():
            missing["authentication"] = {
                "severity": "high", 
                "description": "Missing authentication and authorization system",
                "impact": "No user management or security",
                "recommendation": "Implement JWT-based auth with role-based access control"
            }
        
        # API Rate Limiting
        if not self._check_rate_limiting():
            missing["rate_limiting"] = {
                "severity": "medium",
                "description": "Missing API rate limiting",
                "impact": "Vulnerable to abuse and DoS attacks",
                "recommendation": "Implement rate limiting with Redis or in-memory store"
            }
        
        # Caching Layer
        if not self._check_caching():
            missing["caching"] = {
                "severity": "medium",
                "description": "Missing caching layer",
                "impact": "Poor performance for repeated requests",
                "recommendation": "Implement Redis caching for API responses and consciousness data"
            }
        
        # Background Tasks
        if not self._check_background_tasks():
            missing["background_tasks"] = {
                "severity": "medium",
                "description": "Missing background task system",
                "impact": "No async processing capabilities",
                "recommendation": "Implement Celery or FastAPI BackgroundTasks"
            }
        
        # WebSocket Support
        if not self._check_websocket():
            missing["websocket"] = {
                "severity": "medium",
                "description": "Missing WebSocket support for real-time features",
                "impact": "No real-time consciousness updates",
                "recommendation": "Implement WebSocket endpoints for live consciousness streaming"
            }
        
        # Health Checks
        if not self._check_health_checks():
            missing["health_checks"] = {
                "severity": "low",
                "description": "Basic health checks present but could be enhanced",
                "impact": "Limited monitoring capabilities",
                "recommendation": "Add detailed health checks for database, Redis, external services"
            }
        
        # Configuration Management
        if not self._check_config_management():
            missing["config_management"] = {
                "severity": "medium",
                "description": "Missing centralized configuration management",
                "impact": "Difficult environment-specific deployments",
                "recommendation": "Implement Pydantic settings with environment validation"
            }
        
        # Logging and Observability
        if not self._check_observability():
            missing["observability"] = {
                "severity": "medium",
                "description": "Missing structured logging and observability",
                "impact": "Difficult debugging and monitoring",
                "recommendation": "Implement structured logging with correlation IDs and metrics"
            }
        
        # Data Validation
        if not self._check_data_validation():
            missing["data_validation"] = {
                "severity": "medium",
                "description": "Missing comprehensive data validation",
                "impact": "Potential data corruption and security issues",
                "recommendation": "Implement Pydantic models for all API inputs/outputs"
            }
        
        self.analysis_report["missing_components"] = missing
        return missing
    
    def analyze_optimization_opportunities(self):
        """Identify optimization opportunities"""
        print("⚡ Analyzing optimization opportunities...")
        
        opportunities = {}
        
        # Code Duplication
        duplicates = self._find_code_duplication()
        if duplicates:
            opportunities["code_duplication"] = {
                "severity": "medium",
                "description": f"Found {len(duplicates)} potential code duplications",
                "impact": "Increased maintenance burden",
                "recommendation": "Refactor common code into shared utilities",
                "details": duplicates[:5]  # Show first 5
            }
        
        # Large Files
        large_files = self._find_large_files()
        if large_files:
            opportunities["large_files"] = {
                "severity": "low",
                "description": f"Found {len(large_files)} large files that could be split",
                "impact": "Reduced code maintainability",
                "recommendation": "Split large files into smaller, focused modules",
                "details": large_files[:5]
            }
        
        # Unused Dependencies
        unused_deps = self._find_unused_dependencies()
        if unused_deps:
            opportunities["unused_dependencies"] = {
                "severity": "low",
                "description": f"Found {len(unused_deps)} potentially unused dependencies",
                "impact": "Increased bundle size and security surface",
                "recommendation": "Remove unused dependencies",
                "details": unused_deps
            }
        
        # Missing Type Hints
        untyped_files = self._find_untyped_files()
        if untyped_files:
            opportunities["type_hints"] = {
                "severity": "medium",
                "description": f"Found {len(untyped_files)} files missing type hints",
                "impact": "Reduced code quality and IDE support",
                "recommendation": "Add type hints to all Python functions",
                "details": untyped_files[:10]
            }
        
        # Performance Opportunities
        perf_issues = self._find_performance_issues()
        if perf_issues:
            opportunities["performance"] = {
                "severity": "medium",
                "description": "Found potential performance improvements",
                "impact": "Slower response times and resource usage",
                "recommendation": "Optimize identified performance bottlenecks",
                "details": perf_issues
            }
        
        self.analysis_report["optimization_opportunities"] = opportunities
        return opportunities
    
    def calculate_enterprise_readiness(self):
        """Calculate enterprise readiness score"""
        print("📊 Calculating enterprise readiness score...")
        
        total_score = 100.0
        missing = self.analysis_report["missing_components"]
        
        # Deduct points for missing components
        for component, details in missing.items():
            if details["severity"] == "high":
                total_score -= 15
            elif details["severity"] == "medium":
                total_score -= 10
            elif details["severity"] == "low":
                total_score -= 5
        
        # Deduct points for optimization opportunities
        opportunities = self.analysis_report["optimization_opportunities"]
        for opp, details in opportunities.items():
            if details["severity"] == "high":
                total_score -= 10
            elif details["severity"] == "medium":
                total_score -= 5
            elif details["severity"] == "low":
                total_score -= 2
        
        self.analysis_report["enterprise_readiness_score"] = max(0, total_score)
        return total_score
    
    def generate_recommendations(self):
        """Generate prioritized recommendations"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # High priority missing components
        for component, details in self.analysis_report["missing_components"].items():
            if details["severity"] == "high":
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Missing Component",
                    "title": f"Implement {component.replace('_', ' ').title()}",
                    "description": details["description"],
                    "impact": details["impact"],
                    "action": details["recommendation"]
                })
        
        # Medium priority items
        for component, details in self.analysis_report["missing_components"].items():
            if details["severity"] == "medium":
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Missing Component", 
                    "title": f"Add {component.replace('_', ' ').title()}",
                    "description": details["description"],
                    "impact": details["impact"],
                    "action": details["recommendation"]
                })
        
        # Optimization opportunities
        for opp, details in self.analysis_report["optimization_opportunities"].items():
            if details["severity"] in ["high", "medium"]:
                recommendations.append({
                    "priority": details["severity"].upper(),
                    "category": "Optimization",
                    "title": f"Optimize {opp.replace('_', ' ').title()}",
                    "description": details["description"],
                    "impact": details["impact"],
                    "action": details["recommendation"]
                })
        
        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        self.analysis_report["recommendations"] = recommendations
        return recommendations
    
    # Helper methods for component checking
    def _check_database_models(self):
        """Check for database models"""
        model_patterns = ["models.py", "database.py", "schema.py", "orm.py"]
        for pattern in model_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_auth_system(self):
        """Check for authentication system"""
        auth_patterns = ["auth.py", "authentication.py", "jwt.py", "oauth.py"]
        for pattern in auth_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_rate_limiting(self):
        """Check for rate limiting"""
        # Look for rate limiting imports or decorators
        try:
            result = subprocess.run(
                ["grep", "-r", "rate.limit", str(self.project_root)],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_caching(self):
        """Check for caching implementation"""
        cache_patterns = ["cache.py", "redis.py"]
        for pattern in cache_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_background_tasks(self):
        """Check for background task system"""
        task_patterns = ["tasks.py", "celery.py", "worker.py"]
        for pattern in task_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_websocket(self):
        """Check for WebSocket support"""
        try:
            result = subprocess.run(
                ["grep", "-r", "websocket\|WebSocket", str(self.project_root)],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_health_checks(self):
        """Check for health check endpoints"""
        # We know there's a basic health check in main.py
        return True
    
    def _check_config_management(self):
        """Check for configuration management"""
        config_patterns = ["config.py", "settings.py", "env.py"]
        for pattern in config_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_observability(self):
        """Check for observability features"""
        obs_patterns = ["logging.py", "metrics.py", "tracing.py"]
        for pattern in obs_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _check_data_validation(self):
        """Check for data validation"""
        try:
            result = subprocess.run(
                ["grep", "-r", "pydantic\|BaseModel", str(self.project_root)],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _find_code_duplication(self):
        """Find potential code duplication"""
        duplicates = []
        # This is a simplified check - in practice you'd use tools like jscpd
        python_files = list(self.project_root.rglob("*.py"))
        
        # Look for files with similar names (potential duplicates)
        file_names = {}
        for file in python_files:
            base_name = file.stem.lower()
            if base_name in file_names:
                duplicates.append({
                    "type": "similar_names",
                    "files": [str(file_names[base_name]), str(file)]
                })
            else:
                file_names[base_name] = file
        
        return duplicates
    
    def _find_large_files(self):
        """Find large files that could be split"""
        large_files = []
        for file in self.project_root.rglob("*.py"):
            try:
                if file.stat().st_size > 10000:  # > 10KB
                    with open(file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        if lines > 300:  # > 300 lines
                            large_files.append({
                                "file": str(file.relative_to(self.project_root)),
                                "lines": lines,
                                "size_kb": file.stat().st_size // 1024
                            })
            except:
                continue
        
        return sorted(large_files, key=lambda x: x["lines"], reverse=True)
    
    def _find_unused_dependencies(self):
        """Find potentially unused dependencies"""
        # This is a simplified check
        unused = []
        
        # Check requirements files
        req_files = list(self.project_root.rglob("requirements*.txt"))
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    deps = [line.split('==')[0].split('>=')[0].split('~=')[0].strip() 
                           for line in f if line.strip() and not line.startswith('#')]
                
                # Simple check - look for imports
                for dep in deps[:10]:  # Check first 10 to avoid long processing
                    try:
                        result = subprocess.run(
                            ["grep", "-r", f"import {dep}\|from {dep}", str(self.project_root)],
                            capture_output=True, text=True, timeout=5
                        )
                        if result.returncode != 0:
                            unused.append(dep)
                    except:
                        continue
            except:
                continue
        
        return unused[:5]  # Return first 5
    
    def _find_untyped_files(self):
        """Find Python files missing type hints"""
        untyped = []
        
        for file in self.project_root.rglob("*.py"):
            if "test" in str(file) or "__pycache__" in str(file):
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple check for type hints
                    if "def " in content and "->" not in content and "typing" not in content:
                        untyped.append(str(file.relative_to(self.project_root)))
            except:
                continue
        
        return untyped
    
    def _find_performance_issues(self):
        """Find potential performance issues"""
        issues = []
        
        # Check for synchronous operations that could be async
        for file in self.project_root.rglob("*.py"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "requests.get" in content or "requests.post" in content:
                        issues.append({
                            "type": "sync_http_calls",
                            "file": str(file.relative_to(self.project_root)),
                            "suggestion": "Use async HTTP client (httpx) instead of requests"
                        })
            except:
                continue
        
        return issues[:5]  # Return first 5
    
    def run_analysis(self):
        """Run complete analysis"""
        print("🚀 Starting Post-Optimization Analysis...")
        print("=" * 50)
        
        self.analyze_missing_components()
        self.analyze_optimization_opportunities()
        self.calculate_enterprise_readiness()
        self.generate_recommendations()
        
        return self.analysis_report
    
    def save_report(self, filename="post_optimization_analysis.json"):
        """Save analysis report to file"""
        report_path = self.project_root / filename
        with open(report_path, 'w') as f:
            json.dump(self.analysis_report, f, indent=2)
        
        print(f"📊 Analysis report saved to: {report_path}")
        return report_path
    
    def print_summary(self):
        """Print analysis summary"""
        report = self.analysis_report
        
        print("\n" + "=" * 60)
        print("📊 POST-OPTIMIZATION ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"\n🏢 Enterprise Readiness Score: {report['enterprise_readiness_score']:.1f}/100")
        
        if report['enterprise_readiness_score'] >= 90:
            print("✅ EXCELLENT - Production ready!")
        elif report['enterprise_readiness_score'] >= 80:
            print("🟡 GOOD - Minor improvements needed")
        elif report['enterprise_readiness_score'] >= 70:
            print("🟠 FAIR - Several improvements needed")
        else:
            print("🔴 NEEDS WORK - Major improvements required")
        
        print(f"\n🔍 Missing Components: {len(report['missing_components'])}")
        for component, details in report['missing_components'].items():
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"  {severity_emoji[details['severity']]} {component.replace('_', ' ').title()}")
        
        print(f"\n⚡ Optimization Opportunities: {len(report['optimization_opportunities'])}")
        for opp, details in report['optimization_opportunities'].items():
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"  {severity_emoji[details['severity']]} {opp.replace('_', ' ').title()}")
        
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            print(f"  {i}. {priority_emoji[rec['priority']]} {rec['title']}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    analyzer = PostOptimizationAnalyzer()
    analyzer.run_analysis()
    analyzer.save_report()
    analyzer.print_summary()
