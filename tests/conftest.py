"""
Pytest configuration and shared fixtures for Aeris test suite.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_openaq_locations_response():
    """Mock OpenAQ v3 locations API response."""
    return {
        "results": [
            {
                "id": 12345,
                "name": "Congonhas - CETESB AQS",
                "locality": "São Paulo",
                "timezone": "America/Sao_Paulo",
                "coordinates": {
                    "latitude": -23.6167,
                    "longitude": -46.6639
                },
                "sensors": [
                    {"parameter": {"name": "pm25"}},
                    {"parameter": {"name": "pm10"}},
                    {"parameter": {"name": "o3"}}
                ]
            },
            {
                "id": 12346,
                "name": "Pinheiros - CETESB AQS",
                "locality": "São Paulo",
                "timezone": "America/Sao_Paulo",
                "coordinates": {
                    "latitude": -23.5613,
                    "longitude": -46.7013
                },
                "sensors": [
                    {"parameter": {"name": "pm25"}},
                    {"parameter": {"name": "no2"}}
                ]
            }
        ]
    }


@pytest.fixture
def mock_openaq_measurements_response():
    """Mock OpenAQ v3 latest measurements API response."""
    return {
        "results": [
            {
                "location": {
                    "id": 12345,
                    "name": "Congonhas - CETESB AQS"
                },
                "sensors": [
                    {
                        "parameter": {"name": "pm25"},
                        "latest": {
                            "datetime": {
                                "utc": "2025-01-15T18:00:00Z",
                                "local": "2025-01-15T15:00:00-03:00"
                            },
                            "value": 25.5,
                            "unit": "µg/m³"
                        }
                    },
                    {
                        "parameter": {"name": "pm10"},
                        "latest": {
                            "datetime": {
                                "utc": "2025-01-15T18:00:00Z",
                                "local": "2025-01-15T15:00:00-03:00"
                            },
                            "value": 45.2,
                            "unit": "µg/m³"
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_requests_session():
    """Create a mock requests session for API testing."""
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"results": []}
    response.raise_for_status = Mock()
    session.get.return_value = response
    return session


@pytest.fixture
def sample_city_data():
    """Sample city location data for testing."""
    return {
        "location_id": 12345,
        "city_name": "São Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "station_name": "Test Station",
        "parameters": ["pm25", "pm10", "o3"]
    }


@pytest.fixture
def sample_measurement_data():
    """Sample measurement data for testing."""
    return {
        "location_id": 12345,
        "city_name": "São Paulo",
        "timestamp": "2025-01-15T15:00:00-03:00",
        "parameter": "pm25",
        "value": 25.5,
        "unit": "µg/m³"
    }


@pytest.fixture
def sample_aqi_data():
    """Sample pollutant concentrations for AQI testing."""
    return {
        "pm25": 35.5,  # Moderate
        "pm10": 55.0,  # Moderate
        "o3": 0.070,   # Good (ppm)
        "no2": 0.100,  # Good (ppm)
        "so2": 0.035,  # Good (ppm)
        "co": 4.5      # Good (ppm)
    }


@pytest.fixture(autouse=True)
def reset_env_vars():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for view testing."""
    mock_st = MagicMock()
    mock_st.cache_data = lambda ttl=None: lambda f: f
    mock_st.cache_resource = lambda: lambda f: f
    mock_st.session_state = {}
    return mock_st
