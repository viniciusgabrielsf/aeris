"""
City dashboard view for detailed air quality metrics.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import time

from config import BrazilianCities
from data.data_collector import OpenAQClient, DataProcessor
from utils.aqi import (
    calculate_aqi,
    get_aqi_description,
    format_parameter_name,
    calculate_dominant_aqi
)
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=900)  # Cache for 15 minutes
def fetch_city_data(city_name: str):
    """
    Fetch comprehensive data for a city.

    Args:
        city_name: Name of the city

    Returns:
        Tuple of (locations, measurements_df, latest_aqi_data)
    """
    try:
        client = OpenAQClient()
        processor = DataProcessor()

        lat, lon = BrazilianCities.get_coordinates(city_name)

        # Get locations
        raw_locations = client.get_locations_by_coordinates(lat, lon, radius=25000, limit=10)
        locations = processor.process_locations(raw_locations, city_name)

        if not locations:
            return [], None, None

        # Collect measurements
        all_measurements = []
        for location in locations[:5]:  # Limit to first 5 locations
            location_id = location["location_id"]
            latest_data = client.get_location_latest(int(location_id))

            if latest_data:
                measurements = processor.process_latest_measurements(
                    latest_data,
                    city_name,
                    location_id
                )
                all_measurements.extend(measurements)

            time.sleep(0.2)

        # Convert to DataFrame
        if all_measurements:
            df = pd.DataFrame(all_measurements)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Calculate AQI for each measurement
            df['aqi'] = df.apply(
                lambda row: calculate_aqi(row['value'], row['parameter']),
                axis=1
            )

            # Get latest AQI data
            latest_measurements = {}
            for _, row in df.iterrows():
                param = row['parameter'].lower()
                if param not in latest_measurements:
                    latest_measurements[param] = row['value']

            dominant_aqi, dominant_param, all_aqis = calculate_dominant_aqi(latest_measurements)
            aqi_info = get_aqi_description(dominant_aqi)

            latest_aqi_data = {
                'aqi': dominant_aqi,
                'info': aqi_info,
                'dominant_param': dominant_param,
                'all_aqis': all_aqis,
                'measurements': latest_measurements
            }

            return locations, df, latest_aqi_data

        return locations, None, None

    except Exception as e:
        logger.error(f"Failed to fetch city data: {e}")
        return [], None, None


def show(city_name: str):
    """
    Display the city dashboard page.

    Args:
        city_name: Name of the city to display
    """

    # Header
    st.title(f"📊 {city_name} - Air Quality Dashboard")

    # City info
    city_info = BrazilianCities.CITIES.get(city_name, {})
    st.caption(f"📍 {city_info.get('state', '')} • Population: {city_info.get('population', 0):,}")

    st.markdown("---")

    # Fetch data
    with st.spinner("Loading air quality data..."):
        locations, df, latest_aqi_data = fetch_city_data(city_name)

    if not latest_aqi_data:
        st.warning(f"⚠️ No air quality data available for {city_name} at the moment.")
        st.info("💡 This could mean there are no active monitoring stations near this city, or data is temporarily unavailable.")
        return

    # Current AQI Display
    st.subheader("🌡️ Current Air Quality")

    aqi_info = latest_aqi_data['info']
    aqi = latest_aqi_data['aqi']

    # Large AQI display
    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        st.markdown(f"""
        <div style="
            padding: 30px;
            border-radius: 15px;
            background: linear-gradient(135deg, {aqi_info['color']}33, {aqi_info['color']}11);
            border: 3px solid {aqi_info['color']};
            text-align: center;
        ">
            <h1 style="
                font-size: 72px;
                margin: 0;
                color: {aqi_info['color']};
                font-weight: bold;
            ">{aqi}</h1>
            <p style="
                font-size: 24px;
                margin: 10px 0 0 0;
                font-weight: bold;
            ">{aqi_info['category']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        ### Health Implications
        {aqi_info['health_message']}

        **Dominant Pollutant:** {format_parameter_name(latest_aqi_data['dominant_param'])}
        """)

        # Health recommendations based on AQI
        if aqi <= 50:
            st.success("✅ Enjoy outdoor activities!")
        elif aqi <= 100:
            st.info("ℹ️ Sensitive individuals should limit prolonged outdoor exertion.")
        elif aqi <= 150:
            st.warning("⚠️ Sensitive groups should reduce outdoor activity.")
        elif aqi <= 200:
            st.warning("⚠️ Everyone should reduce outdoor activity.")
        else:
            st.error("🚨 Avoid all outdoor activities!")

    with col3:
        st.metric(
            "Monitoring Stations",
            len(locations),
            delta=None
        )

        st.metric(
            "Last Updated",
            datetime.now().strftime("%H:%M"),
            delta=None
        )

    st.markdown("---")

    # Individual pollutant metrics
    st.subheader("💨 Pollutant Levels")

    if df is not None and not df.empty:
        # Get latest value for each parameter
        latest_params = df.groupby('parameter').first().reset_index()

        cols = st.columns(min(len(latest_params), 4))

        for idx, (_, row) in enumerate(latest_params.iterrows()):
            col_idx = idx % 4
            with cols[col_idx]:
                param_aqi = latest_aqi_data['all_aqis'].get(row['parameter'].lower())
                if param_aqi:
                    aqi_cat = get_aqi_description(param_aqi)

                    st.markdown(f"""
                    <div style="
                        padding: 15px;
                        border-radius: 10px;
                        border-left: 4px solid {aqi_cat['color']};
                        background-color: rgba(255, 255, 255, 0.05);
                        margin-bottom: 10px;
                    ">
                        <h4 style="margin: 0;">{format_parameter_name(row['parameter'])}</h4>
                        <h2 style="margin: 10px 0; color: {aqi_cat['color']};">{param_aqi}</h2>
                        <p style="margin: 0; font-size: 12px;">{row['value']:.1f} {row['unit']}</p>
                        <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.7;">{aqi_cat['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Time series chart
        st.subheader("📈 Trend Analysis")

        # Group by parameter for plotting
        fig = go.Figure()

        for parameter in df['parameter'].unique():
            param_df = df[df['parameter'] == parameter].sort_values('timestamp')

            fig.add_trace(go.Scatter(
                x=param_df['timestamp'],
                y=param_df['aqi'],
                mode='lines+markers',
                name=format_parameter_name(parameter),
                line=dict(width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title="AQI Over Time by Pollutant",
            xaxis_title="Time",
            yaxis_title="AQI",
            hovermode='x unified',
            height=400,
            template='plotly_dark'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Data table
        with st.expander("📋 View Raw Data"):
            display_df = df[['timestamp', 'parameter', 'value', 'unit', 'aqi']].copy()
            display_df['parameter'] = display_df['parameter'].apply(format_parameter_name)
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df = display_df.sort_values('timestamp', ascending=False)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": "Timestamp",
                    "parameter": "Parameter",
                    "value": st.column_config.NumberColumn("Value", format="%.2f"),
                    "unit": "Unit",
                    "aqi": st.column_config.NumberColumn("AQI", format="%d")
                }
            )

    # Monitoring locations
    st.markdown("---")
    st.subheader("📍 Monitoring Locations")

    if locations:
        location_df = pd.DataFrame(locations)

        # Create map
        if 'latitude' in location_df.columns and 'longitude' in location_df.columns:
            map_df = location_df[['station_name', 'latitude', 'longitude']].dropna()

            if not map_df.empty:
                fig = px.scatter_mapbox(
                    map_df,
                    lat='latitude',
                    lon='longitude',
                    hover_name='station_name',
                    zoom=10,
                    height=400,
                )

                fig.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r": 0, "t": 0, "l": 0, "b": 0}
                )

                st.plotly_chart(fig, use_container_width=True)

        # Location details
        with st.expander("ℹ️ Station Details"):
            st.dataframe(
                location_df[['station_name', 'location_id', 'latitude', 'longitude']],
                use_container_width=True,
                hide_index=True
            )

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
