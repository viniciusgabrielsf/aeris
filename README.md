# Aeris - Air Quality Dashboard for Brazilian Cities

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Aeris is a real-time air quality monitoring dashboard for Brazilian cities. Built with Python, Streamlit, and the OpenAQ API v3, it provides an intuitive interface for tracking PM2.5, PM10, O3, NO2, SO2, and CO levels with interactive visualizations and multi-city comparisons.

## 🎥 Video Demo

> **Coming Soon!** A video demonstration showcasing the dashboard features and functionality.

<!--
To add your video, replace this comment with one of the following:

For YouTube:
[![Watch the demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

For Vimeo:
[![Watch the demo](https://i.vimeocdn.com/video/YOUR_VIDEO_ID_1280x720.jpg)](https://vimeo.com/YOUR_VIDEO_ID)

For Loom:
[![Watch the demo](https://cdn.loom.com/sessions/thumbnails/YOUR_VIDEO_ID-with-play.gif)](https://www.loom.com/share/YOUR_VIDEO_ID)

Or use a simple link:
[🎬 Watch Video Demo](YOUR_VIDEO_LINK_HERE)
-->

## 🎯 Features

- **Real-time Monitoring**: Live air quality data from OpenAQ API v3
- **Multi-city Support**: Track air quality across Brazilian cities (São Paulo, Rio de Janeiro, and more)
- **Interactive Visualizations**: Plotly charts and OpenStreetMap integration
- **Color-coded AQI**: EPA standard Air Quality Index with health recommendations
- **City Comparisons**: Side-by-side comparison of multiple cities with rankings
- **Detailed Analysis**: Individual pollutant levels and monitoring station locations
- **Smart Caching**: Optimized data fetching with configurable cache duration

## 🏙️ Monitored Cities

The dashboard supports the following Brazilian cities:

- **São Paulo (SP)** - ✅ Data available
- **Rio de Janeiro (RJ)** - ✅ Data available
- Belo Horizonte (MG) - Limited/no data
- Curitiba (PR) - Limited/no data
- Brasília (DF) - Limited/no data
- Salvador (BA) - Limited/no data
- Fortaleza (CE) - Limited/no data
- Porto Alegre (RS) - Limited/no data

**Note:** Data availability depends on active monitoring stations reporting to OpenAQ. Most Brazilian cities outside São Paulo and Rio de Janeiro have limited air quality monitoring infrastructure.

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAQ API key (free - see [API Key Setup Guide](claude_code_explore_plan/API_KEY_SETUP.md))
- Internet connection

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aeris
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAQ API key
nano .env  # or use your preferred editor
```

Add your API key to the `.env` file:
```bash
OPENAQ_API_KEY=your_api_key_here
```

**Need an API key?** See the detailed [API Key Setup Guide](claude_code_explore_plan/API_KEY_SETUP.md) for step-by-step instructions.

### 5. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically open at: http://localhost:8501

### 6. (Optional) Test API Connection

Run the test collection script to verify API connectivity:

```bash
python test_collection.py
```

## 📁 Project Structure

```
aeris/
├── app.py                     # Main Streamlit application
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── test_collection.py         # API testing script
│
├── data/                      # Data collection modules
│   ├── __init__.py
│   └── data_collector.py     # OpenAQ API v3 client
│
├── database/                  # Database operations
│   ├── __init__.py
│   └── database.py           # SQLite operations (ready, not integrated)
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py             # Logging system
│   └── aqi.py                # AQI calculations
│
├── views/                     # Dashboard pages
│   ├── __init__.py
│   ├── home.py               # Home page
│   ├── dashboard.py          # City dashboard
│   ├── comparison.py         # City comparison
│   └── about.py              # About page
│
├── tests/                     # Unit tests suite (178 tests)
│
└── data_storage/              # Local data storage
    ├── aeris.db              # SQLite database
    └── aeris.log             # Application logs
```

## 🗄️ Database Schema

The database module is fully implemented but **not currently integrated** with the dashboard. The dashboard uses direct API calls with Streamlit caching for optimal performance. See [DATABASE_USAGE.md](DATABASE_USAGE.md) for architecture details.

### Implemented Tables

1. **cities** - Monitoring locations and stations
2. **air_measurements** - Time series air quality data
3. **alerts** - Air quality alerts and notifications

### Features (Ready for Integration)

- Optimized indexes for fast queries
- 90-day data retention (configurable)
- Automatic cleanup of old data
- Support for all major air quality parameters

## 🔧 Configuration

Edit `.env` file to customize:

```bash
# OpenAQ API
OPENAQ_API_KEY=your_key_here
OPENAQ_API_BASE_URL=https://api.openaq.org/v3

# Database
DATABASE_PATH=data_storage/aeris.db
RAW_DATA_RETENTION_DAYS=90

# Logging
LOG_LEVEL=INFO
LOG_FILE=data_storage/aeris.log

# Data Collection
COLLECTION_INTERVAL_MINUTES=30

# Caching
CACHE_TTL_MINUTES=30
```

## 📊 Air Quality Parameters

| Parameter | Full Name | Unit | WHO Guideline |
|-----------|-----------|------|---------------|
| PM2.5 | Particulate Matter 2.5 | µg/m³ | 25 (24h) |
| PM10 | Particulate Matter 10 | µg/m³ | 50 (24h) |
| O3 | Ozone | µg/m³ | 100 (8h) |
| NO2 | Nitrogen Dioxide | µg/m³ | 40 (annual) |
| SO2 | Sulfur Dioxide | µg/m³ | 20 (24h) |
| CO | Carbon Monoxide | µg/m³ | 10000 (8h) |

## 🎨 AQI Color Scale

| AQI Range | Category | Color | Health Impact |
|-----------|----------|-------|---------------|
| 0-50 | Good | 🟢 Green | Minimal |
| 51-100 | Moderate | 🟡 Yellow | Acceptable |
| 101-150 | Unhealthy for Sensitive | 🟠 Orange | Sensitive groups |
| 151-200 | Unhealthy | 🔴 Red | Everyone |
| 201-300 | Very Unhealthy | 🟣 Purple | Serious effects |
| 301+ | Hazardous | 🟤 Maroon | Emergency |

## 🧪 Testing

The project includes a comprehensive test suite with 98 unit tests covering core functionality.

### Quick Test Commands

```bash
# Run all unit tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_aqi.py -v

# Run only passing tests
pytest --lf
```

### Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| **AQI Calculations** | 57 tests | ✅ All passing |
| **Logging** | 41 tests | ✅ All passing |
| **Total** | **98 tests** | **✅ 100% passing** |

### Integration Testing

Test the OpenAQ API connection:

```bash
python test_collection.py
```

Expected output:
- API connection test ✓
- Database initialization ✓
- Data collection for 3 cities ✓
- Summary statistics

### Documentation

For detailed testing documentation, see **[tests/README.md](tests/README.md)** which includes:
- Test organization and structure
- Running specific test suites
- Writing new tests
- Fixtures and mocking
- Coverage goals and best practices

## 📝 Development Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] Project structure
- [x] Configuration management
- [x] OpenAQ API v3 client with authentication
- [x] Database schema and operations
- [x] Logging system
- [x] AQI calculation utilities
- [x] Test collection script

### Phase 2: API v3 Migration ✅ (Complete)
- [x] Updated API client for v3 endpoints
- [x] Implemented API key authentication
- [x] Tested with real API credentials
- [x] Updated error handling for v3
- [x] Response format processing

### Phase 3: Dashboard ✅ (Complete)
- [x] Main dashboard application
- [x] Home page with city overview
- [x] City dashboard with detailed metrics
- [x] Multi-city comparison page
- [x] About page with documentation
- [x] Interactive Plotly visualizations
- [x] Real-time AQI display with color coding
- [x] Health recommendations

### Phase 4: Testing & Quality ✅ (Complete)
- [x] Comprehensive unit test suite (98 tests - 100% passing)
- [x] Test fixtures and mocking
- [x] Coverage reporting configuration
- [x] Testing documentation

### Phase 5: Future Enhancements 📋 (Planned)
- [ ] Database integration for historical data
- [ ] Background scheduler for automated collection
- [ ] 7-day and 30-day trend analysis
- [ ] Data export functionality (CSV, Excel)
- [ ] Email/SMS alerts for poor air quality
- [ ] Docker deployment
- [ ] Mobile responsiveness improvements

## ⚠️ Known Limitations

1. **Limited City Coverage**
   - Status: Expected behavior
   - Details: Only São Paulo and Rio de Janeiro have active monitoring stations reporting to OpenAQ
   - Reason: Real-world infrastructure limitation in Brazil
   - Impact: Other cities show "no data available" message

2. **No Historical Data**
   - Status: By design (current architecture)
   - Details: Dashboard uses direct API calls without database persistence
   - Impact: Cannot show historical trends (7-day, 30-day)
   - Resolution: See [DATABASE_USAGE.md](DATABASE_USAGE.md) for integration guide

3. **Data Freshness**
   - Status: Working as designed
   - Details: Data cached for 15-30 minutes for performance
   - Impact: May not show absolute real-time data
   - Resolution: Use "Refresh Data" button for latest data

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAQ** - For providing free air quality data
- **Streamlit** - For the amazing dashboard framework
- **Claude Code by Anthropic** - AI-assisted development that accelerated project implementation
- **Cursor** - AI-powered code editor used for development
- **Python Community** - For excellent libraries and tools

### Development Tools

This project was built with the support of AI-powered development tools:

- **[Claude Code](https://claude.ai/code)** - Anthropic's AI coding assistant that helped with architecture design, code generation, API integration, and comprehensive documentation
- **[Cursor](https://cursor.com)** - AI-powered code editor that enhanced the development workflow

These tools significantly accelerated the development process, from initial concept to production-ready dashboard.

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the research documents in project root

## 📚 Additional Documentation

### Core Documentation
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current project status and progress
- [DATABASE_USAGE.md](DATABASE_USAGE.md) - Database architecture and integration guide
- [CLAUDE.md](CLAUDE.md) - Claude Code development guidelines
- **[tests/README.md](tests/README.md)** - Comprehensive testing guide

### Research & Planning (in `claude_code_explore_plan/`)
- [API_KEY_SETUP.md](claude_code_explore_plan/API_KEY_SETUP.md) - Detailed API key setup guide
- [V3_MIGRATION_COMPLETE.md](claude_code_explore_plan/V3_MIGRATION_COMPLETE.md) - API v3 migration details
- [ARCHITECTURE.md](claude_code_explore_plan/ARCHITECTURE.md) - System architecture
- [AIR_QUALITY_RESEARCH.md](claude_code_explore_plan/AIR_QUALITY_RESEARCH.md) - API research
- [IMPLEMENTATION_GUIDE.md](claude_code_explore_plan/IMPLEMENTATION_GUIDE.md) - Implementation steps

## 🔄 Recent Changes

### Version 1.1.0-beta (2025-11-01)

**Testing Infrastructure Added** 🧪

- ✅ **Comprehensive Unit Test Suite**
  - 98 unit tests - 100% passing
  - Full coverage for AQI calculations (57 tests)
  - Complete logger testing (41 tests)
  - Pytest configuration with markers and coverage reporting
  - Shared fixtures and mocking utilities

- 📝 **Testing Documentation**
  - Comprehensive tests/README.md guide
  - Test organization and best practices
  - Examples and troubleshooting

### Version 1.0.0-beta (2025-11-01)

**Major Release - Full Dashboard Operational** 🎉

- ✅ **OpenAQ API v3 Integration Complete**
  - Updated all API endpoints to v3
  - Implemented API key authentication
  - Added support for both list and dict response formats

- ✅ **Full Streamlit Dashboard**
  - Home page with multi-city overview
  - City dashboard with detailed metrics
  - City comparison with interactive charts
  - About page with comprehensive documentation

- ✅ **AQI Calculation System**
  - EPA standard formulas for all pollutants (PM2.5, PM10, O₃, NO₂, SO₂, CO)
  - Color-coded categories with health recommendations
  - Dominant pollutant identification

- ✅ **Interactive Visualizations**
  - Plotly time series charts
  - OpenStreetMap integration for station locations
  - Real-time data updates

- ✅ **Performance Optimizations**
  - Smart caching (15-30 minute TTL)
  - Optimized API usage
  - Fast page loads

- 📝 **Comprehensive Documentation**
  - IMPLEMENTATION_STATUS.md - Full project status
  - DATABASE_USAGE.md - Architecture guide
  - API_KEY_SETUP.md - Setup instructions

**Status:** Production-ready for real-time air quality monitoring ✅

---

**Last Updated**: November 1, 2025
**Version**: 1.0.0-beta
**Status**: Active Development
