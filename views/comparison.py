"""
City comparison view for multi-city air quality analysis.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time

from config import BrazilianCities
from data.data_collector import OpenAQClient, DataProcessor
from utils.aqi import calculate_aqi, get_aqi_category, format_parameter_name
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=900)  # Cache for 15 minutes
def fetch_comparison_data(cities: list):
    """
    Fetch air quality data for multiple cities.

    Args:
        cities: List of city names

    Returns:
        Dictionary mapping city names to their data
    """
    try:
        client = OpenAQClient()
        processor = DataProcessor()

        cities_data = {}

        for city in cities:
            lat, lon = BrazilianCities.get_coordinates(city)

            # Get locations
            raw_locations = client.get_locations_by_coordinates(lat, lon, radius=25000, limit=5)
            locations = processor.process_locations(raw_locations, city)

            if locations:
                # Get latest data from first location
                location_id = locations[0]["location_id"]
                latest_data = client.get_location_latest(int(location_id))

                if latest_data:
                    measurements = processor.process_latest_measurements(
                        latest_data,
                        city,
                        location_id
                    )

                    # Calculate AQI for each measurement
                    measurement_dict = {}
                    for m in measurements:
                        param = m['parameter'].lower()
                        aqi = calculate_aqi(m['value'], param)
                        measurement_dict[param] = {
                            'value': m['value'],
                            'unit': m['unit'],
                            'aqi': aqi
                        }

                    # Find dominant AQI
                    dominant_aqi = 0
                    dominant_param = 'unknown'
                    for param, data in measurement_dict.items():
                        if data['aqi'] and data['aqi'] > dominant_aqi:
                            dominant_aqi = data['aqi']
                            dominant_param = param

                    cities_data[city] = {
                        'aqi': dominant_aqi,
                        'dominant_param': dominant_param,
                        'measurements': measurement_dict,
                        'location_count': len(locations)
                    }

            time.sleep(0.3)

        return cities_data

    except Exception as e:
        logger.error(f"Failed to fetch comparison data: {e}")
        return {}


def show(cities: list):
    """
    Display the city comparison page.

    Args:
        cities: List of city names to compare
    """

    # Header
    st.title("🔄 City Comparison")
    st.markdown("Compare air quality across multiple Brazilian cities")

    st.markdown("---")

    if not cities or len(cities) < 2:
        st.warning("⚠️ Please select at least 2 cities from the sidebar to compare.")
        return

    # Fetch data
    with st.spinner("Loading comparison data..."):
        cities_data = fetch_comparison_data(cities)

    if not cities_data:
        st.error("❌ Unable to load comparison data. Please try again later.")
        return

    # Overview comparison cards
    st.subheader("📊 AQI Overview")

    cols = st.columns(len(cities))

    for idx, city in enumerate(cities):
        if city in cities_data:
            data = cities_data[city]
            aqi = data['aqi']
            category = get_aqi_category(aqi)

            with cols[idx]:
                st.markdown(f"""
                <div style="
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid {category.color};
                    background-color: rgba(255, 255, 255, 0.05);
                    text-align: center;
                ">
                    <h4 style="margin: 0;">{city}</h4>
                    <h1 style="margin: 15px 0; color: {category.color}; font-size: 48px;">{aqi}</h1>
                    <p style="margin: 0; font-size: 14px;">{category.label}</p>
                    <p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.7;">
                        Stations: {data['location_count']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            with cols[idx]:
                st.warning(f"No data for {city}")

    st.markdown("---")

    # AQI Bar Chart
    st.subheader("📊 AQI Comparison Chart")

    # Prepare data for chart
    chart_data = []
    for city, data in cities_data.items():
        aqi = data['aqi']
        category = get_aqi_category(aqi)
        chart_data.append({
            'City': city,
            'AQI': aqi,
            'Category': category.label,
            'Color': category.color
        })

    if chart_data:
        df = pd.DataFrame(chart_data).sort_values('AQI', ascending=False)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['City'],
            y=df['AQI'],
            marker_color=df['Color'],
            text=df['AQI'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>AQI: %{y}<br>%{customdata}<extra></extra>',
            customdata=df['Category']
        ))

        # Add AQI category reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5,
                     annotation_text="Good", annotation_position="right")
        fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5,
                     annotation_text="Moderate", annotation_position="right")
        fig.add_hline(y=150, line_dash="dash", line_color="gray", opacity=0.5,
                     annotation_text="Unhealthy (Sensitive)", annotation_position="right")

        fig.update_layout(
            title="Air Quality Index by City",
            xaxis_title="City",
            yaxis_title="AQI",
            height=400,
            template='plotly_dark',
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Pollutant comparison
    st.subheader("💨 Pollutant Comparison")

    # Collect all parameters
    all_params = set()
    for data in cities_data.values():
        all_params.update(data['measurements'].keys())

    if all_params:
        # Create tabs for each parameter
        param_tabs = st.tabs([format_parameter_name(p) for p in sorted(all_params)])

        for tab_idx, param in enumerate(sorted(all_params)):
            with param_tabs[tab_idx]:
                # Prepare data for this parameter
                param_data = []
                for city, data in cities_data.items():
                    if param in data['measurements']:
                        measurement = data['measurements'][param]
                        param_data.append({
                            'City': city,
                            'AQI': measurement['aqi'],
                            'Value': measurement['value'],
                            'Unit': measurement['unit']
                        })

                if param_data:
                    param_df = pd.DataFrame(param_data).sort_values('AQI', ascending=False)

                    # Create bar chart
                    fig = go.Figure()

                    colors = [get_aqi_category(aqi).color for aqi in param_df['AQI']]

                    fig.add_trace(go.Bar(
                        x=param_df['City'],
                        y=param_df['AQI'],
                        marker_color=colors,
                        text=param_df['AQI'],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>AQI: %{y}<br>Value: %{customdata[0]:.2f} %{customdata[1]}<extra></extra>',
                        customdata=param_df[['Value', 'Unit']].values
                    ))

                    fig.update_layout(
                        title=f"{format_parameter_name(param)} AQI Comparison",
                        xaxis_title="City",
                        yaxis_title="AQI",
                        height=350,
                        template='plotly_dark',
                        showlegend=False
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Show values table
                    st.dataframe(
                        param_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "City": "City",
                            "AQI": st.column_config.NumberColumn("AQI", format="%d"),
                            "Value": st.column_config.NumberColumn("Concentration", format="%.2f"),
                            "Unit": "Unit"
                        }
                    )
                else:
                    st.info(f"No {format_parameter_name(param)} data available for selected cities.")

    st.markdown("---")

    # Rankings
    st.subheader("🏆 Rankings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Best Air Quality")
        sorted_cities = sorted(cities_data.items(), key=lambda x: x[1]['aqi'])

        for rank, (city, data) in enumerate(sorted_cities[:3], 1):
            aqi = data['aqi']
            category = get_aqi_category(aqi)
            medal = ["🥇", "🥈", "🥉"][rank - 1]

            st.markdown(f"""
            <div style="
                padding: 10px;
                margin: 5px 0;
                border-left: 4px solid {category.color};
                background-color: rgba(255, 255, 255, 0.05);
            ">
                {medal} <strong>{city}</strong> - AQI: {aqi} ({category.label})
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Needs Attention")
        sorted_cities_desc = sorted(cities_data.items(), key=lambda x: x[1]['aqi'], reverse=True)

        for rank, (city, data) in enumerate(sorted_cities_desc[:3], 1):
            aqi = data['aqi']
            category = get_aqi_category(aqi)

            st.markdown(f"""
            <div style="
                padding: 10px;
                margin: 5px 0;
                border-left: 4px solid {category.color};
                background-color: rgba(255, 255, 255, 0.05);
            ">
                <strong>{city}</strong> - AQI: {aqi} ({category.label})
            </div>
            """, unsafe_allow_html=True)

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
