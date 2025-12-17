# CoursePulse
Cloud-native decision-support platform for forecasting university course demand and optimizing academic resources.

## Development

### Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

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

### Generating Synthetic Data

Run the data generation pipeline:
```bash
python services/data_pipeline/generate_synthetic_data.py
```

This will generate CSV files in `data/sample/`:
- `terms.csv` - Academic terms
- `courses.csv` - Course catalog
- `sections.csv` - Section offerings
- `enrollments.csv` - Enrollment data
