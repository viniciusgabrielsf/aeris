# Implementation Guide - Aeris Air Quality Dashboard

**Based on comprehensive research completed November 1, 2024**

---

## QUICK START

### For Developers New to This Project

**Step 1: Understand the Architecture**
Read: `CLAUDE.md` (project overview and conventions)

**Step 2: Choose Your Focus**
- API Integration: Start with `openaq_client.py` implementation
- Database: Start with schema creation in `database/schema.py`
- Dashboard: Start with Streamlit pages in `views/`

**Step 3: Use This Guide**
- Copy code examples directly into your modules
- Follow the recommended patterns
- Test with sample data before deployment

---

## RECOMMENDED TECH STACK SUMMARY

```yaml
Category              | Recommendation      | Reason
=====================================================
Data Source          | OpenAQ API v2       | Free, no auth, excellent Brazilian coverage
Secondary Source     | IQAir (optional)    | Enhanced forecasts, validation
REST Client          | requests            | Simple, synchronous sufficient
Data Processing      | Pandas              | Time series, aggregations, cleaning
Database             | SQLite              | Zero setup, sufficient scale
Dashboard Framework  | Streamlit           | Fast development, caching, multi-page
Visualization        | Plotly              | Interactive, maps, time series
Scheduling           | APScheduler         | Simple, no external deps, background tasks
```

**Cost: COMPLETELY FREE**

---

## FILE STRUCTURE SETUP

```
aeris/
├── app.py                      # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── aeris.db                   # SQLite database (auto-created)
├── data/
│   ├── __init__.py
│   ├── openaq_client.py       # OpenAQ API client
│   ├── processor.py           # Data validation/cleaning
│   └── scheduler.py           # APScheduler setup
├── database/
│   ├── __init__.py
│   └── schema.py              # SQLite schema/operations
├── views/
│   ├── __init__.py
│   ├── home.py               # Main dashboard page
│   ├── comparison.py         # Multi-city comparison
│   └── analytics.py          # Historical analysis
├── utils/
│   ├── __init__.py
│   ├── config.py             # Configuration from env
│   ├── logger.py             # Structured logging
│   └── aqi.py                # AQI calculations
├── tests/
│   ├── test_openaq_client.py
│   ├── test_database.py
│   └── test_processor.py
└── docker/
    └── Dockerfile            # Production deployment
```

---

## IMPLEMENTATION STEPS

### Step 1: Set Up Project Structure

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Create directory structure
mkdir -p data database views utils tests docker

# Initialize Python packages
touch data/__init__.py database/__init__.py views/__init__.py utils/__init__.py tests/__init__.py
```

### Step 2: Install Dependencies

Create `requirements.txt`:
```
# Core API and data
requests==2.31.0
pandas==2.1.1
numpy==1.24.3

# Database (sqlite3 is built-in)

# Dashboard and visualization
streamlit==1.28.0
plotly==5.17.0
streamlit-folium==0.17.0

# Scheduling
apscheduler==3.10.4

# Configuration
python-dotenv==1.0.0
pytz==2023.3
Pillow==10.0.0

# Development
pytest==7.4.2
pytest-cov==4.1.0
ruff==0.0.292
mypy==1.5.1
```

Install:
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create `.env` file:
```env
# API Configuration
OPENAQ_API_BASE_URL=https://api.openaq.org/v2
IQAIR_API_BASE_URL=https://api.waqi.info
IQAIR_API_KEY=your_api_key_here  # Optional

# Database
DATABASE_PATH=./aeris.db

# Collection
COLLECTION_INTERVAL_MINUTES=30
TARGET_CITIES=São Paulo,Rio de Janeiro,Belo Horizonte,Curitiba,Brasília,Salvador,Fortaleza,Porto Alegre

# Visualization
STREAMLIT_SERVER_PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aeris.log

# Cache
CACHE_TTL_SECONDS=3600
```

Create `utils/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API
    OPENAQ_API_BASE_URL = os.getenv('OPENAQ_API_BASE_URL', 'https://api.openaq.org/v2')
    IQAIR_API_BASE_URL = os.getenv('IQAIR_API_BASE_URL', 'https://api.waqi.info')
    IQAIR_API_KEY = os.getenv('IQAIR_API_KEY', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'aeris.db')
    
    # Collection
    COLLECTION_INTERVAL_MINUTES = int(os.getenv('COLLECTION_INTERVAL_MINUTES', '30'))
    TARGET_CITIES = os.getenv('TARGET_CITIES', 'São Paulo,Rio de Janeiro,Belo Horizonte').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/aeris.log')
    
    # Cache
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '3600'))
```

### Step 4: Implement Database Schema

Create `database/schema.py`:
```python
# See AIR_QUALITY_RESEARCH.md Part 3 for full implementation
# Code example included in that document

