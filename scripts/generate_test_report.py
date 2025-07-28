#!/usr/bin/env python3
"""
Comprehensive Test Report Generator

Generates comprehensive test reports combining coverage, performance, security, and test results.
Used in CI/CD pipeline for consolidated reporting.
"""

import json
import argparse
import sys
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import re


def parse_coverage_xml(coverage_file: str) -> Dict[str, Any]:
    """Parse coverage XML report."""
    if not Path(coverage_file).exists():
        return {}
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Extract overall coverage
        coverage_data = {
            'line_rate': float(root.get('line-rate', 0)) * 100,
            'branch_rate': float(root.get('branch-rate', 0)) * 100,
            'lines_covered': int(root.get('lines-covered', 0)),
            'lines_valid': int(root.get('lines-valid', 0)),
            'branches_covered': int(root.get('branches-covered', 0)),
            'branches_valid': int(root.get('branches-valid', 0)),
            'packages': []
        }
        
        # Extract package-level coverage
        packages = root.find('packages')
        if packages is not None:
            for package in packages.findall('package'):
                package_data = {
                    'name': package.get('name', ''),
                    'line_rate': float(package.get('line-rate', 0)) * 100,
                    'branch_rate': float(package.get('branch-rate', 0)) * 100,
                    'classes': []
                }
                
                classes = package.find('classes')
                if classes is not None:
                    for cls in classes.findall('class'):
                        class_data = {
                            'name': cls.get('name', ''),
                            'filename': cls.get('filename', ''),
                            'line_rate': float(cls.get('line-rate', 0)) * 100,
                            'branch_rate': float(cls.get('branch-rate', 0)) * 100
                        }
                        package_data['classes'].append(class_data)
                
                coverage_data['packages'].append(package_data)
        
        return coverage_data
        
    except Exception as e:
        print(f"Error parsing coverage XML: {e}")
        return {}


def parse_junit_xml(junit_files: List[str]) -> Dict[str, Any]:
    """Parse JUnit XML test results."""
    test_data = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'error_tests': 0,
        'total_time': 0.0,
        'test_suites': []
    }
    
    for junit_file in junit_files:
        if not Path(junit_file).exists():
            continue
            
        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()
            
            # Handle both testsuite and testsuites root elements
            if root.tag == 'testsuites':
                testsuites = root.findall('testsuite')
            else:
                testsuites = [root]
            
            for testsuite in testsuites:
                suite_data = {
                    'name': testsuite.get('name', ''),
                    'tests': int(testsuite.get('tests', 0)),
                    'failures': int(testsuite.get('failures', 0)),
                    'errors': int(testsuite.get('errors', 0)),
                    'skipped': int(testsuite.get('skipped', 0)),
                    'time': float(testsuite.get('time', 0)),
                    'test_cases': []
                }
                
                test_data['total_tests'] += suite_data['tests']
                test_data['failed_tests'] += suite_data['failures']
                test_data['error_tests'] += suite_data['errors']
                test_data['skipped_tests'] += suite_data['skipped']
                test_data['total_time'] += suite_data['time']
                
                # Parse individual test cases
                for testcase in testsuite.findall('testcase'):
                    case_data = {
                        'name': testcase.get('name', ''),
                        'classname': testcase.get('classname', ''),
                        'time': float(testcase.get('time', 0)),
                        'status': 'passed'
                    }
                    
                    if testcase.find('failure') is not None:
                        case_data['status'] = 'failed'
                        case_data['failure_message'] = testcase.find('failure').text
                    elif testcase.find('error') is not None:
                        case_data['status'] = 'error'
                        case_data['error_message'] = testcase.find('error').text
                    elif testcase.find('skipped') is not None:
                        case_data['status'] = 'skipped'
                        case_data['skip_message'] = testcase.find('skipped').text
                    
                    suite_data['test_cases'].append(case_data)
                
                test_data['test_suites'].append(suite_data)
        
        except Exception as e:
            print(f"Error parsing JUnit XML {junit_file}: {e}")
    
    test_data['passed_tests'] = test_data['total_tests'] - test_data['failed_tests'] - test_data['error_tests'] - test_data['skipped_tests']
    return test_data


