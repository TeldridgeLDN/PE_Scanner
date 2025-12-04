# StockSignal Usage Guide

Complete guide to using StockSignal for portfolio analysis and stock screening.

## Table of Contents
- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Portfolio Setup](#portfolio-setup)
- [Analysis Examples](#analysis-examples)
- [Understanding Results](#understanding-results)
- [Advanced Usage](#advanced-usage)

---

## Installation

### Prerequisites
- Python 3.13+ (tested with 3.13.5)
- Virtual environment recommended

### Setup
```bash
cd /Users/tomeldridge/StockSignal
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Verify Installation
```bash
pe-scanner --version
pe-scanner status
```

---

## Basic Commands

### Fetch Individual Stock Data
```bash
# US stocks
pe-scanner fetch --ticker AAPL
pe-scanner fetch --ticker MSFT
pe-scanner fetch --ticker NVDA

# UK stocks (auto-corrects pence/pounds)
pe-scanner fetch --ticker BATS.L
pe-scanner fetch --ticker RR.L
```

### Analyze Portfolios
```bash
# Analyze specific portfolio
pe-scanner analyze --portfolio ISA
pe-scanner analyze --portfolio SIPP
pe-scanner analyze --portfolio WISHLIST

# Analyze all portfolios
pe-scanner analyze --all

# Save report to file
pe-scanner analyze --portfolio ISA --output reports/isa_analysis.md
```

### Manual Verification
```bash
# Get verification checklist for suspicious data
pe-scanner verify --ticker HOOD
pe-scanner verify --ticker NFLX
```

### System Management
```bash
# Check configuration and status
pe-scanner status

# Cache management
pe-scanner cache --stats      # View cache statistics
pe-scanner cache --clear      # Clear cached data
```

---

## Portfolio Setup

### CSV Format
Create CSV files in `portfolios/` directory:

```csv
ticker,shares,cost_basis
AAPL,100,150.00
MSFT,50,300.00
GOOGL,25,2800.00
BATS.L,200,28.50
```

### Portfolio Types
- `portfolios/isa.csv` - ISA holdings
- `portfolios/sipp.csv` - SIPP holdings
- `portfolios/wishlist.csv` - Watch list

### Optional Columns
```csv
ticker,shares,cost_basis,portfolio_type,notes
AAPL,100,150.00,ISA,Tech holdings
MO,50,45.00,SIPP,Income
```

---

## Analysis Examples

### Example 1: Tech Stock Comparison

**AAPL (Apple)**
```bash
$ pe-scanner fetch --ticker AAPL

📊 AAPL (Apple Inc.)
Current Price: $280.51
Trailing P/E: 37.55
Forward P/E: 33.76

📈 P/E COMPRESSION ANALYSIS
Compression: +10.11%
Signal: CONSIDER BUYING
Implied EPS Growth: +11.24%

💰 FAIR VALUE SCENARIOS
Bear Case (17.5x): $145.43 (-48.1%)
Bull Case (37.5x): $311.62 (+11.1%)

🎯 RECOMMENDATION
✅ CONSIDER BUYING - Moderate positive compression
```

**NVDA (NVIDIA)**
```bash
$ pe-scanner fetch --ticker NVDA

📊 NVDA (NVIDIA Corporation)
Current Price: $179.48
Trailing P/E: 44.43
Forward P/E: 43.56

📈 P/E COMPRESSION ANALYSIS
Compression: +1.94%
Signal: HOLD
Implied EPS Growth: +1.98%

🎯 RECOMMENDATION
🟡 HOLD - Minimal compression
Trading at 43.6x forward (premium valuation)
AI boom growth may be priced in
```

**GOOGL (Alphabet)**
```bash
$ pe-scanner fetch --ticker GOOGL

📊 GOOGL (Alphabet Inc.)
Current Price: $317.30
Trailing P/E: 31.35
Forward P/E: 35.41

📈 P/E COMPRESSION ANALYSIS
Compression: -12.95%
Signal: CAUTION
Implied EPS Growth: -11.46%

🎯 RECOMMENDATION
⚠️ CAUTION - Negative compression
Market expects EPS to decline 11.5%
```

**Comparison:**
| Stock | Compression | Signal | Ranking |
|-------|-------------|--------|---------|
| AAPL | +10.11% | ✅ Buy | 🥇 Best Value |
| NVDA | +1.94% | 🟡 Hold | 🥈 Neutral |
| GOOGL | -12.95% | ⚠️ Caution | 🥉 Weakest |

### Example 2: UK Stock Auto-Correction

**BATS.L (British American Tobacco)**
```bash
$ pe-scanner fetch --ticker BATS.L

🔧 UK STOCK CORRECTION APPLIED
Original Forward P/E: 0.085
Corrected Forward P/E: 8.50
Reason: Pence-to-pounds conversion (100x correction)

✅ Data quality issue automatically fixed!
```

### Example 3: Turnaround Detection

**VOD (Vodafone)**
```bash
$ pe-scanner fetch --ticker VOD

⚠️ TURNAROUND SITUATION DETECTED
• Trailing EPS: $-1.90 (LOSS)
• Forward EPS: $0.85 (PROFIT expected)
• No trailing P/E available due to negative earnings

💰 FAIR VALUE SCENARIOS
Bear Case (17.5x): $14.88 (+21.9%)
Bull Case (37.5x): $31.88 (+161.2%)

🎯 ANALYSIS
This is a TURNAROUND play:
• Company currently loss-making
• Analysts expect return to profitability
• Higher risk/reward than typical value stocks
```

### Example 4: Value Stock

**MO (Altria)**
```bash
$ pe-scanner fetch --ticker MO

📊 MO (Altria Group, Inc.)
Current Price: $59.06
Trailing P/E: 11.27
Forward P/E: 11.04

📈 P/E COMPRESSION ANALYSIS
Compression: +2.06%
Signal: HOLD
Implied EPS Growth: +2.10%

💰 FAIR VALUE SCENARIOS
Bear Case (17.5x): $93.62 (+58.5%)
Bull Case (37.5x): $200.62 (+239.7%)

🎯 VERDICT
HOLD - Minimal compression (+2%)
However, fair value shows +58% upside even in bear case
May be undervalued at tobacco-sector-low multiples
```

---

## Understanding Results

### P/E Compression Signals

| Compression | Signal | Meaning |
|-------------|--------|---------|
| > +30% | 🚀 STRONG BUY | Exceptional undervaluation |
| +20% to +30% | ✅ BUY | Strong positive signal |
| +10% to +20% | ✅ CONSIDER | Moderate positive |
| +5% to +10% | 🟡 HOLD | Slightly positive |
| -5% to +5% | 🟡 HOLD | Neutral range |
| -10% to -5% | ⚠️ CAUTION | Slightly negative |
| -20% to -10% | ⚠️ CAUTION | Moderate negative |
| < -20% | 🔴 SELL | Strong negative signal |

### Data Quality Levels

| Level | Confidence | Meaning |
|-------|------------|---------|
| VERIFIED | 100% | All data checks passed |
| ACCEPTABLE | 70-99% | Minor warnings, usable |
| SUSPICIOUS | 40-69% | Multiple concerns, verify manually |
| UNRELIABLE | < 40% | Major issues, do not trade |

### Fair Value Scenarios

**Bear Case (17.5x P/E):**
- Conservative valuation
- Suitable for defensive/value stocks
- Below market average multiple

**Bull Case (37.5x P/E):**
- Optimistic valuation
- Suitable for growth stocks
- Above market average multiple

**Current Forward P/E:**
- What market is currently paying
- Compare to bear/bull to gauge valuation

---

## Advanced Usage

### Configuration

Edit `config.yaml` to customize:

```yaml
data:
  cache_ttl: 3600        # Cache duration (seconds)
  rate_limit_delay: 0.2  # API call delay
  max_retries: 3
  timeout: 30

validation:
  max_pe_threshold: 500
  max_growth_threshold: 200
  stale_estimate_days: 180

scenarios:
  bear_pe_multiple: 17.5
  bull_pe_multiple: 37.5
```

### Batch Analysis

```bash
# Create a watchlist CSV
cat > portfolios/watchlist.csv << EOF
ticker,shares,cost_basis
AAPL,0,0
MSFT,0,0
GOOGL,0,0
NVDA,0,0
META,0,0
EOF

# Analyze entire watchlist
pe-scanner analyze --portfolio WISHLIST
```

### Report Formats

```bash
# Markdown (default)
pe-scanner analyze --portfolio ISA --output report.md

# Console output with rich formatting
pe-scanner analyze --portfolio ISA --format console

# Include methodology section
pe-scanner analyze --portfolio ISA --methodology
```

### Fresh Data (Bypass Cache)

```bash
# Force fresh API calls
pe-scanner analyze --portfolio ISA --no-cache
pe-scanner fetch --ticker AAPL --no-cache
```

### Integration with Momentum_Squared

```bash
# StockSignal supports Momentum_Squared CSV format
# Copy your master portfolio:
cp ~/Momentum_Squared/portfolios/master.csv portfolios/isa.csv

# Analyze with sync validation
pe-scanner analyze --portfolio ISA
```

---

## Common Use Cases

### 1. Weekly Portfolio Review
```bash
# Clear cache for fresh data
pe-scanner cache --clear

# Analyze all portfolios
pe-scanner analyze --all --output reports/weekly_$(date +%Y%m%d).md

# Review top signals
grep "BUY\|SELL" reports/weekly_*.md
```

### 2. Pre-Trade Due Diligence
```bash
# Analyze candidate stock
pe-scanner fetch --ticker AAPL

# Check for data quality issues
pe-scanner verify --ticker AAPL

# Compare with portfolio holdings
pe-scanner analyze --portfolio ISA
```

### 3. Rebalancing Analysis
```bash
# Identify overvalued positions (candidates to trim)
pe-scanner analyze --portfolio ISA | grep "SELL\|CAUTION"

# Identify undervalued opportunities (candidates to add)
pe-scanner analyze --portfolio WISHLIST | grep "BUY"
```

### 4. Sector Rotation
```bash
# Compare similar stocks
pe-scanner fetch --ticker AAPL  # Tech
pe-scanner fetch --ticker MSFT  # Tech
pe-scanner fetch --ticker GOOGL # Tech

# Look for best compression signal
# AAPL: +10.11% ✅
# NVDA: +1.94% 🟡
# GOOGL: -12.95% ⚠️
# → Favor AAPL
```

---

## Troubleshooting

### API Rate Limits
```bash
# Increase delay between calls
# Edit config.yaml:
data:
  rate_limit_delay: 0.5  # Increase from 0.2
```

### Missing Data
```bash
# Check ticker symbol
pe-scanner fetch --ticker AAPL  # ✅ Correct
pe-scanner fetch --ticker APPLE # ❌ Wrong

# For UK stocks, add .L suffix
pe-scanner fetch --ticker BATS.L  # ✅ Correct
```

### Data Quality Warnings
```bash
# Use manual verification
pe-scanner verify --ticker HOOD

# Check against alternative sources:
# - Bloomberg Terminal
# - Company SEC filings
# - FactSet data
```

---

## Performance Notes

- **Concurrent Fetching**: 25 tickers in <2 seconds
- **Cache TTL**: 1 hour default (3600 seconds)
- **Test Coverage**: 82% (399 tests passing)
- **Supports**: ISA, SIPP, Wishlist portfolios
- **Markets**: US (NYSE, NASDAQ), UK (LSE .L suffix)

---

## Further Reading

- **PRD**: `.taskmaster/docs/prd.txt` - Complete requirements
- **Changelog**: `Changelog.md` - Version history
- **Tasks**: `.taskmaster/tasks/tasks.json` - Development roadmap
- **Reference Analysis**: `/Users/tomeldridge/Momentum_Squared/analysis/PE_Compression_Analysis_Corrected_Nov2024.md`

---

**Version**: 0.1.0  
**Last Updated**: December 1, 2025  
**Repository**: https://github.com/TeldridgeLDN/StockSignal



