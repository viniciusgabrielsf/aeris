"""
Aeris Configuration Module

This module contains all configuration settings for the Aeris Air Quality Dashboard.
It loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent
DATA_STORAGE_DIR = BASE_DIR / "data_storage"
CACHE_DIR = DATA_STORAGE_DIR / "cache"

# Ensure directories exist
DATA_STORAGE_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)


# ==============================================================================
# OpenAQ API Configuration
# ==============================================================================

class OpenAQConfig:
    """
    OpenAQ API v3 configuration.

    IMPORTANT: OpenAQ v1 and v2 were retired on January 31, 2025.
    v3 requires API key authentication (free tier available).

    Get your free API key at: https://explore.openaq.org/register
    """

    # API Key (REQUIRED for v3)
    API_KEY = os.getenv("OPENAQ_API_KEY")

    # Base URL for v3 API
    BASE_URL = os.getenv("OPENAQ_API_BASE_URL", "https://api.openaq.org/v3")

    # v3 Endpoints
    ENDPOINTS = {
        "locations": f"{BASE_URL}/locations",              # List/search locations
        "location": f"{BASE_URL}/locations/{{id}}",        # Specific location details
        "sensors": f"{BASE_URL}/locations/{{id}}/sensors",  # Sensors at location
        "measurements": f"{BASE_URL}/sensors/{{id}}/measurements",  # Sensor measurements
        "latest": f"{BASE_URL}/locations/{{id}}/latest",   # Latest measurements for location
        "parameters": f"{BASE_URL}/parameters",            # Available parameters
        "countries": f"{BASE_URL}/countries",              # Available countries
    }

    # Request settings
    TIMEOUT = int(os.getenv("OPENAQ_TIMEOUT", "10"))  # seconds
    MAX_RETRIES = int(os.getenv("OPENAQ_MAX_RETRIES", "3"))
    RETRY_BACKOFF = float(os.getenv("OPENAQ_RETRY_BACKOFF", "1.0"))  # seconds

    # Rate limiting (check OpenAQ docs for v3 free tier limits)
    RATE_LIMIT_REQUESTS = int(os.getenv("OPENAQ_RATE_LIMIT", "500"))
    RATE_LIMIT_WINDOW = int(os.getenv("OPENAQ_RATE_LIMIT_WINDOW", "3600"))  # seconds

    # API response limits
    DEFAULT_LIMIT = 100  # Results per page
    MAX_LIMIT = 1000     # Maximum results per request

    @classmethod
    def validate_api_key(cls) -> bool:
        """Check if API key is configured."""
        if not cls.API_KEY or cls.API_KEY == "your_api_key_here":
            return False
        return True

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get request headers with API key."""
        if not cls.validate_api_key():
            raise ValueError(
                "OpenAQ API key not configured. "
                "Get your free key at https://explore.openaq.org/register "
                "and add it to your .env file as OPENAQ_API_KEY=your_key_here"
            )
        return {
            "X-API-Key": cls.API_KEY,
            "Content-Type": "application/json"
        }


# ==============================================================================
# Brazilian Cities Configuration
# ==============================================================================

class BrazilianCities:
    """
    Brazilian cities configuration with coordinates and priority.

    Priority levels:
    1 = Highest priority (best data availability)
    5 = Lower priority (limited data availability)
    """

    CITIES: Dict[str, Dict[str, any]] = {
        "São Paulo": {
            "lat": -23.5505,
            "lon": -46.6333,
            "state": "SP",
            "priority": 1,
            "timezone": "America/Sao_Paulo",
            "population": 12_300_000,
        },
        "Rio de Janeiro": {
            "lat": -22.9068,
            "lon": -43.1729,
            "state": "RJ",
            "priority": 2,
            "timezone": "America/Sao_Paulo",
            "population": 6_700_000,
        },
        "Belo Horizonte": {
            "lat": -19.9167,
            "lon": -43.9345,
            "state": "MG",
            "priority": 3,
            "timezone": "America/Sao_Paulo",
            "population": 2_500_000,
        },
        "Curitiba": {
            "lat": -25.4284,
            "lon": -49.2733,
            "state": "PR",
            "priority": 4,
            "timezone": "America/Sao_Paulo",
            "population": 1_900_000,
        },
        "Brasília": {
            "lat": -15.8267,
            "lon": -47.9218,
            "state": "DF",
            "priority": 5,
            "timezone": "America/Sao_Paulo",
            "population": 3_000_000,
        },
        "Salvador": {
            "lat": -12.9714,
            "lon": -38.5014,
            "state": "BA",
            "priority": 6,
            "timezone": "America/Bahia",
            "population": 2_900_000,
        },
        "Fortaleza": {
            "lat": -3.7172,
            "lon": -38.5433,
            "state": "CE",
            "priority": 7,
            "timezone": "America/Fortaleza",
            "population": 2_600_000,
        },
        "Porto Alegre": {
            "lat": -30.0346,
            "lon": -51.2177,
            "state": "RS",
            "priority": 8,
            "timezone": "America/Sao_Paulo",
            "population": 1_500_000,
        },
    }

    @classmethod
    def get_city_names(cls) -> list:
        """Get list of all city names"""
        return list(cls.CITIES.keys())

    @classmethod
    def get_priority_cities(cls, max_priority: int = 4) -> list:
        """Get cities up to a certain priority level"""
        return [
            name for name, info in cls.CITIES.items()
            if info["priority"] <= max_priority
        ]

    @classmethod
    def get_coordinates(cls, city: str) -> Tuple[float, float]:
        """Get (latitude, longitude) for a city"""
        if city not in cls.CITIES:
            raise ValueError(f"Unknown city: {city}")
        city_info = cls.CITIES[city]
        return (city_info["lat"], city_info["lon"])