# Quick implementation:
import sqlite3
from pathlib import Path
from utils.config import Config

class Database:
    def __init__(self, db_path=Config.DATABASE_PATH):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        """Create all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Copy full schema from AIR_QUALITY_RESEARCH.md
        # See section "Database Schema Design"
        
        conn.commit()
        conn.close()
```

### Step 5: Implement OpenAQ Client

Create `data/openaq_client.py`:
```python
# See AIR_QUALITY_RESEARCH.md Part 7 "Code Examples"
# for complete OpenAQClient implementation

import requests
import pandas as pd
from typing import Dict, List
from utils.config import Config

class OpenAQClient:
    """OpenAQ API v2 client"""
    
    def __init__(self):
        self.base_url = Config.OPENAQ_API_BASE_URL
        self.session = requests.Session()
    
    def get_latest_measurements(self, city: str, parameter: str = 'pm25') -> Dict:
        """Get latest measurements for a city"""
        response = self.session.get(
            f'{self.base_url}/latest',
            params={'city': city, 'parameter': parameter},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    # See full code in AIR_QUALITY_RESEARCH.md
```

### Step 6: Implement Data Processor

Create `data/processor.py`:
```python
import pandas as pd
import numpy as np
from typing import DataFrame

def clean_air_quality_data(df: DataFrame) -> DataFrame:
    """
    Clean air quality measurements
    
    Handles:
    - Missing data (forward fill, interpolation)
    - Outliers (IQR method)
    - Sanity validation (WHO limits)
    """
    
    # 1. Handle missing values
    df['value'] = df.groupby(['city', 'parameter'])['value'].fillna(method='ffill', limit=3)
    df['value'] = df.groupby(['city', 'parameter'])['value'].interpolate(
        method='linear', limit_direction='both', limit=24
    )
    
    # 2. Detect outliers using IQR
    for city in df['city'].unique():
        for param in df['parameter'].unique():
            mask = (df['city'] == city) & (df['parameter'] == param)
            subset = df.loc[mask, 'value']
            
            Q1 = subset.quantile(0.25)
            Q3 = subset.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (df.loc[mask, 'value'] < lower_bound) | (df.loc[mask, 'value'] > upper_bound)
            df.loc[mask & outliers, 'value'] = subset.median()
    
    # 3. Sanity validation
    parameter_limits = {
        'pm25': (0, 500),
        'pm10': (0, 500),
        'o3': (0, 200),
        'no2': (0, 500),
        'so2': (0, 500),
        'co': (0, 50000)
    }
    
    for param, (min_val, max_val) in parameter_limits.items():
        param_mask = df['parameter'] == param
        df.loc[param_mask & (df['value'] < min_val), 'value'] = np.nan
        df.loc[param_mask & (df['value'] > max_val), 'value'] = np.nan
    
    df = df.dropna(subset=['value'])
    
    return df
```

### Step 7: Implement Scheduler

Create `data/scheduler.py`:
```python
# See AIR_QUALITY_RESEARCH.md Part 7
# for complete DataCollectionScheduler implementation

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from data.openaq_client import OpenAQClient
from database.schema import Database
from utils.config import Config
import logging

logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.client = OpenAQClient()
        self.db = Database()
    
    def start(self):
        """Start background scheduler"""
        self.scheduler.add_job(
            self.collect_all_cities,
            trigger=IntervalTrigger(minutes=Config.COLLECTION_INTERVAL_MINUTES),
            id='collect_data'
        )
        self.scheduler.start()
        logger.info("Data collection scheduler started")
    
    def collect_all_cities(self):
        """Collect data for all target cities"""
        for city in Config.TARGET_CITIES:
            try:
                # Implementation
                pass
            except Exception as e:
                logger.error(f"Failed to collect {city}: {e}")
    
    def stop(self):
        self.scheduler.shutdown()
```

### Step 8: Create Main Dashboard App

Create `app.py`:
```python
import streamlit as st
import pandas as pd
from database.schema import Database
from data.scheduler import DataCollectionScheduler
from utils.config import Config
import logging

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize scheduler (runs once)
@st.cache_resource
def init_scheduler():
    scheduler = DataCollectionScheduler()
    scheduler.start()
    return scheduler

# Initialize database
@st.cache_resource
def init_database():
    return Database(Config.DATABASE_PATH)

# Configure Streamlit
st.set_page_config(
    page_title="Aeris Air Quality Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Aeris - Air Quality Dashboard")
st.markdown("Real-time air quality monitoring for Brazilian cities")

# Initialize
scheduler = init_scheduler()
db = init_database()

# Sidebar
with st.sidebar:
    st.header("Settings")
    selected_cities = st.multiselect(
        "Select Cities",
        options=Config.TARGET_CITIES,
        default=Config.TARGET_CITIES[:3]
    )
    
    selected_parameters = st.multiselect(
        "Select Parameters",
        options=['pm25', 'pm10', 'o3', 'no2', 'so2', 'co'],
        default=['pm25', 'pm10']
    )
    
    time_range = st.radio(
        "Time Range",
        options=['24h', '7d', '30d'],
        horizontal=True
    )

# Main content
tab1, tab2, tab3 = st.tabs(["Latest Readings", "Time Series", "Comparison"])

with tab1:
    st.header("Latest Air Quality Readings")
    # Load latest data from database
    # Display with color coding
    # See views/home.py for implementation

with tab2:
    st.header("Historical Trends")
    # Plot time series charts
    # See views/analytics.py for implementation

with tab3:
    st.header("City Comparison")
    # Compare multiple cities
    # See views/comparison.py for implementation

# Footer
st.markdown("---")
st.markdown(f"Data source: OpenAQ API v2 | Last update: {pd.Timestamp.now()}")
```

### Step 9: Create Dashboard Pages

Create `views/home.py`:
```python
import streamlit as st
import pandas as pd
import plotly.express as px
from database.schema import Database
from utils.config import Config
from utils.aqi import calculate_aqi, get_aqi_color

@st.cache_data(ttl=Config.CACHE_TTL_SECONDS)
def load_latest_data():
    """Load latest measurements from database"""
    db = Database(Config.DATABASE_PATH)
    
    # Query latest measurements per city
    conn = db._get_connection()
    query = """
        SELECT m.*, l.city, l.location_name
        FROM measurements m
        JOIN locations l ON m.location_id = l.id
        WHERE m.timestamp = (
            SELECT MAX(timestamp) FROM measurements
        )
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def display_latest_aqi():
    """Display latest AQI for each city"""
    df = load_latest_data()
    
    # Group by city and get PM2.5 for AQI
    cities_data = df[df['parameter'] == 'pm25'].sort_values('value', ascending=False)
    
    # Display as grid
    cols = st.columns(3)
    for idx, (_, row) in enumerate(cities_data.iterrows()):
        with cols[idx % 3]:
            aqi = calculate_aqi(row['value'], 'pm25')
            color = get_aqi_color(aqi)
            
            st.metric(
                label=row['city'],
                value=f"AQI: {aqi}",
                delta=f"PM2.5: {row['value']:.1f} µg/m³",
                delta_color="off"
            )
