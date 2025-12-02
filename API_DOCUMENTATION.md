# StockSignal API v2.0 Documentation

REST API for stock analysis with tiered modes, anchors, and viral-optimized headlines.

## Base URL

```
http://localhost:5000
```

## Endpoints

### Root Endpoint

**`GET /`**

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "StockSignal API v2.0",
  "version": "2.0.0",
  "description": "Stock analysis API with tiered modes, anchors, and headlines",
  "endpoints": {
    "analyze": "/api/analyze/<ticker>",
    "deprecated_compression": "/api/compression/<ticker> (redirects to /api/analyze)"
  },
  "documentation": "https://github.com/yourusername/StockSignal",
  "timestamp": "2025-12-02T12:00:00Z"
}
```

---

### Health Check

**`GET /health`**

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T12:00:00Z"
}
```

---

### Analyze Stock (v2.0)

**`GET /api/analyze/<ticker>`**

Perform complete v2.0 stock analysis with tiered modes, anchors, and headlines.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticker` | string | Stock ticker symbol (e.g., AAPL, MSFT, GOOGL) |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_anchor` | boolean | `true` | Include memorable anchor statement |
| `include_headline` | boolean | `true` | Include viral-optimized headline |
| `include_share_urls` | boolean | `true` | Include social media share URLs |
| `base_url` | string | `""` | Base URL for share links (optional) |

#### Response Schema

```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "current_price": 283.10,
  "analysis_mode": "GROWTH (PEG Ratio)",
  "metrics": {
    "trailing_pe": 37.9,
    "earnings_growth_pct": 0,
    "peg_ratio": 0
  },
  "signal": "BUY",
  "confidence": "high",
  "anchor": "Growing profits 1.4x would return AAPL to fair value",
  "headline": "🚀 $AAPL: GROWTH BUY! PEG ratio of 0.88...",
  "share_urls": {
    "twitter": "https://twitter.com/intent/tweet?text=...",
    "linkedin": "https://www.linkedin.com/sharing/share-offsite/?url=...",
    "copy_text": "🚀 $AAPL: GROWTH BUY! PEG ratio..."
  },
  "data_quality": "verified",
  "warnings": [],
  "timestamp": "2025-12-02T12:00:00Z"
}
```

#### Analysis Modes

The API automatically selects the appropriate analysis mode based on the stock's characteristics:

| Mode | Criteria | Key Metrics |
|------|----------|-------------|
| **VALUE** | P/E < 25 | `compression_pct`, `implied_growth_pct` |
| **GROWTH** | P/E 25-50 | `peg_ratio`, `earnings_growth_pct` |
| **HYPER_GROWTH** | P/E > 50 or loss-making | `price_to_sales`, `rule_of_40_score` |

#### Signals

| Signal | Description |
|--------|-------------|
| `STRONG_BUY` | Strong buy opportunity (VALUE mode only) |
| `BUY` | Buy opportunity |
| `HOLD` | Neutral, fairly valued |
| `SELL` | Sell signal |
| `STRONG_SELL` | Strong sell signal (VALUE mode only) |
| `DATA_ERROR` | Insufficient or invalid data |

#### Examples

**Full analysis with all fields:**
```bash
GET /api/analyze/AAPL
```

**Analysis without anchor:**
```bash
GET /api/analyze/AAPL?include_anchor=false
```

**Minimal response (core data only):**
```bash
GET /api/analyze/AAPL?include_anchor=false&include_headline=false&include_share_urls=false
```

**With custom base URL for share links:**
```bash
GET /api/analyze/AAPL?base_url=https://mysite.com
```

#### Error Responses

**404 - Invalid Ticker:**
```json
{
  "error": "InvalidTicker",
  "message": "Ticker symbol 'INVALID' not found",
  "ticker": "INVALID",
  "timestamp": "2025-12-02T12:00:00Z"
}
```

**500 - Analysis Error:**
```json
{
  "error": "AnalysisError",
  "message": "Failed to analyze AAPL: <error details>",
  "ticker": "AAPL",
  "timestamp": "2025-12-02T12:00:00Z"
}
```

---

### Compression Analysis (DEPRECATED)

**`GET /api/compression/<ticker>`** ⚠️ **DEPRECATED**

⚠️ This endpoint is deprecated and will be removed on **2026-01-01**.  
Please migrate to `/api/analyze/<ticker>`.

#### Deprecation Headers

- `X-Deprecated: true`
- `X-Sunset-Date: 2026-01-01`
- `Link: </api/analyze/<ticker>>; rel="successor-version"`

#### Response

Returns the same analysis as `/api/analyze/<ticker>` but wrapped in a deprecation warning:

```json
{
  "warning": "This endpoint is deprecated and will be removed on 2026-01-01",
  "deprecated_endpoint": "/api/compression/AAPL",
  "new_endpoint": "/api/analyze/AAPL",
  "migration_guide": "https://docs.pescanner.com/migration-v2",
  "sunset_date": "2026-01-01",
  "data": {
    "ticker": "AAPL",
    "analysis_mode": "GROWTH (PEG Ratio)",
    "signal": "BUY",
    ...
  }
}
```

#### Migration Guide

**Before:**
```python
response = requests.get("http://localhost:5000/api/compression/AAPL")
data = response.json()
```

**After:**
```python
response = requests.get("http://localhost:5000/api/analyze/AAPL")
data = response.json()
# All the same fields are available, plus new v2.0 enhancements
```

---

## Rate Limiting

Currently no rate limiting is enforced, but this may change in future versions.

## CORS

CORS is enabled for all origins. Suitable for development and simple web applications.

## Running the API

### Development Server

```bash
cd /Users/tomeldridge/StockSignal
source venv/bin/activate
python -m pe_scanner.api.app
```

The API will be available at `http://localhost:5000`.

### Production Deployment

For production use, deploy with a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'pe_scanner.api.app:create_app()'
```

## Testing

```bash
# Basic test
python test_api.py

# Detailed test with all features
python test_api_detailed.py

# Integration tests (pytest)
pytest tests/integration/test_api.py
```

## Dependencies

Required packages (already in `requirements.txt`):
- `flask>=3.0.0`
- `flask-cors>=4.0.0`
- `pydantic>=2.0.0`

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Changelog

### v2.0.0 (2025-12-02)

**Added:**
- Complete v2.0 API with tiered analysis (VALUE, GROWTH, HYPER_GROWTH)
- Anchor statements ("what would have to be true")
- Viral-optimized headlines with emojis
- Social media share URLs (Twitter, LinkedIn)
- Query parameters for selective field inclusion
- Comprehensive error handling
- CORS support

**Deprecated:**
- `/api/compression/<ticker>` endpoint (sunset: 2026-01-01)

**Migration Path:**
- Use `/api/analyze/<ticker>` instead of `/api/compression/<ticker>`
- All existing fields remain available
- New fields are optional and can be excluded via query parameters

