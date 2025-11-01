# Air Quality APIs - Detailed Comparison Matrix

## API Comparison Table

### OpenAQ API v2
```
CATEGORY                    | RATING/VALUE
============================================
License                     | Open Data Commons Attribution License
Cost                       | FREE (0)
Authentication Required   | NO
API Key Registration      | NO - Public API
Setup Time                | < 5 minutes
Documentation Quality    | EXCELLENT
Rate Limiting            | ~500 requests/hour
Brazilian Coverage       | EXCELLENT (SP, Rio, BH, Curitiba)
Parameters Available     | 9+ (PM2.5, PM10, O3, NO2, SO2, CO, BC, NO, NOx)
Historical Data Depth    | 90 days typical
Real-time Data          | YES (1-3 hour updates)
Forecast Data           | NO
Health Recommendations  | NO
Reliability             | HIGH (stable, well-maintained)
Recommended For         | PRIMARY data source
```

#### OpenAQ Strengths
- Completely free, no hidden costs
- Zero authentication overhead
- Large global dataset with good Brazilian coverage
- Well-documented with developer community
- Stable, maintained by Open Data community
- No registration required
- CORS-enabled for web requests

#### OpenAQ Limitations
- Limited historical data (90 days)
- Coverage gaps in smaller cities
- Rate limiting for heavy requests
- Data quality varies by location
- Dependent on local monitoring networks

#### OpenAQ Use Case
PRIMARY data source for all Brazilian cities. Supports:
- Latest air quality readings
- Time series analysis
- Multi-city comparisons
- Trend monitoring
- Historical analysis (3 months)

---

### IQAir/WAQI API
```
CATEGORY                    | RATING/VALUE
============================================
License                     | Proprietary (WAQI data)
Cost                        | FREE tier + Premium ($99/mo)
Authentication Required    | YES
API Key Registration       | YES (Free tier available)
Setup Time                 | 10-15 minutes
Documentation Quality     | GOOD
Rate Limiting             | 100 requests/minute (free), unlimited (paid)
Brazilian Coverage        | EXCELLENT
Parameters Available      | 8 (PM10, PM2.5, O3, NO2, SO2, CO, + AQI)
Historical Data Depth     | 30 days (free), unlimited (paid)
Real-time Data            | YES (updated frequently)
Forecast Data             | YES (daily forecasts)
Health Recommendations    | YES
Reliability               | VERY HIGH (commercial service)
Recommended For           | SECONDARY/COMPLEMENTARY source
```

#### IQAir/WAQI Strengths
- Excellent Brazilian city coverage
- Includes forecasting capabilities
- Health recommendations and alerts
- AQI calculation provided (no need to compute)
- Fast, reliable commercial service
- Combines multiple data sources
- Good UI for manual checking

#### IQAir/WAQI Limitations
- Not completely free (quota-based)
- API key required and registration overhead
- Free tier: 10,000 requests/month (~330/day)
- Monthly quota instead of rate limiting flexibility
- Closed data sources (proprietary algorithms)
- More expensive at scale

#### IQAir/WAQI Use Case
SECONDARY data source for:
- Validation/verification of OpenAQ data
- Enhanced forecasting
- Health recommendations
- Cities with limited OpenAQ coverage
- Multi-API reliability

**Cost-Benefit Analysis:**
- 10,000 requests/month = ~333/day = ~14/hour
- Sufficient for hourly collection (8 cities x 8 parameters = 64 requests/hour if called every 4 hours)
- Free tier adequate for initial dashboard (NOT for real-time every 30min collection)

---

### CETESB-SP (São Paulo)
```
CATEGORY                    | RATING/VALUE
============================================
License                     | Public (Brazilian gov data)
Cost                        | FREE
Authentication Required    | NO
API Key Registration       | NO
Setup Time                 | HIGH (web scraping required)
Documentation Quality     | POOR (no formal API)
Rate Limiting             | No formal limits (but scraping sensitive)
Brazilian Coverage        | SP ONLY
Parameters Available      | 8+ (complete air quality data)
Historical Data Depth     | 1+ years
Real-time Data            | YES (hourly updates)
Forecast Data             | NO
Health Recommendations    | AQI provided
Reliability               | MEDIUM (HTML parsing fragile)
Recommended For           | VERIFICATION/BACKUP source (SP only)
```

