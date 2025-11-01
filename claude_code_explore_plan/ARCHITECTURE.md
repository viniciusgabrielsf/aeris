# Aeris - Air Quality Dashboard Architecture

## 1. PROJECT DIRECTORY STRUCTURE

```
aeris/
├── .gitignore                 # Python gitignore (already exists)
├── CLAUDE.md                  # Claude Code guidance (already exists)
├── README.md                  # Project documentation
├── ARCHITECTURE.md            # This file
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── config.py                  # Configuration management
├── app.py                     # Main Streamlit application entry point
│
├── data/                      # Data collection and processing
│   ├── __init__.py
│   ├── openaq_client.py      # OpenAQ API client
│   ├── data_processor.py     # Data validation and transformation
│   └── scheduler.py           # APScheduler for periodic data collection
│
├── database/                  # Database operations
│   ├── __init__.py
│   ├── models.py             # SQLite schema definitions
│   ├── operations.py         # CRUD operations
│   └── migrations.py         # Database initialization and updates
│
├── utils/                     # Shared utilities
│   ├── __init__.py
│   ├── aqi_calculator.py     # AQI calculation and color mapping
│   ├── constants.py          # Brazilian cities, pollutants, thresholds
│   ├── logger.py             # Logging configuration
│   └── cache.py              # Caching utilities
│
├── views/                     # Streamlit dashboard pages
│   ├── __init__.py
│   ├── home.py               # Main dashboard with city selector
│   ├── comparison.py         # Multi-city comparison view
│   ├── trends.py             # Time series analysis view
│   └── about.py              # About page with data sources info
│
├── tests/                     # Unit and integration tests
│   ├── __init__.py
│   ├── test_openaq_client.py
│   ├── test_data_processor.py
│   ├── test_aqi_calculator.py
│   ├── test_database.py
│   └── fixtures/             # Test data fixtures
│       └── sample_responses.json
│
├── docker/                    # Docker deployment
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── assets/                    # Static assets
│   ├── logo.png
│   └── favicon.ico
│
└── data_storage/              # Local data storage (gitignored)
    ├── aeris.db              # SQLite database
    └── cache/                # Cached API responses
```

## 2. MAIN COMPONENTS

### A. Data Collection Layer (`data/`)
**Responsibility:** Fetch air quality data from OpenAQ API

**Components:**
- **OpenAQ Client** (`openaq_client.py`)
  - HTTP requests to OpenAQ API v2
  - Endpoints: `/latest`, `/measurements`, `/locations`
  - Error handling with exponential backoff
  - Response caching (15-30 min TTL)
  - Rate limiting awareness (500 req/hour)

- **Data Processor** (`data_processor.py`)
  - Validate API responses
  - Clean and normalize data
  - Convert units (µg/m³ standardization)
  - Calculate AQI from raw pollutant values
  - Handle missing data and outliers

- **Scheduler** (`scheduler.py`)
  - APScheduler background jobs
  - Collect data every 30 minutes
  - Update locations daily
  - Cleanup old data weekly
  - Job persistence and recovery

### B. Storage Layer (`database/`)
**Responsibility:** Persist and retrieve air quality data

**Components:**
- **Models** (`models.py`)
  - Table definitions (locations, measurements, daily_aggregates, cache)
  - Indexes for optimized queries
  - Data validation constraints

- **Operations** (`operations.py`)
  - CRUD operations
  - Bulk inserts for efficiency
  - Time-range queries with aggregations
  - Connection pooling

- **Migrations** (`migrations.py`)
  - Initial schema creation
  - Version management
  - Data migration scripts

### C. Processing Layer (`utils/`)
**Responsibility:** Business logic and calculations

**Components:**
- **AQI Calculator** (`aqi_calculator.py`)
  - Convert pollutant concentrations to AQI
  - Support PM2.5, PM10, O3, NO2, SO2, CO
  - EPA AQI breakpoints
  - Color and category mapping

- **Constants** (`constants.py`)
  - Brazilian cities with coordinates
  - Pollutant WHO limits
  - AQI thresholds and colors
  - API configuration

