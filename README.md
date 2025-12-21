# CoursePulse
Cloud-native decision-support platform for forecasting university course demand and optimizing academic resources.

## Overview

CoursePulse is a synthetic data generation pipeline for creating realistic university course enrollment data. The system generates comprehensive academic datasets including terms, courses, sections, and enrollments with realistic patterns such as seasonality, trends, and capacity constraints.

## Features

- **Synthetic Data Generation**: Generate realistic university course enrollment data using Python standard library only
- **Realistic Patterns**: Includes seasonality (Fall vs Spring), enrollment trends (upward/downward/stable), and capacity constraints
- **Data Validation**: Comprehensive validation ensures data quality and referential integrity
- **Reporting**: Automated report generation with metrics and validation results
- **CI/CD Integration**: Automated testing and validation via GitHub Actions
- **Deterministic Generation**: Seeded random number generation for reproducible results

## Project Structure

```
CoursePulse/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── data/
│   └── sample/                 # Generated CSV files
│       ├── terms.csv
│       ├── courses.csv
│       ├── sections.csv
│       └── enrollments.csv
├── docs/
│   └── data_schema.md          # Data schema documentation
├── reports/                     # Generated validation reports
│   └── latest.json
├── services/
│   └── data_pipeline/
│       ├── generate_synthetic_data.py  # Main data generation script
│       ├── report_run.py               # Report generation
│       └── validate_report.py          # Validation checker
├── tests/
│   └── test_data_pipeline.py   # Comprehensive test suite
├── requirements-dev.txt        # Development dependencies
└── README.md
```

## Development

### Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel test execution

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_data_pipeline.py
```

Run a specific test class:
```bash
pytest tests/test_data_pipeline.py::TestEnrollmentGeneration
```

Run a specific test:
```bash
pytest tests/test_data_pipeline.py::TestEnrollmentGeneration::test_enrollments_respect_capacity
```

Run tests with coverage:
```bash
pytest --cov=services/data_pipeline --cov-report=html
```

The test suite includes:
- Term generation validation
- Course generation and constraints
- Section generation and foreign key validation
- Enrollment generation and capacity constraints
- Pattern testing (seasonality, trends)
- Determinism testing

### Generating Synthetic Data

Run the data generation pipeline:
```bash
python services/data_pipeline/generate_synthetic_data.py
```

This will generate CSV files in `data/sample/`:
- `terms.csv` - Academic terms (Fall/Spring by year)
- `courses.csv` - Course catalog with departments, levels, and capacity info
- `sections.csv` - Section offerings linked to courses and terms
- `enrollments.csv` - Enrollment data with waitlist information

**Default Configuration:**
- Time period: 2020-2024 (10 terms: Fall 2020 through Spring 2025)
- Departments: 18
- Courses: 200
- Random seed: 42 (for reproducibility)

### Validating and Reporting

After generating data, generate a validation report:
```bash
python services/data_pipeline/report_run.py data/sample 42 18 200 0.0
```

Arguments:
- `data/sample` - Directory containing CSV files
- `42` - Random seed used
- `18` - Number of departments
- `200` - Number of courses
- `0.0` - Runtime in seconds (optional)

This generates:
- `reports/latest.json` - Latest validation report
- `reports/report_YYYYMMDD_HHMMSS.json` - Timestamped report

The report includes:
- Data counts (terms, courses, sections, enrollments)
- Validation pass rate and violations
- Enrollment statistics (min/median/max)
- Runtime metrics

Check validation pass rate:
```bash
python services/data_pipeline/validate_report.py
```

This script:
- Reads `reports/latest.json`
- Checks validation pass rate (must be 100%)
- Exits with code 0 (success) or 1 (failure) for CI/CD

## Continuous Integration

The project includes GitHub Actions CI workflow (`.github/workflows/ci.yml`) that automatically:

1. **Runs on**: Pushes and pull requests to `main`, `master`, and `develop` branches
2. **Test Suite**: Executes pytest with verbose output
3. **Data Generation**: Generates synthetic data at medium scale
4. **Validation**: Runs report generation and validates pass rate
5. **Artifacts**: Uploads reports and CSV files (retained for 7 days)

The CI ensures:
- All tests pass
- Data generation works correctly
- Generated data meets quality standards (100% validation pass rate)
- Reports are generated successfully

## Data Quality

The pipeline enforces several data quality constraints:

- **Referential Integrity**: Sections reference valid courses and terms; enrollments reference valid sections
- **Capacity Constraints**: Enrollments never exceed section capacity
- **Waitlist Logic**: Waitlists only exist when enrollment equals capacity
- **Course Numbering**: Course numbers match their level (Undergraduate: 100-499, Graduate: 500-699, Mixed: 300-499)
- **Date Validity**: Term start dates are before end dates
- **Positive Values**: All counts and capacities are positive

## License

[Add your license information here]