#### CETESB Strengths
- Completely free
- Official São Paulo state data (most authoritative for SP)
- Excellent historical data
- No registration needed
- High-quality measurements (direct from stations)

#### CETESB Limitations
- NO formal REST API (requires web scraping)
- Limited to São Paulo state only
- HTML structure changes break parsers
- Terms of service may not permit automation
- Fragile, high maintenance burden
- Not recommended as primary source

#### CETESB Use Case
VERIFICATION/BACKUP source for São Paulo only:
- Cross-check OpenAQ data for SP cities
- Long-term historical analysis
- Backup if OpenAQ SP data unavailable
- Validation of outliers

**Implementation Complexity:**
```python
# Scraping required (fragile)
import requests
from bs4 import BeautifulSoup

response = requests.get('https://cetesb.sp.gov.br/ar/qualidade-do-ar/publicacoes-e-relatorios/')
soup = BeautifulSoup(response.content, 'html.parser')
# Parse HTML structure (breaks when CETESB changes layout)
```

---

### INMET (Brazilian Meteorological Institute)
```
CATEGORY                    | RATING/VALUE
============================================
License                     | Public (Brazilian gov data)
Cost                        | FREE
Authentication Required    | NO
API Key Registration       | NO
Setup Time                 | MEDIUM
Documentation Quality     | FAIR
Rate Limiting             | Not specified
Brazilian Coverage        | NATIONWIDE (meteorological)
Parameters Available      | Temperature, humidity, pressure, wind (NOT air quality)
Historical Data Depth     | Years available
Real-time Data            | YES
Forecast Data             | YES
Health Recommendations    | NO
Reliability               | HIGH
Recommended For           | COMPLEMENTARY DATA ONLY
```

#### INMET Use Case
NOT recommended for primary air quality monitoring (meteorological focus).
Use only for:
- Correlating weather with air quality
- Temperature and humidity context
- Wind pattern analysis

---

## Side-by-Side API Comparison

| Feature | OpenAQ | IQAir/WAQI | CETESB | INMET |
|---------|--------|-----------|--------|-------|
| **Cost** | FREE | FREE (10k/mo) | FREE | FREE |
| **Registration** | NO | YES | NO | NO |
| **API Type** | REST | REST | Web scraping | REST |
| **Documentation** | EXCELLENT | GOOD | POOR | FAIR |
| **Setup Complexity** | LOW | MEDIUM | HIGH | MEDIUM |
| **SP Coverage** | Excellent | Excellent | Excellent | N/A |
| **Other BR Cities** | Good | Good | Limited to SP | Nationwide |
| **Real-time Data** | YES (1-3h) | YES | YES (hourly) | YES |
| **Historical (Free)** | 90 days | 30 days | 1+ years | Years |
| **Forecasts** | NO | YES | NO | YES |
| **Reliability** | HIGH | VERY HIGH | MEDIUM | HIGH |
| **Maintenance** | LOW | LOW | HIGH | LOW |
| **Recommended** | PRIMARY | SECONDARY | VERIFY (SP only) | CONTEXT |

---

## Recommended Multi-API Strategy

### Tier 1: Primary Data Source (REQUIRED)
**OpenAQ API v2**
- Collect every 30 minutes
- All 8 target Brazilian cities
- Collect all parameters (PM2.5, PM10, O3, NO2, SO2, CO)
- Dashboard primary data source
- Cost: FREE

### Tier 2: Secondary Data Source (OPTIONAL)
**IQAir/WAQI API** (if budget available)
- Collect every 2-4 hours
- Focus on major cities (SP, Rio, BH)
- Use for forecast and health alerts
- Validate OpenAQ outliers
- Cost: FREE (10k/month quota)

### Tier 3: Verification (For São Paulo Only)
**CETESB-SP** (weekly, not automated)
- Manual verification of SP data
- Compare with OpenAQ/IQAir
- Use if OpenAQ data suspicious
- Cost: FREE (manual effort only)

