# StockSignal

**P/E Compression Analysis Tool for Portfolio Management**

StockSignal is a Python-based investment analysis tool that identifies opportunities through P/E (Price-to-Earnings) compression analysis. It automatically screens portfolios to find stocks where market expectations diverge significantly from current valuations.

## 🎯 What It Does

**Core Functionality:**
- Analyzes P/E compression (Trailing P/E vs Forward P/E)
- Identifies undervalued opportunities (positive compression)
- Detects overvalued positions (negative compression)
- Provides actionable buy/sell/hold recommendations

**Data Quality Features:**
- Auto-corrects UK stock data errors (pence/pounds conversion)
- Detects stock split data inconsistencies
- Flags suspicious growth projections for manual review
- Validates analyst estimates against actual financials

**Fair Value Scenarios:**
- Bear Case: 17.5x P/E multiple
- Bull Case: 37.5x P/E multiple
- Calculates upside/downside potential for each position

## 📊 Example Use Case

Based on actual November 2024 analysis that identified:
- **✅ Confirmed Sell**: HOOD (Robinhood) with -113% compression = 53% earnings collapse expected
- **❌ False Signal**: NFLX (Netflix) had +89% compression due to stock split data error
- **🟢 Buy Opportunities**: ORA.PA (+70% compression), ENGI.PA (+7% compression, +280% bull upside)

## 🏗️ Architecture

### Full Stack Architecture
StockSignal consists of two main components:

**Backend (Python + Flask):**
- REST API v2.0 for stock analysis
- P/E compression engine (VALUE/GROWTH/HYPER_GROWTH modes)
- Portfolio batch processing
- Data quality validation

**Frontend (Next.js 15):**
- Web interface at `web/` directory
- Ticker search and results display
- Portfolio upload interface
- Shareable analysis headlines

### PAI/diet103 Integration
StockSignal follows the Orchestrator_Project architecture patterns:
- **PAI Global Layer**: Cross-project template sharing and orchestration
- **diet103 Local Layer**: Project-specific hooks and validation
- **Shared Patterns**: Data pipeline consistency with Momentum_Squared

### Project Structure
```
StockSignal/
├── src/
│   └── pe_scanner/
│       ├── analysis/          # P/E compression, fair value calculations
│       ├── api/               # Flask REST API v2.0
│       ├── data/              # Yahoo Finance integration, validation
│       ├── portfolios/        # Portfolio loading, ranking, reporting
│       └── cli.py             # Command-line interface
├── web/                       # Next.js 15 frontend (NEW)
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   └── lib/                   # Frontend utilities
├── tests/                     # Test suite
├── scripts/                   # Analysis scripts
├── portfolios/                # Portfolio CSV files (ISA, SIPP, Wishlist)
├── outputs/                   # Generated reports
└── .taskmaster/               # Task Master project management
```

## 🚀 Quick Start

### Backend Installation (Python)

```bash
# Clone repository
git clone https://github.com/yourusername/StockSignal.git
cd StockSignal

# Install Python backend
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Frontend Installation (Next.js)

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Copy environment variables
cp env.example .env.local

# Start development server
npm run dev
# Open http://localhost:3000
```

### Backend Usage (CLI)

```bash
# Analyze individual stocks
pe-scanner fetch --ticker AAPL
pe-scanner fetch --ticker MO
pe-scanner fetch --ticker BATS.L  # UK stocks auto-corrected

# Analyze your portfolio
pe-scanner analyze --portfolio ISA
pe-scanner analyze --all  # All portfolios

# Generate saved reports
pe-scanner analyze --portfolio SIPP --output reports/sipp_analysis.md

# Manual verification for suspicious signals
pe-scanner verify --ticker HOOD

# Check system status
pe-scanner status
pe-scanner cache --stats
```

### Real Examples

**Tested Live:**
```bash
# Apple - Positive compression (+10.11%)
$ pe-scanner fetch --ticker AAPL
✅ CONSIDER BUYING - Moderate positive compression
Bear: $145.43 (-48.1%) | Bull: $311.62 (+11.1%)

# NVIDIA - Minimal compression (+1.94%)
$ pe-scanner fetch --ticker NVDA
🟡 HOLD - Compression within normal range
Trading at 43.6x forward (premium valuation justified)

# Alphabet - Negative compression (-12.95%)
$ pe-scanner fetch --ticker GOOGL
⚠️  CAUTION - EPS expected to decline 11.5%
P/E expanding from 31.4x to 35.4x

# Vodafone - Turnaround play
$ pe-scanner fetch --ticker VOD
⚠️ TURNAROUND PLAY - Currently loss-making
Analysts expect return to profitability
```

