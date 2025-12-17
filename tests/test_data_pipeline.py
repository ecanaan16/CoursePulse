"""
Unit tests for the synthetic data pipeline.

Tests validate data quality, constraints, and realistic patterns.
"""

#pycache is created to store the compiled python files in bytecode
import pytest
import random
import sys
import os
from datetime import datetime

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.data_pipeline.generate_synthetic_data import (
    generate_terms,
    generate_departments,
    generate_courses,
    generate_sections,
    generate_enrollments,
    apply_trend,
    apply_seasonality,
    apply_capacity_constraints,
    generate_realistic_enrollment
)


@pytest.fixture
def seed_random():
    """Fixture to seed random for deterministic tests."""
    random.seed(42)
    yield
    random.seed(None)


@pytest.fixture
def sample_config():
    """Fixture with sample configuration."""
    return {
        'start_year': 2020,
        'end_year': 2024,
        'num_departments': 5,
        'num_courses': 20
    }


class TestTermGeneration:
    """Tests for term generation."""
    
    def test_generate_terms_count(self, seed_random, sample_config):
        """Test that correct number of terms are generated."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        # 5 years * 2 semesters = 10 terms
        assert len(terms) == 10
    
    def test_generate_terms_structure(self, seed_random, sample_config):
        """Test that terms have correct structure and values."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        
        # Check first term
        assert terms[0]['term_name'] == 'Fall 2020'
        assert terms[0]['semester'] == 'Fall'
        assert terms[0]['year'] == 2020
        assert 'term_id' in terms[0]
        assert 'start_date' in terms[0]
        assert 'end_date' in terms[0]
    
    def test_generate_terms_date_validity(self, seed_random, sample_config):
        """Test that term dates are valid (start < end)."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        
        for term in terms:
            start = datetime.strptime(term['start_date'], '%Y-%m-%d')
            end = datetime.strptime(term['end_date'], '%Y-%m-%d')
            assert start < end, f"Term {term['term_name']} has invalid date range"
    
    def test_generate_terms_semester_alternation(self, seed_random, sample_config):
        """Test that terms alternate between Fall and Spring."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        
        for i, term in enumerate(terms):
            if i % 2 == 0:
                assert term['semester'] == 'Fall', f"Term {i} should be Fall"
            else:
                assert term['semester'] == 'Spring', f"Term {i} should be Spring"


class TestCourseGeneration:
    """Tests for course generation."""
    
    def test_generate_courses_count(self, seed_random, sample_config):
        """Test that correct number of courses are generated."""
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        
        assert len(courses) == sample_config['num_courses']
    
    def test_course_number_matches_level(self, seed_random, sample_config):
        """Test that course numbers match their level."""
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        
        for course in courses:
            if course['level'] == 'Undergraduate':
                assert 100 <= course['course_number'] < 500, \
                    f"Undergraduate course {course['course_id']} has invalid number"
            elif course['level'] == 'Graduate':
                assert 500 <= course['course_number'] < 700, \
                    f"Graduate course {course['course_id']} has invalid number"
            elif course['level'] == 'Mixed':
                assert 300 <= course['course_number'] < 500, \
                    f"Mixed course {course['course_id']} has invalid number"
    
    def test_course_capacity_constraints(self, seed_random, sample_config):
        """Test that course capacity ranges are valid."""
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        
        for course in courses:
            assert course['typical_enrollment_min'] <= course['typical_enrollment_max'], \
                f"Course {course['course_id']} has invalid enrollment range"
            assert course['typical_enrollment_max'] <= course['max_capacity'], \
                f"Course {course['course_id']} enrollment max exceeds capacity"
            assert course['max_capacity'] > 0, \
                f"Course {course['course_id']} has non-positive capacity"
    
    def test_course_credits_valid(self, seed_random, sample_config):
        """Test that course credits are valid values."""
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        
        for course in courses:
            assert course['credits'] in [1, 2, 3, 4], \
                f"Course {course['course_id']} has invalid credits: {course['credits']}"
    
    def test_courses_distributed_across_departments(self, seed_random, sample_config):
        """Test that courses are distributed across departments."""
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        
        dept_course_counts = {}
        for course in courses:
            dept = course['department']
            dept_course_counts[dept] = dept_course_counts.get(dept, 0) + 1
        
        # Each department should have at least some courses
        assert len(dept_course_counts) == sample_config['num_departments']
        assert all(count > 0 for count in dept_course_counts.values())


