# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Cursor, Copilot, etc.) when working with code in this repository. It follows the [AGENTS.md standard](https://agents.md/).

## Project Overview

**PE Scanner** - Stock Valuation Made Simple

A free tool (with Pro tier) that analyzes stocks using P/E compression to identify overvalued positions. Features tiered analysis (VALUE, GROWTH, HYPER_GROWTH), shareable headlines, and portfolio scanning.

- **Target Market**: UK investors (ISA/SIPP), retail investors, portfolio managers
- **Revenue Model**: Freemium (Free 10/day → Pro £25/mo → Premium £49/mo)
- **Tech Stack**: Flask + Python (backend), Next.js 15 + Vercel (frontend), Railway (hosting)
- **Launch Timeline**: 6 weeks to public launch
- **Budget**: £15/mo (MVP costs)

## Essential Commands

### Development
```bash
# Backend (Flask)
python -m pytest                 # Run all tests
python -m pytest --cov           # Run tests with coverage
python -m pytest tests/unit/     # Run unit tests only
python -m pe_scanner.cli analyze --portfolio portfolios/example_isa.csv

# Frontend (Next.js - future)
npm run dev                      # Start dev server (port 3000)
npm run build                    # Production build
npm run lint                     # Run ESLint
```

### Task Master
```bash
task-master list                    # View all tasks
task-master next                    # Get next task to work on
task-master show <id>               # View task details (use commas for multiple)
task-master set-status --id=<id> --status=done  # Mark complete
task-master expand --id=<id> --research         # Break down task
task-master update-subtask --id=<id> --prompt="notes"  # Add notes
```

## Architecture

### Tech Stack

**Backend (Current - Railway)**
- **Flask**: REST API (v2.0 complete)
- **Python 3.11+**: Core language
- **yfinance**: Market data fetching
- **pandas/numpy**: Data processing
- **pydantic**: Data validation
- **pytest**: Testing (399 tests, 82% coverage)

**Frontend (Planned - Vercel)**
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS
- **Resend**: Email service
- **Plausible**: Privacy-friendly analytics

**Infrastructure**
- **Railway**: Backend API hosting (~£5/mo)
- **Redis**: Rate limiting (Railway free tier)
- **Vercel**: Frontend hosting (free hobby plan)
- **Domain**: pe-scanner.com (~£10/year)

### Directory Structure
```
PE_Scanner/
├── src/pe_scanner/
│   ├── analysis/              # Analysis engines
│   │   ├── anchoring.py      # "What Would Have To Be True" engine
│   │   ├── classification.py # VALUE/GROWTH/HYPER_GROWTH classifier
│   │   ├── compression.py    # P/E compression calculator
│   │   ├── fair_value.py     # Bear/bull scenarios
│   │   ├── growth.py         # PEG ratio analysis (GROWTH mode)
│   │   ├── headlines.py      # Viral headline generator
│   │   ├── hyper_growth.py   # P/S + Rule of 40 (HYPER_GROWTH)
│   │   └── router.py         # Tiered analysis router
│   ├── api/                   # REST API v2.0
│   │   ├── app.py            # Flask application
│   │   ├── schema.py         # Pydantic models
│   │   └── service.py        # Business logic
│   ├── data/                  # Data layer
│   │   ├── fetcher.py        # Yahoo Finance integration
│   │   ├── corrector.py      # UK stock corrections (pence→pounds)
│   │   └── validator.py      # Data quality checks
│   ├── portfolios/            # Portfolio analysis
│   │   ├── loader.py         # CSV/JSON parsing
│   │   ├── ranker.py         # Signal prioritization
│   │   └── reporter.py       # Markdown report generation
│   ├── integration/           # External integrations
│   │   ├── hooks.py          # diet103 validation hooks
│   │   └── momentum_squared.py # Momentum_Squared compatibility
│   ├── cli.py                # Command-line interface
│   └── verification.py       # Manual verification support
├── tests/
│   ├── unit/                 # Unit tests (comprehensive)
│   ├── integration/          # Integration tests
│   └── conftest.py           # pytest configuration
├── portfolios/               # Example portfolios
│   └── example_isa.csv      # ISA portfolio example
├── .taskmaster/             # Task Master config
│   ├── docs/
│   │   ├── prd.txt          # Product requirements
│   │   └── web_launch_strategy.md  # Launch strategy
│   └── tasks/
│       └── tasks.json       # Task tracking (58 tasks)
├── .cursor/
│   ├── rules/               # Cursor IDE rules
│   └── skills/              # AI-assisted skills (ported from Pirouette)
└── requirements.txt         # Python dependencies
```

