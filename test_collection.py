#!/usr/bin/env python3
"""
Test Data Collection Script for Aeris

This script tests the complete data collection pipeline:
1. Tests API connection to OpenAQ v3
2. Collects air quality data from 3 Brazilian cities
3. Saves data to SQLite database
4. Displays summary statistics

IMPORTANT: OpenAQ v3 requires API key authentication.
Get your free key at: https://explore.openaq.org/register
See API_KEY_SETUP.md for detailed setup instructions.

Usage:
    python test_collection.py
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

from config import BrazilianCities, AppConfig, OpenAQConfig
from data.data_collector import OpenAQClient, DataProcessor, collect_city_data
from database.database import AerisDatabase
from utils.logger import get_logger


logger = get_logger(__name__)


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    width = 80
    print(f"\n{char * width}")
    print(f"{text.center(width)}")
    print(f"{char * width}\n")


def print_section(text: str):
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"▸ {text}")
    print(f"{'─' * 80}")


def check_api_key_setup() -> bool:
    """
    Check if OpenAQ API key is properly configured.

    Returns:
        True if API key is configured, False otherwise
    """
    print_section("Checking API Key Configuration")

    if not OpenAQConfig.validate_api_key():
        print("✗ OpenAQ API key not configured!")
        print()
        print("IMPORTANT: OpenAQ v3 requires API key authentication (free tier available)")
        print()
        print("To get started:")
        print("  1. Register at: https://explore.openaq.org/register")
        print("  2. Get your free API key from account settings")
        print("  3. Create .env file: cp .env.example .env")
        print("  4. Add your key to .env: OPENAQ_API_KEY=your_key_here")
        print()
        print("For detailed instructions, see: API_KEY_SETUP.md")
        print()
        logger.error("API key not configured")
        return False

    print("✓ API key configured")
    logger.info("API key validation passed")
    return True


def test_api_connection() -> bool:
    """
    Test connection to OpenAQ API v3.

    Returns:
        True if connection successful, False otherwise
    """
    print_section("Testing OpenAQ API v3 Connection")

    try:
        client = OpenAQClient()

        # Try to fetch Brazilian locations (simple test)
        print("→ Sending test request to OpenAQ API v3...")
        logger.info("Testing API v3 connection")

        # Use a test query with minimal data
        test_data = client.get_locations_by_country("BR", limit=5)

        if test_data and len(test_data) > 0:
            print("✓ API connection successful!")
            print(f"✓ Received {len(test_data)} locations from Brazil")
            logger.info("API connection test passed")
            return True
        else:
            print("✗ API returned empty response (might be normal if no data available)")
            logger.warning("API returned empty response")
            # Don't fail the test, as empty response might be valid
            return True

    except ValueError as e:
        # This is specifically for API key errors
        print(f"✗ API key error: {e}")
        logger.error(f"API key validation failed: {e}")
        return False

    except Exception as e:
        print(f"✗ API connection failed: {e}")
        logger.error(f"API connection test failed: {e}")
        return False


def test_database_connection(db: AerisDatabase) -> bool:
    """
    Test database connection and schema.

    Args:
        db: Database instance

    Returns:
        True if connection successful, False otherwise
    """
    print_section("Testing Database Connection")

    try:
        print("→ Checking database connection...")

        # Test query
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

        table_names = [t["name"] for t in tables]

        print("✓ Database connection successful!")
        print(f"✓ Found {len(table_names)} tables: {', '.join(table_names)}")

        # Verify required tables exist
        required_tables = ["cities", "air_measurements", "alerts"]
        missing_tables = [t for t in required_tables if t not in table_names]

        if missing_tables:
            print(f"✗ Missing tables: {', '.join(missing_tables)}")
            return False

        print("✓ All required tables present")
        logger.info("Database connection test passed")
        return True

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        logger.error(f"Database connection test failed: {e}")
        return False


def collect_and_save_city_data(
    city: str,
    db: AerisDatabase
) -> Dict:
    """
    Collect and save data for a single city.

    Args:
        city: City name
        db: Database instance

    Returns:
        Dictionary with collection statistics
    """
    print_section(f"Collecting Data for {city}")

    stats = {
        "city": city,
        "measurements": 0,
        "locations": 0,
        "success": False
    }

    try:
        # Collect data
        print(f"→ Fetching data from OpenAQ API...")
        measurements, locations = collect_city_data(city)

        print(f"✓ Retrieved {len(measurements)} measurements")
        print(f"✓ Retrieved {len(locations)} monitoring locations")

        # Save locations to database
        print(f"→ Saving locations to database...")
        for location in locations:
            db.insert_city(location)

        # Save measurements to database
        print(f"→ Saving measurements to database...")
        inserted = db.insert_measurements_bulk(measurements)

        print(f"✓ Saved {inserted} measurements to database")

        stats["measurements"] = inserted
        stats["locations"] = len(locations)
        stats["success"] = True

        logger.info(f"Data collection successful for {city}")
        return stats

    except Exception as e:
        print(f"✗ Error collecting data for {city}: {e}")
        logger.error(f"Data collection failed for {city}: {e}")
        return stats


def display_data_summary(db: AerisDatabase, cities: List[str]):
    """
    Display summary of collected data.

    Args:
        db: Database instance
        cities: List of city names
    """
    print_section("Data Summary")

    for city in cities:
        try:
            # Get latest measurements
            measurements = db.get_latest_measurements(city, limit=10)

            if not measurements:
                print(f"\n{city}: No data available")
                continue

            print(f"\n📍 {city}")
            print(f"   Total measurements: {len(measurements)}")

            # Group by parameter
            by_parameter = {}
            for m in measurements:
                param = m["parameter"]
                if param not in by_parameter:
                    by_parameter[param] = []
                by_parameter[param].append(m)

            print(f"   Parameters: {', '.join(by_parameter.keys())}")

            # Show latest value for each parameter
            print(f"   Latest readings:")
            for param, values in by_parameter.items():
                latest = values[0]
                print(f"      • {param}: {latest['value']:.2f} {latest['unit']}")

        except Exception as e:
            print(f"\n{city}: Error retrieving data - {e}")
            logger.error(f"Error displaying summary for {city}: {e}")


def main():
    """Main test function."""
    print_header("AERIS - Air Quality Data Collection Test (v3)")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test cities (top 3 with best data availability)
    test_cities = ["São Paulo", "Rio de Janeiro", "Belo Horizonte"]

    print(f"\nTest configuration:")
    print(f"  • API Version: OpenAQ v3")
    print(f"  • Cities: {', '.join(test_cities)}")
    print(f"  • Database: {AppConfig.LOG_FILE}")

    # =========================================================================
    # Step 0: Check API Key Setup
    # =========================================================================
    if not check_api_key_setup():
        print("\n❌ API key not configured. Please set up your API key first.")
        logger.error("Test aborted: API key not configured")
        sys.exit(1)

    # =========================================================================
    # Step 1: Test API Connection
    # =========================================================================
    if not test_api_connection():
        print("\n❌ API connection test failed. Exiting.")
        logger.error("Test aborted: API connection failed")
        sys.exit(1)

    # =========================================================================
    # Step 2: Initialize Database
    # =========================================================================
    print_section("Initializing Database")
    try:
        db = AerisDatabase()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

    # Test database connection
    if not test_database_connection(db):
        print("\n❌ Database connection test failed. Exiting.")
        logger.error("Test aborted: Database connection failed")
        sys.exit(1)

    # =========================================================================
    # Step 3: Collect Data for Test Cities
    # =========================================================================
    print_header("Data Collection Phase", "=")

    all_stats = []

    for city in test_cities:
        stats = collect_and_save_city_data(city, db)
        all_stats.append(stats)

        # Small delay between cities to be respectful to API
        import time
        time.sleep(1)

    # =========================================================================
    # Step 4: Display Results
    # =========================================================================
    print_header("Test Results", "=")

    # Overall statistics
    total_measurements = sum(s["measurements"] for s in all_stats)
    total_locations = sum(s["locations"] for s in all_stats)
    successful_cities = sum(1 for s in all_stats if s["success"])

    print("\n📊 Overall Statistics:")
    print(f"   • Cities tested: {len(test_cities)}")
    print(f"   • Successful collections: {successful_cities}/{len(test_cities)}")
    print(f"   • Total measurements: {total_measurements}")
    print(f"   • Total locations: {total_locations}")

    # Per-city statistics
    print("\n📈 Per-City Statistics:")
    for stats in all_stats:
        status = "✓" if stats["success"] else "✗"
        print(f"   {status} {stats['city']}: "
              f"{stats['measurements']} measurements, "
              f"{stats['locations']} locations")

    # Display data summary
    if total_measurements > 0:
        display_data_summary(db, test_cities)

    # =========================================================================
    # Step 5: Final Report
    # =========================================================================
    print_header("Test Complete", "=")

    if successful_cities == len(test_cities) and total_measurements > 0:
        print("✓ All tests passed successfully!")
        print(f"✓ Data collected and saved to database: {db.db_path}")
        print("\nNext steps:")
        print("  1. Run the Streamlit dashboard: streamlit run app.py")
        print("  2. Explore the data in the database")
        print("  3. Set up automated collection with scheduler")
        logger.info("Test suite completed successfully")
        return 0
    else:
        print("⚠ Some tests failed or no data was collected")
        print("  Check the log file for details:")
        print(f"  {AppConfig.LOG_FILE}")
        logger.warning("Test suite completed with failures")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error in test suite")
        sys.exit(1)
