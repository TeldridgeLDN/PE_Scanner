"""
Unit tests for Command Line Interface
"""

import pytest
from click.testing import CliRunner
from pathlib import Path

from pe_scanner.cli import cli, load_config


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config file."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
data:
  source: yahoo_finance
  cache_ttl: 3600
analysis:
  compression_thresholds:
    strong_buy: 50
    buy: 20
""")
    return config_path


# =============================================================================
# load_config Tests
# =============================================================================


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_existing_config(self, temp_config):
        """Test loading existing config file."""
        config = load_config(str(temp_config))
        assert "data" in config
        assert config["data"]["source"] == "yahoo_finance"

    def test_load_missing_config(self, tmp_path):
        """Test loading non-existent config returns empty dict."""
        config = load_config(str(tmp_path / "nonexistent.yaml"))
        assert config == {}


# =============================================================================
# CLI Group Tests
# =============================================================================


class TestCLIGroup:
    """Tests for main CLI group."""

    def test_help(self, runner):
        """Test --help shows usage."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PE Scanner" in result.output
        assert "analyze" in result.output
        assert "verify" in result.output

    def test_version(self, runner):
        """Test --version shows version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "pe-scanner" in result.output


# =============================================================================
# Analyze Command Tests
# =============================================================================


class TestAnalyzeCommand:
    """Tests for analyze command."""

    def test_analyze_help(self, runner):
        """Test analyze --help."""
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "--portfolio" in result.output
        assert "--all" in result.output
        assert "--output" in result.output

    def test_analyze_no_args_error(self, runner):
        """Test analyze without args shows error."""
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code == 1
        assert "Specify --portfolio or --all" in result.output

    def test_analyze_portfolio_choice(self, runner):
        """Test portfolio choices are validated."""
        # Valid choice
        result = runner.invoke(cli, ["analyze", "--help"])
        # Click shows choices in lowercase
        assert "isa" in result.output.lower()
        assert "sipp" in result.output.lower()
        assert "wishlist" in result.output.lower()


# =============================================================================
# Verify Command Tests
# =============================================================================


class TestVerifyCommand:
    """Tests for verify command."""

    def test_verify_help(self, runner):
        """Test verify --help."""
        result = runner.invoke(cli, ["verify", "--help"])
        assert result.exit_code == 0
        assert "--ticker" in result.output

    def test_verify_requires_ticker(self, runner):
        """Test verify requires --ticker."""
        result = runner.invoke(cli, ["verify"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()


# =============================================================================
# Fetch Command Tests
# =============================================================================


class TestFetchCommand:
    """Tests for fetch command."""

    def test_fetch_help(self, runner):
        """Test fetch --help."""
        result = runner.invoke(cli, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--ticker" in result.output
        assert "--no-cache" in result.output

    def test_fetch_requires_ticker(self, runner):
        """Test fetch requires --ticker."""
        result = runner.invoke(cli, ["fetch"])
        assert result.exit_code != 0


# =============================================================================
# Status Command Tests
# =============================================================================


class TestStatusCommand:
    """Tests for status command."""

    def test_status_runs(self, runner):
        """Test status command runs."""
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "PE Scanner Status" in result.output
        assert "Version" in result.output

    def test_status_shows_config(self, runner):
        """Test status shows config status."""
        result = runner.invoke(cli, ["status"])
        assert "Config" in result.output


# =============================================================================
# Cache Command Tests
# =============================================================================


class TestCacheCommand:
    """Tests for cache command."""

    def test_cache_stats(self, runner):
        """Test cache shows stats."""
        result = runner.invoke(cli, ["cache"])
        assert result.exit_code == 0
        assert "entries" in result.output.lower()

    def test_cache_clear(self, runner):
        """Test cache --clear."""
        result = runner.invoke(cli, ["cache", "--clear"])
        assert result.exit_code == 0
        assert "cleared" in result.output.lower()


# =============================================================================
# Integration Tests
# =============================================================================


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_verbose_flag(self, runner):
        """Test -v verbose flag is accepted."""
        result = runner.invoke(cli, ["-v", "status"])
        assert result.exit_code == 0

    def test_config_option(self, runner, temp_config):
        """Test -c config option."""
        result = runner.invoke(cli, ["-c", str(temp_config), "status"])
        assert result.exit_code == 0


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_command(self, runner):
        """Test invalid command shows error."""
        result = runner.invoke(cli, ["invalid_command"])
        assert result.exit_code != 0

    def test_invalid_portfolio(self, runner):
        """Test invalid portfolio choice."""
        result = runner.invoke(cli, ["analyze", "--portfolio", "INVALID"])
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