- **Logger** (`logger.py`)
  - Structured logging setup
  - File and console handlers
  - Log rotation
  - Different levels per module

- **Cache** (`cache.py`)
  - In-memory caching (TTL)
  - File-based cache for API responses
  - Cache invalidation strategies

### D. Visualization Layer (`views/` + `app.py`)
**Responsibility:** User interface and data presentation

**Components:**
- **Home View** (`views/home.py`)
  - City selector dropdown
  - Current AQI display with color
  - Latest measurements table
  - Quick stats (24h avg, trend)
  - Alert notifications

- **Comparison View** (`views/comparison.py`)
  - Multi-city selector
  - Side-by-side AQI comparison
  - Synchronized time series charts
  - Ranking table

- **Trends View** (`views/trends.py`)
  - Time range selector (24h, 7d, 30d, custom)
  - Interactive Plotly charts
  - Pollutant selector
  - Statistical summaries
  - Download data option

- **About View** (`views/about.py`)
  - Data sources information
  - AQI explanation
  - Health recommendations by level
  - Last update timestamp

## 3. DATA FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                     AERIS DATA FLOW                              │
└─────────────────────────────────────────────────────────────────┘

1. DATA COLLECTION (Every 30 minutes)
   ┌──────────────┐
   │ APScheduler  │ Triggers job
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ OpenAQ Client    │ Fetches from API
   │ - /latest        │ GET https://api.openaq.org/v2/latest
   │ - /measurements  │ ?country=BR&city=São Paulo
   └──────┬───────────┘
          │ Raw JSON
          ▼
   ┌──────────────────┐
   │ Data Processor   │ Validates & transforms
   │ - Clean data     │
   │ - Calculate AQI  │
   │ - Handle outliers│
   └──────┬───────────┘
          │ Processed data
          ▼
   ┌──────────────────┐
   │ SQLite Database  │ Persists to disk
   │ - measurements   │ INSERT INTO measurements
   │ - daily_aggs     │ UPDATE daily_aggregates
   └──────────────────┘

2. USER REQUEST (Streamlit Dashboard)
   ┌──────────────┐
   │ User Browser │ Visits http://localhost:8501
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ Streamlit App    │ Renders UI
   │ app.py           │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ View Layer       │ Selects city, time range
   │ views/home.py    │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ @st.cache_data   │ Checks Streamlit cache
   └──────┬───────────┘
          │ Cache miss
          ▼
   ┌──────────────────┐
   │ Database Ops     │ Queries data
   │ operations.py    │ SELECT * FROM measurements
   └──────┬───────────┘  WHERE city='São Paulo'
          │ Dataframe
          ▼
   ┌──────────────────┐
   │ AQI Calculator   │ Computes AQI if needed
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Plotly Charts    │ Renders visualizations
   │ - Line charts    │
   │ - Bar charts     │
   │ - Maps           │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ User Browser     │ Displays dashboard
   └──────────────────┘

3. ERROR HANDLING FLOW
   ┌──────────────────┐
   │ API Request      │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Error Occurred?  │
   └──────┬───────────┘
          │ Yes
          ▼
   ┌──────────────────┐
   │ Exponential      │ Retry with backoff
   │ Backoff (3x)     │ 1s, 2s, 4s
   └──────┬───────────┘
          │ Still fails
          ▼
   ┌──────────────────┐
   │ Use Cached Data  │ Fallback to last known good
   │ - database cache │
   │ - file cache     │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Log Warning      │ Alert monitoring
   │ Display Notice   │ "Using cached data from..."
   └──────────────────┘
