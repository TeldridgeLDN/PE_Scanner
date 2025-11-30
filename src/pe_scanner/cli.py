"""
PE Scanner Command Line Interface

Provides commands for portfolio analysis, manual verification,
and report generation.

Usage:
    pe-scanner analyze --portfolio ISA
    pe-scanner analyze --all
    pe-scanner verify --ticker HOOD
    pe-scanner analyze --portfolio SIPP --output reports/sipp_analysis.md
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Package imports
from pe_scanner import __version__
from pe_scanner.analysis.compression import analyze_batch as compression_batch
from pe_scanner.analysis.fair_value import analyze_fair_value_batch
from pe_scanner.data.fetcher import batch_fetch, clear_cache, get_cache_stats
from pe_scanner.data.validator import validate_batch, filter_usable
from pe_scanner.data.corrector import apply_corrections
from pe_scanner.portfolios.loader import (
    load_portfolio,
    load_all_portfolios,
    PortfolioType,
)
from pe_scanner.portfolios.ranker import rank_portfolio
from pe_scanner.portfolios.reporter import (
    generate_report,
    generate_summary,
    save_report,
    print_to_console,
    ReportConfig,
    ReportFormat,
)
from pe_scanner.verification import (
    create_verification_checklist,
    format_checklist_markdown,
)

console = Console()
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Loading
# =============================================================================


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


# =============================================================================
# Main CLI Group
# =============================================================================


@click.group()
@click.version_option(version=__version__, prog_name="pe-scanner")
@click.option("--config", "-c", type=click.Path(), default="config.yaml", help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, config: str, verbose: bool, debug: bool) -> None:
    """
    PE Scanner - P/E Compression Analysis Tool

    Analyze portfolio positions for P/E compression opportunities.
    Identifies undervalued (buy) and overvalued (sell) positions based
    on trailing vs forward P/E ratios.

    Examples:
        pe-scanner analyze --portfolio ISA
        pe-scanner analyze --all --output report.md
        pe-scanner verify --ticker HOOD
        pe-scanner fetch --ticker AAPL
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["config"] = load_config(config)
    ctx.obj["verbose"] = verbose

    # Setup logging
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s")
    elif verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")


# =============================================================================
# Analyze Command
# =============================================================================