```

### Step 10: Configure Logging

Create `utils/logger.py`:
```python
import logging
from utils.config import Config
from pathlib import Path

def setup_logging():
    """Configure structured logging"""
    Path(Config.LOG_FILE).parent.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

### Step 11: Implement AQI Calculations

Create `utils/aqi.py`:
```python
def calculate_aqi(value: float, parameter: str) -> int:
    """
    Calculate US EPA AQI from pollutant concentration
    
    Parameters:
    - value: Pollutant concentration
    - parameter: 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co'
    
    Returns:
    - AQI value (0-500+)
    """
    
    # EPA AQI breakpoints
    aqi_breakpoints = {
        'pm25': [
            (0, 12, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 999999, 301, 500),
        ],
        'pm10': [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 999999, 301, 500),
        ],
        'o3': [
            (0, 54, 0, 50),
            (55, 70, 51, 100),
            (71, 85, 101, 150),
            (86, 105, 151, 200),
            (106, 200, 201, 300),
            (201, 999999, 301, 500),
        ],
        # Add others as needed
    }
    
    if parameter not in aqi_breakpoints:
        return None
    
    for conc_min, conc_max, aqi_min, aqi_max in aqi_breakpoints[parameter]:
        if conc_min <= value <= conc_max:
            # Linear interpolation
            aqi = (aqi_max - aqi_min) * (value - conc_min) / (conc_max - conc_min) + aqi_min
            return int(round(aqi))
    
    return 500

def get_aqi_color(aqi: int) -> str:
    """Get color for AQI value"""
    if aqi <= 50:
        return "green"      # Good
    elif aqi <= 100:
        return "yellow"     # Moderate
    elif aqi <= 150:
        return "orange"     # Unhealthy for Sensitive Groups
    elif aqi <= 200:
        return "red"        # Unhealthy
    elif aqi <= 300:
        return "purple"     # Very Unhealthy
    else:
        return "maroon"     # Hazardous
```

