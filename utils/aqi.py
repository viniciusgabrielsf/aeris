"""
AQI (Air Quality Index) Calculation Utilities

This module provides functions to calculate AQI values and determine air quality
categories based on pollutant concentrations.

Standards used:
- US EPA AQI calculation method
- WHO Air Quality Guidelines for reference
"""

from typing import Dict, Tuple, Optional
from enum import Enum


class AQICategory(Enum):
    """AQI categories with color codes."""
    GOOD = ("Good", "#00E400", 0, 50)
    MODERATE = ("Moderate", "#FFFF00", 51, 100)
    UNHEALTHY_SENSITIVE = ("Unhealthy for Sensitive Groups", "#FF7E00", 101, 150)
    UNHEALTHY = ("Unhealthy", "#FF0000", 151, 200)
    VERY_UNHEALTHY = ("Very Unhealthy", "#8F3F97", 201, 300)
    HAZARDOUS = ("Hazardous", "#7E0023", 301, 500)

    def __init__(self, label: str, color: str, low: int, high: int):
        self.label = label
        self.color = color
        self.aqi_low = low
        self.aqi_high = high


# PM2.5 Breakpoints (µg/m³)
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500),
]

# PM10 Breakpoints (µg/m³)
PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500),
]

# O3 (Ozone) Breakpoints (ppb, 8-hour average)
O3_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 70, 51, 100),
    (71, 85, 101, 150),
    (86, 105, 151, 200),
    (106, 200, 201, 300),
]

# CO (Carbon Monoxide) Breakpoints (ppm, 8-hour average)
CO_BREAKPOINTS = [
    (0.0, 4.4, 0, 50),
    (4.5, 9.4, 51, 100),
    (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200),
    (15.5, 30.4, 201, 300),
    (30.5, 50.4, 301, 500),
]

# NO2 (Nitrogen Dioxide) Breakpoints (ppb, 1-hour average)
NO2_BREAKPOINTS = [
    (0, 53, 0, 50),
    (54, 100, 51, 100),
    (101, 360, 101, 150),
    (361, 649, 151, 200),
    (650, 1249, 201, 300),
    (1250, 2049, 301, 500),
]

# SO2 (Sulfur Dioxide) Breakpoints (ppb, 1-hour average)
SO2_BREAKPOINTS = [
    (0, 35, 0, 50),
    (36, 75, 51, 100),
    (76, 185, 101, 150),
    (186, 304, 151, 200),
    (305, 604, 201, 300),
    (605, 1004, 301, 500),
]


def get_breakpoints(parameter: str) -> Optional[list]:
    """
    Get AQI breakpoints for a specific parameter.

    Args:
        parameter: Pollutant parameter name (pm25, pm10, o3, co, no2, so2)

    Returns:
        List of breakpoint tuples or None if parameter not supported
    """
    parameter_lower = parameter.lower().replace(".", "").replace("_", "")

    breakpoint_map = {
        "pm25": PM25_BREAKPOINTS,
        "pm10": PM10_BREAKPOINTS,
        "o3": O3_BREAKPOINTS,
        "co": CO_BREAKPOINTS,
        "no2": NO2_BREAKPOINTS,
        "so2": SO2_BREAKPOINTS,
    }

    return breakpoint_map.get(parameter_lower)


def calculate_aqi(concentration: float, parameter: str) -> Optional[int]:
    """
    Calculate AQI value for a given pollutant concentration.

    Uses the EPA AQI formula:
    AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low

    Where:
    - C = pollutant concentration
    - C_low, C_high = concentration breakpoints
    - I_low, I_high = AQI breakpoints

    Args:
        concentration: Pollutant concentration value
        parameter: Pollutant parameter name

    Returns:
        Calculated AQI value (0-500) or None if parameter not supported
    """
    breakpoints = get_breakpoints(parameter)

    if not breakpoints:
        return None

    if concentration < 0:
        return 0

    # Find the appropriate breakpoint range
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            # Apply EPA AQI formula
            aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            return round(aqi)

    # If concentration exceeds all breakpoints, return hazardous
    return 500


