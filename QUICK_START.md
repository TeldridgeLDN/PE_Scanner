# PE_Scanner Quick Start Guide

**For AI Agents starting work on this project**

## Project Context

**Name**: PE_Scanner  
**Location**: `/Users/tomeldridge/PE_Scanner`  
**Type**: Python-based P/E Compression Analysis Tool  
**Architecture**: PAI Global Layer + diet103 Local Layer  
**Status**: Initialized, ready for Task #1

## Immediate Next Steps

### 1. Setup Development Environment (Task #1)

```bash
cd /Users/tomeldridge/PE_Scanner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"

# Verify installation
python -c "import pandas, numpy, yfinance, pydantic, tabulate, rich; print('✅ All dependencies imported')"
pytest --version
```

### 2. View Current Task

```bash
# See next task
task-master next

# View task details
task-master show 1

# Mark as in-progress when starting
task-master set-status --id=1 --status=in-progress
```

### 3. Key Files to Know

- **PRD**: `.taskmaster/docs/prd.txt` - Complete requirements
- **Tasks**: `.taskmaster/tasks/tasks.json` - All 15 development tasks
- **Config**: `config.yaml` - Application settings
- **Reference**: `/Users/tomeldridge/Momentum_Squared/analysis/PE_Compression_Analysis_Corrected_Nov2024.md`

## Development Workflow

1. `task-master next` - Identify next task
2. `task-master show <id>` - Review task details
3. `task-master set-status --id=<id> --status=in-progress`
4. Implement the task
5. Test implementation
6. `task-master set-status --id=<id> --status=done`
7. Commit changes
8. Repeat

## Project Goals

**Core Mission**: Build a P/E compression analysis tool that:
- Analyzes portfolios in <2 minutes
- Achieves 95%+ accuracy
- Auto-corrects data quality issues
- Provides actionable buy/sell/hold signals

**Reference Test Cases** (from Momentum_Squared):
- ✅ HOOD: -113.70% compression → SELL (verified)
- ❌ NFLX: +89.91% compression → FALSE (stock split error)
- 🟢 ORA.PA: +70.69% compression → BUY

## Architecture Patterns

**From Orchestrator_Project**:
- Task Master AI integration
- Cursor rules for AI assistance
- Cross-project template sharing

**From Momentum_Squared**:
- Portfolio CSV format
- Analysis methodology
- Verified test cases

**diet103 Hooks** (to implement):
- Pre-Analysis Validator
- Data Quality Guardian
- Portfolio Sync Validator
- Results Validator

## Useful Commands

```bash
# Task management
task-master list                    # All tasks
task-master next                    # Next task
task-master show <id>               # Task details
task-master set-status --id=<id> --status=<status>

# Development
pytest                              # Run tests
pytest --cov                        # With coverage
black src/                          # Format code
ruff check src/                     # Lint code

# Documentation
cat .taskmaster/docs/prd.txt       # Read PRD
cat PROJECT_INITIALIZATION.md       # Initialization summary
```

## When You're Ready

Start with: `task-master next`

This will show you Task #1: "Setup Project Environment and Dependencies"

Good luck! 🚀
