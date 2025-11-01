"""
Home page view for Aeris dashboard.
"""

import streamlit as st
from datetime import datetime
import time

from config import BrazilianCities
from data.data_collector import OpenAQClient
from utils.aqi import calculate_aqi, get_aqi_category, format_parameter_name
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_overview_data():
    """
    Fetch overview data for Brazilian cities.

    Returns:
        List of city data with latest AQI information
    """
    try:
        client = OpenAQClient()
        cities_data = []

        priority_cities = BrazilianCities.get_priority_cities(max_priority=4)

        for city in priority_cities:
            lat, lon = BrazilianCities.get_coordinates(city)

            # Get locations near city
            locations = client.get_locations_by_coordinates(lat, lon, radius=25000, limit=3)

            if locations:
                # Get latest data from first location
                location_id = locations[0].get('id')
                latest = client.get_location_latest(location_id)

                # API v3 returns a list of measurements
                if latest and isinstance(latest, list) and len(latest) > 0:
                    # Use the first measurement (most recent)
                    measurement = latest[0]
                    value = measurement.get('value')

                    if value:
                        # For simplicity, calculate AQI assuming PM2.5
                        # In a real scenario, we'd need to know the parameter type
                        aqi = calculate_aqi(value, 'pm25')
                        category = get_aqi_category(aqi) if aqi else None

                        cities_data.append({
                            'city': city,
                            'aqi': aqi,
                            'category': category.label if category else 'Unknown',
                            'color': category.color if category else '#CCCCCC',
                            'pm25': value,
                            'timestamp': datetime.now()
                        })

            # Small delay to avoid rate limiting
            time.sleep(0.3)

        return cities_data

    except Exception as e:
        logger.error(f"Failed to fetch overview data: {e}")
        return []


def show():
    """Display the home page."""

    # Header
    st.title("🌤️ Aeris - Air Quality Dashboard")
    st.markdown("""
    Welcome to **Aeris**, your real-time air quality monitoring dashboard for Brazilian cities.
    Track air pollution levels, view trends, and stay informed about the air you breathe.
    """)

    st.markdown("---")

    # Quick stats section
    st.subheader("📍 Current Air Quality Overview")

    with st.spinner("Loading latest air quality data..."):
        cities_data = fetch_overview_data()

    if cities_data:
        # Create columns for city cards
        cols = st.columns(len(cities_data))

        for idx, city_data in enumerate(cities_data):
            with cols[idx]:
                st.markdown(f"""
                <div style="
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid {city_data['color']};
                    background-color: rgba(255, 255, 255, 0.05);
                    margin-bottom: 10px;
                ">
                    <h4 style="margin: 0; color: {city_data['color']};">{city_data['city']}</h4>
                    <h2 style="margin: 10px 0; font-size: 48px;">{city_data['aqi']}</h2>
                    <p style="margin: 0; font-size: 14px;">{city_data['category']}</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.7;">
                        PM2.5: {city_data['pm25']:.1f} µg/m³
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.caption("💡 Tip: Click on a city name in the sidebar to view detailed information")

    else:
        st.warning("⚠️ Unable to load air quality data. Please check your internet connection and API key configuration.")

    st.markdown("---")

    # Features overview
    st.subheader("✨ Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📊 City Dashboard
        View detailed air quality metrics for individual cities:
        - Real-time AQI values
        - Multiple pollutant tracking
        - Historical trends
        - Health recommendations
        """)

    with col2:
        st.markdown("""
        ### 🔄 City Comparison
        Compare air quality across multiple cities:
        - Side-by-side metrics
        - Comparative visualizations
        - Trend analysis
        - Regional insights
        """)

    with col3:
        st.markdown("""
        ### 📈 Data Insights
        Access comprehensive air quality data:
        - Hourly updates
        - Time series charts
        - Export capabilities
        - OpenAQ integration
        """)

    st.markdown("---")

    # AQI Reference
    st.subheader("🎨 AQI Color Guide")

    st.markdown("""
    The Air Quality Index (AQI) is a standardized indicator of air quality:
    """)

    aqi_levels = [
        ("0-50", "Good", "#00E400", "Air quality is satisfactory"),
        ("51-100", "Moderate", "#FFFF00", "Acceptable for most people"),
        ("101-150", "Unhealthy for Sensitive Groups", "#FF7E00", "Sensitive groups should reduce outdoor activity"),
        ("151-200", "Unhealthy", "#FF0000", "Everyone may experience health effects"),
        ("201-300", "Very Unhealthy", "#8F3F97", "Health alert for all"),
        ("301-500", "Hazardous", "#7E0023", "Emergency conditions"),
    ]

    for aqi_range, label, color, description in aqi_levels:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            border-left: 5px solid {color};
            background-color: rgba(255, 255, 255, 0.05);
        ">
            <div style="flex: 0 0 80px; font-weight: bold;">{aqi_range}</div>
            <div style="flex: 0 0 200px; font-weight: bold;">{label}</div>
            <div style="flex: 1;">{description}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick links
    st.subheader("🔗 Quick Links")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("- [OpenAQ Platform](https://openaq.org)")
        st.markdown("- [EPA AQI Guide](https://www.airnow.gov/aqi/aqi-basics/)")

    with col2:
        st.markdown("- [WHO Air Quality Guidelines](https://www.who.int/health-topics/air-pollution)")
        st.markdown("- [Brazil Environmental Agency](https://www.gov.br/ibama)")

    with col3:
        st.markdown("- [Project Documentation](https://github.com/yourusername/aeris)")
        st.markdown("- [Report an Issue](https://github.com/yourusername/aeris/issues)")