### Step 12: Write Tests

Create `tests/test_openaq_client.py`:
```python
import pytest
from data.openaq_client import OpenAQClient

def test_openaq_connectivity():
    """Test OpenAQ API is accessible"""
    client = OpenAQClient()
    data = client.get_cities('BR')
    assert len(data) > 0

def test_get_latest_measurements():
    """Test fetching latest measurements"""
    client = OpenAQClient()
    data = client.get_latest_measurements('São Paulo', 'pm25')
    assert 'results' in data
    assert len(data['results']) > 0

def test_get_locations():
    """Test fetching station locations"""
    client = OpenAQClient()
    df = client.get_locations('São Paulo')
    assert len(df) > 0
    assert 'location_name' in df.columns
```

### Step 13: Run the Dashboard

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux

# Run Streamlit
streamlit run app.py

# Dashboard will be available at http://localhost:8501
```

---

## TESTING CHECKLIST

Before deploying to production:

```
Data Collection:
[ ] OpenAQ API connectivity test
[ ] All 8 Brazilian cities accessible
[ ] All 6 parameters retrievable
[ ] Data validation working (no invalid values)
[ ] Duplicates prevented by database constraints
[ ] Timestamps stored correctly (UTC)

Database:
[ ] Schema created successfully
[ ] All indices present
[ ] Query performance acceptable
[ ] Backup/restore procedures tested
[ ] Old data cleanup working

Dashboard:
[ ] Streamlit pages load quickly
[ ] Caching working (check load time)
[ ] Multi-city comparison accurate
[ ] AQI calculations correct
[ ] Time series plots responsive

Error Handling:
[ ] API timeout handled gracefully
[ ] Network error recovery working
[ ] Invalid data rejected
[ ] Scheduler restarts on error
[ ] Logs show all errors/warnings

Performance:
[ ] Dashboard loads in <3 seconds
[ ] Database query performance <500ms
[ ] API requests complete <10s
[ ] Memory usage stable over 24h
[ ] CPU usage <10% when idle
```

---

## DEPLOYMENT CHECKLIST

```
Preparation:
[ ] Code reviewed and tested
[ ] Dependencies in requirements.txt
[ ] Environment variables documented
[ ] Logging configured
[ ] Error handling comprehensive

Docker:
[ ] Dockerfile created
[ ] Image builds successfully
[ ] Container runs locally
[ ] Port mappings correct
[ ] Volume mounts for persistent storage

Cloud (if using):
[ ] Environment variables set
[ ] Database path writable
[ ] API access allowed (firewall)
[ ] Logs accessible
[ ] Monitoring configured

Operations:
[ ] Runbook documented
[ ] Backup procedure in place
[ ] Monitoring alerts configured
[ ] Team trained on troubleshooting
```

---

## MONITORING & MAINTENANCE

### Daily Tasks
- Check error logs for issues
- Monitor API response times
- Verify data collection happening

### Weekly Tasks
- Verify database growth normal
- Check data quality metrics
- Review system performance

### Monthly Tasks
- Archive old data
- Analyze coverage gaps
- Plan feature improvements
- Update dependencies

---

## SUPPORT & TROUBLESHOOTING

### API not responding
```python
# Check connectivity
import requests
response = requests.get('https://api.openaq.org/v2/cities?country=BR')
print(response.status_code)  # Should be 200
```

### Database locked
```bash
# Restart scheduler
kill <process_id>
# Remove stale locks
rm -f aeris.db-wal aeris.db-shm
# Restart application
```

### High memory usage
```python
# Check for large cached queries
st.cache_clear()  # In Streamlit console
# Reduce CACHE_TTL_SECONDS in .env
```

---

## NEXT STEPS AFTER SETUP

1. Deploy to Streamlit Cloud (free tier available)
2. Add IQAir API for enhanced features (optional)
3. Implement email alerts for hazardous conditions
4. Add historical data export functionality
5. Create mobile-friendly responsive design

---

## RESOURCES

- OpenAQ Documentation: https://docs.openaq.org/
- Streamlit Docs: https://docs.streamlit.io/
- Plotly Guide: https://plotly.com/python/
- SQLite Best Practices: https://www.sqlite.org/bestpractice.html
- APScheduler: https://apscheduler.readthedocs.io/

