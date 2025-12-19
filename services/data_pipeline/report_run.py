"""
Report generation for synthetic data pipeline runs.

Generates metrics and validation reports, writes to reports/latest.json.
"""
import json
import csv
import os
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple


def read_csv(filepath: str) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries."""
    data = []
    if not os.path.exists(filepath):
        return data
    
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    
    return data


def validate_data(terms: List[Dict], courses: List[Dict], 
                 sections: List[Dict], enrollments: List[Dict]) -> Tuple[int, int]:
    """
    Validate generated data and return (violations, total_rows).
    
    Returns:
        Tuple of (violation_count, total_rows_checked)
    """
    violations = 0
    total_rows = len(terms) + len(courses) + len(sections) + len(enrollments)
    
    # Validate terms
    for term in terms:
        try:
            start = datetime.strptime(term['start_date'], '%Y-%m-%d')
            end = datetime.strptime(term['end_date'], '%Y-%m-%d')
            if start >= end:
                violations += 1
        except (ValueError, KeyError):
            violations += 1
    
    # Validate courses
    course_ids = set()
    for course in courses:
        try:
            course_id = int(course['course_id'])
            if course_id in course_ids:
                violations += 1  # Duplicate course_id
            course_ids.add(course_id)
            
            # Validate capacity constraints
            min_enroll = int(course['typical_enrollment_min'])
            max_enroll = int(course['typical_enrollment_max'])
            capacity = int(course['max_capacity'])
            
            if min_enroll > max_enroll or max_enroll > capacity:
                violations += 1
            
            # Validate course number matches level
            course_num = int(course['course_number'])
            level = course['level']
            if level == 'Undergraduate' and not (100 <= course_num < 500):
                violations += 1
            elif level == 'Graduate' and not (500 <= course_num < 700):
                violations += 1
        except (ValueError, KeyError):
            violations += 1
    
    # Validate sections
    section_ids = set()
    course_ids_set = {int(c['course_id']) for c in courses}
    term_ids_set = {int(t['term_id']) for t in terms}
    
    for section in sections:
        try:
            section_id = int(section['section_id'])
            if section_id in section_ids:
                violations += 1
            section_ids.add(section_id)
            
            # Validate foreign keys
            if int(section['course_id']) not in course_ids_set:
                violations += 1
            if int(section['term_id']) not in term_ids_set:
                violations += 1
            
            # Validate capacity
            if int(section['capacity']) <= 0:
                violations += 1
        except (ValueError, KeyError):
            violations += 1
    
    # Validate enrollments
    section_ids_set = {int(s['section_id']) for s in sections}
    section_capacities = {int(s['section_id']): int(s['capacity']) for s in sections}
    
    for enrollment in enrollments:
        try:
            section_id = int(enrollment['section_id'])
            if section_id not in section_ids_set:
                violations += 1
            
            # Validate enrollment doesn't exceed capacity
            enrollment_count = int(enrollment['enrollment_count'])
            capacity = section_capacities.get(section_id, 0)
            
            if enrollment_count > capacity:
                violations += 1
            
            # Validate waitlist only when at capacity
            waitlist_count = int(enrollment['waitlist_count'])
            if waitlist_count > 0 and enrollment_count != capacity:
                violations += 1
            
            # Validate enrollment is positive
            if enrollment_count <= 0:
                violations += 1
        except (ValueError, KeyError):
            violations += 1
    
    return violations, total_rows


def calculate_enrollment_stats(enrollments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate min/median/max for enrollment and waitlist counts."""
    enrollment_counts = [int(e['enrollment_count']) for e in enrollments]
    waitlist_counts = [int(e['waitlist_count']) for e in enrollments]
    
    stats = {
        'enrollment': {
            'min': min(enrollment_counts) if enrollment_counts else 0,
            'median': int(statistics.median(enrollment_counts)) if enrollment_counts else 0,
            'max': max(enrollment_counts) if enrollment_counts else 0
        },
        'waitlist': {
            'min': min(waitlist_counts) if waitlist_counts else 0,
            'median': int(statistics.median(waitlist_counts)) if waitlist_counts else 0,
            'max': max(waitlist_counts) if waitlist_counts else 0
        }
    }
    
    return stats


