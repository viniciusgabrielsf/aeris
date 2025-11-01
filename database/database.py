"""
Database Module for Aeris

This module handles SQLite database operations including:
- Schema creation and migrations
- CRUD operations for cities, measurements, and alerts
- Optimized queries with proper indexing
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from config import DatabaseConfig
from utils.logger import get_logger, log_database_operation, log_error_with_context


logger = get_logger(__name__)


class AerisDatabase:
    """
    SQLite database manager for Aeris.

    Manages air quality data storage with three main tables:
    - cities: Brazilian cities and monitoring locations
    - air_measurements: Time series air quality data
    - alerts: Air quality alerts and notifications
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file (default: from config)
        """
        self.db_path = db_path or DatabaseConfig.DB_PATH

        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Database initialized | Path: {self.db_path}")

        # Initialize schema
        self.initialize_schema()

        # Optimize database settings
        self._optimize_database()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection

        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cities")
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=DatabaseConfig.TIMEOUT,
                check_same_thread=DatabaseConfig.CHECK_SAME_THREAD
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            log_error_with_context(logger, e, {"db_path": self.db_path})
            raise
        finally:
            if conn:
                conn.close()

    def _optimize_database(self):
        """Apply SQLite performance optimizations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Enable Write-Ahead Logging for better concurrency
            cursor.execute(f"PRAGMA journal_mode = {DatabaseConfig.JOURNAL_MODE}")

            # Set synchronous mode
            cursor.execute(f"PRAGMA synchronous = {DatabaseConfig.SYNCHRONOUS}")

            # Set cache size
            cursor.execute(f"PRAGMA cache_size = {DatabaseConfig.CACHE_SIZE}")

            # Enable memory-mapped I/O
            cursor.execute(f"PRAGMA mmap_size = {DatabaseConfig.MMAP_SIZE}")

            conn.commit()

        logger.info("Database optimizations applied")

    def initialize_schema(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # ================================================================
            # Table 1: Cities
            # ================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_id TEXT UNIQUE NOT NULL,
                    city_name TEXT NOT NULL,
                    country TEXT DEFAULT 'BR',
                    state TEXT,
                    latitude REAL,
                    longitude REAL,
                    station_name TEXT,
                    is_active INTEGER DEFAULT 1,
                    parameters TEXT,  -- JSON array of available parameters
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Indexes for cities
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cities_name
                ON cities(city_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cities_location
                ON cities(location_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cities_active
                ON cities(is_active)
            """)

            # ================================================================
            # Table 2: Air Measurements
            # ================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS air_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_id TEXT NOT NULL,
                    city_name TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    parameter TEXT NOT NULL,  -- pm25, pm10, o3, no2, so2, co
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    source TEXT DEFAULT 'OpenAQ',
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (location_id) REFERENCES cities(location_id)
                )
            """)

            # Critical indexes for query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_city_time
                ON air_measurements(city_name, timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_param_time
                ON air_measurements(parameter, timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_location
                ON air_measurements(location_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_timestamp
                ON air_measurements(timestamp DESC)
            """)

            # ================================================================
            # Table 3: Alerts
            # ================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    alert_level TEXT NOT NULL,  -- good, moderate, unhealthy, etc.
                    parameter TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Indexes for alerts
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_city
                ON alerts(city_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_active
                ON alerts(is_active)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_created
                ON alerts(created_at DESC)
            """)

            conn.commit()

        logger.info("Database schema initialized successfully")

    # =========================================================================
    # CITIES TABLE OPERATIONS
    # =========================================================================

    def insert_city(self, city_data: Dict) -> bool:
        """
        Insert a city/location record.

        Args:
            city_data: Dictionary with city information

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Convert parameters list to JSON string
                parameters_json = json.dumps(city_data.get("parameters", []))

                cursor.execute("""
                    INSERT OR REPLACE INTO cities
                    (location_id, city_name, country, latitude, longitude,
                     station_name, is_active, parameters, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    city_data["location_id"],
                    city_data["city"],
                    city_data.get("country", "BR"),
                    city_data.get("latitude"),
                    city_data.get("longitude"),
                    city_data.get("station_name"),
                    city_data.get("is_active", 1),
                    parameters_json
                ))

                conn.commit()

                log_database_operation(logger, "INSERT", "cities", 1)
                return True

        except Exception as e:
            logger.error(f"Failed to insert city: {city_data.get('city')}")
            log_error_with_context(logger, e, city_data)
            return False

    def get_cities(self, active_only: bool = True) -> List[Dict]:
        """
        Get all cities from database.

        Args:
            active_only: Only return active monitoring locations

        Returns:
            List of city dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM cities"
                if active_only:
                    query += " WHERE is_active = 1"
                query += " ORDER BY city_name"

                cursor.execute(query)
                rows = cursor.fetchall()

                cities = []
                for row in rows:
                    city = dict(row)
                    # Parse JSON parameters
                    if city.get("parameters"):
                        city["parameters"] = json.loads(city["parameters"])
                    cities.append(city)

                log_database_operation(logger, "SELECT", "cities", len(cities))
                return cities

        except Exception as e:
            logger.error("Failed to fetch cities")
            log_error_with_context(logger, e)
            return []

    # =========================================================================
    # AIR MEASUREMENTS TABLE OPERATIONS
    # =========================================================================

    def insert_measurement(self, measurement: Dict) -> bool:
        """
        Insert a single air quality measurement.

        Args:
            measurement: Dictionary with measurement data

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO air_measurements
                    (location_id, city_name, timestamp, parameter, value, unit,
                     latitude, longitude, source, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    measurement["location_id"],
                    measurement["city"],
                    measurement["timestamp"],
                    measurement["parameter"],
                    measurement["value"],
                    measurement["unit"],
                    measurement.get("latitude"),
                    measurement.get("longitude"),
                    measurement.get("source", "OpenAQ"),
                    measurement.get("collected_at", datetime.utcnow().isoformat())
                ))

                conn.commit()
                return True

        except sqlite3.IntegrityError:
            # Duplicate entry - this is OK, just skip
            logger.debug(f"Duplicate measurement skipped")
            return False

        except Exception as e:
            logger.error(f"Failed to insert measurement")
            log_error_with_context(logger, e, measurement)
            return False

    def insert_measurements_bulk(self, measurements: List[Dict]) -> int:
        """
        Insert multiple measurements efficiently.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Number of successfully inserted measurements
        """
        if not measurements:
            return 0

        inserted = 0

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for measurement in measurements:
                    try:
                        cursor.execute("""
                            INSERT INTO air_measurements
                            (location_id, city_name, timestamp, parameter, value, unit,
                             latitude, longitude, source, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            measurement["location_id"],
                            measurement["city"],
                            measurement["timestamp"],
                            measurement["parameter"],
                            measurement["value"],
                            measurement["unit"],
                            measurement.get("latitude"),
                            measurement.get("longitude"),
                            measurement.get("source", "OpenAQ"),
                            measurement.get("collected_at", datetime.utcnow().isoformat())
                        ))
                        inserted += 1

                    except sqlite3.IntegrityError:
                        # Skip duplicates
                        continue

                conn.commit()

                log_database_operation(logger, "BULK INSERT", "air_measurements", inserted)
                return inserted

        except Exception as e:
            logger.error(f"Failed to bulk insert measurements")
            log_error_with_context(logger, e, {"count": len(measurements)})
            return inserted

    def get_latest_measurements(
        self,
        city: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get latest measurements for a city.

        Args:
            city: City name
            limit: Maximum number of results

        Returns:
            List of measurement dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM air_measurements
                    WHERE city_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (city, limit))

                rows = cursor.fetchall()
                measurements = [dict(row) for row in rows]

                log_database_operation(logger, "SELECT", "air_measurements", len(measurements))
                return measurements

        except Exception as e:
            logger.error(f"Failed to fetch measurements for {city}")
            log_error_with_context(logger, e, {"city": city})
            return []

    def get_measurements_by_timerange(
        self,
        city: str,
        hours: int = 24,
        parameter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get measurements within a time range.

        Args:
            city: City name
            hours: Number of hours to look back
            parameter: Specific parameter (optional)

        Returns:
            List of measurement dictionaries
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                if parameter:
                    cursor.execute("""
                        SELECT * FROM air_measurements
                        WHERE city_name = ?
                          AND parameter = ?
                          AND timestamp >= ?
                        ORDER BY timestamp DESC
                    """, (city, parameter, cutoff_time.isoformat()))
                else:
                    cursor.execute("""
                        SELECT * FROM air_measurements
                        WHERE city_name = ?
                          AND timestamp >= ?
                        ORDER BY timestamp DESC
                    """, (city, cutoff_time.isoformat()))

                rows = cursor.fetchall()
                measurements = [dict(row) for row in rows]

                log_database_operation(logger, "SELECT", "air_measurements", len(measurements))
                return measurements

        except Exception as e:
            logger.error(f"Failed to fetch time range measurements")
            log_error_with_context(logger, e, {"city": city, "hours": hours})
            return []

    # =========================================================================
    # ALERTS TABLE OPERATIONS
    # =========================================================================

    def create_alert(
        self,
        city: str,
        alert_level: str,
        parameter: str,
        value: float,
        threshold: float,
        message: str
    ) -> bool:
        """
        Create a new air quality alert.

        Args:
            city: City name
            alert_level: Alert level (good, moderate, unhealthy, etc.)
            parameter: Air quality parameter
            value: Measured value
            threshold: Threshold that was exceeded
            message: Alert message

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO alerts
                    (city_name, alert_level, parameter, value, threshold, message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (city, alert_level, parameter, value, threshold, message))

                conn.commit()

                log_database_operation(logger, "INSERT", "alerts", 1)
                logger.info(f"Alert created for {city}: {alert_level} - {message}")
                return True

        except Exception as e:
            logger.error(f"Failed to create alert for {city}")
            log_error_with_context(logger, e, {"city": city, "level": alert_level})
            return False

    def get_active_alerts(self, city: Optional[str] = None) -> List[Dict]:
        """
        Get active alerts.

        Args:
            city: City name (optional, gets all cities if None)

        Returns:
            List of alert dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if city:
                    cursor.execute("""
                        SELECT * FROM alerts
                        WHERE city_name = ? AND is_active = 1
                        ORDER BY created_at DESC
                    """, (city,))
                else:
                    cursor.execute("""
                        SELECT * FROM alerts
                        WHERE is_active = 1
                        ORDER BY created_at DESC
                    """)

                rows = cursor.fetchall()
                alerts = [dict(row) for row in rows]

                log_database_operation(logger, "SELECT", "alerts", len(alerts))
                return alerts

        except Exception as e:
            logger.error("Failed to fetch active alerts")
            log_error_with_context(logger, e, {"city": city})
            return []

    def resolve_alert(self, alert_id: int) -> bool:
        """
        Mark an alert as resolved.

        Args:
            alert_id: Alert ID

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE alerts
                    SET is_active = 0, resolved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (alert_id,))

                conn.commit()

                log_database_operation(logger, "UPDATE", "alerts", 1)
                return True

        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}")
            log_error_with_context(logger, e, {"alert_id": alert_id})
            return False

    # =========================================================================
    # UTILITY OPERATIONS
    # =========================================================================

    def get_statistics(self, city: str, hours: int = 24) -> Dict:
        """
        Get statistics for a city.

        Args:
            city: City name
            hours: Time range in hours

        Returns:
            Dictionary with statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        parameter,
                        COUNT(*) as count,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value
                    FROM air_measurements
                    WHERE city_name = ? AND timestamp >= ?
                    GROUP BY parameter
                """, (city, cutoff_time.isoformat()))

                rows = cursor.fetchall()
                stats = {row["parameter"]: dict(row) for row in rows}

                logger.info(f"Statistics retrieved for {city}")
                return stats

        except Exception as e:
            logger.error(f"Failed to get statistics for {city}")
            log_error_with_context(logger, e, {"city": city})
            return {}

    def cleanup_old_data(self, days: int = 90) -> int:
        """
        Remove old measurements.

        Args:
            days: Keep data newer than this many days

        Returns:
            Number of deleted records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM air_measurements
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))

                deleted = cursor.rowcount
                conn.commit()

                log_database_operation(logger, "DELETE", "air_measurements", deleted)
                logger.info(f"Cleaned up {deleted} old measurements (older than {days} days)")
                return deleted

        except Exception as e:
            logger.error("Failed to cleanup old data")
            log_error_with_context(logger, e, {"days": days})
            return 0

    def vacuum(self):
        """Optimize database by running VACUUM."""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
            logger.info("Database vacuumed successfully")

        except Exception as e:
            logger.error("Failed to vacuum database")
            log_error_with_context(logger, e)
