# Aeris - Air Quality Dashboard for Brazilian Cities

![Status](https://img.shields.io/badge/status-development-yellow)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Aeris is an air quality monitoring dashboard that provides real-time and historical air quality data for major Brazilian cities. Built with Python, Streamlit, and SQLite, it offers an intuitive interface for tracking PM2.5, PM10, O3, NO2, SO2, and CO levels.

## 🎯 Features

- **Real-time Monitoring**: Live air quality data from OpenAQ network
- **Multi-city Support**: Track air quality across 8 major Brazilian cities
- **Time Series Analysis**: View trends over 24h, 7 days, and 30 days
- **Visual Alerts**: Color-coded AQI (Air Quality Index) indicators
- **City Comparisons**: Compare air quality across multiple cities
- **Data Export**: Download data in CSV format
- **Automated Collection**: Background scheduler for continuous data updates

## 🏙️ Monitored Cities

- São Paulo (SP)
- Rio de Janeiro (RJ)
- Belo Horizonte (MG)
- Curitiba (PR)
- Brasília (DF)
- Salvador (BA)
- Fortaleza (CE)
- Porto Alegre (RS)

## 🚨 IMPORTANT: OpenAQ API v3 Update

**⚠️ Breaking Change**: OpenAQ has migrated to v3 API (as of January 31, 2025)

- **v1 and v2 APIs are RETIRED** and no longer work
- **v3 requires API authentication** (free tier available)
- You must register and obtain an API key

### Getting Your Free API Key

1. **Register** at: https://explore.openaq.org/register
2. **Sign in** and navigate to your account settings
3. **Copy your API key** from the settings page
4. **Add to `.env` file** (see Setup section below)

**Note**: The API key is free, but registration is required. Treat your API key like a password.

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAQ API key (free - see above)
- 500 MB free disk space (for database)
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

Add this line to your `.env` file:
```bash
OPENAQ_API_KEY=your_api_key_here
```

### 5. Test the Setup

Run the test collection script to verify everything works:

```bash
python test_collection.py
```

This will:
- Test API connectivity
- Initialize the database
- Collect sample data from 3 cities
- Display summary statistics

### 6. Run the Dashboard (Coming Soon)

```bash
streamlit run app.py
```

The dashboard will be available at: http://localhost:8501

## 📁 Project Structure

```
aeris/
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── test_collection.py         # Test data collection
│
├── data/                      # Data collection modules
│   ├── __init__.py
│   └── data_collector.py     # OpenAQ API client
│
├── database/                  # Database operations
│   ├── __init__.py
│   └── database.py           # SQLite operations
│
├── utils/                     # Utilities
│   ├── __init__.py
│   └── logger.py             # Logging configuration
│
├── views/                     # Streamlit dashboard pages
│   └── (to be implemented)
│
├── tests/                     # Unit tests
│   └── (to be implemented)
│
└── data_storage/              # Local data storage
    ├── aeris.db              # SQLite database
    ├── aeris.log             # Application logs
    └── cache/                # API response cache
```

## 🗄️ Database Schema

### Tables

1. **cities** - Monitoring locations and stations
2. **air_measurements** - Time series air quality data
3. **alerts** - Air quality alerts and notifications

### Key Features

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

Run the test collection script:

```bash
python test_collection.py
```

Expected output:
- API connection test ✓
- Database initialization ✓
- Data collection for 3 cities ✓
- Summary statistics

## 📝 Development Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Project structure
- [x] Configuration management
- [x] OpenAQ API client (v3 support needed)
- [x] Database schema and operations
- [x] Logging system
- [x] Test collection script

### Phase 2: API v3 Migration 🚧 (Next)
- [ ] Update API client for v3 endpoints
- [ ] Implement API key authentication
- [ ] Test with real API credentials
- [ ] Update error handling for v3

### Phase 3: Dashboard (Upcoming)
- [ ] Main dashboard view
- [ ] City selector
- [ ] Real-time AQI display
- [ ] Time series charts
- [ ] Alert system

### Phase 4: Advanced Features (Future)
- [ ] Multi-city comparison
- [ ] Data export functionality
- [ ] Historical data analysis
- [ ] Predictive analytics
- [ ] Mobile responsive design

## ⚠️ Known Issues

1. **OpenAQ API v3 Migration Required**
   - Status: In progress
   - Impact: Data collection not functional until v3 implementation complete
   - Resolution: Update data_collector.py to use v3 endpoints

2. **API Key Authentication**
   - Status: Needs implementation
   - Impact: Cannot fetch data without proper authentication
   - Resolution: Implement X-API-Key header in requests

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
- **Python Community** - For excellent libraries and tools

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the research documents in project root

## 📚 Additional Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [CLAUDE.md](CLAUDE.md) - Claude Code guidance
- [AIR_QUALITY_RESEARCH.md](AIR_QUALITY_RESEARCH.md) - API research and analysis
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Step-by-step implementation

## 🔄 Recent Changes

### 2025-11-01
- ✅ Initial project structure created
- ✅ Configuration system implemented
- ✅ Database schema designed
- ✅ OpenAQ client skeleton created
- ⚠️ Discovered OpenAQ v3 API migration requirement
- 📝 Documented API key requirement

---

**Note**: This project is under active development. The OpenAQ API v3 migration is the current priority. Check back for updates!

**Last Updated**: November 1, 2025
