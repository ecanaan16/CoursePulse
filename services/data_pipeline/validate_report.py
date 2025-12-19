"""
Validate report and exit with appropriate code for CI/CD.

Exits with code 0 if validation passes, 1 if it fails.
"""
import json
import sys
import os


def main():
    """Validate report and exit with appropriate code."""
    report_path = os.environ.get('REPORT_PATH', 'reports/latest.json')
    
    if not os.path.exists(report_path):
        print(f"❌ Report file not found: {report_path}")
        sys.exit(1)
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    pass_rate = report['validation']['pass_rate_percent']
    violations = report['validation']['violations']
    total_rows = report['validation']['total_rows_checked']
    
    print(f"Validation Results:")
    print(f"  Pass Rate: {pass_rate}%")
    print(f"  Violations: {violations} / {total_rows} rows")
    
    if pass_rate < 100.0 or violations > 0:
        print(f"❌ Validation failed: {violations} violations, {pass_rate}% pass rate")
        sys.exit(1)
    else:
        print(f"✅ Validation passed: {pass_rate}% pass rate, 0 violations")
        sys.exit(0)


if __name__ == '__main__':
    main()

