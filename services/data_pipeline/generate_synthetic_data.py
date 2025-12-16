"""
Synthetic Data Pipeline Phase 1
Generate realistic university course enrollment data using Python standard library only.
"""
"""
what is the purpose of this code, why are we generating synthetic data?
Synthetic data is data that is created to look like real data, but is not real data.
It is used to test and **validate the data pipeline**.
It is also used to generate data for **training and testing machine learning models**.
"""

import csv
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any #allows for type hinting


def generate_terms(start_year: int, end_year: int) -> List[Dict[str, Any]]:
    """
    Generate academic terms (Fall/Spring by year).
    
    Args:
        start_year: Starting year (e.g., 2020)
        end_year: Ending year (e.g., 2025)
    
    Returns:
        List of term dictionaries with term_id, term_name, year, semester, start_date, end_date
    """
    terms = []
    term_id = 1
    
    for year in range(start_year, end_year + 1):
        # Fall semester: August to December
        fall_start = datetime(year, 8, 15)
        fall_end = datetime(year, 12, 15)
        terms.append({
            'term_id': term_id,
            'term_name': f'Fall {year}',
            'year': year,
            'semester': 'Fall',
            'start_date': fall_start.strftime('%Y-%m-%d'),
            'end_date': fall_end.strftime('%Y-%m-%d')
        })
        term_id += 1
        
        # Spring semester: January to May
        spring_start = datetime(year + 1, 1, 10) #adding 1 yr for the next sem
        spring_end = datetime(year + 1, 5, 10)
        terms.append({
            'term_id': term_id,
            'term_name': f'Spring {year + 1}',
            'year': year + 1,
            'semester': 'Spring',
            'start_date': spring_start.strftime('%Y-%m-%d'), #format the date to YYYY-MM-DD
            'end_date': spring_end.strftime('%Y-%m-%d')
        })
        term_id += 1
    
    return terms


def generate_departments(num_departments: int) -> List[Dict[str, str]]:
    """
    Generate department codes and names.
    
    Args:
        num_departments: Number of departments to generate
    
    Returns:
        List of department dictionaries with code and name
    """
    common_departments = [
        ('CS', 'Computer Science'),
        ('MATH', 'Mathematics'),
        ('ENGL', 'English'),
        ('HIST', 'History'),
        ('BIOL', 'Biology'),
        ('CHEM', 'Chemistry'),
        ('PHYS', 'Physics'),
        ('PSYC', 'Psychology'),
        ('ECON', 'Economics'),
        ('PHIL', 'Philosophy'),
        ('ART', 'Art'),
        ('MUS', 'Music'),
        ('POL', 'Political Science'),
        ('SOC', 'Sociology'),
        ('BUS', 'Business'),
        ('ENG', 'Engineering'),
        ('EDU', 'Education'),
        ('NURS', 'Nursing'),
        ('COMM', 'Communications'),
        ('LANG', 'Languages')
    ]
    
    # Use common departments first, then generate additional ones if needed
    departments = common_departments[:num_departments]
    
    # If we need more, generate generic ones
    if num_departments > len(common_departments):
        for i in range(len(common_departments), num_departments):
            dept_code = f'DEPT{i:02d}'
            dept_name = f'Department {i}'
            departments.append((dept_code, dept_name))
    
    return [{'code': code, 'name': name} for code, name in departments]


