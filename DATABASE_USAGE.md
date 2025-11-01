# Database Usage in Aeris

## 📋 Executive Summary

**Current Status:** The Aeris dashboard is **NOT using the database** for data storage. All data is fetched directly from the OpenAQ API on-demand and cached in memory using Streamlit's caching mechanism.

**Database Module Status:** Fully implemented but not integrated with the Streamlit dashboard.

---

## 🔍 Current Implementation

### How the Dashboard Works Now

```
User Request → Streamlit App → OpenAQ API v3 → Display Data
                     ↓
              Cache in Memory
              (15-30 minutes TTL)
```

### Data Flow

1. **User visits a page** (Home, Dashboard, Comparison)
2. **Streamlit fetches data** directly from OpenAQ API using `OpenAQClient`
3. **Data is cached** in memory using `@st.cache_data(ttl=900)` decorator
4. **Results displayed** immediately to user
5. **Cache expires** after 15-30 minutes, then fresh data is fetched

### Current Components

```
aeris/
├── app.py                    # Main Streamlit app
├── views/
│   ├── home.py              # Fetches API → Displays
│   ├── dashboard.py         # Fetches API → Displays
│   └── comparison.py        # Fetches API → Displays
├── data/
│   └── data_collector.py    # OpenAQ API client
└── database/
    └── database.py          # ⚠️ EXISTS but NOT USED by dashboard
```

### Where Database IS Used

- ✅ `test_collection.py` - Testing script only
- ❌ Dashboard views - NOT using database
- ❌ Scheduled collection - NOT implemented

---

## 📊 Architecture Comparison

### Option 1: Current Architecture (Direct API)

```
┌──────────────────────────────────────┐
│         Streamlit Dashboard          │
│  (home.py, dashboard.py, etc.)       │
└────────────────┬─────────────────────┘
                 │
                 │ fetch_city_data()
                 ↓
┌──────────────────────────────────────┐
│       OpenAQ API v3 Client           │
│     (data_collector.py)              │
└────────────────┬─────────────────────┘
                 │
                 │ HTTP GET requests
                 ↓
┌──────────────────────────────────────┐
│         OpenAQ API v3                │
│     (api.openaq.org/v3)              │
└──────────────────────────────────────┘
```

**Characteristics:**
- Data fetched on every page visit (with caching)
- Cache stored in RAM (lost on restart)
- No persistent storage
- No historical analysis

**Pros:**
- ✅ Simple implementation
- ✅ Always fresh data
- ✅ No database maintenance
- ✅ Easy to understand and debug
- ✅ Works great for prototypes

**Cons:**
- ❌ API calls on every cache expiration
- ❌ Slower page loads (network latency)
- ❌ No historical data storage
- ❌ No offline capability
- ❌ Rate limit concerns with many users
- ❌ All data lost on restart

---

### Option 2: Full Architecture (With Database)

```
┌──────────────────────────────────────┐
│         Streamlit Dashboard          │
│  (home.py, dashboard.py, etc.)       │
└────────────────┬─────────────────────┘
                 │
                 │ read_from_database()
                 ↓
┌──────────────────────────────────────┐
│          SQLite Database             │
│  Tables:                             │
│  - cities                            │
│  - air_measurements                  │
│  - alerts                            │
└────────────────┬─────────────────────┘
                 ↑
                 │ write_measurements()
                 │ (every 30 minutes)
┌────────────────┴─────────────────────┐
│      Background Scheduler            │
│        (APScheduler)                 │
└────────────────┬─────────────────────┘
                 │
                 │ collect_city_data()
                 ↓
┌──────────────────────────────────────┐
│       OpenAQ API v3 Client           │
│     (data_collector.py)              │
└────────────────┬─────────────────────┘
                 │
                 │ HTTP GET requests
                 ↓
┌──────────────────────────────────────┐
│         OpenAQ API v3                │
│     (api.openaq.org/v3)              │
└──────────────────────────────────────┘
```

**Characteristics:**
- Background job fetches data every 30 minutes
- Data stored in local SQLite database
- Dashboard reads from database (fast)
- Historical data available for analysis

