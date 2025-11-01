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
    By providing real-time monitoring and easy-to-understand visualizations,
    we empower citizens to make informed decisions about their health and environment.

    ### Current Implementation

    **Version:** 1.0.0-beta (Production-ready)

    - **Real-time Monitoring**: Live data from OpenAQ API v3
    - **Four Dashboard Pages**: Home overview, City details, Comparison, and About
    - **Multiple Pollutants**: PM2.5, PM10, O₃, NO₂, SO₂, and CO tracking
    - **EPA AQI Calculations**: Color-coded categories with health recommendations
    - **Interactive Visualizations**: Plotly charts and OpenStreetMap integration
    - **Multi-city Comparisons**: Side-by-side analysis with rankings
    - **Smart Caching**: 15-30 minute data caching for optimal performance
    - **Monitoring Stations**: Display locations on interactive maps

    ### Architecture

    The dashboard uses a **direct API approach** for simplicity and real-time data:
    - Data fetched on-demand from OpenAQ API v3
    - Cached in memory for performance (15-30 minutes)
    - No database persistence (current design choice)
    - See [DATABASE_USAGE.md](https://github.com/viniciusgabrielsf/aeris/blob/main/DATABASE_USAGE.md) for details and alternative architectures
    """)

    st.markdown("---")

    # Technical Stack
    st.subheader("🛠️ Technical Stack")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Frontend
        - **Streamlit 1.31** - Interactive web framework
        - **Plotly 5.18** - Data visualization
        - **Pandas 2.2** - Data processing

        ### Backend
        - **Python 3.9+** - Core language
        - **Requests** - HTTP client for API calls
        - **SQLite** - Database (ready, not integrated)
        - **Direct API** - Current data architecture
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

    Air quality monitoring in Brazil varies significantly by region:
    - **São Paulo**: ✅ **Active** - Excellent coverage with CETESB stations
    - **Rio de Janeiro**: ✅ **Active** - Good coverage with INEA stations
    - **Other major cities**: ⚠️ **Limited/No Data** - Most Brazilian cities outside São Paulo and Rio have limited or no monitoring stations reporting to OpenAQ

    **Current Reality**: Only São Paulo and Rio de Janeiro have active monitoring stations with data available through OpenAQ. This reflects the real-world infrastructure limitation in Brazil, not a limitation of the dashboard.

    **Note**: The dashboard is designed to support all major Brazilian cities, but data availability depends entirely on local monitoring infrastructure and whether stations report to the OpenAQ platform.
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
        - [GitHub Repository](https://github.com/viniciusgabrielsf/aeris)
        - [Documentation](https://github.com/viniciusgabrielsf/aeris)
        - [Report Issues](https://github.com/viniciusgabrielsf/aeris/issues)
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
        **Dashboard Caching:** Data is cached for 15-30 minutes depending on the page:
        - Home page: 30 minutes
        - City dashboard: 15 minutes
        - Comparison page: 15 minutes

        **OpenAQ Updates:** The OpenAQ platform aggregates data from government monitoring stations with update frequencies ranging from hourly to daily, depending on the source.

        **Refresh Data:** You can manually refresh data using the "🔄 Refresh Data" button at the bottom of most pages to clear the cache and fetch the latest data.
        """)

    with st.expander("Why is there no data for my city?"):
        st.markdown("""
        **Current Status:** Only São Paulo and Rio de Janeiro have active monitoring stations reporting to OpenAQ.

        **Reason:** This is a real-world infrastructure limitation, not a dashboard limitation. Most Brazilian cities outside these two major metropolitan areas either:
        - Don't have air quality monitoring stations
        - Have stations that don't report to the OpenAQ platform
        - Have monitoring programs that only share data through local/regional systems

        **What you can do:**
        - Check nearby larger cities (São Paulo or Rio de Janeiro)
        - Contact your local environmental agency to inquire about air quality monitoring
        - Advocate for better air quality monitoring infrastructure in your region
        - Check if your city has a local air quality monitoring website or app
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

    with st.expander("Why is there no historical data or trends?"):
        st.markdown("""
        **Current Architecture:** The dashboard uses a direct API approach without database persistence.

        **By Design:** This keeps the application simple, fast, and always shows the most recent data. Data is cached in memory for 15-30 minutes for performance but not permanently stored.

        **What this means:**
        - You see current/recent air quality data
        - No 7-day or 30-day historical trends
        - No time-based analysis or predictions
        - Simpler architecture with fewer moving parts

        **Future Plans:** Database integration for historical data is documented and ready to implement. See [DATABASE_USAGE.md](https://github.com/viniciusgabrielsf/aeris/blob/main/DATABASE_USAGE.md) for technical details about alternative architectures.
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

        Visit our [GitHub repository](https://github.com/viniciusgabrielsf/aeris) to get started.
        """)

    st.markdown("---")

    # Credits
    st.subheader("🙏 Credits & Acknowledgments")

    st.markdown("""
    Aeris is made possible by:

    - **OpenAQ** - For providing free access to global air quality data
    - **Streamlit** - For the amazing web framework
    - **Claude Code by Anthropic** - AI-assisted development that accelerated the entire project implementation
    - **Brazilian Environmental Agencies** - For maintaining monitoring stations
    - **Open Source Community** - For the tools and libraries that power this project

    ### Development

    This project was built with the support of **Claude Code** (claude.ai/code), Anthropic's AI-powered coding assistant, which helped with:
    - Architecture design and implementation planning
    - Code generation for all dashboard components
    - API integration and data processing
    - Documentation and best practices
    - Debugging and optimization

    ### License

    Aeris is released under the MIT License. See the project repository for details.
    """)

    st.markdown("---")

    # Contact
    st.subheader("📧 Contact")

    st.markdown("""
    For questions, suggestions, or collaboration opportunities:

    - **GitHub**: [Open an issue](https://github.com/viniciusgabrielsf/aeris/issues)
    - **Project**: [github.com/viniciusgabrielsf/aeris](https://github.com/viniciusgabrielsf/aeris)
    - **Email**: alinecristinapinto@ufmg.br
    - **Email**: viniciusgabrielsf@ufmg.br

    """)

    st.markdown("---")

    st.info("💙 Thank you for using Aeris! Together, we can work towards cleaner air for everyone.")
