"""
Data Collector for OpenAQ API v3

This module provides a client for fetching air quality data from OpenAQ API v3.
OpenAQ v3 requires API key authentication (free tier available).

IMPORTANT: v1 and v2 APIs were retired on January 31, 2025. Use v3 only.
Get your free API key at: https://explore.openaq.org/register
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import OpenAQConfig, BrazilianCities
from utils.logger import get_logger, log_api_request, log_api_response, log_error_with_context


logger = get_logger(__name__)


class OpenAQClient:
    """
    Client for OpenAQ API v3.

    OpenAQ v3 requires API key authentication. The API provides access to
    global air quality data with updated endpoint structure.

    Changes from v2:
    - X-API-Key header required for all requests
    - Different endpoint structure (/v3/locations, /v3/sensors, etc.)
    - Modified response format (meta + results structure)
    - Use iso=BR to filter for Brazil
    """

    def __init__(self):
        """Initialize the OpenAQ v3 client."""
        self.base_url = OpenAQConfig.BASE_URL
        self.endpoints = OpenAQConfig.ENDPOINTS
        self.timeout = OpenAQConfig.TIMEOUT

        # Validate API key
        if not OpenAQConfig.validate_api_key():
            logger.error("OpenAQ API key not configured!")
            raise ValueError(
                "OpenAQ API key required. Get your free key at: "
                "https://explore.openaq.org/register"
            )

        self.headers = OpenAQConfig.get_headers()
        self.session = self._create_session()

        logger.info(f"OpenAQ v3 Client initialized | Base URL: {self.base_url}")

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=OpenAQConfig.MAX_RETRIES,
            backoff_factor=OpenAQConfig.RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(self.headers)

        return session

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make a GET request to the OpenAQ API v3.

        Args:
            endpoint: API endpoint URL
            params: Query parameters

        Returns:
            JSON response as dictionary, or None on failure

        Raises:
            requests.exceptions.RequestException: On request failure
        """
        params = params or {}

        # Log request
        log_api_request(logger, "GET", endpoint, params)

        try:
            start_time = time.time()

            response = self.session.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )

            response_time = time.time() - start_time

            # Log response
            log_api_response(logger, response.status_code, response_time)

            # Raise exception for bad status codes
            response.raise_for_status()

            data = response.json()

            # v3 API returns data in meta + results structure
            if "results" not in data:
                logger.warning(f"Unexpected v3 response structure: {list(data.keys())}")

            return data

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s | Endpoint: {endpoint}")
            raise

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error | Endpoint: {endpoint}")
            log_error_with_context(logger, e, {"endpoint": endpoint, "params": params})
            raise

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 401:
                logger.error("API key authentication failed - check your API key")
            elif status_code == 429:
                logger.warning("Rate limit exceeded | Try again later")
            elif status_code >= 500:
                logger.error(f"Server error: {status_code}")
            else:
                logger.error(f"HTTP error: {status_code}")

            log_error_with_context(logger, e, {"endpoint": endpoint, "status": status_code})
            raise

        except Exception as e:
            logger.exception(f"Unexpected error in API request")
            log_error_with_context(logger, e, {"endpoint": endpoint})
            raise

    def get_locations_by_country(
        self,
        country_iso: str = "BR",
        limit: int = 100,
        parameters_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get monitoring locations for a country.

        Args:
            country_iso: ISO 3166-1 alpha-2 country code (default: BR for Brazil)
            limit: Maximum number of results (default: 100)
            parameters_id: Filter by parameter ID (e.g., 2 for PM2.5)

        Returns:
            List of location dictionaries

        Raises:
            requests.exceptions.RequestException: On API error
        """
        logger.info(f"Fetching locations for country: {country_iso}")

        params = {
            "iso": country_iso,
            "limit": limit
        }

        if parameters_id:
            params["parameters_id"] = parameters_id

        try:
            response = self._make_request(self.endpoints["locations"], params)

            if not response or "results" not in response:
                logger.warning(f"No locations returned for {country_iso}")
                return []

            results = response["results"]
            logger.info(f"Retrieved {len(results)} locations for {country_iso}")

            # Log metadata
            if "meta" in response:
                meta = response["meta"]
                logger.debug(f"Total found: {meta.get('found', 'unknown')}")

            return results

        except Exception as e:
            logger.error(f"Failed to fetch locations for {country_iso}")
            log_error_with_context(logger, e, {"country": country_iso})
            return []

    def get_locations_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        radius: int = 25000,  # 25km radius (max allowed)
        limit: int = 100
    ) -> List[Dict]:
        """
        Get locations near specific coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters (max: 25000m = 25km)
            limit: Maximum number of results

        Returns:
            List of location dictionaries
        """
        logger.info(f"Fetching locations near ({latitude}, {longitude}) within {radius}m")

        # v3 API expects coordinates in "latitude,longitude" format
        coordinates_str = f"{latitude},{longitude}"

        params = {
            "coordinates": coordinates_str,
            "radius": min(radius, 25000),  # Enforce max radius
            "limit": limit
        }

        try:
            response = self._make_request(self.endpoints["locations"], params)

            if not response or "results" not in response:
                logger.warning(f"No locations returned for coordinates")
                return []

            results = response["results"]
            logger.info(f"Retrieved {len(results)} locations near coordinates")

            return results

        except Exception as e:
            logger.error(f"Failed to fetch locations by coordinates")
            log_error_with_context(logger, e, {"lat": latitude, "lon": longitude})
            return []

    def get_location_latest(self, location_id: int) -> Optional[Dict]:
        """
        Get latest measurements for a specific location.

        Args:
            location_id: OpenAQ location ID

        Returns:
            Latest measurement data or None
        """
        logger.info(f"Fetching latest data for location {location_id}")

        # Build endpoint URL with location ID
        endpoint = self.endpoints["latest"].replace("{id}", str(location_id))

        try:
            response = self._make_request(endpoint)

            if not response or "results" not in response:
                logger.warning(f"No latest data returned for location {location_id}")
                return None

            results = response["results"]
            logger.info(f"Retrieved latest data for location {location_id}")

            return results

        except Exception as e:
            logger.error(f"Failed to fetch latest data for location {location_id}")
            log_error_with_context(logger, e, {"location_id": location_id})
            return None

    def get_sensor_measurements(
        self,
        sensor_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get measurements from a specific sensor.

        Args:
            sensor_id: Sensor ID
            date_from: Start date (default: 24 hours ago)
            date_to: End date (default: now)
            limit: Maximum number of results

        Returns:
            List of measurement dictionaries
        """
        # Default to last 24 hours
        if date_from is None:
            date_from = datetime.utcnow() - timedelta(hours=24)
        if date_to is None:
            date_to = datetime.utcnow()

        logger.info(
            f"Fetching measurements for sensor {sensor_id} "
            f"from {date_from.isoformat()} to {date_to.isoformat()}"
        )

        # Build endpoint URL with sensor ID
        endpoint = self.endpoints["measurements"].replace("{id}", str(sensor_id))

        params = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "limit": limit
        }

        try:
            response = self._make_request(endpoint, params)

            if not response or "results" not in response:
                logger.warning(f"No measurements returned for sensor {sensor_id}")
                return []

            results = response["results"]
            logger.info(f"Retrieved {len(results)} measurements for sensor {sensor_id}")

            return results

        except Exception as e:
            logger.error(f"Failed to fetch measurements for sensor {sensor_id}")
            log_error_with_context(logger, e, {"sensor_id": sensor_id})
            return []


