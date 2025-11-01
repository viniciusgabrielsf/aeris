"""
Aeris - Air Quality Dashboard for Brazilian Cities

Main Streamlit application entry point.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import BrazilianCities
from utils.logger import get_logger

logger = get_logger(__name__)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Aeris - Air Quality Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/viniciusgabrielsf/aeris',
        'Report a bug': 'https://github.com/viniciusgabrielsf/aeris/issues',
        'About': """
        # Aeris Air Quality Dashboard

        Real-time air quality monitoring for Brazilian cities using OpenAQ data.

        **Data Source:** OpenAQ API v3
        **Coverage:** São Paulo, Rio de Janeiro, Belo Horizonte, and more

        Built with Streamlit, Plotly, and Python.
        """
    }
)

# ==============================================================================
# Sidebar Navigation
# ==============================================================================

with st.sidebar:
    st.title("🌤️ Aeris")
    st.markdown("**Air Quality Dashboard**")
    st.markdown("---")

    # Page selection
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 City Dashboard", "🔄 Compare Cities", "ℹ️ About"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # City selector (available for dashboard and comparison pages)
    if page in ["📊 City Dashboard", "🔄 Compare Cities"]:
        st.subheader("Select City")

        cities = list(BrazilianCities.CITIES.keys())

        if page == "📊 City Dashboard":
            selected_city = st.selectbox(
                "City",
                cities,
                index=0,
                label_visibility="collapsed"
            )
            st.session_state['selected_city'] = selected_city
        else:
            selected_cities = st.multiselect(
                "Cities to Compare",
                cities,
                default=cities[:3],
                label_visibility="collapsed"
            )
            st.session_state['selected_cities'] = selected_cities

    st.markdown("---")

    # Info footer
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Data from OpenAQ API v3")

# ==============================================================================
# Main Content Area
# ==============================================================================

# Import page modules
from views import home, dashboard, comparison, about

# Route to selected page
if page == "🏠 Home":
    home.show()
elif page == "📊 City Dashboard":
    dashboard.show(st.session_state.get('selected_city', 'São Paulo'))
elif page == "🔄 Compare Cities":
    comparison.show(st.session_state.get('selected_cities', ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte']))
elif page == "ℹ️ About":
    about.show()

# ==============================================================================
# Footer
# ==============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🌍 Data Source: [OpenAQ](https://openaq.org)")

with col2:
    st.caption("📖 [Documentation](https://github.com/viniciusgabrielsf/aeris)")

with col3:
    st.caption("Made with ❤️ using Streamlit")
