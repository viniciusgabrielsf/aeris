# Comprehensive Air Quality APIs and Technologies Research
# Aeris Air Quality Dashboard Project

## PART 1: AIR QUALITY APIs ANALYSIS

### 1. OpenAQ API v2
**Website:** https://docs.openaq.org/

#### Authentication & Pricing
- **Free:** YES - Completely free, no API key required
- **Authentication:** NO - Public API, open access
- **Rate Limiting:** ~500 requests per hour (estimated), no hard limits enforced
- **Terms:** Open Data Commons Attribution License (ODC-By)

#### API Endpoints & Structure
**Base URL:** `https://api.openaq.org/v2/`

**Key Endpoints:**
1. `/latest` - Get latest measurements
   - Request: `GET /latest?city=São Paulo&parameter=pm25`
   - Response: JSON with latest values from all monitoring stations

2. `/measurements` - Get historical time series
   - Request: `GET /measurements?city=São Paulo&parameter=pm25&limit=1000&date_from=2024-01-01T00:00:00Z`
   - Response: JSON array with timestamped measurements

3. `/locations` - Get available monitoring stations
   - Request: `GET /locations?city=São Paulo`
   - Response: Station metadata with coordinates

4. `/countries` - Get supported countries
5. `/cities` - Get cities by country

#### Example API Response Structure

```json
{
  "results": [
    {
      "location": "Imigrantes",
      "city": "São Paulo",
      "country": "BR",
      "coordinates": {
        "latitude": -23.6529,
        "longitude": -46.4735
      },
      "measurements": [
        {
          "parameter": "pm25",
          "value": 28,
          "unit": "µg/m³",
          "lastUpdated": "2024-11-01T10:00:00Z"
        },
        {
          "parameter": "pm10",
          "value": 42,
          "unit": "µg/m³",
          "lastUpdated": "2024-11-01T10:00:00Z"
        }
      ]
    }
  ],
  "meta": {
    "name": "openaq-api",
    "license": "CC BY 4.0",
    "website": "https://openaq.org"
  }
}
```

#### Data Coverage - Brazilian Cities
- **São Paulo:** EXCELLENT - Multiple stations (Imigrantes, Congonhas, Pinheiros)
- **Rio de Janeiro:** GOOD - Several stations
- **Belo Horizonte:** GOOD - Available data
- **Brasília:** LIMITED - Few stations
- **Salvador:** LIMITED - Minimal coverage
- **Fortaleza:** MINIMAL - Very limited
- **Curitiba:** GOOD - Available
- **Porto Alegre:** LIMITED - Few stations

#### Available Parameters
- PM2.5 (Fine particulate matter)
- PM10 (Coarse particulate matter)
- O3 (Ozone)
- NO2 (Nitrogen dioxide)
- SO2 (Sulfur dioxide)
- CO (Carbon monoxide)
- BC (Black carbon)
- NO (Nitric oxide)
- NOx (Nitrogen oxides)

#### Data Characteristics
- **Real-time:** Updated frequently (typically every 1-3 hours)
- **Historical:** Available for recent data (typically 90 days to 1 year)
- **Granularity:** Hourly measurements
- **Accuracy:** Varies by station and parameter

#### Pros
- Completely free
- No authentication overhead
- Large global dataset
- Multiple parameters
- Good Brazilian coverage for major cities
- Well-documented
- Stable, maintained project

#### Cons
- Limited historical data depth
- Coverage gaps for smaller cities
- Rate limiting for heavy usage
- Data quality varies by location
- Dependent on local monitoring networks

---

### 2. IQAir API
**Website:** https://www.iqair.com/air-pollution-data-api

#### Authentication & Pricing
- **Free:** PARTIAL - Free tier available with limitations
- **Authentication:** YES - Requires API key
- **Free Tier Limits:** 10,000 requests/month (~330/day)
- **Paid Plans:** Start at $99/month for extended access
- **Rate Limiting:** 100 requests/minute on free tier

#### API Endpoints & Structure
**Base URL:** `https://api.waqi.info/` (for free WAQI data) or IQAir proprietary endpoints

**Key Endpoints:**
1. `/feed/{city_name}/?token=API_KEY` - Current city air quality
2. `/feed/geo:{lat};{lng}/?token=API_KEY` - Air quality by coordinates
3. `/search/?keyword={query}&token=API_KEY` - Search cities

#### Example API Response

```json
{
  "status": "ok",
  "data": {
    "aqi": 72,
    "idx": 12345,
    "attribution": [
      {
        "url": "https://www.iqair.com",
        "name": "IQAir"
      }
    ],
    "city": "São Paulo",
    "dominentpol": "pm25",
    "iaqi": {
      "h": {"v": 65},
      "p": {"v": 1020},
      "pm10": {"v": 45},
      "pm25": {"v": 32},
      "o3": {"v": 28},
      "no2": {"v": 35},
      "so2": {"v": 12},
      "co": {"v": 285}
    },
    "time": {
      "s": "2024-11-01 10:00:00",
      "tz": "-03:00",
      "v": 1730445600
    },
    "forecast": {
      "daily": {
        "pm10": [{"avg": 45, "day": "2024-11-02", "max": 50, "min": 40}]
      }
    }
  ]
}
```