class DataProcessor:
    """
    Process and standardize raw OpenAQ v3 data.

    Converts OpenAQ API v3 responses into a standardized format suitable
    for database storage.
    """

    @staticmethod
    def process_locations(raw_data: List[Dict], city_name: Optional[str] = None) -> List[Dict]:
        """
        Process location data from OpenAQ API v3.

        Args:
            raw_data: Raw API v3 response results
            city_name: Optional city name to filter/tag locations

        Returns:
            List of processed location dictionaries
        """
        processed = []

        for item in raw_data:
            try:
                # Extract city from locality or name
                locality = item.get("locality") or item.get("name")

                # If city_name specified, filter by it
                if city_name and locality and city_name.lower() not in locality.lower():
                    continue

                processed_item = {
                    "location_id": str(item.get("id")),
                    "city": locality or "Unknown",
                    "country": item.get("country", {}).get("code", "BR"),
                    "latitude": item.get("coordinates", {}).get("latitude"),
                    "longitude": item.get("coordinates", {}).get("longitude"),
                    "station_name": item.get("name"),
                    "is_active": True,  # Assume active if returned by API
                    "parameters": [
                        p.get("name") for instrument in item.get("instruments", [])
                        for sensor in instrument.get("sensors", [])
                        for p in sensor.get("parameters", [])
                    ],
                    "created_at": datetime.utcnow().isoformat()
                }

                # Validate required fields
                if processed_item["location_id"] and processed_item["station_name"]:
                    processed.append(processed_item)
                else:
                    logger.warning(f"Skipping incomplete location: {processed_item}")

            except Exception as e:
                logger.warning(f"Error processing location: {e}")
                continue

        logger.info(f"Processed {len(processed)} valid locations from {len(raw_data)} raw items")
        return processed

    @staticmethod
    def process_latest_measurements(raw_data, city_name: str, location_id: str) -> List[Dict]:
        """
        Process latest measurements from OpenAQ API v3.

        Args:
            raw_data: Raw API v3 latest response (can be dict or list)
            city_name: City name for tagging
            location_id: Location ID

        Returns:
            List of processed measurement dictionaries
        """
        processed = []

        if not raw_data:
            logger.warning("No latest data provided")
            return processed

        try:
            # API v3 returns a list of measurements directly
            if isinstance(raw_data, list):
                for measurement in raw_data:
                    value = measurement.get("value")
                    timestamp = measurement.get("datetime", {}).get("utc")
                    coordinates = measurement.get("coordinates", {})

                    if value is not None and timestamp:
                        processed_item = {
                            "location_id": location_id,
                            "city": city_name,
                            "country": "BR",
                            "latitude": coordinates.get("latitude"),
                            "longitude": coordinates.get("longitude"),
                            "parameter": "pm25",  # Default to PM2.5 for now
                            "value": value,
                            "unit": "µg/m³",
                            "timestamp": timestamp,
                            "source": "OpenAQ",
                            "collected_at": datetime.utcnow().isoformat()
                        }
                        processed.append(processed_item)

            # Handle dict format (older code path)
            elif isinstance(raw_data, dict):
                measurements_data = raw_data
                coordinates = measurements_data.get("coordinates", {})
                latitude = coordinates.get("latitude")
                longitude = coordinates.get("longitude")

                # Process sensors and their measurements
                for sensor_data in measurements_data.get("sensors", []):
                    parameter = sensor_data.get("parameter", {})
                    parameter_name = parameter.get("name", "unknown")

                    latest = sensor_data.get("latest", {})
                    value = latest.get("value")
                    timestamp = latest.get("datetime", {}).get("utc")

                    if value is not None and timestamp:
                        processed_item = {
                            "location_id": location_id,
                            "city": city_name,
                            "country": "BR",
                            "latitude": latitude,
                            "longitude": longitude,
                            "parameter": parameter_name,
                            "value": value,
                            "unit": parameter.get("units", "µg/m³"),
                            "timestamp": timestamp,
                            "source": "OpenAQ",
                            "collected_at": datetime.utcnow().isoformat()
                        }
                        processed.append(processed_item)

        except Exception as e:
            logger.warning(f"Error processing latest measurements: {e}")

        logger.info(f"Processed {len(processed)} valid measurements")
        return processed