## 📋 Development Status

**Current Phase**: ✅ **COMPLETE** - Production Ready

**Implemented**:
- ✅ All 15 PRD tasks completed (100%)
- ✅ 399 tests passing
- ✅ 82% code coverage
- ✅ Yahoo Finance data fetcher with caching
- ✅ UK stock pence-to-pounds auto-correction
- ✅ Stock split detection
- ✅ P/E compression analysis with signals
- ✅ Fair value scenarios (bear/bull)
- ✅ Portfolio ranking and reporting
- ✅ CLI with analyze/verify/fetch commands
- ✅ Momentum_Squared integration
- ✅ diet103 validation hooks

## 🔗 Related Projects

- **Orchestrator_Project**: Multi-project AI orchestration system (PAI + diet103)
- **Momentum_Squared**: Investment analysis platform with diet103 enhancements
- **Portfolio Management**: Master portfolio tracking and Workflow 9 analysis

## 🚀 Deployment

### Backend (Railway)
**Status**: ✅ Production-ready (Task 39 complete)

```bash
# Quick deploy (15 minutes)
# See DEPLOY_NOW.md for step-by-step guide

1. Create Railway project from GitHub
2. Add Redis service (free tier)
3. Set environment variables
4. Deploy automatically builds and runs

# Full details in RAILWAY_DEPLOYMENT.md
```

**Cost**: ~$5/month (or FREE with Railway credits)

### Frontend (Vercel)
**Status**: 🚧 Task 40 (pending)
- Next.js 15 app in `web/` directory
- Deploy to Vercel (free Hobby plan)
- Set `NEXT_PUBLIC_API_URL` to Railway URL

---

## 📚 Documentation

- **PRD**: `.taskmaster/docs/prd.txt` - Complete product requirements
- **Tasks**: `.taskmaster/tasks/` - Development roadmap  
- **Deployment**: `RAILWAY_DEPLOYMENT.md` - Full deployment guide
- **Quick Deploy**: `DEPLOY_NOW.md` - 15-minute setup
- **Methodology**: Reference implementation at `/Users/tomeldridge/Momentum_Squared/analysis/PE_Compression_Analysis_Corrected_Nov2024.md`

## 🧪 Testing Strategy

- **Unit Tests**: P/E calculations, data corrections, fair value scenarios
- **Integration Tests**: End-to-end portfolio analysis
- **Validation Tests**: Verify against manual calculations (HOOD, NFLX cases)
- **Edge Cases**: Missing data, extreme values, delisted stocks

## 🎓 P/E Compression Methodology

### What is P/E Compression?
```
Compression % = ((Trailing P/E - Forward P/E) / Trailing P/E) × 100
```

- **Positive compression** = Forward P/E is lower → Market expects earnings to GROW
- **Negative compression** = Forward P/E is higher → Market expects earnings to DECLINE

### Example: HOOD (Robinhood)
```
Trailing P/E: 73.27 (based on 2024 actual EPS $1.56)
Forward P/E: 156.58 (based on forward EPS $0.73)
Compression: (73.27 - 156.58) / 73.27 = -113.70%

Interpretation: Market expects 53% earnings collapse
Signal: SELL ✅ (confirmed with actual financials)
```

## 🛠️ Tech Stack

**Core**:
- Python 3.13+ (tested with 3.13.5)
- pandas>=2.0.0, numpy>=1.24.0 (data analysis)
- yfinance>=0.2.28 (Yahoo Finance API)
- pydantic>=2.0.0 (data validation)

**Reporting**:
- rich>=13.0.0 (terminal formatting)
- tabulate>=0.9.0 (table generation)
- click>=8.0.0 (CLI framework)

**Testing**:
- pytest>=7.4.0, pytest-cov>=4.1.0
- 399 tests, 82% coverage

**Performance**:
- ThreadPoolExecutor for concurrent fetching
- In-memory caching with TTL
- 25 tickers analyzed in <2 seconds

**Project Management**:
- Task Master AI (task-driven development)

## 🤝 Contributing

StockSignal is in active development. See `.taskmaster/tasks/` for current development priorities.

---

**Created**: November 29, 2025  
**Architecture Pattern**: PAI Global Layer + diet103 Local Layer  
**Reference Analysis**: Momentum Squared PE Compression Analysis (Nov 2024)