def generate_courses(departments: List[Dict[str, str]], num_courses: int) -> List[Dict[str, Any]]:
    """
    Generate course catalog with detailed attributes.
    
    Args:
        departments: List of department dictionaries
        num_courses: Total number of courses to generate
    
    Returns:
        List of course dictionaries with all required fields
    """
    courses = []
    course_id = 1
    
    # Course level distributions
    levels = ['Undergraduate', 'Graduate', 'Mixed']
    level_weights = [0.7, 0.2, 0.1]  # 70% undergrad, 20% grad, 10% mixed
    
    # Common course titles by department type
    course_templates = {
        'STEM': ['Introduction to', 'Advanced', 'Principles of', 'Fundamentals of', 
                 'Topics in', 'Special Topics in', 'Research Methods in'],
        'HUMANITIES': ['Introduction to', 'Survey of', 'History of', 'Topics in',
                      'Advanced Studies in', 'Seminar in', 'Readings in'],
        'SOCIAL': ['Introduction to', 'Principles of', 'Survey of', 'Topics in',
                  'Advanced', 'Research Methods in', 'Seminar in']
    }
    
    # Classify departments
    stem_depts = ['CS', 'MATH', 'BIOL', 'CHEM', 'PHYS', 'ENG']
    humanities_depts = ['ENGL', 'HIST', 'PHIL', 'ART', 'MUS', 'LANG']
    
    # This loop iterates through each department to assign courses to them.
    # Loop through each department. For each one, we calculate how many courses should be assigned to it.
    # The 'base number of courses' is the even share every department should get if we divide num_courses by the number of departments (ignoring remainder).
    # Any leftover courses (the remainder) are assigned to the first department in the list.
    for dept in departments:
        dept_code = dept['code']
        num_dept_courses = num_courses // len(departments) #there could be remainder due to integer division
        remaining = num_courses - (num_dept_courses * len(departments)) #leftover goes to first department
        
        # Distribute remaining courses
        if dept == departments[0]:
            num_dept_courses += remaining
        
        # Determine course type
        # If the current department code is in the list of STEM departments,
        # For example, for a STEM department with code 'CS', select the STEM templates list; 
        # For the subject in the course title, use the first word of the department name if it contains spaces 
        # (e.g., "Computer Science" -> "Computer"), otherwise use the department name as is.
        # otherwise use the full name. This 'subject' is combined with templates to construct course titles.
        if dept_code in stem_depts:
            templates = course_templates['STEM']
            subject = dept['name'].split()[0] if ' ' in dept['name'] else dept['name']
        elif dept_code in humanities_depts:
            templates = course_templates['HUMANITIES']
            subject = dept['name']
        else:
            templates = course_templates['SOCIAL']
            subject = dept['name']
        
        for i in range(num_dept_courses):
            # Course number: 100-499 for undergrad, 500-699 for grad
            level = random.choices(levels, weights=level_weights)[0]
            if level == 'Undergraduate':
                course_num = random.randint(100, 499)
            elif level == 'Graduate':
                course_num = random.randint(500, 699)
            else:  # Mixed
                course_num = random.randint(300, 499)
            
            # Generate title
            # random.choice picks a single random element from the sequence 'templates'
            template = random.choice(templates)
            title = f"{template} {subject}"
            if course_num >= 400:
                title = f"Advanced {title}"
            
            # Credits: typically 3, sometimes 1, 2, or 4
            credits = random.choices([1, 2, 3, 4], weights=[0.05, 0.1, 0.75, 0.1])[0]
            
            # Prerequisites: 30% have prerequisites
            has_prereq = random.random() < 0.3
            if has_prereq and course_num >= 200:
                prereq_course_num = random.randint(100, course_num - 1)
                prerequisites = f"{dept_code}{prereq_course_num}"
            else:
                prerequisites = ""
            
            # Capacity and typical enrollment ranges
            # STEM courses typically higher capacity
            if dept_code in stem_depts:
                max_capacity = random.randint(30, 150)
                typical_min = int(max_capacity * 0.6)
                typical_max = int(max_capacity * 0.95)
            elif dept_code in humanities_depts:
                max_capacity = random.randint(15, 40)
                typical_min = int(max_capacity * 0.4)
                typical_max = int(max_capacity * 0.9)
            else:
                max_capacity = random.randint(20, 60)
                typical_min = int(max_capacity * 0.5)
                typical_max = int(max_capacity * 0.9)
            
            courses.append({
                'course_id': course_id,
                'department': dept_code,
                'course_number': course_num,
                'title': title,
                'credits': credits,
                'level': level,
                'prerequisites': prerequisites,
                'max_capacity': max_capacity,
                'typical_enrollment_min': typical_min,
                'typical_enrollment_max': typical_max
            })
            course_id += 1
    
    return courses