## Analysis Engine

The core analysis engine uses a **3-tier approach** based on P/E ratios:

### 1. **VALUE Mode** (P/E < 25)
- **Primary Metric**: P/E Compression
- **Formula**: `((Trailing PE - Forward PE) / Trailing PE) × 100`
- **Signals**: 
  - Negative compression → SELL (market expects decline)
  - Positive compression → BUY (market expects growth)
- **Fair Value**: Bull/bear scenarios using forward EPS

### 2. **GROWTH Mode** (25 ≤ P/E ≤ 50)
- **Primary Metric**: PEG Ratio
- **Formula**: `P/E ÷ Earnings Growth %`
- **Signals**:
  - PEG < 1.0 → BUY (undervalued relative to growth)
  - PEG > 2.0 → SELL (overvalued)
  - 1.0 ≤ PEG ≤ 2.0 → HOLD

### 3. **HYPER_GROWTH Mode** (P/E > 50 or unprofitable)
- **Primary Metrics**: Price/Sales + Rule of 40
- **Rule of 40**: `Revenue Growth % + Profit Margin %`
- **Signals**:
  - P/S < 5 AND Rule of 40 ≥ 40 → BUY
  - P/S > 15 OR Rule of 40 < 20 → SELL

### Supporting Features
- **Headline Generator**: Viral-optimized, shareable headlines for Twitter/LinkedIn
- **Anchoring Engine**: "What Would Have To Be True" memorable statements
- **Data Quality**: UK stock corrections, split detection, staleness checks
- **Share URLs**: Pre-formatted Twitter, LinkedIn, copy-text

## API v2.0

**Main Endpoint:** `GET /api/analyze/<ticker>`

### Query Parameters
- `include_anchor` (bool): Include anchoring statement
- `include_headline` (bool): Include shareable headline
- `include_share_urls` (bool): Include Twitter/LinkedIn URLs
- `base_url` (string): Base URL for share links

### Response Schema
```json
{
  "ticker": "HOOD",
  "analysis_mode": "VALUE",
  "metrics": {
    "trailing_pe": 47.62,
    "forward_pe": 156.58,
    "compression_pct": -113.7,
    "current_price": 35.21
  },
  "signal": "SELL",
  "confidence": "high",
  "anchor": "HOOD would need to 2.5x profits...",
  "headline": "🚨 HOOD is priced like it's going bankrupt",
  "share_urls": {
    "twitter": "https://twitter.com/intent/tweet?text=...",
    "linkedin": "https://linkedin.com/feed/?shareActive=true&text=...",
    "copy_text": "🚨 HOOD is priced like it's going bankrupt..."
  },
  "data_quality": {
    "flags": [],
    "uk_corrected": false
  },
  "timestamp": "2024-12-02T10:30:00Z"
}
```

## Task Master Integration

### Configuration
- **Config**: `.taskmaster/config.json`
- **Tasks**: `.taskmaster/tasks/tasks.json` (58 tasks total)
- **PRD**: `.taskmaster/docs/prd.txt`
- **Launch Strategy**: `.taskmaster/docs/web_launch_strategy.md`