# ==============================================================================
# Database Configuration
# ==============================================================================

class DatabaseConfig:
    """SQLite database configuration"""

    # Database file path
    DB_PATH = os.getenv(
        "DATABASE_PATH",
        str(DATA_STORAGE_DIR / "aeris.db")
    )

    # Connection settings
    TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))  # seconds
    CHECK_SAME_THREAD = False  # Allow multi-threaded access

    # Performance settings
    JOURNAL_MODE = "WAL"  # Write-Ahead Logging for better concurrency
    SYNCHRONOUS = "NORMAL"  # Balance between safety and speed
    CACHE_SIZE = -64000  # 64MB cache (negative = KB)
    MMAP_SIZE = 268435456  # 256MB memory-mapped I/O

    # Data retention policy
    RAW_DATA_RETENTION_DAYS = int(os.getenv("RAW_DATA_RETENTION_DAYS", "90"))
    AGGREGATE_RETENTION_DAYS = int(os.getenv("AGGREGATE_RETENTION_DAYS", "365"))


# ==============================================================================
# Air Quality Parameters
# ==============================================================================

class AirQualityParameters:
    """Air quality pollutant parameters and their properties"""

    PARAMETERS = {
        "pm25": {
            "name": "PM2.5",
            "full_name": "Particulate Matter 2.5",
            "unit": "µg/m³",
            "description": "Fine particles ≤ 2.5 micrometers",
            "who_limit_24h": 25,  # WHO 24-hour guideline
            "who_limit_annual": 10,
        },
        "pm10": {
            "name": "PM10",
            "full_name": "Particulate Matter 10",
            "unit": "µg/m³",
            "description": "Coarse particles ≤ 10 micrometers",
            "who_limit_24h": 50,
            "who_limit_annual": 20,
        },
        "o3": {
            "name": "O3",
            "full_name": "Ozone",
            "unit": "µg/m³",
            "description": "Ground-level ozone",
            "who_limit_8h": 100,
        },
        "no2": {
            "name": "NO2",
            "full_name": "Nitrogen Dioxide",
            "unit": "µg/m³",
            "description": "Traffic-related pollutant",
            "who_limit_1h": 200,
            "who_limit_annual": 40,
        },
        "so2": {
            "name": "SO2",
            "full_name": "Sulfur Dioxide",
            "unit": "µg/m³",
            "description": "Industrial pollutant",
            "who_limit_24h": 20,
        },
        "co": {
            "name": "CO",
            "full_name": "Carbon Monoxide",
            "unit": "µg/m³",
            "description": "Combustion pollutant",
            "who_limit_8h": 10000,  # 10 mg/m³
        },
    }

    @classmethod
    def get_parameter_names(cls) -> list:
        """Get list of all parameter names"""
        return [p["name"] for p in cls.PARAMETERS.values()]


# ==============================================================================
# Application Configuration
# ==============================================================================

class AppConfig:
    """General application configuration"""

    # Application metadata
    APP_NAME = "Aeris"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Air Quality Dashboard for Brazilian Cities"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", str(DATA_STORAGE_DIR / "aeris.log"))
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Scheduler settings
    COLLECTION_INTERVAL_MINUTES = int(
        os.getenv("COLLECTION_INTERVAL_MINUTES", "30")
    )

    # Cache settings
    CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "30"))
    ENABLE_FILE_CACHE = os.getenv("ENABLE_FILE_CACHE", "true").lower() == "true"

    # Streamlit settings
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    # Development mode
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# ==============================================================================
# Export all configurations
# ==============================================================================

__all__ = [
    "OpenAQConfig",
    "BrazilianCities",
    "DatabaseConfig",
    "AirQualityParameters",
    "AppConfig",
    "BASE_DIR",
    "DATA_STORAGE_DIR",
    "CACHE_DIR",
]