def generate_report(data_dir: str = 'data/sample', 
                   seed: int = 42,
                   num_departments: int = 18,
                   num_courses: int = 200,
                   runtime_seconds: float = 0.0) -> Dict[str, Any]:
    """
    Generate report from generated CSV files.
    
    Args:
        data_dir: Directory containing CSV files
        seed: Random seed used for generation
        num_departments: Number of departments generated
        num_courses: Number of courses generated
        runtime_seconds: Generation runtime in seconds
    
    Returns:
        Dictionary containing report data
    """
    # Read CSV files
    terms = read_csv(os.path.join(data_dir, 'terms.csv'))
    courses = read_csv(os.path.join(data_dir, 'courses.csv'))
    sections = read_csv(os.path.join(data_dir, 'sections.csv'))
    enrollments = read_csv(os.path.join(data_dir, 'enrollments.csv'))
    
    # Validate data
    violations, total_rows = validate_data(terms, courses, sections, enrollments)
    validation_pass_rate = ((total_rows - violations) / total_rows * 100) if total_rows > 0 else 100.0
    
    # Calculate enrollment statistics
    enrollment_stats = calculate_enrollment_stats(enrollments)
    
    # Build report
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'seed': seed,
            'scale': {
                'departments': num_departments,
                'courses': num_courses
            }
        },
        'counts': {
            'terms': len(terms),
            'courses': len(courses),
            'sections': len(sections),
            'enrollments': len(enrollments)
        },
        'runtime': {
            'seconds': round(runtime_seconds, 3)
        },
        'validation': {
            'violations': violations,
            'total_rows_checked': total_rows,
            'pass_rate_percent': round(validation_pass_rate, 2)
        },
        'enrollment_stats': enrollment_stats
    }
    
    return report


def write_report(report: Dict[str, Any], output_dir: str = 'reports') -> str:
    """
    Write report to JSON file.
    
    Args:
        report: Report dictionary
        output_dir: Directory to write report to
    
    Returns:
        Path to written report file
    """
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write to latest.json
    latest_path = os.path.join(output_dir, 'latest.json')
    with open(latest_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also write timestamped version
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_path = os.path.join(output_dir, f'report_{timestamp}.json')
    with open(timestamped_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return latest_path


def print_report(report: Dict[str, Any]) -> None:
    """Print formatted report to console."""
    print("\n" + "="*60)
    print("SYNTHETIC DATA GENERATION REPORT")
    print("="*60)
    
    # Metadata
    print(f"\nGenerated: {report['metadata']['generated_at']}")
    print(f"Seed: {report['metadata']['seed']}")
    print(f"Scale: {report['metadata']['scale']['departments']} departments, "
          f"{report['metadata']['scale']['courses']} courses")
    
    # Counts
    print(f"\n📊 Data Counts:")
    print(f"   Terms: {report['counts']['terms']}")
    print(f"   Courses: {report['counts']['courses']}")
    print(f"   Sections: {report['counts']['sections']}")
    print(f"   Enrollments: {report['counts']['enrollments']}")
    
    # Runtime
    print(f"\n⏱️  Runtime: {report['runtime']['seconds']} seconds")
    
    # Validation
    print(f"\n✅ Validation:")
    print(f"   Pass Rate: {report['validation']['pass_rate_percent']}%")
    print(f"   Violations: {report['validation']['violations']} / {report['validation']['total_rows_checked']} rows")
    
    # Enrollment stats
    print(f"\n📈 Enrollment Statistics:")
    print(f"   Enrollment Count:")
    print(f"      Min: {report['enrollment_stats']['enrollment']['min']}")
    print(f"      Median: {report['enrollment_stats']['enrollment']['median']}")
    print(f"      Max: {report['enrollment_stats']['enrollment']['max']}")
    print(f"   Waitlist Count:")
    print(f"      Min: {report['enrollment_stats']['waitlist']['min']}")
    print(f"      Median: {report['enrollment_stats']['waitlist']['median']}")
    print(f"      Max: {report['enrollment_stats']['waitlist']['max']}")
    
    print("\n" + "="*60)


def main():
    """Standalone execution: generate report from existing CSV files."""
    import sys
    
    # Default values
    data_dir = 'data/sample'
    seed = 42
    num_departments = 18
    num_courses = 200
    runtime = 0.0
    
    # Try to read from command line args if provided
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
    if len(sys.argv) > 3:
        num_departments = int(sys.argv[3])
    if len(sys.argv) > 4:
        num_courses = int(sys.argv[4])
    if len(sys.argv) > 5:
        runtime = float(sys.argv[5])
    
    # Generate and save report
    report = generate_report(data_dir, seed, num_departments, num_courses, runtime)
    report_path = write_report(report)
    print_report(report)
    print(f"\n📄 Report saved to: {report_path}")


if __name__ == '__main__':
    main()