### Development Workflow
1. `task-master next` - Get next available task
2. `task-master show <id>` - Review requirements
3. Implement the feature
4. `task-master update-subtask --id=<id> --prompt="notes"` - Log progress
5. `task-master set-status --id=<id> --status=done` - Complete

## Current Status

### Backend (92% Complete)
- [x] Core analysis engine (VALUE/GROWTH/HYPER_GROWTH)
- [x] P/E compression calculator
- [x] PEG ratio analyzer
- [x] P/S + Rule of 40 analyzer
- [x] Headline generator (97% test coverage)
- [x] Anchoring engine (90% test coverage)
- [x] REST API v2.0 with full schema
- [x] Data quality validation
- [x] UK stock corrections
- [x] Portfolio analysis (CLI)
- [x] Comprehensive test suite (399 tests)
- [ ] CLI enhancements (Tasks 23-24 pending)

### Frontend (0% Complete - Tasks 26-58)
- [ ] Next.js 15 project initialization
- [ ] Landing page with ticker search
- [ ] Results display page
- [ ] Share buttons (Twitter/LinkedIn)
- [ ] Email capture modal
- [ ] Portfolio upload interface
- [ ] Pricing page (£25 Pro / £49 Premium)
- [ ] Analytics integration (Plausible)

### Deployment (Not Started)
- [ ] Railway backend deployment
- [ ] Vercel frontend deployment
- [ ] Custom domain setup (pe-scanner.com)
- [ ] Rate limiting with Redis

## Environment Variables

Required in `.env` (CLI/Railway):
```bash
# Optional: API Keys (for specific providers)
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
# ... (other providers as needed)

# Railway Production
REDIS_URL=redis://...
RESEND_API_KEY=re_...
ALLOWED_ORIGINS=https://pe-scanner.com,https://www.pe-scanner.com
```

See `assets/env.example` for template.

## Cursor Skills

Available in `.cursor/skills/` (ported from Pirouette):
- `project-scaffolder.md` - Rapid project setup
- `skill-import-assistant.md` - Import from sibling projects
- `scaling-calculator.md` - Cost projections
- `email-touchpoint-mapper.md` - Email strategy
- `prd-progress-tracker.md` - PRD alignment checking

## Success Metrics

### Launch Goals (6 weeks)
- **Week 2**: Frontend MVP live at pe-scanner.com
- **Week 4**: Email capture + portfolio upload functional
- **Week 6**: Public launch (Product Hunt, Reddit, Twitter)

### Revenue Targets
- **Month 1**: 100 free signups (validation)
- **Month 2**: 500 signups + 10% conversion = 50 paid users = £1,250 MRR
- **Month 6**: 5,000 signups + 500 paid users = £12,500 MRR
- **Break-even**: 1 customer at £25/mo (covers £15/mo infrastructure)

## Important Notes

### UK English
All content should use UK English spelling and grammar.

### Performance Targets
- Analysis time: < 5 seconds per ticker
- Portfolio analysis: < 2 minutes for 20 stocks
- API response time: < 500ms (excluding data fetch)

### Security
- No user data stored (stateless for free tier)
- Rate limiting via Redis (3/day anon, 10/day free, unlimited Pro)
- API keys never exposed to client
- CORS properly configured

### Pricing Strategy
- **Free**: 10 tickers/day (with signup), 3/day (anonymous)
- **Pro**: £25/mo - Unlimited + portfolio upload
- **Premium**: £49/mo - API access + webhooks
- **Annual**: 20% discount (£240/yr Pro, £470/yr Premium)

## References

- **PRD**: `.taskmaster/docs/prd.txt`
- **Launch Strategy**: `.taskmaster/docs/web_launch_strategy.md`
- **Gap Analysis**: `.taskmaster/docs/gap_analysis_summary.md`
- **API Docs**: `API_DOCUMENTATION.md`
- **Changelog**: `Changelog.md` (comprehensive history)
- **Quick Start**: `QUICK_START.md`

---

*Built with ❤️ for investors who deserve better valuation tools*