---

## Implementation Recommendation Summary

### For MVP (Minimum Viable Product)
```
Use: OpenAQ API v2 ONLY
├─ Collection interval: Every 30 minutes
├─ Cities: São Paulo, Rio, BH, Curitiba
├─ Parameters: PM2.5, PM10, O3, NO2, SO2, CO
└─ Cost: FREE
```

### For Full Feature Dashboard
```
Use: OpenAQ + IQAir (parallel collection)
├─ OpenAQ (primary):
│  ├─ Collection: Every 30 minutes
│  ├─ Priority: Latest measurements
│  └─ Cost: FREE
├─ IQAir (secondary):
│  ├─ Collection: Every 4 hours
│  ├─ Priority: Forecasts, health alerts
│  └─ Cost: FREE (10k/month)
└─ CETESB (validation, SP only):
   ├─ Collection: Manual or weekly
   ├─ Priority: Data verification
   └─ Cost: FREE (manual)
```

---

## Request Rate Analysis

### OpenAQ Collection Pattern
```
Collection interval: 30 minutes
Target cities: 8 (SP, Rio, BH, Curitiba, Brasília, Salvador, Fortaleza, Porto Alegre)
Parameters per city: 6 (PM2.5, PM10, O3, NO2, SO2, CO)

Requests per collection cycle:
- /locations endpoint: 8 calls (get stations per city)
- /latest endpoint: 8 x 6 = 48 calls (get latest for each parameter)
- Total per cycle: ~56 calls
- Calls per day: 56 x 48 cycles = 2,688 calls
- Calls per month: 2,688 x 30 = 80,640 calls

OpenAQ limit: ~500 calls/hour = 12,000/day = 360,000/month
Usage: 2,688/day = 22.4% of hourly limit
Result: WELL WITHIN LIMITS (with room for retries and redundancy)
```

### IQAir Collection Pattern (Optional)
```
Collection interval: 4 hours (not 30 minutes for cost)
Target cities: 3 major (SP, Rio, BH)

Requests per collection cycle:
- /feed endpoint: 3 calls per cycle
- Total per cycle: 3 calls
- Calls per day: 3 x 6 cycles = 18 calls
- Calls per month: 18 x 30 = 540 calls

IQAir free limit: 10,000 requests/month
Usage: 540/month = 5.4% of monthly limit
Result: WELL WITHIN FREE TIER
```

---

## API Endpoint Reference

### OpenAQ v2 Endpoints

```bash
# Base URL
https://api.openaq.org/v2/

# 1. Get latest measurements
GET /latest?city=São Paulo&parameter=pm25&limit=100

# 2. Get historical measurements
GET /measurements?city=São Paulo&parameter=pm25&limit=1000&date_from=2024-10-01T00:00:00Z

# 3. Get available locations (monitoring stations)
GET /locations?city=São Paulo

# 4. Get available cities in country
GET /cities?country=BR

# 5. Get all supported countries
GET /countries

# Response format: JSON with results array
# No pagination: use limit parameter (max 10,000)
# No authentication: no headers needed
```

### IQAir/WAQI Endpoints

```bash
# Base URL
https://api.waqi.info/

# 1. Get current city air quality
GET /feed/{city_name}/?token=YOUR_API_KEY

# 2. Get by coordinates
GET /feed/geo:{latitude};{longitude}/?token=YOUR_API_KEY

# 3. Search cities
GET /search/?keyword={query}&token=YOUR_API_KEY

# Example response:
{
  "status": "ok",
  "data": {
    "aqi": 72,
    "idx": 12345,
    "dominentpol": "pm25",
    "iaqi": {
      "pm25": {"v": 32},
      "pm10": {"v": 45},
      "o3": {"v": 28},
      "no2": {"v": 35},
      "so2": {"v": 12},
      "co": {"v": 285}
    },
    "forecast": {...},
    "time": {"s": "2024-11-01 10:00:00", "tz": "-03:00"}
  }
}
```

---

## Error Handling by API

