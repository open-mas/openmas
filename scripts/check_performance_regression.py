#!/usr/bin/env python3
"""
Performance Regression Checker

Compares current performance results with baseline to detect regressions.
Used in CI/CD pipeline for automated performance monitoring.
"""

import json
import argparse
import sys
from typing import Dict, Any, List
from pathlib import Path


def load_benchmark_results(file_path: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def compare_benchmarks(current: Dict[str, Any], baseline: Dict[str, Any], tolerance: float) -> Dict[str, Any]:
    """Compare current benchmarks with baseline."""
    comparison = {
        'regressions': [],
        'improvements': [],
        'new_benchmarks': [],
        'missing_benchmarks': [],
        'summary': {}
    }
    
    current_benchmarks = current.get('benchmarks', [])
    baseline_benchmarks = baseline.get('benchmarks', [])
    
    # Create lookup dictionaries
    current_lookup = {b['name']: b for b in current_benchmarks}
    baseline_lookup = {b['name']: b for b in baseline_benchmarks}
    
    # Find new and missing benchmarks
    current_names = set(current_lookup.keys())
    baseline_names = set(baseline_lookup.keys())
    
    comparison['new_benchmarks'] = list(current_names - baseline_names)
    comparison['missing_benchmarks'] = list(baseline_names - current_names)
    
    # Compare common benchmarks
    common_benchmarks = current_names & baseline_names
    
    for name in common_benchmarks:
        current_bench = current_lookup[name]
        baseline_bench = baseline_lookup[name]
        
        # Compare execution time (lower is better)
        current_time = current_bench.get('stats', {}).get('mean', 0)
        baseline_time = baseline_bench.get('stats', {}).get('mean', 0)
        
        if baseline_time > 0:
            time_change = ((current_time - baseline_time) / baseline_time) * 100
            
            if time_change > tolerance:
                comparison['regressions'].append({
                    'benchmark': name,
                    'metric': 'execution_time',
                    'current': current_time,
                    'baseline': baseline_time,
                    'change_percent': time_change,
                    'severity': 'high' if time_change > tolerance * 2 else 'medium'
                })
            elif time_change < -tolerance:
                comparison['improvements'].append({
                    'benchmark': name,
                    'metric': 'execution_time',
                    'current': current_time,
                    'baseline': baseline_time,
                    'change_percent': abs(time_change)
                })
        
        # Compare memory usage if available
        current_memory = current_bench.get('extra_info', {}).get('memory_usage_mb', 0)
        baseline_memory = baseline_bench.get('extra_info', {}).get('memory_usage_mb', 0)
        
        if baseline_memory > 0:
            memory_change = ((current_memory - baseline_memory) / baseline_memory) * 100
            
            if memory_change > tolerance:
                comparison['regressions'].append({
                    'benchmark': name,
                    'metric': 'memory_usage',
                    'current': current_memory,
                    'baseline': baseline_memory,
                    'change_percent': memory_change,
                    'severity': 'high' if memory_change > tolerance * 2 else 'medium'
                })
            elif memory_change < -tolerance:
                comparison['improvements'].append({
                    'benchmark': name,
                    'metric': 'memory_usage',
                    'current': current_memory,
                    'baseline': baseline_memory,
                    'change_percent': abs(memory_change)
                })
    
    # Generate summary
    comparison['summary'] = {
        'total_benchmarks': len(current_benchmarks),
        'regressions_count': len(comparison['regressions']),
        'improvements_count': len(comparison['improvements']),
        'new_benchmarks_count': len(comparison['new_benchmarks']),
        'missing_benchmarks_count': len(comparison['missing_benchmarks']),
        'has_regressions': len(comparison['regressions']) > 0
    }
    
    return comparison


def generate_report(comparison: Dict[str, Any], output_file: str = None) -> str:
    """Generate human-readable performance comparison report."""
    report_lines = []
    
    # Header
    report_lines.append("# Performance Regression Report")
    report_lines.append("")
    
    # Summary
    summary = comparison['summary']
    report_lines.append("## Summary")
    report_lines.append(f"- Total benchmarks: {summary['total_benchmarks']}")
    report_lines.append(f"- Regressions detected: {summary['regressions_count']}")
    report_lines.append(f"- Improvements detected: {summary['improvements_count']}")
    report_lines.append(f"- New benchmarks: {summary['new_benchmarks_count']}")
    report_lines.append(f"- Missing benchmarks: {summary['missing_benchmarks_count']}")
    report_lines.append("")
    
    # Regressions
    if comparison['regressions']:
        report_lines.append("## ⚠️ Performance Regressions")
        report_lines.append("")
        
        for regression in comparison['regressions']:
            severity_emoji = "🔴" if regression['severity'] == 'high' else "🟡"
            report_lines.append(f"{severity_emoji} **{regression['benchmark']}** ({regression['metric']})")
            report_lines.append(f"  - Current: {regression['current']:.4f}")
            report_lines.append(f"  - Baseline: {regression['baseline']:.4f}")
            report_lines.append(f"  - Change: +{regression['change_percent']:.1f}%")
            report_lines.append("")
    
    # Improvements
    if comparison['improvements']:
        report_lines.append("## ✅ Performance Improvements")
        report_lines.append("")
        
        for improvement in comparison['improvements']:
            report_lines.append(f"🟢 **{improvement['benchmark']}** ({improvement['metric']})")
            report_lines.append(f"  - Current: {improvement['current']:.4f}")
            report_lines.append(f"  - Baseline: {improvement['baseline']:.4f}")
            report_lines.append(f"  - Improvement: {improvement['change_percent']:.1f}%")
            report_lines.append("")
    
    # New benchmarks
    if comparison['new_benchmarks']:
        report_lines.append("## 🆕 New Benchmarks")
        report_lines.append("")
        for benchmark in comparison['new_benchmarks']:
            report_lines.append(f"- {benchmark}")
        report_lines.append("")
    
    # Missing benchmarks
    if comparison['missing_benchmarks']:
        report_lines.append("## ❓ Missing Benchmarks")
        report_lines.append("")
        for benchmark in comparison['missing_benchmarks']:
            report_lines.append(f"- {benchmark}")
        report_lines.append("")
    
    report = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report written to {output_file}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Check for performance regressions")
    parser.add_argument("--current", required=True, help="Current benchmark results JSON file")
    parser.add_argument("--baseline", required=True, help="Baseline benchmark results JSON file")
    parser.add_argument("--tolerance", type=float, default=10.0, help="Regression tolerance percentage (default: 10.0)")
    parser.add_argument("--output", help="Output report file (optional)")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit with error code if regressions detected")
    parser.add_argument("--json-output", help="Output comparison results as JSON file")
    
    args = parser.parse_args()
    
    # Load benchmark data
    print(f"Loading current results from {args.current}")
    current = load_benchmark_results(args.current)
    
    print(f"Loading baseline results from {args.baseline}")
    baseline = load_benchmark_results(args.baseline)
    
    # Compare benchmarks
    print(f"Comparing benchmarks with {args.tolerance}% tolerance")
    comparison = compare_benchmarks(current, baseline, args.tolerance)
    
    # Generate and display report
    report = generate_report(comparison, args.output)
    print(report)
    
    # Save JSON output if requested
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"JSON comparison saved to {args.json_output}")
    
    # Exit with error if regressions detected and fail-on-regression is set
    if args.fail_on_regression and comparison['summary']['has_regressions']:
        print("❌ Performance regressions detected!")
        sys.exit(1)
    
    if comparison['summary']['has_regressions']:
        print("⚠️ Performance regressions detected, but not failing build")
    else:
        print("✅ No performance regressions detected")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
