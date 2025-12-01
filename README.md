# PE Scanner

**P/E Compression Analysis Tool for Portfolio Management**

PE Scanner is a Python-based investment analysis tool that identifies opportunities through P/E (Price-to-Earnings) compression analysis. It automatically screens portfolios to find stocks where market expectations diverge significantly from current valuations.

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

### PAI/diet103 Integration
PE Scanner follows the Orchestrator_Project architecture patterns:
- **PAI Global Layer**: Cross-project template sharing and orchestration
- **diet103 Local Layer**: Project-specific hooks and validation
- **Shared Patterns**: Data pipeline consistency with Momentum_Squared

### Project Structure
```
PE_Scanner/
├── src/
│   └── pe_scanner/
│       ├── analysis/          # P/E compression, fair value calculations
│       ├── data/              # Yahoo Finance integration, validation
│       ├── portfolios/        # Portfolio loading, ranking, reporting
│       └── cli.py             # Command-line interface
├── tests/                     # Test suite
├── scripts/                   # Analysis scripts
├── portfolios/                # Portfolio CSV files (ISA, SIPP, Wishlist)
├── outputs/                   # Generated reports
└── .taskmaster/               # Task Master project management
```

## 🚀 Quick Start

### Installation

```bash
cd /Users/tomeldridge/PE_Scanner
source venv/bin/activate
pip install -e .
```

### Basic Usage

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

## 📚 Documentation

- **PRD**: `.taskmaster/docs/prd.txt` - Complete product requirements
- **Tasks**: `.taskmaster/tasks/` - Development roadmap
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

PE Scanner is in active development. See `.taskmaster/tasks/` for current development priorities.

---

**Created**: November 29, 2025  
**Architecture Pattern**: PAI Global Layer + diet103 Local Layer  
**Reference Analysis**: Momentum Squared PE Compression Analysis (Nov 2024)