### OpenAQ Error Codes
```
200 OK - Success
400 Bad Request - Invalid parameters
429 Too Many Requests - Rate limited
500 Server Error - Server issue

Recommended response:
- 200: Process response
- 400: Log error, skip request (invalid query)
- 429: Backoff and retry (exponential backoff)
- 500: Log error, retry (server temporarily down)
```

### IQAir Error Codes
```
200 OK - Success (check status field)
"status": "ok" - Data valid
"status": "error" - Data error

400 Bad Request - Invalid token
403 Forbidden - Quota exceeded
500 Server Error - Server issue

Recommended response:
- status=ok: Process response
- status=error: Log, skip request
- 403: Wait before retry (quota reset)
- Other: Standard exponential backoff
```

---

## Authentication Examples

### OpenAQ (NO Authentication)
```python
import requests

# No headers needed!
response = requests.get('https://api.openaq.org/v2/latest',
                       params={'city': 'São Paulo', 'parameter': 'pm25'})
data = response.json()
```

### IQAir/WAQI (With API Key)
```python
import requests

API_KEY = 'your_free_api_key_from_waqi.info'

response = requests.get('https://api.waqi.info/feed/São Paulo/?token=' + API_KEY)
data = response.json()

# Check status in response
if data['status'] == 'ok':
    aqi = data['data']['aqi']
else:
    print(f"Error: {data['status']}")
```

---

## Recommended Collection Schedule

### Collection Timeline

```
Every 30 minutes:
├─ OpenAQ /latest (all cities, all parameters)
├─ Parallel batch requests to reduce time
├─ Store in database with timestamp
└─ On failure: retry with exponential backoff

Every 4 hours (optional):
├─ IQAir /feed (major cities only)
├─ Update forecast and health alerts
└─ Store in separate alerts table

Every day at 00:00:
├─ Compute daily aggregates
├─ Move complete days to summary table
└─ Cleanup cache table entries

Every week (Sunday 3 AM):
├─ Archive measurements >90 days
├─ Remove old cache entries
├─ Run VACUUM on database
└─ Backup database to archive storage

Every month:
├─ Analyze data quality
├─ Check API coverage per city
├─ Review error rates
└─ Plan improvements
```

---

## Migration Path

### Phase 1: MVP (Week 1)
```
✓ OpenAQ only
✓ 3 major cities: SP, Rio, BH
✓ PM2.5 parameter only
✓ Collection every 4 hours
✓ Database storage
✓ Basic dashboard
```

### Phase 2: Enhancement (Week 2-3)
```
✓ Add all 8 target cities
✓ Add all 6 parameters
✓ Reduce collection to 30 minutes
✓ Add time series visualization
✓ Multi-city comparison
```

### Phase 3: Advanced (Week 4)
```
✓ Add IQAir for forecasts (optional)
✓ Add health alerts
✓ Add daily aggregates
✓ Performance optimization
✓ Deploy to production
```

---

## Testing Strategy by API

### OpenAQ Testing
```python
import requests

# Test 1: Verify API connectivity
response = requests.get('https://api.openaq.org/v2/cities?country=BR')
assert response.status_code == 200
print(f"Found {len(response.json()['results'])} Brazilian cities")

# Test 2: Verify data structure
response = requests.get('https://api.openaq.org/v2/latest?city=São Paulo&limit=1')
data = response.json()
assert 'results' in data
assert 'measurements' in data['results'][0]

# Test 3: Verify parameters
params = [m['parameter'] for m in data['results'][0]['measurements']]
assert 'pm25' in params or 'pm10' in params

# Test 4: Verify timestamps
timestamp = data['results'][0]['measurements'][0]['lastUpdated']
assert 'Z' in timestamp  # UTC format
```

### IQAir Testing
```python
# Test 1: Verify registration and token
response = requests.get(f'https://api.waqi.info/feed/São Paulo/?token={API_KEY}')
data = response.json()
assert data['status'] == 'ok'

# Test 2: Verify quota
# Check monthly request usage in IQAir dashboard

# Test 3: Verify data format
assert 'data' in data
assert 'aqi' in data['data']
```