**Pros:**
- ✅ Much faster page loads (local database)
- ✅ Historical data for trends (7 days, 30 days, etc.)
- ✅ Fewer API calls (scheduled collection)
- ✅ Better rate limit management
- ✅ Offline capability (shows cached data)
- ✅ Persistent storage (survives restarts)
- ✅ Advanced queries (time series, aggregations)

**Cons:**
- ❌ More complex implementation
- ❌ Requires background scheduler
- ❌ Database maintenance needed
- ❌ Slightly delayed data (up to 30 min old)
- ❌ Disk storage required

---

### Option 3: Hybrid Architecture (Best of Both)

```
┌──────────────────────────────────────┐
│         Streamlit Dashboard          │
└─────────┬──────────────────┬─────────┘
          │                  │
          │ Historical       │ Latest/Refresh
          ↓                  ↓
┌─────────────────┐    ┌──────────────┐
│  SQLite DB      │    │ OpenAQ API   │
│  (Historical)   │    │ (Real-time)  │
└─────────────────┘    └──────────────┘
          ↑
          │
┌─────────┴───────┐
│   Scheduler     │
│ (Background)    │
└─────────────────┘
```

**Characteristics:**
- Historical data from database
- Current/refresh from API
- Best of both worlds

**Pros:**
- ✅ Fast historical queries
- ✅ Fresh data on demand
- ✅ Flexible approach

**Cons:**
- ❌ Most complex to implement
- ❌ Two data sources to manage

---

## 🗄️ Database Schema (Already Implemented)

The database module in `database/database.py` includes these tables:

### Table: `cities`
Stores monitoring locations and station information.

```sql
CREATE TABLE cities (
    location_id TEXT PRIMARY KEY,
    city_name TEXT NOT NULL,
    country TEXT DEFAULT 'BR',
    latitude REAL,
    longitude REAL,
    station_name TEXT,
    is_active BOOLEAN DEFAULT 1,
    available_parameters TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `air_measurements`
Stores time series air quality measurements.

```sql
CREATE TABLE air_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    city_name TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    parameter TEXT NOT NULL,      -- pm25, pm10, o3, etc.
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES cities(location_id)
);

-- Optimized indexes for fast queries
CREATE INDEX idx_measurements_city ON air_measurements(city_name);
CREATE INDEX idx_measurements_timestamp ON air_measurements(timestamp);
CREATE INDEX idx_measurements_parameter ON air_measurements(parameter);
```

### Table: `alerts`
Stores air quality alerts and notifications.

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL,
    alert_level TEXT NOT NULL,    -- good, moderate, unhealthy, etc.
    parameter TEXT,
    threshold_value REAL,
    current_value REAL,
    message TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## 📈 Performance Comparison

### Current Approach (Direct API)

| Metric | Performance |
|--------|-------------|
| Initial page load | 2-5 seconds (API call) |
| Cached page load | <100ms (memory) |
| Historical analysis | Not available |
| Trend charts (7 days) | Not available |
| API calls per day | ~50-100 (depends on users) |

### With Database

| Metric | Performance |
|--------|-------------|
| Initial page load | <200ms (local DB) |
| Cached page load | <100ms (memory) |
| Historical analysis | Fast (indexed queries) |
| Trend charts (7 days) | Available |
| API calls per day | ~48 (every 30 min) |

---

## 🚀 Implementation Options

### Option A: Keep Current Setup (Recommended for Now)

**When to choose:**
- You're still prototyping
- You mainly care about current air quality
- You have few users (rate limits not a concern)
- You don't need historical trends

**Action:** No changes needed! Current setup works great.

---

### Option B: Add Database Integration

**When to choose:**
- You want historical trends and analysis
- You need faster page loads
- You expect many users (rate limit concerns)
- You want to build advanced features (weekly reports, predictions, etc.)

**Implementation Steps:**

1. **Add Scheduler Module** (`scheduler.py`)
   ```python
   # Runs background job every 30 minutes
   # Fetches data from OpenAQ
   # Stores in SQLite database
   ```

2. **Update Views** (home.py, dashboard.py, etc.)
   ```python
   # Change from:
   client.get_locations_by_coordinates()

   # To:
   db.get_city_measurements()
   ```

3. **Add Historical Features**
   - 7-day trend charts
   - 30-day averages
   - Weekly reports
   - Alert history

4. **Start Background Scheduler**
   ```bash
   # In separate process or Docker container
   python scheduler.py
   ```

**Estimated Effort:** 4-6 hours

---

### Option C: Hybrid Approach

**When to choose:**
- You want both historical AND real-time data
- Users can choose between fast (cached) or fresh (API) data
- You're building a production application

**Implementation Steps:**
1. Implement Option B (database + scheduler)
2. Add "Refresh" button to fetch latest from API
3. Use database for historical views
4. Use API for real-time alerts

**Estimated Effort:** 6-8 hours

---

## 💡 Recommendations

### For Your Current Use Case

Given that you're:
- Learning/exploring the project
- Testing with OpenAQ API
- Running locally (not production)
- Interested in understanding the architecture

**Recommendation: Keep the current direct API approach for now.**

**Why:**
1. ✅ It's working well
2. ✅ Simpler to understand and debug
3. ✅ Fewer moving parts
4. ✅ Easy to modify and experiment

### When to Add Database

Consider adding database integration when:
1. You want to deploy to production
2. You need historical trend analysis
3. You want automated data collection
4. Page load speed becomes an issue
5. You're hitting API rate limits

---

## 🔧 Quick Implementation Guide (If You Choose Option B)

If you decide to add database integration, here's what needs to be done:

### Step 1: Create Scheduler Service

Create `scheduler.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from data.data_collector import collect_multiple_cities
from database.database import AerisDatabase

