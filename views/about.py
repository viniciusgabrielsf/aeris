"""
About page view with project information and documentation.
"""

import streamlit as st
from config import OpenAQConfig


def show():
    """Display the about page."""

    # Header
    st.title("ℹ️ About Aeris")

    st.markdown("""
    **Aeris** is an open-source air quality monitoring dashboard for Brazilian cities,
    providing real-time air quality data and insights powered by the OpenAQ platform.
    """)

    st.markdown("---")

    # Project information
    st.subheader("🎯 Project Mission")

    st.markdown("""
    Aeris aims to make air quality data accessible and understandable for everyone in Brazil.
    By providing real-time monitoring, historical trends, and easy-to-understand visualizations,
    we empower citizens to make informed decisions about their health and environment.

    ### Key Features

    - **Real-time Monitoring**: Track current air quality levels across major Brazilian cities
    - **Multiple Pollutants**: Monitor PM2.5, PM10, O₃, NO₂, SO₂, and CO
    - **AQI Calculations**: Standardized Air Quality Index based on EPA guidelines
    - **Interactive Visualizations**: Charts, maps, and trends powered by Plotly
    - **City Comparisons**: Compare air quality across multiple cities
    - **OpenAQ Integration**: Data from the world's largest open air quality database
    """)

    st.markdown("---")

    # Technical Stack
    st.subheader("🛠️ Technical Stack")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Frontend
        - **Streamlit** - Interactive web framework
        - **Plotly** - Data visualization
        - **Pandas** - Data processing

        ### Backend
        - **Python 3.9+** - Core language
        - **SQLite** - Local data storage
        - **APScheduler** - Background jobs
        """)

    with col2:
        st.markdown("""
        ### Data Source
        - **OpenAQ API v3** - Air quality data
        - **Free tier** - No cost for usage
        - **Global coverage** - 100+ countries

        ### Tools
        - **pytest** - Testing framework
        - **ruff** - Code linting
        - **mypy** - Type checking
        """)

    st.markdown("---")

    # Data Sources
    st.subheader("📊 Data Sources")

    st.markdown(f"""
    ### OpenAQ Platform

    Aeris uses data from [OpenAQ](https://openaq.org), a non-profit organization that aggregates
    air quality data from government monitoring stations worldwide.

    **Current API Configuration:**
    - API Version: v3
    - Base URL: `{OpenAQConfig.BASE_URL}`
    - Authentication: API Key (configured ✅)
    - Rate Limit: {OpenAQConfig.RATE_LIMIT_REQUESTS} requests per {OpenAQConfig.RATE_LIMIT_WINDOW//60} minutes

    ### Data Coverage in Brazil

    Air quality monitoring in Brazil varies by region:
    - **São Paulo**: Excellent coverage with CETESB stations
    - **Rio de Janeiro**: Good coverage with INEA stations
    - **Other major cities**: Moderate to limited coverage

    **Note**: Data availability depends on local monitoring infrastructure and may vary over time.
    """)

    st.markdown("---")

    # AQI Information
    st.subheader("🎨 Understanding AQI")

    st.markdown("""
    The **Air Quality Index (AQI)** is a standardized indicator that tells you how clean or
    polluted your air is, and what associated health effects might be a concern.

    ### AQI Scale

    | Range | Category | Health Implications |
    |-------|----------|-------------------|
    | 0-50 | Good | Air quality is satisfactory |
    | 51-100 | Moderate | Acceptable for most people |
    | 101-150 | Unhealthy for Sensitive Groups | Sensitive individuals should limit outdoor activity |
    | 151-200 | Unhealthy | Everyone may experience health effects |
    | 201-300 | Very Unhealthy | Health alert for all |
    | 301-500 | Hazardous | Emergency conditions |

    ### Monitored Pollutants

    - **PM2.5**: Fine particulate matter (≤2.5 micrometers)
    - **PM10**: Coarse particulate matter (≤10 micrometers)
    - **O₃**: Ground-level ozone
    - **NO₂**: Nitrogen dioxide
    - **SO₂**: Sulfur dioxide
    - **CO**: Carbon monoxide

    The overall AQI is determined by the pollutant with the highest individual AQI value.
    """)

    st.markdown("---")

    # Project Information
    st.subheader("📖 Documentation & Resources")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### Project Links
        - [GitHub Repository](https://github.com/yourusername/aeris)
        - [Documentation](https://github.com/yourusername/aeris/wiki)
        - [Report Issues](https://github.com/yourusername/aeris/issues)
        """)

    with col2:
        st.markdown("""
        ### External Resources
        - [OpenAQ Platform](https://openaq.org)
        - [OpenAQ Documentation](https://docs.openaq.org)
        - [EPA AQI Guide](https://www.airnow.gov/aqi/)
        """)

    with col3:
        st.markdown("""
        ### Brazilian Resources
        - [CETESB (São Paulo)](https://cetesb.sp.gov.br)
        - [INEA (Rio de Janeiro)](http://www.inea.rj.gov.br)
        - [IBAMA](https://www.gov.br/ibama)
        """)

    st.markdown("---")

    # FAQs
    st.subheader("❓ Frequently Asked Questions")

    with st.expander("How often is the data updated?"):
        st.markdown("""
        Data is fetched from OpenAQ every 15-30 minutes depending on the page.
        The OpenAQ platform aggregates data from various sources, with update
        frequencies ranging from hourly to daily.
        """)

    with st.expander("Why is there no data for my city?"):
        st.markdown("""
        Air quality monitoring coverage in Brazil varies significantly. Some cities
        have extensive monitoring networks, while others have limited or no coverage.
        This depends on local government infrastructure and monitoring programs.

        If your city has no data, consider:
        - Checking nearby larger cities
        - Contacting your local environmental agency
        - Advocating for better air quality monitoring in your region
        """)

    with st.expander("How accurate is this data?"):
        st.markdown("""
        Aeris displays data directly from official government monitoring stations
        via the OpenAQ platform. Data accuracy depends on:
        - Proper maintenance of monitoring equipment
        - Calibration of sensors
        - Quality control procedures of source agencies

        We recommend using this data as a general indicator rather than for
        critical health decisions. Consult official sources for authoritative information.
        """)

    with st.expander("Can I export the data?"):
        st.markdown("""
        Currently, you can view and explore the data through the dashboard.
        Export functionality for CSV/Excel formats is planned for a future release.

        For now, you can access raw data directly through the OpenAQ API or
        contact the project maintainers for bulk data access.
        """)

    with st.expander("How can I contribute?"):
        st.markdown("""
        Aeris is an open-source project and welcomes contributions!

        You can help by:
        - Reporting bugs or suggesting features on GitHub
        - Improving documentation
        - Adding support for more cities
        - Contributing code improvements
        - Sharing the project with others

        Visit our [GitHub repository](https://github.com/yourusername/aeris) to get started.
        """)

    st.markdown("---")

    # Credits
    st.subheader("🙏 Credits & Acknowledgments")

    st.markdown("""
    Aeris is made possible by:

    - **OpenAQ** - For providing free access to global air quality data
    - **Streamlit** - For the amazing web framework
    - **Brazilian Environmental Agencies** - For maintaining monitoring stations
    - **Open Source Community** - For the tools and libraries that power this project

    ### License

    Aeris is released under the MIT License. See the project repository for details.
    """)

    st.markdown("---")

    # Contact
    st.subheader("📧 Contact")

    st.markdown("""
    For questions, suggestions, or collaboration opportunities:

    - **GitHub**: [Open an issue](https://github.com/yourusername/aeris/issues)
    - **Email**: your.email@example.com
    - **Project**: [github.com/yourusername/aeris](https://github.com/yourusername/aeris)
    """)

    st.markdown("---")

    st.info("💙 Thank you for using Aeris! Together, we can work towards cleaner air for everyone.")