def parse_performance_json(performance_file: str) -> Dict[str, Any]:
    """Parse performance benchmark JSON."""
    if not Path(performance_file).exists():
        return {}
    
    try:
        with open(performance_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error parsing performance JSON: {e}")
        return {}


def parse_security_json(security_file: str) -> Dict[str, Any]:
    """Parse security scan JSON results."""
    if not Path(security_file).exists():
        return {}
    
    try:
        with open(security_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error parsing security JSON: {e}")
        return {}


def generate_html_report(
    coverage_data: Dict[str, Any],
    test_data: Dict[str, Any],
    performance_data: Dict[str, Any],
    security_data: Dict[str, Any],
    output_dir: str
) -> None:
    """Generate comprehensive HTML report."""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenMAS Comprehensive Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .metric-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007acc; }
        .metric-label { color: #666; margin-top: 5px; }
        .status-passed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-warning { color: #ffc107; }
        .progress-bar { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background-color: #007acc; transition: width 0.3s ease; }
        .table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .table th, .table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        .table th { background-color: #f8f9fa; font-weight: bold; }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; }
        .alert-success { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
        .alert-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; color: #856404; }
        .alert-danger { background-color: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OpenMAS Comprehensive Test Report</h1>
            <p>Generated on {timestamp}</p>
        </div>
        
        {coverage_section}
        {test_section}
        {performance_section}
        {security_section}
        
        <div class="section">
            <h2>Summary</h2>
            {summary_section}
        </div>
    </div>
</body>
</html>
"""
    
    # Generate sections
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    coverage_section = generate_coverage_section(coverage_data)
    test_section = generate_test_section(test_data)
    performance_section = generate_performance_section(performance_data)
    security_section = generate_security_section(security_data)
    summary_section = generate_summary_section(coverage_data, test_data, performance_data, security_data)
    
    html_content = html_template.format(
        timestamp=timestamp,
        coverage_section=coverage_section,
        test_section=test_section,
        performance_section=performance_section,
        security_section=security_section,
        summary_section=summary_section
    )
    
    # Write HTML report
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "index.html", 'w') as f:
        f.write(html_content)


def generate_coverage_section(coverage_data: Dict[str, Any]) -> str:
    """Generate coverage section HTML."""
    if not coverage_data:
        return '<div class="section"><h2>Code Coverage</h2><p>No coverage data available.</p></div>'
    
    line_rate = coverage_data.get('line_rate', 0)
    branch_rate = coverage_data.get('branch_rate', 0)
    
    status_class = "status-passed" if line_rate >= 85 else "status-warning" if line_rate >= 70 else "status-failed"
    
    return f"""
    <div class="section">
        <h2>Code Coverage</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value {status_class}">{line_rate:.1f}%</div>
                <div class="metric-label">Line Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{branch_rate:.1f}%</div>
                <div class="metric-label">Branch Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{coverage_data.get('lines_covered', 0)}</div>
                <div class="metric-label">Lines Covered</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{coverage_data.get('lines_valid', 0)}</div>
                <div class="metric-label">Total Lines</div>
            </div>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {line_rate}%"></div>
        </div>
    </div>
    """


def generate_test_section(test_data: Dict[str, Any]) -> str:
    """Generate test results section HTML."""
    if not test_data or test_data.get('total_tests', 0) == 0:
        return '<div class="section"><h2>Test Results</h2><p>No test data available.</p></div>'
    
    total = test_data['total_tests']
    passed = test_data['passed_tests']
    failed = test_data['failed_tests']
    errors = test_data['error_tests']
    skipped = test_data['skipped_tests']
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    status_class = "status-passed" if failed == 0 and errors == 0 else "status-failed"
    
    return f"""
    <div class="section">
        <h2>Test Results</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value {status_class}">{pass_rate:.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-passed">{passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-failed">{failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-failed">{errors}</div>
                <div class="metric-label">Errors</div>
            </div>
        </div>
    </div>
    """


def generate_performance_section(performance_data: Dict[str, Any]) -> str:
    """Generate performance section HTML."""
    if not performance_data:
        return '<div class="section"><h2>Performance</h2><p>No performance data available.</p></div>'
    
    benchmarks = performance_data.get('benchmarks', [])
    if not benchmarks:
        return '<div class="section"><h2>Performance</h2><p>No benchmark data available.</p></div>'
    
    return f"""
    <div class="section">
        <h2>Performance Benchmarks</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{len(benchmarks)}</div>
                <div class="metric-label">Benchmarks</div>
            </div>
        </div>
        <table class="table">
            <thead>
                <tr>
                    <th>Benchmark</th>
                    <th>Mean Time (s)</th>
                    <th>Std Dev</th>
                    <th>Min Time</th>
                    <th>Max Time</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td>{b['name']}</td><td>{b.get('stats', {}).get('mean', 0):.4f}</td><td>{b.get('stats', {}).get('stddev', 0):.4f}</td><td>{b.get('stats', {}).get('min', 0):.4f}</td><td>{b.get('stats', {}).get('max', 0):.4f}</td></tr>" for b in benchmarks])}
            </tbody>
        </table>
    </div>
    """


def generate_security_section(security_data: Dict[str, Any]) -> str:
    """Generate security section HTML."""
    if not security_data:
        return '<div class="section"><h2>Security Scan</h2><p>No security data available.</p></div>'
    
    results = security_data.get('results', [])
    high_issues = len([r for r in results if r.get('issue_severity') == 'HIGH'])
    medium_issues = len([r for r in results if r.get('issue_severity') == 'MEDIUM'])
    low_issues = len([r for r in results if r.get('issue_severity') == 'LOW'])
    
    status_class = "status-passed" if high_issues == 0 else "status-failed"
    
    return f"""
    <div class="section">
        <h2>Security Scan</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value {status_class}">{high_issues}</div>
                <div class="metric-label">High Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-warning">{medium_issues}</div>
                <div class="metric-label">Medium Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{low_issues}</div>
                <div class="metric-label">Low Issues</div>
            </div>
        </div>
    </div>
    """


def generate_summary_section(coverage_data, test_data, performance_data, security_data) -> str:
    """Generate summary section HTML."""
    alerts = []
    
    # Coverage alerts
    line_rate = coverage_data.get('line_rate', 0)
    if line_rate < 85:
        alerts.append(f'<div class="alert alert-warning">⚠️ Code coverage ({line_rate:.1f}%) is below the 85% threshold.</div>')
    else:
        alerts.append(f'<div class="alert alert-success">✅ Code coverage ({line_rate:.1f}%) meets the 85% threshold.</div>')
    
    # Test alerts
    failed_tests = test_data.get('failed_tests', 0)
    error_tests = test_data.get('error_tests', 0)
    if failed_tests > 0 or error_tests > 0:
        alerts.append(f'<div class="alert alert-danger">❌ {failed_tests + error_tests} test(s) failed or had errors.</div>')
    else:
        alerts.append('<div class="alert alert-success">✅ All tests passed successfully.</div>')
    
    # Security alerts
    high_issues = len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'HIGH'])
    if high_issues > 0:
        alerts.append(f'<div class="alert alert-danger">🔒 {high_issues} high-severity security issue(s) detected.</div>')
    else:
        alerts.append('<div class="alert alert-success">🔒 No high-severity security issues detected.</div>')
    
    return ''.join(alerts)


def generate_markdown_summary(coverage_data, test_data, performance_data, security_data, output_dir: str) -> None:
    """Generate markdown summary for PR comments."""
    
    summary_lines = [
        "# 📊 OpenMAS Test Report Summary",
        "",
        "## Coverage",
        f"- **Line Coverage**: {coverage_data.get('line_rate', 0):.1f}%",
        f"- **Branch Coverage**: {coverage_data.get('branch_rate', 0):.1f}%",
        "",
        "## Tests",
        f"- **Total**: {test_data.get('total_tests', 0)}",
        f"- **Passed**: {test_data.get('passed_tests', 0)} ✅",
        f"- **Failed**: {test_data.get('failed_tests', 0)} ❌",
        f"- **Errors**: {test_data.get('error_tests', 0)} ⚠️",
        "",
        "## Performance",
        f"- **Benchmarks**: {len(performance_data.get('benchmarks', []))}",
        "",
        "## Security",
        f"- **High Issues**: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'HIGH'])}",
        f"- **Medium Issues**: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'MEDIUM'])}",
        f"- **Low Issues**: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'LOW'])}",
        ""
    ]
    
    # Add status indicators
    line_rate = coverage_data.get('line_rate', 0)
    failed_tests = test_data.get('failed_tests', 0) + test_data.get('error_tests', 0)
    high_security = len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'HIGH'])
    
    if line_rate >= 85 and failed_tests == 0 and high_security == 0:
        summary_lines.insert(1, "## ✅ All Quality Gates Passed")
    else:
        summary_lines.insert(1, "## ⚠️ Quality Gate Issues Detected")
        if line_rate < 85:
            summary_lines.insert(2, f"- Coverage below 85% threshold ({line_rate:.1f}%)")
        if failed_tests > 0:
            summary_lines.insert(2, f"- {failed_tests} test failures")
        if high_security > 0:
            summary_lines.insert(2, f"- {high_security} high-severity security issues")
    
    summary_lines.append("")
    
    # Write summary
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "summary.md", 'w') as f:
        f.write('\n'.join(summary_lines))


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive test report")
    parser.add_argument("--output-dir", required=True, help="Output directory for reports")
    parser.add_argument("--coverage-xml", help="Coverage XML file")
    parser.add_argument("--junit-xml", action="append", help="JUnit XML files (can be specified multiple times)")
    parser.add_argument("--performance-json", help="Performance benchmark JSON file")
    parser.add_argument("--security-json", help="Security scan JSON file")
    
    args = parser.parse_args()
    
    # Parse all data sources
    coverage_data = parse_coverage_xml(args.coverage_xml) if args.coverage_xml else {}
    test_data = parse_junit_xml(args.junit_xml or [])
    performance_data = parse_performance_json(args.performance_json) if args.performance_json else {}
    security_data = parse_security_json(args.security_json) if args.security_json else {}
    
    # Generate reports
    print(f"Generating comprehensive test report in {args.output_dir}")
    
    generate_html_report(coverage_data, test_data, performance_data, security_data, args.output_dir)
    generate_markdown_summary(coverage_data, test_data, performance_data, security_data, args.output_dir)
    
    print("✅ Test report generation completed")
    
    # Print summary to console
    print("\n📊 Report Summary:")
    print(f"  Coverage: {coverage_data.get('line_rate', 0):.1f}%")
    print(f"  Tests: {test_data.get('passed_tests', 0)}/{test_data.get('total_tests', 0)} passed")
    print(f"  Performance: {len(performance_data.get('benchmarks', []))} benchmarks")
    print(f"  Security: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'HIGH'])} high-severity issues")


if __name__ == "__main__":
    main()