def generate_sections(courses: List[Dict[str, Any]], terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate section offerings per course per term.
    Not all courses are offered every term.
    
    Args:
        courses: List of course dictionaries
        terms: List of term dictionaries
    
    Returns:
        List of section dictionaries
    """
    sections = []
    section_id = 1
    
    # 60% of courses are popular (offered every term), 40% are occasional (2-3 terms per year)
    popular_courses = random.sample(courses, int(len(courses) * 0.6))
    occasional_courses = [c for c in courses if c not in popular_courses]
    
    # Generate sections for popular courses (every term)
    for course in popular_courses:
        for term in terms:
            # Some popular courses might have multiple sections
            num_sections = 1
            if random.random() < 0.2:  # 20% chance of multiple sections
                num_sections = random.randint(2, 3)
            
            for section_num in range(1, num_sections + 1):
                # Capacity might vary slightly per section
                capacity_variance = random.randint(-5, 5)
                capacity = max(10, course['max_capacity'] + capacity_variance)
                
                # Generate instructor name
                first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 
                              'Robert', 'Jessica', 'William', 'Ashley', 'James', 'Amanda']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                             'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez']
                instructor = f"{random.choice(first_names)} {random.choice(last_names)}"
                
                sections.append({
                    'section_id': section_id,
                    'course_id': course['course_id'],
                    'term_id': term['term_id'],
                    'section_number': section_num,
                    'capacity': capacity,
                    'instructor_name': instructor
                })
                section_id += 1
    
    # Generate sections for occasional courses (2-3 terms per year)
    for course in occasional_courses:
        # Randomly select 2-3 terms per year
        terms_per_year = random.randint(2, 3)
        # random.sample returns a new list with k unique elements chosen from the sequence given (here, terms).
        # Randomly select a subset of terms for this course (2-3 terms, or total available if fewer)
        selected_terms = random.sample(terms, min(terms_per_year, len(terms)))
        
        for term in selected_terms:
            capacity_variance = random.randint(-5, 5)
            capacity = max(10, course['max_capacity'] + capacity_variance)
            
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
            instructor = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            sections.append({
                'section_id': section_id,
                'course_id': course['course_id'],
                'term_id': term['term_id'],
                'section_number': 1,
                'capacity': capacity,
                'instructor_name': instructor
            })
            section_id += 1
    
    return sections


def apply_trend(base_value: float, term_index: int, trend_type: str) -> float:
    """
    Apply upward/downward trends to enrollment values.
    
    Args:
        base_value: Base enrollment value
        term_index: Index of term (0-based)
        trend_type: 'upward', 'downward', or 'stable'
    
    Returns:
        Adjusted value with trend applied
    """
    if trend_type == 'upward':
        # Gradual increase: 2-5% per term
        multiplier = 1 + (term_index * random.uniform(0.02, 0.05))
    elif trend_type == 'downward':
        # Gradual decrease: 1-3% per term
        multiplier = 1 - (term_index * random.uniform(0.01, 0.03))
    else:  # stable
        # Small random variation
        multiplier = random.uniform(0.95, 1.05)
    
    return base_value * multiplier


def apply_seasonality(base_value: float, semester: str) -> float:
    """
    Apply seasonality: Fall enrollment ~1.15x Spring enrollment.
    
    Args:
        base_value: Base enrollment value
        semester: 'Fall' or 'Spring'
    
    Returns:
        Adjusted value with seasonality applied
    """
    if semester == 'Fall':
        return base_value * random.uniform(1.10, 1.20)  # 10-20% higher
    else:  # Spring
        return base_value * random.uniform(0.85, 0.95)  # 5-15% lower


def apply_capacity_constraints(enrollment: float, capacity: int) -> tuple[int, int]:
    """
    Cap enrollments and generate waitlists.
    70-90% of sections hit capacity, 10-30% have waitlists.
    
    Args:
        enrollment: Calculated enrollment value
        capacity: Section capacity
    
    Returns:
        Tuple of (enrollment_count, waitlist_count)
    """
    # Determine if section hits capacity
    hits_capacity = random.random() < 0.8  # 80% hit capacity
    
    if hits_capacity:
        enrollment_count = capacity
        # 10-30% have waitlists
        has_waitlist = random.random() < 0.2  # 20% have waitlists
        if has_waitlist:
            waitlist_count = random.randint(1, int(capacity * 0.3))
        else:
            waitlist_count = 0
    else:
        # Enrollment below capacity
        enrollment_count = max(1, int(enrollment))
        if enrollment_count > capacity:
            enrollment_count = capacity
            waitlist_count = random.randint(1, int(capacity * 0.2))
        else:
            waitlist_count = 0
    
    return (enrollment_count, waitlist_count)


def generate_realistic_enrollment(course: Dict[str, Any], term: Dict[str, Any], 
                                  historical_data: Dict[int, List[float]]) -> tuple[int, int]:
    """
    Combine all patterns to generate realistic enrollment.
    
    Args:
        course: Course dictionary
        term: Term dictionary
        historical_data: Dictionary mapping course_id to list of historical enrollments
    
    Returns:
        Tuple of (enrollment_count, waitlist_count)
    """
    course_id = course['course_id']
    # This line counts how many previous enrollment values exist for this course in historical_data.
    # It's used as a "term index" to track which number term is being generated for this course.
    # For example, if 3 enrollment values already exist, this will be 3 and the new value will be the 4th.
    term_index = len([t for t in historical_data.get(course_id, [])])
    
    # Base enrollment from typical range
    base_enrollment = random.uniform(
        course['typical_enrollment_min'],
        course['typical_enrollment_max']
    )
    
    # Determine trend type: 30% upward, 20% downward, 50% stable
    trend_roll = random.random()
    if trend_roll < 0.3:
        trend_type = 'upward'
    elif trend_roll < 0.5:
        trend_type = 'downward'
    else:
        trend_type = 'stable'
    
    # Apply trend
    enrollment = apply_trend(base_enrollment, term_index, trend_type)
    
    # Apply seasonality
    enrollment = apply_seasonality(enrollment, term['semester'])
    
    # Add some random noise
    enrollment = enrollment * random.uniform(0.9, 1.1)
    
    # Apply capacity constraints
    enrollment_count, waitlist_count = apply_capacity_constraints(
        enrollment, course['max_capacity']
    )
    
    # Store historical data
    if course_id not in historical_data:
        historical_data[course_id] = []
    historical_data[course_id].append(enrollment_count)
    
    return (enrollment_count, waitlist_count)


def generate_enrollments(sections: List[Dict[str, Any]], terms: List[Dict[str, Any]], 
                         courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate enrollment data per section with realistic patterns.
    
    Args:
        sections: List of section dictionaries
        terms: List of term dictionaries
        courses: List of course dictionaries (for lookup)
    
    Returns:
        List of enrollment dictionaries
    """
    enrollments = []
    # historical_data keeps a running record of enrollment numbers for each course across multiple terms.
    # This allows the synthetic data generator to introduce time-based trends and dependencies,
    # so that enrollments in later terms for the same course can be based on historical patterns rather than being totally random.
    historical_data = {}
    
    # Create course lookup
    course_lookup = {c['course_id']: c for c in courses}
    term_lookup = {t['term_id']: t for t in terms}
    
    for section in sections:
        course = course_lookup[section['course_id']]
        term = term_lookup[section['term_id']]
        
        # Generate enrollment with patterns
        # In Python, a function can return multiple values as a tuple.
        # Here, generate_realistic_enrollment returns a tuple: (enrollment_count, waitlist_count).
        # We can "unpack" this tuple into two variables on the left of the assignment.
        enrollment_count, waitlist_count = generate_realistic_enrollment(
            course, term, historical_data
        )
        
        # Use section capacity instead of course max_capacity
        enrollment_count, waitlist_count = apply_capacity_constraints(
            enrollment_count, section['capacity']
        )
        
        # Generate enrollment date (typically 1-2 months before term start)
        term_start = datetime.strptime(term['start_date'], '%Y-%m-%d')
        enrollment_date = term_start - timedelta(days=random.randint(30, 60))
        
        enrollments.append({
            'section_id': section['section_id'],
            'term_id': section['term_id'],
            'enrollment_count': enrollment_count,
            'waitlist_count': waitlist_count,
            'enrollment_date': enrollment_date.strftime('%Y-%m-%d')
        })
    
    return enrollments


def write_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]) -> None:
    """
    Write data to CSV file in data/sample/ directory.
    
    Args:
        data: List of dictionaries to write
        filename: Name of CSV file
        fieldnames: List of field names for CSV header
    """
    # Create directory if it doesn't exist
    os.makedirs('data/sample', exist_ok=True)
    
    filepath = os.path.join('data/sample', filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Generated {filepath} with {len(data)} records")


#generate synthetic data onto csvs
def main():
    """
    Orchestrate generation with seeded random for determinism.
    """
    # Set seed for reproducible results
    
    random.seed(42)
    
    # Configuration
    #constant information
    start_year = 2020
    end_year = 2024  # This will generate Fall 2020 through Spring 2025 (10 terms)
    num_departments = 18
    num_courses = 200
    
    #verifiable information
    print("Generating synthetic university course enrollment data...")
    print(f"Configuration: {num_departments} departments, {num_courses} courses")
    print(f"Time period: {start_year} - {end_year + 1}\n")
    
    # Generate terms
    print("Generating terms...")
    terms = generate_terms(start_year, end_year)
    write_csv(terms, 'terms.csv', 
              ['term_id', 'term_name', 'year', 'semester', 'start_date', 'end_date'])
    
    # Generate departments
    print("Generating departments...")
    departments = generate_departments(num_departments)
    
    # Generate courses
    print("Generating courses...")
    courses = generate_courses(departments, num_courses)
    write_csv(courses, 'courses.csv',
              ['course_id', 'department', 'course_number', 'title', 'credits', 
               'level', 'prerequisites', 'max_capacity', 'typical_enrollment_min', 
               'typical_enrollment_max'])
    
    # Generate sections
    print("Generating sections...")
    sections = generate_sections(courses, terms)
    write_csv(sections, 'sections.csv',
              ['section_id', 'course_id', 'term_id', 'section_number', 'capacity', 
               'instructor_name'])
    
    # Generate enrollments
    print("Generating enrollments...")
    enrollments = generate_enrollments(sections, terms, courses)
    write_csv(enrollments, 'enrollments.csv',
              ['section_id', 'term_id', 'enrollment_count', 'waitlist_count', 
               'enrollment_date'])
    
    print("\n✅ Synthetic data generation complete!")
    print(f"   - {len(terms)} terms")
    print(f"   - {len(courses)} courses")
    print(f"   - {len(sections)} sections")
    print(f"   - {len(enrollments)} enrollments")


if __name__ == '__main__':
    main()