```

## 4. TECHNOLOGY STACK DETAILS

### Frontend - Streamlit
**Why:** Rapid development, built-in caching, reactive updates
```python
# Key features used:
st.cache_data()          # Cache data queries (TTL: 5 min)
st.cache_resource()      # Cache DB connections
st.sidebar               # Navigation
st.columns()             # Responsive layout
st.plotly_chart()        # Interactive visualizations
st.metric()              # KPI display with deltas
st.selectbox()           # City/pollutant selection
st.date_input()          # Time range selection
```

### Visualization - Plotly
**Why:** Interactive, responsive, map support
```python
# Chart types:
plotly.graph_objects.Scatter()    # Time series
plotly.graph_objects.Bar()        # AQI comparison
plotly.express.line()             # Quick plots
plotly.graph_objects.Scattermapbox()  # City locations
```

### Database - SQLite
**Why:** Zero setup, single file, efficient for read-heavy workloads
```sql
-- Optimizations:
- Indexes on (city, timestamp)
- Materialized aggregates (daily_aggregates table)
- WAL mode for concurrent reads
- PRAGMA optimizations
```

### Data Processing - Pandas
**Why:** Time series operations, data cleaning, aggregations
```python
# Key operations:
df.resample('1H').mean()          # Hourly averages
df.fillna(method='ffill')         # Handle missing data
df.rolling(window=24).mean()      # Moving averages
df.groupby('city').agg()          # Multi-city aggregations
```

### Scheduling - APScheduler
**Why:** Lightweight, no external dependencies, persistent jobs
```python
# Job schedule:
IntervalTrigger(minutes=30)       # Data collection
CronTrigger(hour=0)               # Daily cleanup
```

### HTTP Client - Requests
**Why:** Simple, reliable, well-documented
```python
# Features:
requests.get(url, timeout=10)     # Timeout protection
requests.adapters.HTTPAdapter()   # Connection pooling
requests.packages.urllib3.Retry() # Automatic retries
```

## 5. MVP FEATURES

### Phase 1: Core Functionality (Week 1)
- [x] OpenAQ API integration
- [x] SQLite database with schema
- [x] Data collection scheduler (30 min intervals)
- [x] Basic AQI calculation
- [x] Single city view with current AQI
- [x] Simple time series chart (24h)

### Phase 2: Multi-City Support (Week 2)
- [ ] Multiple Brazilian cities selection
  - São Paulo, Rio de Janeiro, Belo Horizonte, Curitiba
  - Brasília, Salvador, Fortaleza, Porto Alegre
- [ ] City comparison view
  - Side-by-side AQI display
  - Synchronized time series
  - Ranking table
- [ ] Enhanced time ranges
  - 24 hours (hourly data)
  - 7 days (6-hour aggregates)
  - 30 days (daily aggregates)
  - Custom date range selector

### Phase 3: Visual Enhancements (Week 3)
- [ ] Visual alerts based on quality levels
  - Color-coded AQI display (Green→Red gradient)
  - Alert banners for unhealthy levels
  - Health recommendations
- [ ] Advanced visualizations
  - Multiple pollutants on one chart
  - Heatmap calendar view
  - Interactive map with city pins
  - Gauge charts for current AQI
- [ ] Responsive design
  - Mobile-friendly layout
  - Collapsible sidebar
  - Adaptive chart sizing

### Phase 4: Performance & Polish (Week 4)
- [ ] Multi-level caching
  - Streamlit @st.cache_data (5 min TTL)
  - Database query cache
  - API response cache (30 min TTL)
- [ ] Data export
  - CSV download
  - JSON export
  - PDF report generation
- [ ] Error handling
  - Graceful API failure handling
  - User-friendly error messages
  - Offline mode with cached data
- [ ] Documentation
  - User guide
  - API documentation
  - Deployment guide

### Feature Details

#### A. Multiple Brazilian Cities Selection
```python
CITIES = {
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333, 'priority': 1},
    'Rio de Janeiro': {'lat': -22.9068, 'lon': -43.1729, 'priority': 2},
    'Belo Horizonte': {'lat': -19.9167, 'lon': -43.9345, 'priority': 3},
    'Curitiba': {'lat': -25.4284, 'lon': -49.2733, 'priority': 4},
    'Brasília': {'lat': -15.8267, 'lon': -47.9218, 'priority': 5},
    'Salvador': {'lat': -12.9714, 'lon': -38.5014, 'priority': 6},
    'Fortaleza': {'lat': -3.7172, 'lon': -38.5433, 'priority': 7},
    'Porto Alegre': {'lat': -30.0346, 'lon': -51.2177, 'priority': 8},
}
```

#### B. Real-time AQI Display
- Large metric card with current AQI value
- Color-coded background (EPA AQI colors)
- Category label (Good, Moderate, Unhealthy, etc.)
- Dominant pollutant indicator
- Last update timestamp
- Trend indicator (↑ ↓ →)

#### C. Time Series Charts
```python
# Chart configurations
TIME_RANGES = {
    '24h': {'hours': 24, 'resolution': '1H', 'points': 24},
    '7d': {'hours': 168, 'resolution': '6H', 'points': 28},
    '30d': {'hours': 720, 'resolution': '1D', 'points': 30},
}
```

#### D. Visual Alerts
```python
AQI_LEVELS = {
    'Good': {'range': (0, 50), 'color': '#00E400', 'icon': '✓'},
    'Moderate': {'range': (51, 100), 'color': '#FFFF00', 'icon': '⚠'},
    'Unhealthy for Sensitive': {'range': (101, 150), 'color': '#FF7E00', 'icon': '⚠⚠'},
    'Unhealthy': {'range': (151, 200), 'color': '#FF0000', 'icon': '⛔'},
    'Very Unhealthy': {'range': (201, 300), 'color': '#8F3F97', 'icon': '⛔⛔'},
    'Hazardous': {'range': (301, 500), 'color': '#7E0023', 'icon': '☠'},
}
```

#### E. City Comparison
- Select 2-4 cities
- Display current AQI for each
- Synchronized time series (same X-axis)
- Statistics table (min, max, avg, std)
- Highlight best/worst performing city

## 6. DATABASE STRUCTURE

### Schema Design

```sql
-- Table 1: Locations (Monitoring Stations)
CREATE TABLE locations (
    location_id TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT DEFAULT 'BR',
    latitude REAL,
    longitude REAL,
    station_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_city ON locations(city);
CREATE INDEX idx_locations_active ON locations(is_active);

-- Table 2: Measurements (Time Series Data)
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    city TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    parameter TEXT NOT NULL,  -- PM2.5, PM10, O3, NO2, SO2, CO
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    aqi INTEGER,
    aqi_category TEXT,
    source TEXT DEFAULT 'OpenAQ',
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- CRITICAL INDEXES for query performance
CREATE INDEX idx_measurements_city_time ON measurements(city, timestamp DESC);
CREATE INDEX idx_measurements_param_time ON measurements(parameter, timestamp DESC);
CREATE INDEX idx_measurements_location_time ON measurements(location_id, timestamp DESC);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp DESC);
CREATE INDEX idx_measurements_aqi ON measurements(aqi);

