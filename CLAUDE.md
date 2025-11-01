# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aeris is an Air Quality Dashboard for Brazilian Cities that provides real-time air quality monitoring using the OpenAQ API. The application displays AQI (Air Quality Index) data with color-coded alerts, time series visualizations, and supports multi-city comparisons.

**Target Cities:** São Paulo, Rio de Janeiro, Belo Horizonte, Brasília, Salvador, Fortaleza, Curitiba, Porto Alegre.

## Technical Stack

- **Frontend:** Streamlit (Python web framework)
- **Database:** SQLite for local data storage
- **Visualization:** Plotly for interactive charts
- **Data Source:** OpenAQ API v3 (free tier with API key required)
- **Scheduling:** APScheduler for automated data collection
- **Data Processing:** Pandas
- **Python Version:** 3.9+

## Development Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit dashboard
streamlit run app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run linting
ruff check .

# Run type checking
mypy .
```

## Project Structure

The project follows a modular architecture:

- **app.py** - Main Streamlit dashboard entry point
- **data/** - Data collection and processing modules
  - API client for OpenAQ integration
  - Data transformation and cleaning logic
  - Scheduled data collection jobs
- **database/** - Database operations and models
  - SQLite connection management
  - CRUD operations
  - Schema definitions
- **views/** - Dashboard pages and UI components
  - Main dashboard view
  - City comparison view
  - Report generation view
- **utils/** - Shared utilities
  - Configuration management (environment variables)
  - Logging setup
  - AQI calculation and color mapping
- **tests/** - Unit and integration tests
- **docker/** - Docker configuration for deployment

## Common Commands

```bash
# Run single test file
pytest tests/test_data_collection.py -v

# Run tests for specific function
pytest tests/test_database.py::test_insert_measurement -v

# Format code
ruff check --fix .

# Start with specific port
streamlit run app.py --server.port 8501

# Build Docker image
docker build -t aeris-dashboard .

# Run with Docker
docker-compose up
```

## Architecture

### Data Flow
1. **APScheduler** triggers periodic data collection (e.g., every 30 minutes)
2. **Data Collector** fetches air quality measurements from OpenAQ API v2
3. **Data Processor** validates, cleans, and transforms raw API data
4. **Database Layer** persists processed data to SQLite
5. **Streamlit Dashboard** queries database and displays visualizations with Plotly
6. **Caching Layer** reduces database queries for frequently accessed data

### OpenAQ API Integration
- **IMPORTANT**: OpenAQ v1 and v2 were retired January 31, 2025. Use v3 only.
- Base URL: `https://api.openaq.org/v3/`
- **Authentication**: Required - use X-API-Key header
- **API Key**: Free tier available at https://explore.openaq.org/register
- Key endpoints:
  - `/locations` - Monitoring stations
  - `/sensors` - Sensor data and measurements
  - `/latest` - Most recent measurements (v3 structure)
- Rate limiting: Depends on free tier limits (check documentation)
- Response format: JSON (v3 has different structure than v2)

### Database Schema
- **measurements** table: timestamp, city, parameter (PM2.5, PM10, O3, etc.), value, unit, location_id
- **locations** table: location_id, city, coordinates, station_name
- **cache** table: For storing computed aggregations and reports

### AQI Color Coding
Follow standard AQI categories: Good (Green), Moderate (Yellow), Unhealthy for Sensitive Groups (Orange), Unhealthy (Red), Very Unhealthy (Purple), Hazardous (Maroon).

### Streamlit Multi-page Architecture
Use Streamlit's native pages feature with separate Python files in the views/ directory. Each page should be self-contained with its own layout and data queries.

## Code Conventions

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Add comprehensive docstrings (Google style)
- Implement structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Use environment variables for configuration (API settings, database paths, cache durations)
- Write unit tests for critical functions (data processing, AQI calculations, database operations)
- Handle API errors gracefully with retries and fallbacks
- Implement Streamlit caching (`@st.cache_data`, `@st.cache_resource`) for performance

## Environment Variables

Configuration via environment variables or `.env` file:
- `OPENAQ_API_KEY` - **REQUIRED** - Your OpenAQ API key from https://explore.openaq.org
- `OPENAQ_API_BASE_URL` - OpenAQ API endpoint (default: https://api.openaq.org/v3)
- `DATABASE_PATH` - SQLite database file location
- `COLLECTION_INTERVAL_MINUTES` - Data collection frequency
- `LOG_LEVEL` - Logging verbosity
- `CACHE_TTL_SECONDS` - Cache time-to-live
- `STREAMLIT_SERVER_PORT` - Dashboard port

## Key Considerations

- **Performance:** Use Streamlit's caching mechanisms extensively. Cache database queries, API responses, and expensive computations.
- **Error Handling:** OpenAQ API may have intermittent availability. Implement exponential backoff for retries.
- **Data Quality:** OpenAQ data can have gaps or outliers. Implement validation and filtering logic.
- **Brazilian Cities:** OpenAQ coverage varies by city. Some cities may have limited or no monitoring stations.
- **Time Zones:** Handle Brazil's time zones correctly (most cities use BRT/BRST, but Amazon region differs).
- **Production Deployment:** Use Docker for consistent deployment. Configure proper logging and monitoring.