def get_aqi_category(aqi: int) -> AQICategory:
    """
    Get AQI category for a given AQI value.

    Args:
        aqi: AQI value (0-500)

    Returns:
        AQICategory enum with label, color, and range
    """
    for category in AQICategory:
        if category.aqi_low <= aqi <= category.aqi_high:
            return category

    # If AQI exceeds 500, return Hazardous
    return AQICategory.HAZARDOUS


def get_aqi_description(aqi: int) -> Dict[str, str]:
    """
    Get detailed AQI information including health implications.

    Args:
        aqi: AQI value

    Returns:
        Dictionary with category, color, label, and health message
    """
    category = get_aqi_category(aqi)

    health_messages = {
        AQICategory.GOOD: "Air quality is satisfactory, and air pollution poses little or no risk.",
        AQICategory.MODERATE: "Air quality is acceptable. However, there may be a risk for some people who are unusually sensitive to air pollution.",
        AQICategory.UNHEALTHY_SENSITIVE: "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
        AQICategory.UNHEALTHY: "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
        AQICategory.VERY_UNHEALTHY: "Health alert: The risk of health effects is increased for everyone.",
        AQICategory.HAZARDOUS: "Health warning of emergency conditions: everyone is more likely to be affected.",
    }

    return {
        "aqi": aqi,
        "category": category.label,
        "color": category.color,
        "level": category.name,
        "health_message": health_messages.get(category, "No information available"),
    }


def calculate_dominant_aqi(measurements: Dict[str, float]) -> Tuple[int, str, Dict[str, int]]:
    """
    Calculate dominant (highest) AQI from multiple pollutant measurements.

    Args:
        measurements: Dictionary mapping parameter names to concentrations
                     e.g., {"pm25": 35.5, "pm10": 50, "o3": 60}

    Returns:
        Tuple of (dominant_aqi, dominant_parameter, all_aqis)
        - dominant_aqi: Highest AQI value
        - dominant_parameter: Parameter with highest AQI
        - all_aqis: Dictionary of all calculated AQIs
    """
    all_aqis = {}
    dominant_aqi = 0
    dominant_parameter = "unknown"

    for parameter, concentration in measurements.items():
        aqi = calculate_aqi(concentration, parameter)
        if aqi is not None:
            all_aqis[parameter] = aqi
            if aqi > dominant_aqi:
                dominant_aqi = aqi
                dominant_parameter = parameter

    return dominant_aqi, dominant_parameter, all_aqis


def format_parameter_name(parameter: str) -> str:
    """
    Format parameter name for display.

    Args:
        parameter: Raw parameter name (e.g., "pm25", "pm10")

    Returns:
        Formatted name (e.g., "PM2.5", "PM10")
    """
    parameter_lower = parameter.lower()

    format_map = {
        "pm25": "PM2.5",
        "pm2.5": "PM2.5",
        "pm10": "PM10",
        "o3": "O₃",
        "ozone": "O₃",
        "co": "CO",
        "no2": "NO₂",
        "so2": "SO₂",
    }

    return format_map.get(parameter_lower, parameter.upper())


# WHO Air Quality Guidelines (for reference)
WHO_GUIDELINES = {
    "pm25": {
        "annual": 5,  # µg/m³
        "24_hour": 15,  # µg/m³
    },
    "pm10": {
        "annual": 15,  # µg/m³
        "24_hour": 45,  # µg/m³
    },
    "o3": {
        "8_hour": 100,  # µg/m³ (approximately 50 ppb)
    },
    "no2": {
        "annual": 10,  # µg/m³
        "24_hour": 25,  # µg/m³
    },
    "so2": {
        "24_hour": 40,  # µg/m³
    },
}
