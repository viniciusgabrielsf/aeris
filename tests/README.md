# Aeris Test Suite

Comprehensive unit tests for the Aeris Air Quality Dashboard project.

## Overview

This test suite provides comprehensive coverage for the core components of the Aeris project:

- **AQI Calculations** (`test_aqi.py`) - Air Quality Index computation and categorization
- **Logging** (`test_logger.py`) - Logging utilities and structured logging

## Quick Start

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Running Specific Test Files

```bash
# Run AQI tests only
pytest tests/test_aqi.py -v

# Run database tests only
pytest tests/test_database.py -v

# Run data collector tests only
pytest tests/test_data_collector.py -v
```

### Running Specific Test Classes or Functions

```bash
# Run specific test class
pytest tests/test_aqi.py::TestAQICalculation -v

# Run specific test function
pytest tests/test_aqi.py::TestAQICalculation::test_pm25_good_range -v

# Run tests matching pattern
pytest -k "pm25" -v
```

## Test Structure

### Test Files

- **`conftest.py`** - Shared fixtures and pytest configuration
- **`test_aqi.py`** - 57 tests for AQI calculation logic
- **`test_logger.py`** - 41 tests for logging functionality

**Total: 98 tests - All passing ✅**

### Fixtures

Common fixtures available in all tests (defined in `conftest.py`):

- **`temp_database`** - Temporary SQLite database for testing
- **`test_db_connection`** - Pre-initialized test database with schema
- **`mock_openaq_locations_response`** - Mock OpenAQ locations API response
- **`mock_openaq_measurements_response`** - Mock OpenAQ measurements API response
- **`sample_city_data`** - Sample city location data
- **`sample_measurement_data`** - Sample air quality measurement data
- **`sample_aqi_data`** - Sample pollutant concentrations for AQI testing

## Test Categories

### Unit Tests (Default)

Tests individual functions and methods in isolation:

```bash
pytest -m unit
```

### Integration Tests

Tests interactions between components:

```bash
pytest -m integration
```

### API Tests

Tests that require API access (skipped by default):

```bash
pytest -m api
```

### Slow Tests

Tests that take longer to run:

```bash
# Skip slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest --cov=. --cov-report=html
```

Open `htmlcov/index.html` in your browser to view detailed coverage.

### Generate Terminal Coverage Report

```bash
pytest --cov=. --cov-report=term-missing
```

### Coverage Goals

- **Overall Coverage**: >85%
- **Critical Modules** (AQI, Database): >95%
- **API Client**: >80%
- **Utilities**: >90%

## Test Organization

### AQI Tests (`test_aqi.py`)

- **TestAQICalculation** - EPA AQI formula calculations
- **TestAQICategory** - Category determination (Good, Moderate, etc.)
- **TestAQIDescription** - Description and health message generation
- **TestDominantAQI** - Multi-pollutant AQI calculation
- **TestParameterFormatting** - Parameter name formatting
- **TestBreakpoints** - AQI breakpoint retrieval
- **TestEdgeCases** - Boundary conditions and edge cases

### Data Collector Tests (`test_data_collector.py`)

- **TestOpenAQClient** - API client initialization and requests
- **TestDataProcessor** - Response parsing and transformation
- **TestCollectionFunctions** - High-level collection workflows
- **TestDataIntegration** - End-to-end data collection pipeline

### Database Tests (`test_database.py`)

- **TestDatabaseInitialization** - Schema creation and optimization
- **TestCityOperations** - City CRUD operations
- **TestMeasurementOperations** - Measurement CRUD operations
- **TestAlertOperations** - Alert management
- **TestDatabaseUtilities** - Statistics and cleanup
- **TestDatabaseTransactions** - Transaction handling
- **TestDatabasePerformance** - Performance characteristics

### Configuration Tests (`test_config.py`)

- **TestOpenAQConfig** - API configuration
- **TestBrazilianCities** - City definitions and coordinates
- **TestDatabaseConfig** - Database settings
- **TestAirQualityParameters** - Parameter definitions
- **TestAppConfig** - Application settings
- **TestEnvironmentConfiguration** - Environment variable handling

### Logger Tests (`test_logger.py`)

- **TestLoggerSetup** - Logger initialization
- **TestLoggerFormatting** - Log message formatting
- **TestAPILogging** - API request/response logging
- **TestDatabaseLogging** - Database operation logging
- **TestErrorLogging** - Error logging with context

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
def test_calculate_aqi_good_range():
    """Test AQI calculation for PM2.5 in Good range."""
    aqi = calculate_aqi("pm25", 12.0)
    assert 0 <= aqi <= 50
    assert aqi == pytest.approx(50, abs=1)
```

### Using Fixtures

```python
def test_insert_city(test_db_connection, sample_city_data):
    """Test inserting a city into database."""
    db = test_db_connection
    db.insert_city(**sample_city_data)

    cities = db.get_cities()
    assert len(cities) == 1
    assert cities[0]["city_name"] == "São Paulo"
```

### Mocking API Calls

```python
@patch('requests.Session.get')
def test_api_call(mock_get, mock_openaq_locations_response):
    """Test API call with mocked response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_openaq_locations_response
    mock_get.return_value = mock_response

    # Test your API call here
```

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```python
# Good - uses fixture for clean database
def test_insert_city(test_db_connection):
    db = test_db_connection
    # Test code here

# Bad - relies on global state
def test_query_city():
    # Assumes data exists from previous test
```

### 2. Descriptive Test Names

Use clear, descriptive names that explain what is being tested:

```python
# Good
def test_pm25_aqi_calculation_in_unhealthy_range():
    pass

# Bad
def test_aqi():
    pass
```

### 3. Arrange-Act-Assert Pattern

Structure tests with clear sections:

```python
def test_example():
    # Arrange - Set up test data
    city_data = {"name": "São Paulo", ...}

    # Act - Perform the action
    result = process_city(city_data)

    # Assert - Verify the outcome
    assert result["city_name"] == "São Paulo"
```

### 4. Test Edge Cases

Always test boundary conditions and edge cases:

```python
def test_aqi_at_zero():
    """Test AQI with zero concentration."""
    assert calculate_aqi("pm25", 0.0) == 0

def test_aqi_with_negative_value():
    """Test that negative values raise error."""
    with pytest.raises(ValueError):
        calculate_aqi("pm25", -10.0)
```

## Continuous Integration

Tests should pass before merging code. Configure CI to run:

```bash
# Lint code
ruff check .

# Run type checking
mypy .

# Run tests with coverage
pytest --cov=. --cov-report=xml --cov-report=term

# Fail if coverage below threshold
pytest --cov=. --cov-fail-under=85
```

## Troubleshooting

### Tests Fail with Import Errors

Ensure project root is in Python path:

```bash
# Run from project root
cd /path/to/aeris
pytest
```

### Database Lock Errors

Use fixtures that provide clean database instances:

```python
def test_example(test_db_connection):
    # Use test_db_connection, not shared database
```

### Mock Patches Not Working

Ensure you're patching the correct import path:

```python
# Patch where the function is used, not where it's defined
@patch('data.data_collector.OpenAQClient')
def test_example(mock_client):
    pass
```

### Slow Test Execution

Run tests in parallel:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >85% code coverage
4. Update this README if adding new test categories

## Contact

For questions about the test suite, please refer to the main project documentation or open an issue.