#### Brazilian Cities Coverage
- **São Paulo:** EXCELLENT - Multiple sources
- **Rio de Janeiro:** EXCELLENT
- **Belo Horizonte:** GOOD
- **Brasília:** GOOD
- **Other cities:** GOOD coverage overall

#### Pros
- Excellent Brazilian coverage
- Includes forecasts
- Fast, reliable service
- Good documentation
- Combines multiple data sources
- Includes health recommendations

#### Cons
- Not completely free
- API key required (registration overhead)
- Free tier limited to 10k requests/month
- Monthly quota instead of rate limiting flexibility
- More expensive than alternatives for high-volume usage

---

### 3. CETESB-SP (Companhia Ambiental do Estado de São Paulo)
**Website:** https://www.cetesb.sp.gov.br/

#### Status
- **Free:** YES - Free access to SP data
- **API:** NO FORMAL REST API - Data available through:
  - Web portal scraping (https://cetesb.sp.gov.br/ar/qualidade-do-ar/publicacoes-e-relatorios/)
  - Bulk data downloads
  - Station data can be accessed via web requests

#### Data Available
- Real-time AQI for São Paulo state
- Multiple air quality parameters
- Detailed station information
- Hourly updated

#### Access Method
```
# Direct web access (requires parsing HTML)
https://cetesb.sp.gov.br/ar/qualidade-do-ar/publicacoes-e-relatorios/

# Station-specific data may be available through:
GET https://cetesb.sp.gov.br/api/estacoes/[station_id]/dados
(Not officially documented)
```

#### Challenges
- No official REST API
- Requires web scraping (fragile, maintenance-heavy)
- Limited to São Paulo state only
- HTML parsing complexity
- Terms of service may not permit automated access

#### Recommendation
- Use as secondary data source with web scraping (use BeautifulSoup)
- Monitor for API availability changes
- Implement robust error handling for parsing

---

### 4. INMET (Instituto Nacional de Meteorologia) - Brazil
**Website:** https://www.inmet.gov.br/

#### Status
- **Free:** YES
- **API:** YES - Open data available
- **Authentication:** NO

#### Data Available
- Meteorological data (temperature, humidity, pressure)
- Limited direct air quality data
- Good coverage across Brazil

#### Limitation
- Primarily meteorological, not air quality focused
- Better as supplementary data source

---

### 5. WAQI (World Air Quality Index) via AirVisual
**Website:** https://waqi.info/

#### Authentication & Pricing
- **Free:** YES - Free tier available
- **API Key:** Required (free registration)
- **Rate Limiting:** Generous for free tier
- **Endpoints:** Access via https://api.waqi.info/

#### Coverage
- Excellent global coverage
- Good Brazilian data
- Real-time and some historical data

#### Pros
- Good Brazilian coverage
- Free tier is generous
- Simple API
- Easy registration

#### Cons
- Still requires API key
- Not as "free" as OpenAQ
- Same data as IQAir in many cases

---

## PART 2: API COMPARISON TABLE

| Feature | OpenAQ v2 | IQAir | CETESB | WAQI |
|---------|-----------|-------|--------|------|
| **Free Access** | YES | PARTIAL (10k/mo) | YES | YES |
| **API Key Required** | NO | YES | NO | YES |
| **Rate Limit** | ~500/hr | 100/min (free) | N/A | Generous |
| **SP Coverage** | Excellent | Excellent | Excellent | Excellent |
| **Other BR Cities** | Good | Good | Limited to SP | Good |
| **Historical Data** | Limited (90d) | Limited (30d) | Good | Good |
| **Parameters** | 9+ | 8 | 8+ | 8 |
| **Documentation** | Excellent | Good | Limited | Good |
| **Setup Complexity** | Low | Medium | High | Medium |
| **Reliability** | High | High | Medium | High |

---

## PART 3: PYTHON LIBRARIES RESEARCH

### A. REST API Integration

#### 1. requests
```python
import requests

response = requests.get('https://api.openaq.org/v2/latest', 
                        params={'city': 'São Paulo', 'parameter': 'pm25'})
data = response.json()
```
- **Pros:** Simple, widely used, excellent documentation, synchronous
- **Cons:** Blocking I/O, not ideal for high concurrency
- **Use Case:** Simple dashboard with low-frequency API calls
- **Recommendation:** YES for this project (sufficient for Streamlit dashboard)

#### 2. httpx
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('https://api.openaq.org/v2/latest')
    data = response.json()
```
- **Pros:** Async support, HTTP/2, modern library
- **Cons:** Steeper learning curve, overkill for simple use
- **Use Case:** High-concurrency API clients
- **Recommendation:** NO for this project (adds complexity without benefit)

#### 3. aiohttp
```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get('https://api.openaq.org/v2/latest') as resp:
        data = await resp.json()
```
- **Pros:** Async first, efficient for concurrent requests
- **Cons:** Complex error handling, harder to debug
- **Use Case:** Services handling hundreds of concurrent requests
- **Recommendation:** NO for this project

**RECOMMENDATION FOR THIS PROJECT:** Use **requests** library
- Simple, sufficient for dashboard refresh cycles
- Easy to understand and maintain
- Built-in retry mechanisms available
- Excellent error handling

---

### B. Data Processing Libraries

#### 1. Pandas
```python
import pandas as pd

df = pd.read_csv('measurements.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_hourly = df.groupby(pd.Grouper(key='timestamp', freq='1H'))['value'].mean()
```
- **Pros:** Time series handling, excellent for AQI calculations, widely known
- **Cons:** Higher memory usage for large datasets
- **Use Case:** Dashboard data processing, aggregations
- **Recommendation:** YES - Primary choice

#### 2. NumPy
- Used implicitly by Pandas
- Lower-level numerical operations
- Not directly used for this project

#### 3. Polars
```python
import polars as pl

df = pl.read_csv('measurements.csv')
df_filtered = df.filter(pl.col('timestamp') > '2024-01-01')
```
- **Pros:** Faster than Pandas for large datasets, lazy evaluation
- **Cons:** Newer, smaller community, less mature
- **Use Case:** High-volume time series processing
- **Recommendation:** NO - Pandas sufficient, ecosystem better

**RECOMMENDATION FOR THIS PROJECT:** Use **Pandas**
- Standard for data science community
- Excellent time series support
- Easy grouping and aggregations for hourly/daily summaries
- Good integration with Plotly

---

### C. Dashboard Frameworks

#### 1. Streamlit
```python
import streamlit as st
import plotly.graph_objects as go

st.title('Air Quality Dashboard')
fig = go.Figure()
st.plotly_chart(fig)
```
- **Pros:** Fast development, Python-native, excellent caching, Plotly integration
- **Cons:** Limited customization, state management complexity for complex apps
- **Learning Curve:** VERY LOW
- **Performance:** Good for medium-traffic dashboards
- **Recommendation:** YES - Already selected in project

#### 2. Dash (Plotly Dash)
```python
from dash import Dash, dcc, html
import plotly.graph_objects as go

app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='air-quality-graph')
])
```
- **Pros:** More customizable than Streamlit, better for complex layouts
- **Cons:** Steeper learning curve, more boilerplate code
- **Learning Curve:** MEDIUM
- **Recommendation:** NO - Streamlit more suitable for this use case

#### 3. Gradio
```python
import gradio as gr