@cli.command()
@click.option(
    "--portfolio",
    "-p",
    type=click.Choice(["ISA", "SIPP", "WISHLIST"], case_sensitive=False),
    help="Portfolio to analyze",
)
@click.option("--all", "analyze_all", is_flag=True, help="Analyze all portfolios")
@click.option("--output", "-o", type=click.Path(), help="Output file path for report")
@click.option(
    "--format", "-f",
    type=click.Choice(["markdown", "json", "text", "console"]),
    default="console",
    help="Output format",
)
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
@click.option("--methodology", is_flag=True, help="Include methodology section in report")
@click.pass_context
def analyze(
    ctx: click.Context,
    portfolio: Optional[str],
    analyze_all: bool,
    output: Optional[str],
    format: str,
    no_cache: bool,
    methodology: bool,
) -> None:
    """
    Analyze portfolio(s) for P/E compression opportunities.

    Examples:
        pe-scanner analyze --portfolio ISA
        pe-scanner analyze --all --output reports/full_analysis.md
        pe-scanner analyze -p SIPP -f markdown -o sipp.md
    """
    if not portfolio and not analyze_all:
        console.print("[red]Error:[/red] Specify --portfolio or --all")
        sys.exit(1)

    config = ctx.obj.get("config", {})
    verbose = ctx.obj.get("verbose", False)

    try:
        # Load portfolios
        if analyze_all:
            console.print("📂 Loading all portfolios...")
            portfolios = load_all_portfolios(config)
            if not portfolios:
                console.print("[red]Error:[/red] No portfolios found")
                sys.exit(1)
            # Merge all positions
            all_positions = []
            for p in portfolios:
                all_positions.extend(p.positions)
            tickers = list(set(pos.ticker for pos in all_positions))
            portfolio_name = "All Portfolios"
        else:
            portfolio_type = PortfolioType[portfolio.upper()]
            console.print(f"📂 Loading {portfolio} portfolio...")
            p = load_portfolio(portfolio_type, config)
            if not p or not p.positions:
                console.print(f"[red]Error:[/red] Could not load {portfolio} portfolio")
                sys.exit(1)
            tickers = [pos.ticker for pos in p.positions]
            portfolio_name = f"{portfolio} Portfolio"

        console.print(f"   Found [cyan]{len(tickers)}[/cyan] positions")

        # Fetch market data
        console.print("\n📡 Fetching market data...")
        fetch_result = batch_fetch(tickers, use_cache=not no_cache)

        if fetch_result.errors:
            console.print(f"   ⚠️  {len(fetch_result.errors)} fetch errors")
            if verbose:
                for ticker, error in list(fetch_result.errors.items())[:5]:
                    console.print(f"      {ticker}: {error}")

        console.print(f"   ✅ Retrieved data for [cyan]{len(fetch_result.data)}[/cyan] tickers")

        # Apply corrections (UK stocks, etc.)
        console.print("\n🔧 Applying data corrections...")
        corrected_data = []
        for md in fetch_result.data.values():
            correction = apply_corrections(md, auto_correct=True)
            corrected_data.append(correction.corrected_data)

        # Validate data
        console.print("✅ Validating data quality...")
        validation_results = validate_batch(corrected_data, config)
        usable = filter_usable(validation_results)
        console.print(f"   {len(usable)} positions pass quality checks")

        # Prepare analysis input
        compression_input = []
        fair_value_input = []

        for md in corrected_data:
            if md.trailing_pe and md.forward_pe:
                compression_input.append({
                    "ticker": md.ticker,
                    "trailing_pe": md.trailing_pe,
                    "forward_pe": md.forward_pe,
                    "trailing_eps": md.trailing_eps,
                    "forward_eps": md.forward_eps,
                })
            if md.current_price and md.forward_eps:
                fair_value_input.append({
                    "ticker": md.ticker,
                    "current_price": md.current_price,
                    "forward_eps": md.forward_eps,
                })

        # Run compression analysis
        console.print("\n📊 Running P/E compression analysis...")
        compressions = compression_batch(compression_input)
        console.print(f"   Analyzed [cyan]{len(compressions)}[/cyan] positions")

        # Run fair value analysis
        console.print("💰 Calculating fair value scenarios...")
        fair_values = analyze_fair_value_batch(fair_value_input)

        # Rank portfolio
        console.print("🏆 Ranking positions...")
        ranking = rank_portfolio(
            compressions,
            fair_values,
            validation_results,
            portfolio_name=portfolio_name,
        )

        # Generate output
        console.print("")

        if format == "console":
            # Print to console
            print_to_console(ranking, verbose=verbose)
        else:
            # Generate report
            report_format = {
                "markdown": ReportFormat.MARKDOWN,
                "json": ReportFormat.JSON,
                "text": ReportFormat.TEXT,
            }.get(format, ReportFormat.MARKDOWN)

            report_config = ReportConfig(
                format=report_format,
                include_methodology=methodology,
            )
            report = generate_report(ranking, report_config)

            if output:
                path = save_report(report, output)
                console.print(f"\n✅ Report saved to: [cyan]{path}[/cyan]")
            else:
                console.print(report.content)

        # Summary stats
        console.print(Panel(
            f"[green]{len(ranking.buy_signals)}[/green] BUY | "
            f"[yellow]{len(ranking.hold_signals)}[/yellow] HOLD | "
            f"[red]{len(ranking.sell_signals)}[/red] SELL",
            title="Analysis Complete",
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if ctx.obj.get("verbose"):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


# =============================================================================
# Verify Command
# =============================================================================


@cli.command()
@click.option("--ticker", "-t", required=True, help="Ticker symbol to verify")
@click.option("--output", "-o", type=click.Path(), help="Save checklist to file")
@click.pass_context
def verify(ctx: click.Context, ticker: str, output: Optional[str]) -> None:
    """
    Manual verification mode for suspicious signals.

    Displays detailed data for manual cross-checking against
    financial statements and alternative data sources.

    Example:
        pe-scanner verify --ticker HOOD
        pe-scanner verify -t BATS.L -o verification.md
    """
    ticker = ticker.upper()
    config = ctx.obj.get("config", {})

    try:
        console.print(f"📡 Fetching data for [cyan]{ticker}[/cyan]...")

        # Fetch data
        fetch_result = batch_fetch([ticker], use_cache=True)

        if ticker not in fetch_result.data:
            error = fetch_result.errors.get(ticker, "Unknown error")
            console.print(f"[red]Error:[/red] Could not fetch data: {error}")
            sys.exit(1)

        md = fetch_result.data[ticker]

        # Apply corrections
        correction = apply_corrections(md, auto_correct=True)
        md = correction.corrected_data

        # Validate
        validations = validate_batch([md], config)
        val_result = validations[0] if validations else None

        # Run analyses
        compression_result = None
        fair_value_result = None

        if md.trailing_pe and md.forward_pe:
            compressions = compression_batch([{
                "ticker": md.ticker,
                "trailing_pe": md.trailing_pe,
                "forward_pe": md.forward_pe,
                "trailing_eps": md.trailing_eps,
                "forward_eps": md.forward_eps,
            }])
            compression_result = compressions[0] if compressions else None

        if md.current_price and md.forward_eps:
            fair_values = analyze_fair_value_batch([{
                "ticker": md.ticker,
                "current_price": md.current_price,
                "forward_eps": md.forward_eps,
            }])
            fair_value_result = fair_values[0] if fair_values else None

        # Create verification checklist
        checklist = create_verification_checklist(
            md,
            val_result,
            compression_result,
            fair_value_result,
        )

        # Format output
        markdown = format_checklist_markdown(checklist)

        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(markdown)
            console.print(f"\n✅ Checklist saved to: [cyan]{path}[/cyan]")
        else:
            console.print(markdown)

        # Summary
        console.print(Panel(
            f"Status: [bold]{checklist.overall_status.value}[/bold]\n"
            f"Warnings: {checklist.warning_count} | Errors: {checklist.error_count}",
            title=f"Verification: {ticker}",
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# =============================================================================
# Fetch Command
# =============================================================================


@cli.command()
@click.option("--ticker", "-t", required=True, help="Ticker symbol to fetch")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@click.pass_context
def fetch(ctx: click.Context, ticker: str, no_cache: bool) -> None:
    """
    Fetch and display market data for a single ticker.

    Useful for debugging and data inspection.

    Example:
        pe-scanner fetch --ticker AAPL
        pe-scanner fetch -t BATS.L --no-cache
    """
    ticker = ticker.upper()

    try:
        console.print(f"📡 Fetching data for [cyan]{ticker}[/cyan]...")

        result = batch_fetch([ticker], use_cache=not no_cache)

        if ticker not in result.data:
            error = result.errors.get(ticker, "Unknown error")
            console.print(f"[red]Error:[/red] {error}")
            sys.exit(1)

        md = result.data[ticker]

        # Display data table
        table = Table(title=f"Market Data: {ticker}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Current Price", f"${md.current_price:.2f}" if md.current_price else "N/A")
        table.add_row("Trailing P/E", f"{md.trailing_pe:.2f}" if md.trailing_pe else "N/A")
        table.add_row("Forward P/E", f"{md.forward_pe:.2f}" if md.forward_pe else "N/A")
        table.add_row("Trailing EPS", f"${md.trailing_eps:.2f}" if md.trailing_eps else "N/A")
        table.add_row("Forward EPS", f"${md.forward_eps:.2f}" if md.forward_eps else "N/A")
        table.add_row("Market Cap", f"${md.market_cap:,.0f}" if md.market_cap else "N/A")
        table.add_row("Fetched At", md.fetched_at.strftime("%Y-%m-%d %H:%M:%S") if md.fetched_at else "N/A")

        console.print(table)

        # Show compression if possible
        if md.trailing_pe and md.forward_pe:
            compression = ((md.trailing_pe - md.forward_pe) / md.trailing_pe) * 100
            color = "green" if compression > 0 else "red"
            console.print(f"\nP/E Compression: [{color}]{compression:+.1f}%[/{color}]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# =============================================================================
# Status Command
# =============================================================================


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """
    Display PE Scanner status and configuration.

    Shows:
    - Configuration file location
    - Portfolio files detected
    - Data cache status
    - API connectivity
    """
    console.print(Panel("[bold]PE Scanner Status[/bold]"))

    # Version
    console.print(f"Version: [cyan]{__version__}[/cyan]")

    # Config file
    config_path = Path(ctx.obj.get("config_path", "config.yaml"))
    if config_path.exists():
        console.print(f"✅ Config: [cyan]{config_path}[/cyan]")
    else:
        console.print(f"⚠️  Config not found: [yellow]{config_path}[/yellow]")

    # Portfolio files
    portfolio_dir = Path("portfolios")
    if portfolio_dir.exists():
        csv_files = list(portfolio_dir.glob("*.csv"))
        json_files = list(portfolio_dir.glob("*.json"))
        console.print(f"✅ Portfolios: [cyan]{len(csv_files)} CSV, {len(json_files)} JSON[/cyan]")
        for f in csv_files + json_files:
            console.print(f"   - {f.name}")
    else:
        console.print("⚠️  Portfolio directory not found")

    # Cache stats
    stats = get_cache_stats()
    console.print(f"📦 Cache: [cyan]{stats.get('size', 0)}[/cyan] entries")

    # Output directory
    output_dir = Path("outputs")
    if output_dir.exists():
        reports = list(output_dir.glob("*.md")) + list(output_dir.glob("*.json"))
        console.print(f"📄 Reports: [cyan]{len(reports)}[/cyan] in outputs/")

    console.print("\n[dim]Run 'pe-scanner --help' for available commands.[/dim]")


# =============================================================================
# Cache Command
# =============================================================================


@cli.command()
@click.option("--clear", is_flag=True, help="Clear the cache")
@click.pass_context
def cache(ctx: click.Context, clear: bool) -> None:
    """
    Manage the data cache.

    Example:
        pe-scanner cache          # Show cache stats
        pe-scanner cache --clear  # Clear the cache
    """
    if clear:
        clear_cache()
        console.print("✅ Cache cleared")
    else:
        stats = get_cache_stats()
        console.print(f"Cache entries: [cyan]{stats.get('size', 0)}[/cyan]")
        console.print(f"Cache hits: [cyan]{stats.get('hits', 0)}[/cyan]")
        console.print(f"Cache misses: [cyan]{stats.get('misses', 0)}[/cyan]")


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