# ==============================================================================
# Convenience functions
# ==============================================================================

def collect_brazil_locations(city_filter: Optional[str] = None) -> Tuple[List[Dict], Dict[str, List[int]]]:
    """
    Collect monitoring locations in Brazil.

    Args:
        city_filter: Optional city name to filter results

    Returns:
        Tuple of (processed_locations, city_to_location_ids_map)
    """
    client = OpenAQClient()
    processor = DataProcessor()

    logger.info("Collecting Brazilian monitoring locations")

    # Fetch all Brazilian locations
    raw_locations = client.get_locations_by_country("BR", limit=1000)

    # Process locations
    locations = processor.process_locations(raw_locations, city_filter)

    # Create mapping of cities to location IDs for easy lookup
    city_map = {}
    for loc in locations:
        city = loc["city"]
        if city not in city_map:
            city_map[city] = []
        city_map[city].append(int(loc["location_id"]))

    logger.info(
        f"Collected {len(locations)} locations across {len(city_map)} cities"
    )

    return locations, city_map


def collect_city_data(city: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Collect both locations and measurements for a city.

    Note: v3 API requires first finding location IDs, then fetching latest data.

    Args:
        city: City name (from BrazilianCities)

    Returns:
        Tuple of (measurements, locations)
    """
    if city not in BrazilianCities.CITIES:
        raise ValueError(f"Unknown city: {city}")

    client = OpenAQClient()
    processor = DataProcessor()

    logger.info(f"Starting data collection for {city}")

    # Get city coordinates
    lat, lon = BrazilianCities.get_coordinates(city)

    # Find locations near city coordinates
    raw_locations = client.get_locations_by_coordinates(lat, lon, radius=25000, limit=100)
    locations = processor.process_locations(raw_locations, city)

    # Collect latest measurements from each location
    all_measurements = []
    for location in locations:
        location_id = location["location_id"]
        try:
            latest_data = client.get_location_latest(int(location_id))
            if latest_data:
                measurements = processor.process_latest_measurements(
                    latest_data,
                    city,
                    location_id
                )
                all_measurements.extend(measurements)

            # Small delay to avoid rate limiting
            time.sleep(0.2)

        except Exception as e:
            logger.warning(f"Failed to fetch latest data for location {location_id}: {e}")
            continue

    logger.info(
        f"Data collection complete for {city} | "
        f"Measurements: {len(all_measurements)} | Locations: {len(locations)}"
    )

    return all_measurements, locations


def collect_multiple_cities(cities: Optional[List[str]] = None) -> Dict[str, Tuple[List[Dict], List[Dict]]]:
    """
    Collect data for multiple cities.

    Args:
        cities: List of city names (default: priority cities)

    Returns:
        Dictionary mapping city names to (measurements, locations) tuples
    """
    if cities is None:
        cities = BrazilianCities.get_priority_cities(max_priority=4)

    logger.info(f"Collecting data for {len(cities)} cities: {cities}")

    results = {}

    for city in cities:
        try:
            measurements, locations = collect_city_data(city)
            results[city] = (measurements, locations)

            # Delay between cities to respect rate limits
            time.sleep(1)

        except Exception as e:
            logger.error(f"Failed to collect data for {city}")
            log_error_with_context(logger, e, {"city": city})
            results[city] = ([], [])

    logger.info(f"Multi-city collection complete | Cities: {len(results)}")
    return results