def predict_aqi(city):
    return f"AQI for {city}: 72"

gr.Interface(fn=predict_aqi, inputs="text", outputs="text").launch()
```
- **Pros:** Extremely simple for quick prototypes, ML-focused
- **Cons:** Limited for complex dashboards
- **Learning Curve:** VERY LOW
- **Recommendation:** NO - Too simple for full dashboard needs

**RECOMMENDATION FOR THIS PROJECT:** Use **Streamlit**
- Already specified in project
- Perfect for multi-page air quality dashboard
- Native caching mechanisms for performance
- Easy integration with Plotly

---

### D. Visualization Libraries

#### 1. Plotly
```python
import plotly.graph_objects as go
import plotly.express as px

# Time series plot
fig = px.line(df, x='timestamp', y='pm25', color='city',
              title='PM2.5 Over Time')

# Map visualization
fig = px.scatter_mapbox(df, lat='latitude', lon='longitude',
                        hover_name='station', color='aqi')
fig.update_layout(mapbox_style="open-street-map")
```
- **Pros:** Interactive, responsive, excellent for time series, built-in Streamlit support
- **Cons:** Larger bundle size, can be slow with very large datasets
- **Recommendation:** YES - Primary choice

#### 2. Altair
```python
import altair as alt

chart = alt.Chart(df).mark_line().encode(
    x='timestamp:T',
    y='pm25:Q',
    color='city:N'
)
```
- **Pros:** Declarative, elegant syntax, fast
- **Cons:** Less interactive than Plotly, smaller feature set
- **Recommendation:** NO - Plotly superior for this use case

#### 3. Bokeh
```python
from bokeh.plotting import figure, show
from bokeh.models import HoverTool

p = figure(x_axis_type='datetime', title='Air Quality')
p.line(df['timestamp'], df['pm25'], line_width=2)
```
- **Pros:** Server-based interactivity, good performance
- **Cons:** Steeper learning curve, not as intuitive as Plotly
- **Recommendation:** NO - Plotly simpler

**RECOMMENDATION FOR THIS PROJECT:** Use **Plotly**
- Perfect for air quality time series and maps
- Excellent Streamlit integration
- Interactive elements for exploration
- Built-in geographic visualizations

---

### E. Database Libraries

#### 1. SQLite + sqlite3
```python
import sqlite3