class TestSectionGeneration:
    """Tests for section generation."""
    
    def test_sections_reference_valid_courses(self, seed_random, sample_config):
        """Test that sections reference valid course IDs."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        
        course_ids = {c['course_id'] for c in courses}
        
        for section in sections:
            assert section['course_id'] in course_ids, \
                f"Section {section['section_id']} references invalid course_id"
    
    def test_sections_reference_valid_terms(self, seed_random, sample_config):
        """Test that sections reference valid term IDs."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        
        term_ids = {t['term_id'] for t in terms}
        
        for section in sections:
            assert section['term_id'] in term_ids, \
                f"Section {section['section_id']} references invalid term_id"
    
    def test_section_capacity_positive(self, seed_random, sample_config):
        """Test that section capacities are positive."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        
        for section in sections:
            assert section['capacity'] > 0, \
                f"Section {section['section_id']} has non-positive capacity"


class TestEnrollmentGeneration:
    """Tests for enrollment generation."""
    
    def test_enrollments_respect_capacity(self, seed_random, sample_config):
        """Test that enrollments never exceed section capacity."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        enrollments = generate_enrollments(sections, terms, courses)
        
        section_lookup = {s['section_id']: s for s in sections}
        
        for enrollment in enrollments:
            section = section_lookup[enrollment['section_id']]
            capacity = section['capacity']
            
            assert enrollment['enrollment_count'] <= capacity, \
                f"Enrollment {enrollment['section_id']} exceeds capacity"
            assert enrollment['enrollment_count'] > 0, \
                f"Enrollment {enrollment['section_id']} is non-positive"
    
    def test_waitlist_only_when_at_capacity(self, seed_random, sample_config):
        """Test that waitlists only exist when enrollment equals capacity."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        enrollments = generate_enrollments(sections, terms, courses)
        
        section_lookup = {s['section_id']: s for s in sections}
        
        for enrollment in enrollments:
            section = section_lookup[enrollment['section_id']]
            capacity = section['capacity']
            
            if enrollment['waitlist_count'] > 0:
                assert enrollment['enrollment_count'] == capacity, \
                    f"Waitlist exists but enrollment {enrollment['section_id']} not at capacity"
    
    def test_enrollments_reference_valid_sections(self, seed_random, sample_config):
        """Test that enrollments reference valid section IDs."""
        terms = generate_terms(sample_config['start_year'], sample_config['end_year'])
        departments = generate_departments(sample_config['num_departments'])
        courses = generate_courses(departments, sample_config['num_courses'])
        sections = generate_sections(courses, terms)
        enrollments = generate_enrollments(sections, terms, courses)
        
        section_ids = {s['section_id'] for s in sections}
        
        for enrollment in enrollments:
            assert enrollment['section_id'] in section_ids, \
                f"Enrollment references invalid section_id"


class TestPatterns:
    """Tests for enrollment patterns (trends, seasonality, etc.)."""
    
    def test_seasonality_fall_higher(self, seed_random):
        """Test that Fall enrollment is generally higher than Spring."""
        base_value = 100
        fall_values = [apply_seasonality(base_value, 'Fall') for _ in range(100)]
        spring_values = [apply_seasonality(base_value, 'Spring') for _ in range(100)]
        
        fall_avg = sum(fall_values) / len(fall_values)
        spring_avg = sum(spring_values) / len(spring_values)
        
        assert fall_avg > spring_avg, \
            f"Fall average ({fall_avg}) should be higher than Spring average ({spring_avg})"
    
    @pytest.mark.parametrize("semester,expected_higher", [
        ('Fall', True),
        ('Spring', False),
    ])
    def test_seasonality_direction(self, semester, expected_higher, seed_random):
        """Test that seasonality applies in correct direction."""
        base_value = 100
        result = apply_seasonality(base_value, semester)
        
        if expected_higher:
            assert result > base_value, \
                f"{semester} should be higher than base value"
        else:
            assert result < base_value, \
                f"{semester} should be lower than base value"
    
    def test_trend_upward(self, seed_random):
        """Test that upward trend increases over time."""
        base_value = 100
        values = [apply_trend(base_value, i, 'upward') for i in range(10)]
        
        # Later values should generally be higher
        later_avg = sum(values[5:]) / len(values[5:])
        earlier_avg = sum(values[:5]) / len(values[:5])
        
        assert later_avg > earlier_avg, \
            "Upward trend should show increasing values over time"
    
    def test_trend_downward(self, seed_random):
        """Test that downward trend decreases over time."""
        base_value = 100
        values = [apply_trend(base_value, i, 'downward') for i in range(10)]
        
        # Later values should generally be lower
        later_avg = sum(values[5:]) / len(values[5:])
        earlier_avg = sum(values[:5]) / len(values[:5])
        
        assert later_avg < earlier_avg, \
            "Downward trend should show decreasing values over time"
    
    def test_capacity_constraints_enforcement(self, seed_random):
        """Test that capacity constraints cap enrollments correctly."""
        enrollment, waitlist = apply_capacity_constraints(150, 100)
        
        assert enrollment <= 100, "Enrollment should not exceed capacity"
        if waitlist > 0:
            assert enrollment == 100, "Waitlist should only exist when at capacity"


class TestDeterminism:
    """Tests for deterministic behavior with seeded random."""
    
    def test_deterministic_terms(self, sample_config):
        """Test that seeded random produces consistent term generation."""
        random.seed(42)
        terms1 = generate_terms(sample_config['start_year'], sample_config['end_year'])
        
        random.seed(42)
        terms2 = generate_terms(sample_config['start_year'], sample_config['end_year'])
        
        assert terms1 == terms2, "Seeded generation should be deterministic"
    
    def test_deterministic_courses(self, sample_config):
        """Test that seeded random produces consistent course generation."""
        departments = generate_departments(5)
        
        random.seed(42)
        courses1 = generate_courses(departments, 20)
        
        random.seed(42)
        courses2 = generate_courses(departments, 20)
        
        assert courses1 == courses2, "Seeded generation should be deterministic"