-- Table 3: Daily Aggregates (Pre-computed for performance)
CREATE TABLE daily_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    date DATE NOT NULL,
    parameter TEXT NOT NULL,
    avg_value REAL,
    min_value REAL,
    max_value REAL,
    avg_aqi INTEGER,
    max_aqi INTEGER,
    data_points INTEGER,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, date, parameter)
);

CREATE INDEX idx_daily_agg_city_date ON daily_aggregates(city, date DESC);

-- Table 4: API Cache (Response caching)
CREATE TABLE api_cache (
    cache_key TEXT PRIMARY KEY,
    response_data TEXT NOT NULL,  -- JSON string
    cached_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_cache_expires ON api_cache(expires_at);
```

### Data Models (Python)

```python
# database/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Location:
    location_id: str
    city: str
    country: str = 'BR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    station_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Measurement:
    location_id: str
    city: str
    timestamp: datetime
    parameter: str  # PM2.5, PM10, O3, NO2, SO2, CO
    value: float
    unit: str
    aqi: Optional[int] = None
    aqi_category: Optional[str] = None
    source: str = 'OpenAQ'
    collected_at: datetime = None

@dataclass
class DailyAggregate:
    city: str
    date: str  # YYYY-MM-DD
    parameter: str
    avg_value: float
    min_value: float
    max_value: float
    avg_aqi: int
    max_aqi: int
    data_points: int
```

### Data Update Strategy

#### 1. Real-time Collection (Every 30 minutes)
```python
# Scheduler job
@scheduler.scheduled_job('interval', minutes=30, id='collect_latest')
def collect_latest_data():
    """Fetch latest measurements for all cities"""
    for city in CITIES:
        try:
            # Fetch from OpenAQ /latest endpoint
            data = openaq_client.get_latest(city=city)

            # Process and validate
            processed = data_processor.process(data)

            # Calculate AQI
            processed['aqi'] = aqi_calculator.calculate(
                parameter=processed['parameter'],
                value=processed['value']
            )

            # Insert to database
            db.insert_measurements(processed)

            logger.info(f"Collected data for {city}: {len(processed)} records")
        except Exception as e:
            logger.error(f"Failed to collect data for {city}: {e}")
```

#### 2. Historical Backfill (On demand)
```python
@scheduler.scheduled_job('cron', hour=1, id='backfill_missing')
def backfill_missing_data():
    """Fill gaps in historical data"""
    # Identify gaps
    gaps = db.find_data_gaps(hours=48)

    for gap in gaps:
        try:
            # Fetch from OpenAQ /measurements endpoint
            data = openaq_client.get_measurements(
                city=gap['city'],
                date_from=gap['start'],
                date_to=gap['end']
            )
            db.insert_measurements(data)
        except Exception as e:
            logger.warning(f"Could not backfill gap: {e}")
```

#### 3. Daily Aggregation (Daily at midnight)
```python
@scheduler.scheduled_job('cron', hour=0, minute=5, id='aggregate_daily')
def compute_daily_aggregates():
    """Pre-compute daily statistics for performance"""
    yesterday = datetime.now() - timedelta(days=1)

    for city in CITIES:
        for parameter in POLLUTANTS:
            stats = db.compute_daily_stats(
                city=city,
                parameter=parameter,
                date=yesterday
            )
            db.upsert_daily_aggregate(stats)
```

#### 4. Data Retention (Weekly cleanup)
```python
@scheduler.scheduled_job('cron', day_of_week='sun', hour=2, id='cleanup_old')
def cleanup_old_data():
    """Remove old data according to retention policy"""
    # Keep raw measurements for 90 days
    db.delete_measurements_older_than(days=90)

    # Keep daily aggregates for 1 year
    db.delete_aggregates_older_than(days=365)

    # Clear expired cache
    db.delete_expired_cache()

    # Vacuum database
    db.vacuum()
```

## 7. ERROR HANDLING STRATEGY

### A. API Error Handling

#### Connection Errors
```python
# data/openaq_client.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OpenAQClient:
    def __init__(self):
        self.base_url = "https://api.openaq.org/v2"
        self.session = self._create_session()

    def _create_session(self):
        """Create session with retry logic"""
        session = requests.Session()

        # Retry strategy
        retry = Retry(
            total=3,
            backoff_factor=1,  # 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get_latest(self, city, timeout=10):
        """Fetch latest measurements with error handling"""
        try:
            # Check cache first
            cached = self._get_from_cache(city)
            if cached and not self._is_cache_expired(cached):
                logger.info(f"Using cached data for {city}")
                return cached['data']

            # Make API request
            response = self.session.get(
                f"{self.base_url}/latest",
                params={'city': city, 'country': 'BR'},
                timeout=timeout
            )
            response.raise_for_status()

            data = response.json()

            # Cache response
            self._save_to_cache(city, data)

            return data

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching data for {city}")
            return self._fallback_to_cache(city)

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {city}")
            return self._fallback_to_cache(city)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded for {city}")
                return self._fallback_to_cache(city)
            elif e.response.status_code >= 500:
                logger.error(f"Server error for {city}: {e}")
                return self._fallback_to_cache(city)
            else:
                logger.error(f"HTTP error for {city}: {e}")
                raise

        except Exception as e:
            logger.exception(f"Unexpected error for {city}: {e}")
            return self._fallback_to_cache(city)
```

#### Rate Limiting
```python
# Track API usage
class RateLimiter:
    def __init__(self, max_requests=500, window_hours=1):
        self.max_requests = max_requests
        self.window_hours = window_hours
        self.requests = []

    def can_make_request(self):
        """Check if under rate limit"""
        now = datetime.now()
        cutoff = now - timedelta(hours=self.window_hours)

        # Remove old requests
        self.requests = [r for r in self.requests if r > cutoff]

        return len(self.requests) < self.max_requests

    def record_request(self):
        """Record a request"""
        self.requests.append(datetime.now())
```

### B. Data Validation

```python
# data/data_processor.py

class DataValidator:
    # WHO air quality limits (µg/m³)
    LIMITS = {
        'PM2.5': {'min': 0, 'max': 500},    # 24h mean: 25 µg/m³
        'PM10': {'min': 0, 'max': 600},     # 24h mean: 50 µg/m³
        'O3': {'min': 0, 'max': 500},       # 8h mean: 100 µg/m³
        'NO2': {'min': 0, 'max': 400},      # 1h mean: 200 µg/m³
        'SO2': {'min': 0, 'max': 500},      # 24h mean: 20 µg/m³
        'CO': {'min': 0, 'max': 50000},     # 8h mean: 10 mg/m³
    }

    def validate(self, measurement):
        """Validate measurement data"""
        errors = []

        # Check required fields
        required = ['parameter', 'value', 'unit', 'timestamp', 'city']
        for field in required:
            if field not in measurement:
                errors.append(f"Missing required field: {field}")

        # Validate parameter
        if measurement['parameter'] not in self.LIMITS:
            errors.append(f"Unknown parameter: {measurement['parameter']}")

        # Validate value range
        limits = self.LIMITS[measurement['parameter']]
        if not (limits['min'] <= measurement['value'] <= limits['max']):
            errors.append(
                f"Value out of range: {measurement['value']} "
                f"(expected {limits['min']}-{limits['max']})"
            )

        # Validate timestamp
        try:
            ts = datetime.fromisoformat(measurement['timestamp'])
            if ts > datetime.now() + timedelta(hours=1):
                errors.append("Timestamp is in the future")
        except ValueError:
            errors.append("Invalid timestamp format")

        if errors:
            logger.warning(f"Validation errors: {errors}")
            return False, errors

        return True, []
```

### C. Database Error Handling

```python
# database/operations.py

class DatabaseOperations:
    def insert_measurement(self, measurement):
        """Insert with conflict handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO measurements
                    (location_id, city, timestamp, parameter, value, unit, aqi)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    measurement['location_id'],
                    measurement['city'],
                    measurement['timestamp'],
                    measurement['parameter'],
                    measurement['value'],
                    measurement['unit'],
                    measurement['aqi']
                ))
                conn.commit()
                return True

        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate measurement, skipping: {e}")
            return False

        except sqlite3.OperationalError as e:
            logger.error(f"Database locked: {e}")
            # Retry after delay
            time.sleep(0.1)
            return self.insert_measurement(measurement)

        except Exception as e:
            logger.exception(f"Database error: {e}")
            raise
```

### D. Fallback Mechanisms

```python
# Hierarchical fallback strategy

def get_air_quality_data(city, hours=24):
    """Get data with multiple fallback levels"""

    # Level 1: Try database (fastest)
    try:
        data = db.get_recent_measurements(city, hours)
        if data and len(data) > 0:
            logger.info(f"Retrieved {len(data)} records from database")
            return data
    except Exception as e:
        logger.error(f"Database error: {e}")

    # Level 2: Try API with cache
    try:
        data = openaq_client.get_latest(city)
        if data:
            logger.info(f"Retrieved data from API")
            # Save to database
            db.insert_measurements(data)
            return data
    except Exception as e:
        logger.error(f"API error: {e}")

    # Level 3: Use file cache (if database is down)
    try:
        data = file_cache.load(f"backup_{city}.json")
        if data:
            logger.warning(f"Using file cache for {city}")
            return data
    except Exception as e:
        logger.error(f"Cache error: {e}")

    # Level 4: Return empty with notification
    logger.critical(f"All data sources failed for {city}")
    return {
        'error': True,
        'message': f'Unable to retrieve data for {city}. Please try again later.',
        'last_attempt': datetime.now().isoformat()
    }
```

### E. User-Facing Error Messages

```python
# Streamlit error handling

def display_with_error_handling(city):
    """Display data with graceful error handling"""

    try:
        data = get_air_quality_data(city)

        if 'error' in data:
            st.warning(f"⚠️ {data['message']}")
            st.info("💾 Attempting to load cached data...")

            # Try to show last known good data
            cached_data = get_cached_data(city)
            if cached_data:
                st.success(f"Showing data from {cached_data['timestamp']}")
                display_dashboard(cached_data)
            else:
                st.error("No cached data available.")
                st.button("🔄 Retry", on_click=lambda: display_with_error_handling(city))
        else:
            display_dashboard(data)

    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)

        if st.button("📧 Report Issue"):
            send_error_report(e)
```

### F. Monitoring and Alerts

```python
# utils/monitoring.py

class HealthCheck:
    def check_system_health(self):
        """Monitor system health"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }

        # Check database
        try:
            db.execute("SELECT 1")
            health['checks']['database'] = 'ok'
        except Exception as e:
            health['checks']['database'] = f'error: {e}'
            health['status'] = 'degraded'

        # Check API
        try:
            response = requests.get(
                "https://api.openaq.org/v2/latest",
                params={'limit': 1},
                timeout=5
            )
            health['checks']['api'] = 'ok'
        except Exception as e:
            health['checks']['api'] = f'error: {e}'
            health['status'] = 'degraded'

        # Check data freshness
        try:
            last_update = db.get_last_update_time()
            age_minutes = (datetime.now() - last_update).total_seconds() / 60

            if age_minutes > 60:
                health['checks']['data_freshness'] = f'stale: {age_minutes:.0f}m'
                health['status'] = 'degraded'
            else:
                health['checks']['data_freshness'] = 'ok'
        except Exception as e:
            health['checks']['data_freshness'] = f'error: {e}'

        return health
```

## 8. CACHING STRATEGY

### Multi-Level Caching

```python
# Level 1: Streamlit Cache (In-memory, per session)
@st.cache_data(ttl=300)  # 5 minutes
def load_city_data(city, hours=24):
    """Cache city data in Streamlit"""
    return db.get_measurements(city, hours)

# Level 2: Database Cache (Persistent)
# Pre-computed daily_aggregates table

# Level 3: API Response Cache (File-based)
class APICache:
    def __init__(self, cache_dir='data_storage/cache', ttl_minutes=30):
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, key):
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < self.ttl:
                with open(cache_file) as f:
                    return json.load(f)
        return None

    def set(self, key, data):
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump(data, f)
```

## 9. PERFORMANCE TARGETS

- **Page Load Time:** < 2 seconds
- **Chart Rendering:** < 500ms
- **API Response:** < 1 second (with cache)
- **Database Query:** < 100ms (with indexes)
- **Data Collection:** < 30 seconds per city
- **Dashboard Refresh:** < 5 seconds

## 10. DEPLOYMENT CONSIDERATIONS

### Docker Deployment
```dockerfile
# Lightweight Python image
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Create data directory
RUN mkdir -p data_storage/cache

# Expose Streamlit port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables
```bash
# .env.example
OPENAQ_API_BASE_URL=https://api.openaq.org/v2
DATABASE_PATH=data_storage/aeris.db
COLLECTION_INTERVAL_MINUTES=30
CACHE_TTL_MINUTES=30
LOG_LEVEL=INFO
STREAMLIT_SERVER_PORT=8501
```

---

**Last Updated:** 2025-11-01
**Version:** 1.0.0
**Status:** Architecture Design Complete - Ready for Implementation