conn = sqlite3.connect('aeris.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE measurements
                  (timestamp TEXT, city TEXT, pm25 REAL)''')
```
- **Pros:** No setup, single file, zero maintenance, sufficient for dashboard
- **Cons:** Limited concurrency, not ideal for very high volume
- **Use Case:** Small to medium dashboards, local data storage
- **Recommendation:** YES - Already in project

#### 2. PostgreSQL + psycopg2
```python
import psycopg2

conn = psycopg2.connect("dbname=aeris user=postgres")
cursor = conn.cursor()
cursor.execute('SELECT * FROM measurements WHERE timestamp > NOW() - INTERVAL 24h')
```
- **Pros:** Excellent concurrency, time series extensions (TimescaleDB)
- **Cons:** Setup/maintenance overhead, overkill for this project
- **Recommendation:** NO - SQLite sufficient

#### 3. DuckDB
```python
import duckdb

conn = duckdb.connect('aeris.duckdb')
result = conn.execute('SELECT * FROM measurements WHERE pm25 > 50').fetchall()
```
- **Pros:** Fast analytics, perfect for time series, SQL directly on files
- **Cons:** Newer, smaller ecosystem
- **Recommendation:** MAYBE - As secondary option for analytical queries

**RECOMMENDATION FOR THIS PROJECT:** Use **SQLite**
- Simple setup
- No external dependencies
- Sufficient for dashboard-scale data
- Built-in time series support

#### Schema Design

```sql
-- Main measurements table (with proper indexing for time series)
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    location_id INTEGER NOT NULL,
    parameter TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

-- Index strategy for time series queries
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp DESC);
CREATE INDEX idx_measurements_location_parameter ON measurements(location_id, parameter, timestamp DESC);
CREATE INDEX idx_measurements_city ON measurements(timestamp DESC, location_id);

-- Locations table
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    city TEXT NOT NULL,
    station_name TEXT,
    latitude REAL,
    longitude REAL,
    country TEXT DEFAULT 'BR',
    openaq_id TEXT,
    last_updated DATETIME,
    UNIQUE(city, station_name)
);

-- Cache table for aggregated data
CREATE TABLE cache (
    id INTEGER PRIMARY KEY,
    cache_key TEXT UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_expires ON cache(expires_at);
```

---

### F. Scheduling Libraries

#### 1. APScheduler
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(collect_air_quality_data, 'interval', minutes=30)
scheduler.start()
```
- **Pros:** Simple, no external dependencies, good for single-process apps
- **Cons:** Not suitable for distributed systems, limited persistence
- **Use Case:** Streamlit dashboard with background collection
- **Recommendation:** YES - Already in project

#### 2. Celery
```python
from celery import Celery

app = Celery('aeris')

@app.task
def collect_air_quality_data():
    # Long-running task
    pass

app.conf.beat_schedule = {
    'collect-every-30-minutes': {
        'task': 'tasks.collect_air_quality_data',
        'schedule': 30.0 * 60.0,
    },
}
```
- **Pros:** Distributed, persistent, production-grade
- **Cons:** Requires Redis/RabbitMQ, complex setup
- **Recommendation:** NO - Overkill for this project

#### 3. Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG('air_quality_collection', schedule_interval='@hourly')
task = PythonOperator(task_id='collect_data', python_callable=collect_data)
```
- **Pros:** Powerful, scheduling, monitoring, retries
- **Cons:** Very heavy, steep learning curve, infrastructure overhead
- **Recommendation:** NO - Too complex

**RECOMMENDATION FOR THIS PROJECT:** Use **APScheduler**
- Simple and sufficient
- Integrates well with Streamlit
- No external services required
- Easy to implement retry logic

---

## PART 4: BEST PRACTICES FOR TIME SERIES AIR QUALITY DATA

### 1. Data Storage Efficiency

#### Time-based Partitioning
```python
# Monthly partitioned tables
CREATE TABLE measurements_2024_11 (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    location_id INTEGER NOT NULL,
    parameter TEXT NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE INDEX idx_measurements_2024_11_timestamp ON measurements_2024_11(timestamp DESC);
```

#### Column Compression
- Store parameter/unit as references (foreign keys) to reduce storage
- Use TEXT for city names only in cache, use IDs in main tables
- Store timestamps as Unix timestamps (8 bytes vs 19+ bytes for ISO)

```python
# Efficient storage
timestamp_unix = int(datetime.now().timestamp())
# Instead of ISO: '2024-11-01T10:30:45Z'

# Decompose parameter/unit to separate table
CREATE TABLE parameters (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE (PM2.5, PM10, O3, NO2, SO2, CO),
    unit TEXT
);
```

---

### 2. Indexing Strategy for Time Series

#### Query Patterns for Air Quality Dashboard
```python
# Query Pattern 1: Latest values for a city
SELECT * FROM measurements 
WHERE location_id IN (SELECT id FROM locations WHERE city = 'São Paulo')
AND timestamp > datetime('now', '-24 hours')
ORDER BY timestamp DESC
LIMIT 1;

# Query Pattern 2: Historical trend
SELECT timestamp, parameter, value FROM measurements
WHERE location_id = ?
AND parameter = 'pm25'
AND timestamp BETWEEN ? AND ?
ORDER BY timestamp;

# Query Pattern 3: Multi-city comparison
SELECT city, AVG(value) as avg_pm25 FROM measurements
JOIN locations ON measurements.location_id = locations.id
WHERE parameter = 'pm25'
AND timestamp > datetime('now', '-7 days')
GROUP BY city
ORDER BY avg_pm25 DESC;
```

#### Optimal Index Design
```sql
-- Primary index: Most common query (latest data)
CREATE INDEX idx_measurements_location_timestamp 
ON measurements(location_id, timestamp DESC);

-- Secondary index: Parameter + time filtering
CREATE INDEX idx_measurements_parameter_time 
ON measurements(parameter, timestamp DESC);

-- Composite index: Location + Parameter + Time
CREATE INDEX idx_measurements_lpt 
ON measurements(location_id, parameter, timestamp DESC);
```

---

### 3. Data Retention Policy

```python
# Retention Strategy for Air Quality Data
RETENTION_POLICIES = {
    'raw_measurements': 90,      # Keep raw data for 90 days
    'hourly_aggregates': 365,    # 1 year of hourly summaries
    'daily_aggregates': 2555,    # ~7 years of daily summaries
    'monthly_averages': None,    # Keep forever
}

# Cleanup job
def cleanup_old_measurements():
    """Remove measurements older than retention period"""
    cutoff_date = datetime.now() - timedelta(days=90)
    cursor.execute(
        "DELETE FROM measurements WHERE timestamp < ?",
        (cutoff_date.isoformat(),)
    )
    cursor.execute("VACUUM")  # Reclaim space
```

#### Archive Strategy
```python
def archive_measurements(year, month):
    """Archive old measurements to separate file"""
    archive_db = f'archive_{year}_{month:02d}.db'
    
    # Copy old data
    cursor.execute(f"""
        INSERT INTO {archive_db}.measurements
        SELECT * FROM measurements
        WHERE timestamp LIKE '{year}-{month:02d}-%'
    """)
    
    # Delete from main
    cursor.execute(f"""
        DELETE FROM measurements
        WHERE timestamp LIKE '{year}-{month:02d}-%'
    """)
```

---

### 4. Caching Strategy

#### Multi-Level Caching

```python
# Level 1: Application-level cache (Streamlit)
@st.cache_data(ttl=3600)  # 1 hour
def load_latest_measurements(city):
    """Load latest measurements from database"""
    return query_database(f"""
        SELECT * FROM measurements 
        WHERE location_id IN (SELECT id FROM locations WHERE city = ?)
        ORDER BY timestamp DESC LIMIT 1
    """, (city,))

# Level 2: Database cache table
CREATE TABLE cache (
    cache_key TEXT PRIMARY KEY,
    cache_value TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_expires ON cache(expires_at);

# Level 3: Precomputed aggregates
CREATE TABLE daily_aggregates (
    date DATE NOT NULL,
    location_id INTEGER NOT NULL,
    parameter TEXT NOT NULL,
    avg_value REAL,
    min_value REAL,
    max_value REAL,
    measurements_count INTEGER,
    PRIMARY KEY(date, location_id, parameter)
);

# Populate aggregates
def compute_daily_aggregates():
    """Compute daily summaries for faster dashboard queries"""
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    cursor.execute(f"""
        INSERT OR REPLACE INTO daily_aggregates
        SELECT 
            DATE(timestamp) as date,
            location_id,
            parameter,
            AVG(value),
            MIN(value),
            MAX(value),
            COUNT(*)
        FROM measurements
        WHERE DATE(timestamp) = ?
        GROUP BY location_id, parameter
    """, (yesterday,))
```

---

### 5. Handling Missing Data and Outliers

```python
import pandas as pd
import numpy as np

def clean_air_quality_data(df):
    """
    Clean air quality data by handling missing values and outliers
    
    Args:
        df: DataFrame with columns [timestamp, city, parameter, value]
    
    Returns:
        Cleaned DataFrame
    """
    
    # 1. Handle Missing Values
    # Forward fill for up to 3 hours (air quality doesn't change rapidly)
    df['value'] = df.groupby(['city', 'parameter'])['value'].fillna(method='ffill', limit=3)
    
    # For longer gaps, use interpolation
    df['value'] = df.groupby(['city', 'parameter'])['value'].interpolate(
        method='linear', limit_direction='both', limit=24
    )
    
    # 2. Detect and Handle Outliers using IQR method
    for city in df['city'].unique():
        for param in df['parameter'].unique():
            mask = (df['city'] == city) & (df['parameter'] == param)
            
            subset = df.loc[mask, 'value']
            Q1 = subset.quantile(0.25)
            Q3 = subset.quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outlier bounds (1.5 * IQR is standard)
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Mark outliers
            outliers = (df.loc[mask, 'value'] < lower_bound) | (df.loc[mask, 'value'] > upper_bound)
            
            # Replace outliers with median
            median_value = subset.median()
            df.loc[mask & outliers, 'value'] = median_value
    
    # 3. Validate against known ranges
    # WHO air quality guideline values (µg/m³)
    parameter_limits = {
        'pm25': (0, 500),      # Max reasonable value
        'pm10': (0, 500),
        'o3': (0, 200),
        'no2': (0, 500),
        'so2': (0, 500),
        'co': (0, 50000)       # CO in ppb, so higher range
    }
    
    for param, (min_val, max_val) in parameter_limits.items():
        param_mask = df['parameter'] == param
        df.loc[param_mask & (df['value'] < min_val), 'value'] = np.nan
        df.loc[param_mask & (df['value'] > max_val), 'value'] = np.nan
    
    # 4. Remove completely invalid rows
    df = df.dropna(subset=['value'])
    
    return df

# Example usage
df = pd.read_sql_query("SELECT * FROM measurements", conn)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_clean = clean_air_quality_data(df)
```

---

### 6. API Response Caching

```python
import requests
from datetime import datetime, timedelta

class CachedOpenAQClient:
    def __init__(self, cache_db_path='cache.db'):
        self.cache_db = cache_db_path
        self.base_url = 'https://api.openaq.org/v2'
        self._init_cache()
    
    def _init_cache(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.cache_db)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS api_cache (
                url TEXT PRIMARY KEY,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_latest(self, city, parameter, cache_ttl_minutes=30):
        """Get latest measurements with caching"""
        
        # Build cache key
        cache_key = f"{self.base_url}/latest?city={city}&parameter={parameter}"
        
        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Fetch from API
        try:
            response = requests.get(
                f"{self.base_url}/latest",
                params={'city': city, 'parameter': parameter},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self._store_in_cache(cache_key, data, cache_ttl_minutes)
            
            return data
        
        except requests.RequestException as e:
            print(f"API Error: {e}")
            # Fallback to stale cache
            return self._get_from_cache(cache_key, ignore_expiry=True)
    
    def _get_from_cache(self, cache_key, ignore_expiry=False):
        """Retrieve from cache if valid"""
        conn = sqlite3.connect(self.cache_db)
        
        if ignore_expiry:
            query = "SELECT response FROM api_cache WHERE url = ? ORDER BY timestamp DESC LIMIT 1"
            params = (cache_key,)
        else:
            query = """
                SELECT response FROM api_cache 
                WHERE url = ? AND expires_at > CURRENT_TIMESTAMP
                ORDER BY timestamp DESC LIMIT 1
            """
            params = (cache_key,)
        
        cursor = conn.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def _store_in_cache(self, cache_key, data, ttl_minutes):
        """Store response in cache"""
        conn = sqlite3.connect(self.cache_db)
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        
        conn.execute('''
            INSERT OR REPLACE INTO api_cache (url, response, expires_at)
            VALUES (?, ?, ?)
        ''', (cache_key, json.dumps(data), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
```

---

### 7. Error Handling and Retry Logic

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """Decorator for API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    
                    wait_time = backoff_factor ** retries
                    print(f"Retry {retries}/{max_retries} after {wait_time}s. Error: {e}")
                    time.sleep(wait_time)
        
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, backoff_factor=2)
def fetch_openaq_latest(city, parameter):
    """Fetch latest measurements with automatic retries"""
    response = requests.get(
        'https://api.openaq.org/v2/latest',
        params={'city': city, 'parameter': parameter},
        timeout=10
    )
    response.raise_for_status()
    return response.json()
```

---

## PART 5: RECOMMENDED PYTHON STACK

### Final Recommendations

#### Primary Stack (RECOMMENDED)
```python
# requirements.txt

# API Client
requests==2.31.0          # REST API calls

# Data Processing
pandas==2.1.1             # Time series handling, aggregations
numpy==1.24.3             # Numerical operations

# Database
# SQLite built-in, only need:
pandas-sqlite==0.2.0      # If using direct pandas-to-sqlite

# Dashboard
streamlit==1.28.0         # Multi-page dashboard
streamlit-folium==0.17.0  # Map visualization

# Visualization
plotly==5.17.0            # Interactive charts

# Scheduling
apscheduler==3.10.4       # Background data collection

# Utilities
python-dotenv==1.0.0      # Environment variables
pytz==2023.3              # Timezone handling
Pillow==10.0.0            # Image handling

# Development
pytest==7.4.2             # Testing
pytest-cov==4.1.0         # Coverage
ruff==0.0.292             # Linting
mypy==1.5.1               # Type checking
```

#### Optional Enhanced Stack
```python
# For advanced features (not required initially)
# APScheduler advanced: 
apscheduler[gevent]==3.10.4  # For async scheduler

# Database options:
duckdb==0.8.1             # Analytical queries (optional)
sqlalchemy==2.0.21        # ORM (if needed for complex queries)

# Monitoring:
prometheus-client==0.17.1 # Dashboard metrics
```

---

## PART 6: ARCHITECTURE RECOMMENDATION

### Data Flow Architecture

```
OpenAQ API
    |
    v
[Scheduled Collector] (APScheduler)
    |
    v
[Data Processor] (Pandas)
    - Validation
    - Cleaning
    - Aggregation
    |
    v
[SQLite Database]
    |
    +---> [Cache Layer]
    |
    +---> [Raw Measurements]
    |
    +---> [Aggregated Data]
    |
    v
[Streamlit Dashboard]
    |
    +---> Main Page (Latest AQI)
    |
    +---> Time Series View (Plotly)
    |
    +---> Multi-city Comparison
    |
    +---> Health Alerts
    |
    +---> Reports
```

---

## PART 7: CODE EXAMPLES

### Example 1: OpenAQ Client Implementation

```python
# data/openaq_client.py
import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OpenAQClient:
    """Client for OpenAQ API v2"""
    
    BASE_URL = 'https://api.openaq.org/v2'
    RATE_LIMIT = 500  # requests per hour
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Aeris Dashboard'})
    
    def get_latest_measurements(self, city: str, parameter: str = 'pm25') -> Dict:
        """
        Get latest measurements for a city
        
        Args:
            city: City name (e.g., 'São Paulo')
            parameter: Air quality parameter (pm25, pm10, o3, no2, so2, co)
        
        Returns:
            Dictionary with latest measurements
        
        Example:
            >>> client = OpenAQClient()
            >>> data = client.get_latest_measurements('São Paulo', 'pm25')
            >>> print(data['results'][0]['measurements'][0]['value'])
            28
        """
        try:
            response = self.session.get(
                f'{self.BASE_URL}/latest',
                params={
                    'city': city,
                    'parameter': parameter
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch latest measurements: {e}")
            raise
    
    def get_historical_measurements(
        self, 
        city: str, 
        parameter: str = 'pm25',
        days: int = 7,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get historical measurements as DataFrame
        
        Args:
            city: City name
            parameter: Air quality parameter
            days: Number of past days to retrieve
            limit: Maximum results per request
        
        Returns:
            DataFrame with columns: timestamp, value, unit, location, city
        """
        date_from = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        
        try:
            response = self.session.get(
                f'{self.BASE_URL}/measurements',
                params={
                    'city': city,
                    'parameter': parameter,
                    'date_from': date_from,
                    'limit': limit
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Transform to DataFrame
            measurements = []
            for result in data.get('results', []):
                measurements.append({
                    'timestamp': result['date']['utc'],
                    'value': result['value'],
                    'unit': result['unit'],
                    'location': result['location'],
                    'city': result['city'],
                    'parameter': parameter
                })
            
            df = pd.DataFrame(measurements)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        
        except Exception as e:
            logger.error(f"Failed to fetch historical measurements: {e}")
            raise
    
    def get_cities(self, country: str = 'BR') -> List[str]:
        """Get list of available cities in a country"""
        try:
            response = self.session.get(
                f'{self.BASE_URL}/cities',
                params={'country': country},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return [city['city'] for city in data.get('results', [])]
        except Exception as e:
            logger.error(f"Failed to fetch cities: {e}")
            raise
    
    def get_locations(self, city: str) -> pd.DataFrame:
        """Get monitoring stations for a city"""
        try:
            response = self.session.get(
                f'{self.BASE_URL}/locations',
                params={'city': city},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            locations = []
            for loc in data.get('results', []):
                locations.append({
                    'location_id': loc['id'],
                    'location_name': loc['location'],
                    'city': loc['city'],
                    'country': loc['country'],
                    'latitude': loc['coordinates']['latitude'],
                    'longitude': loc['coordinates']['longitude']
                })
            
            return pd.DataFrame(locations)
        
        except Exception as e:
            logger.error(f"Failed to fetch locations: {e}")
            raise
```

### Example 2: Database Schema and Operations

```python
# database/schema.py
import sqlite3
from pathlib import Path
from datetime import datetime

class Database:
    """SQLite database for air quality data"""
    
    def __init__(self, db_path: str = 'aeris.db'):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        """Create database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY,
                openaq_id INTEGER UNIQUE,
                city TEXT NOT NULL,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                country TEXT DEFAULT 'BR',
                last_updated DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Raw measurements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY,
                location_id INTEGER NOT NULL,
                parameter TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp DATETIME NOT NULL,
                source TEXT DEFAULT 'openaq',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(location_id) REFERENCES locations(id),
                UNIQUE(location_id, parameter, timestamp)
            )
        ''')
        
        # Indices for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_measurements_timestamp 
            ON measurements(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_measurements_location_param
            ON measurements(location_id, parameter, timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_locations_city
            ON locations(city)
        ''')
        
        # Daily aggregates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_aggregates (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                location_id INTEGER NOT NULL,
                parameter TEXT NOT NULL,
                avg_value REAL,
                min_value REAL,
                max_value REAL,
                max_value_time TIME,
                min_value_time TIME,
                measurements_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, location_id, parameter),
                FOREIGN KEY(location_id) REFERENCES locations(id)
            )
        ''')
        
        # Cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY,
                cache_key TEXT UNIQUE NOT NULL,
                cache_value TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cache_expires
            ON cache(expires_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_measurements(self, measurements: list) -> int:
        """Insert measurements batch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted_count = 0
        for meas in measurements:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO measurements
                    (location_id, parameter, value, unit, timestamp, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    meas['location_id'],
                    meas['parameter'],
                    meas['value'],
                    meas['unit'],
                    meas['timestamp'],
                    meas.get('source', 'openaq')
                ))
                inserted_count += cursor.rowcount
            except sqlite3.IntegrityError:
                pass  # Duplicate, skip
        
        conn.commit()
        conn.close()
        return inserted_count
    
    def get_latest_measurements(self, city: str, parameter: str = None) -> list:
        """Get latest measurements for a city"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT m.*, l.city, l.location_name, l.latitude, l.longitude
            FROM measurements m
            JOIN locations l ON m.location_id = l.id
            WHERE l.city = ?
        '''
        params = [city]
        
        if parameter:
            query += ' AND m.parameter = ?'
            params.append(parameter)
        
        query += ' ORDER BY m.timestamp DESC LIMIT 1'
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def cleanup_old_data(self, days: int = 90):
        """Remove measurements older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().timestamp() - (days * 86400)
        
        cursor.execute('''
            DELETE FROM measurements 
            WHERE timestamp < datetime(?, 'unixepoch')
        ''', (cutoff_date,))
        
        # Reclaim space
        cursor.execute('VACUUM')
        
        conn.commit()
        conn.close()
```

### Example 3: Data Collection Scheduler

```python
# data/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from data.openaq_client import OpenAQClient
from database.schema import Database
from utils.config import Config

logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    """Manages scheduled data collection"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.client = OpenAQClient()
        self.db = Database(Config.DATABASE_PATH)
        self.target_cities = Config.TARGET_CITIES  # From config
    
    def start(self):
        """Start the scheduler"""
        # Collect data every 30 minutes
        self.scheduler.add_job(
            self.collect_all_cities,
            trigger=IntervalTrigger(minutes=30),
            id='collect_air_quality',
            name='Collect air quality data',
            replace_existing=True
        )
        
        # Compute daily aggregates at midnight
        self.scheduler.add_job(
            self.compute_daily_aggregates,
            trigger=CronTrigger(hour=0, minute=0),
            id='compute_daily_aggregates',
            name='Compute daily aggregates',
            replace_existing=True
        )
        
        # Cleanup old data weekly
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=CronTrigger(day_of_week=0, hour=3),  # Sunday 3 AM
            id='cleanup_old_data',
            name='Cleanup old measurements',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Data collection scheduler started")
    
    def collect_all_cities(self):
        """Collect latest measurements for all target cities"""
        logger.info("Starting data collection cycle")
        
        all_measurements = []
        for city in self.target_cities:
            try:
                # Get locations for city
                locations_df = self.client.get_locations(city)
                
                # For each location, get measurements
                for _, loc_row in locations_df.iterrows():
                    # Get latest PM2.5 and PM10
                    for param in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
                        try:
                            data = self.client.get_latest_measurements(city, param)
                            
                            if data.get('results'):
                                for result in data['results']:
                                    for meas in result.get('measurements', []):
                                        all_measurements.append({
                                            'location_id': loc_row['location_id'],
                                            'parameter': param,
                                            'value': meas['value'],
                                            'unit': meas['unit'],
                                            'timestamp': meas['lastUpdated'],
                                            'source': 'openaq'
                                        })
                        except Exception as e:
                            logger.warning(f"Failed to collect {param} for {city}: {e}")
                            continue
            
            except Exception as e:
                logger.error(f"Failed to collect data for {city}: {e}")
                continue
        
        # Store in database
        if all_measurements:
            inserted = self.db.insert_measurements(all_measurements)
            logger.info(f"Inserted {inserted} measurements")
        
        logger.info("Data collection cycle completed")
    
    def compute_daily_aggregates(self):
        """Compute daily aggregate statistics"""
        logger.info("Computing daily aggregates")
        # Implementation for aggregation
        pass
    
    def cleanup_old_data(self):
        """Cleanup data older than retention policy"""
        logger.info("Starting data cleanup")
        self.db.cleanup_old_data(days=90)
        logger.info("Data cleanup completed")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Data collection scheduler stopped")
```

---

## PART 8: BEST PRACTICES CHECKLIST

### Planning Phase
- [ ] Identify all target cities and verify OpenAQ coverage
- [ ] Document required air quality parameters (PM2.5 minimum, but collect all)
- [ ] Define data retention policy (90 days raw, 1 year aggregated)
- [ ] Plan dashboard pages and user flows

### Development Phase
- [ ] Set up virtual environment with Python 3.9+
- [ ] Create modular code structure (data/, database/, views/, utils/)
- [ ] Implement comprehensive error handling and retry logic
- [ ] Add structured logging throughout
- [ ] Use type hints in all functions
- [ ] Implement Streamlit caching strategies

### Data Collection Phase
- [ ] Test API connectivity and response parsing
- [ ] Implement data validation and cleaning
- [ ] Set up scheduler with proper error handling
- [ ] Monitor initial data collection for gaps
- [ ] Verify timestamp handling and timezone correctness

### Database Phase
- [ ] Create proper schema with foreign keys
- [ ] Implement all recommended indices
- [ ] Test backup and recovery procedures
- [ ] Plan for database growth (disk space)

### Dashboard Phase
- [ ] Implement multi-page structure
- [ ] Add interactive Plotly visualizations
- [ ] Implement proper caching for performance
- [ ] Add error handling UI elements
- [ ] Test with real data

### Testing Phase
- [ ] Write unit tests for data processors
- [ ] Write integration tests for API client
- [ ] Test database CRUD operations
- [ ] Load test with historical data
- [ ] Test error conditions and API failures

### Deployment Phase
- [ ] Containerize with Docker
- [ ] Set up environment variables properly
- [ ] Configure logging for production
- [ ] Plan monitoring and alerting
- [ ] Document runbook for operations

### Monitoring Phase
- [ ] Monitor API response times
- [ ] Track data collection success rate
- [ ] Monitor database size growth
- [ ] Alert on missing data
- [ ] Regular backup verification