def collect_and_store():
    """Collect data and store in database."""
    db = AerisDatabase()
    cities_data = collect_multiple_cities()

    for city, (measurements, locations) in cities_data.items():
        db.insert_measurements(measurements)
        db.upsert_cities(locations)

scheduler = BackgroundScheduler()
scheduler.add_job(collect_and_store, 'interval', minutes=30)
scheduler.start()
```

### Step 2: Update Dashboard Views

Change `views/dashboard.py`:
```python
# FROM:
@st.cache_data(ttl=900)
def fetch_city_data(city_name: str):
    client = OpenAQClient()
    # ... fetch from API ...

# TO:
@st.cache_data(ttl=900)
def fetch_city_data(city_name: str):
    db = AerisDatabase()
    measurements = db.get_measurements_by_city(
        city_name,
        hours=24
    )
    # ... process database results ...
```

### Step 3: Run Scheduler

```bash
# Terminal 1: Run scheduler
python scheduler.py

# Terminal 2: Run dashboard
streamlit run app.py
```

---

## 📚 Additional Resources

### Relevant Files

- `database/database.py` - Full database implementation
- `data/data_collector.py` - API client (already has methods for database integration)
- `test_collection.py` - Example of database usage
- `config.py` - Database configuration settings

### Configuration

Database settings in `config.py`:
```python
class DatabaseConfig:
    DB_PATH = "data_storage/aeris.db"
    TIMEOUT = 30
    JOURNAL_MODE = "WAL"  # Write-Ahead Logging
    CACHE_SIZE = -64000   # 64MB cache
```

---

## 🎯 Summary

| Aspect | Current Setup | With Database |
|--------|---------------|---------------|
| **Implementation** | ✅ Done | ⏸️ Ready to implement |
| **Complexity** | Simple | Moderate |
| **Speed** | Good (with cache) | Excellent |
| **Historical Data** | No | Yes |
| **Best For** | Prototyping, demos | Production, analysis |
| **Maintenance** | Low | Medium |
| **API Usage** | High | Low (scheduled) |

---

## 📞 Next Steps

If you want to proceed with database integration, let me know and I can:

1. Create the scheduler service
2. Update all dashboard views to use the database
3. Add historical trend features
4. Set up automated data collection
5. Add database management commands (cleanup, backup, etc.)

Otherwise, the current setup is perfectly fine for learning and exploring air quality data in Brazilian cities! 🌤️

---

**Document Version:** 1.0
**Last Updated:** November 1, 2025
**Project:** Aeris Air Quality Dashboard
