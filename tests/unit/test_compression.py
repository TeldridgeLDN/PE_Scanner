"""
Unit tests for P/E Compression Calculation Module
"""

import pytest

from pe_scanner.analysis.compression import (
    CompressionConfig,
    CompressionResult,
    CompressionSignal,
    analyze_batch,
    analyze_compression,
    calculate_compression,
    interpret_signal,
    rank_by_compression,
)


# =============================================================================
# calculate_compression Tests
# =============================================================================


class TestCalculateCompression:
    """Tests for calculate_compression function."""

    def test_positive_compression(self):
        """Test positive compression (market expects growth)."""
        # Forward P/E lower than trailing = earnings growth expected
        compression, growth = calculate_compression(40.81, 11.96)
        assert compression > 0
        assert compression == pytest.approx(70.69, rel=0.01)

    def test_negative_compression(self):
        """Test negative compression (market expects decline)."""
        # Forward P/E higher than trailing = earnings decline expected
        compression, growth = calculate_compression(73.27, 156.58)
        assert compression < 0
        assert compression == pytest.approx(-113.70, rel=0.01)

    def test_no_compression(self):
        """Test zero compression (equal P/E ratios)."""
        compression, growth = calculate_compression(20.0, 20.0)
        assert compression == 0.0

    def test_implied_growth_calculation(self):
        """Test implied growth with EPS values."""
        compression, growth = calculate_compression(
            trailing_pe=73.27,
            forward_pe=156.58,
            trailing_eps=1.56,
            forward_eps=0.73,
        )
        # Growth = (0.73 - 1.56) / 1.56 * 100 = -53.21%
        assert growth == pytest.approx(-53.21, rel=0.01)

    def test_implied_growth_positive(self):
        """Test positive implied growth."""
        compression, growth = calculate_compression(
            trailing_pe=20.0,
            forward_pe=10.0,
            trailing_eps=5.0,
            forward_eps=10.0,
        )
        # Growth = (10 - 5) / 5 * 100 = 100%
        assert growth == 100.0

    def test_implied_growth_without_eps(self):
        """Test implied growth is zero when EPS not provided."""
        compression, growth = calculate_compression(40.0, 20.0)
        assert growth == 0.0

    def test_invalid_trailing_pe_zero(self):
        """Test ValueError for zero trailing P/E."""
        with pytest.raises(ValueError, match="positive"):
            calculate_compression(0.0, 20.0)

    def test_invalid_trailing_pe_negative(self):
        """Test ValueError for negative trailing P/E."""
        with pytest.raises(ValueError, match="positive"):
            calculate_compression(-10.0, 20.0)

    def test_invalid_forward_pe_zero(self):
        """Test ValueError for zero forward P/E."""
        with pytest.raises(ValueError, match="positive"):
            calculate_compression(20.0, 0.0)

    def test_invalid_forward_pe_negative(self):
        """Test ValueError for negative forward P/E."""
        with pytest.raises(ValueError, match="positive"):
            calculate_compression(20.0, -10.0)


# =============================================================================
# interpret_signal Tests
# =============================================================================


class TestInterpretSignal:
    """Tests for interpret_signal function."""

    def test_strong_buy_signal(self):
        """Test STRONG_BUY for high positive compression."""
        signal, confidence = interpret_signal(70.0)
        assert signal == CompressionSignal.STRONG_BUY
        assert confidence == "high"

    def test_buy_signal(self):
        """Test BUY for moderate positive compression."""
        signal, confidence = interpret_signal(30.0)
        assert signal == CompressionSignal.BUY
        assert confidence == "medium"

    def test_hold_signal_positive(self):
        """Test HOLD for low positive compression."""
        signal, confidence = interpret_signal(15.0)
        assert signal == CompressionSignal.HOLD
        assert confidence == "low"

    def test_hold_signal_negative(self):
        """Test HOLD for low negative compression."""
        signal, confidence = interpret_signal(-15.0)
        assert signal == CompressionSignal.HOLD
        assert confidence == "low"

    def test_sell_signal(self):
        """Test SELL for moderate negative compression."""
        signal, confidence = interpret_signal(-30.0)
        assert signal == CompressionSignal.SELL
        assert confidence == "medium"

    def test_strong_sell_signal(self):
        """Test STRONG_SELL for high negative compression."""
        signal, confidence = interpret_signal(-70.0)
        assert signal == CompressionSignal.STRONG_SELL
        assert confidence == "high"

    def test_data_error_with_severe_flags(self):
        """Test DATA_ERROR when severe quality issues present."""
        signal, confidence = interpret_signal(
            50.0,
            data_quality_flags=["Stock split error detected"],
        )
        assert signal == CompressionSignal.DATA_ERROR
        assert confidence == "low"

    def test_confidence_reduced_with_warnings(self):
        """Test confidence is reduced with data quality warnings."""
        signal, confidence = interpret_signal(
            70.0,
            data_quality_flags=["Minor warning"],
        )
        # Should still be STRONG_BUY but confidence reduced
        assert signal == CompressionSignal.STRONG_BUY
        assert confidence == "medium"  # Reduced from high

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        # With higher threshold, 30% compression is now HOLD
        signal, confidence = interpret_signal(
            30.0,
            thresholds={"compression_signal": 40.0, "high_compression": 70.0},
        )
        assert signal == CompressionSignal.HOLD


# =============================================================================
# analyze_compression Tests
# =============================================================================


class TestAnalyzeCompression:
    """Tests for analyze_compression function."""

    def test_hood_example(self):
        """Test HOOD example from PRD."""
        result = analyze_compression(
            ticker="HOOD",
            trailing_pe=73.27,
            forward_pe=156.58,
            trailing_eps=1.56,
            forward_eps=0.73,
        )
        assert result.ticker == "HOOD"
        assert result.compression_pct == pytest.approx(-113.70, rel=0.01)
        assert result.implied_growth_pct == pytest.approx(-53.21, rel=0.01)
        assert result.signal == CompressionSignal.STRONG_SELL

    def test_ora_example(self):
        """Test ORA.PA example from PRD."""
        result = analyze_compression(
            ticker="ORA.PA",
            trailing_pe=40.81,
            forward_pe=11.96,
        )
        assert result.ticker == "ORA.PA"
        assert result.compression_pct == pytest.approx(70.69, rel=0.01)
        assert result.signal == CompressionSignal.STRONG_BUY
        assert result.confidence == "high"

    def test_invalid_trailing_pe(self):
        """Test handling of invalid trailing P/E."""
        result = analyze_compression(
            ticker="BAD",
            trailing_pe=0.0,
            forward_pe=20.0,
        )
        assert result.signal == CompressionSignal.DATA_ERROR
        assert result.confidence == "low"
        assert len(result.warnings) > 0

    def test_invalid_forward_pe(self):
        """Test handling of invalid forward P/E."""
        result = analyze_compression(
            ticker="BAD",
            trailing_pe=20.0,
            forward_pe=-5.0,
        )
        assert result.signal == CompressionSignal.DATA_ERROR
        assert "Invalid forward P/E" in result.warnings[0]

    def test_extreme_compression_warning(self):
        """Test warning for extreme compression."""
        result = analyze_compression(
            ticker="EXTREME",
            trailing_pe=10.0,
            forward_pe=100.0,  # -900% compression
        )
        assert any("extreme" in w.lower() for w in result.warnings)

    def test_extreme_growth_warning(self):
        """Test warning for extreme implied growth."""
        result = analyze_compression(
            ticker="GROWTH",
            trailing_pe=20.0,
            forward_pe=10.0,
            trailing_eps=1.0,
            forward_eps=5.0,  # 400% growth
        )
        assert any("extreme" in w.lower() for w in result.warnings)

    def test_data_quality_flags_passed_through(self):
        """Test data quality flags are included in warnings."""
        result = analyze_compression(
            ticker="TEST",
            trailing_pe=20.0,
            forward_pe=15.0,
            data_quality_flags=["UK stock correction applied"],
        )
        assert "UK stock correction applied" in result.warnings


# =============================================================================
# CompressionResult Tests
# =============================================================================


class TestCompressionResult:
    """Tests for CompressionResult dataclass."""

    def test_is_buy_strong_buy(self):
        """Test is_buy for STRONG_BUY signal."""
        result = CompressionResult(
            ticker="TEST",
            trailing_pe=20.0,
            forward_pe=10.0,
            compression_pct=50.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.STRONG_BUY,
            confidence="high",
        )
        assert result.is_buy is True
        assert result.is_sell is False

    def test_is_buy_regular_buy(self):
        """Test is_buy for BUY signal."""
        result = CompressionResult(
            ticker="TEST",
            trailing_pe=20.0,
            forward_pe=15.0,
            compression_pct=25.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.BUY,
            confidence="medium",
        )
        assert result.is_buy is True

    def test_is_sell_strong_sell(self):
        """Test is_sell for STRONG_SELL signal."""
        result = CompressionResult(
            ticker="TEST",
            trailing_pe=20.0,
            forward_pe=50.0,
            compression_pct=-150.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.STRONG_SELL,
            confidence="high",
        )
        assert result.is_sell is True
        assert result.is_buy is False

    def test_is_actionable(self):
        """Test is_actionable property."""
        buy_result = CompressionResult(
            ticker="BUY",
            trailing_pe=20.0,
            forward_pe=10.0,
            compression_pct=50.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.BUY,
            confidence="high",
        )
        assert buy_result.is_actionable is True

        hold_result = CompressionResult(
            ticker="HOLD",
            trailing_pe=20.0,
            forward_pe=18.0,
            compression_pct=10.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.HOLD,
            confidence="low",
        )
        assert hold_result.is_actionable is False


# =============================================================================
# Batch Analysis Tests
# =============================================================================


class TestAnalyzeBatch:
    """Tests for analyze_batch function."""

    def test_batch_analysis(self):
        """Test batch analysis of multiple tickers."""
        data = [
            {"ticker": "HOOD", "trailing_pe": 73.27, "forward_pe": 156.58},
            {"ticker": "ORA.PA", "trailing_pe": 40.81, "forward_pe": 11.96},
        ]
        results = analyze_batch(data)

        assert len(results) == 2
        assert results[0].ticker == "HOOD"
        assert results[1].ticker == "ORA.PA"

    def test_batch_with_invalid_data(self):
        """Test batch handles invalid data gracefully."""
        data = [
            {"ticker": "GOOD", "trailing_pe": 20.0, "forward_pe": 15.0},
            {"ticker": "BAD", "trailing_pe": None, "forward_pe": 15.0},
        ]
        results = analyze_batch(data)

        assert len(results) == 2
        assert results[0].signal != CompressionSignal.DATA_ERROR
        assert results[1].signal == CompressionSignal.DATA_ERROR

    def test_batch_empty_list(self):
        """Test batch with empty list."""
        results = analyze_batch([])
        assert results == []


# =============================================================================
# Ranking Tests
# =============================================================================


class TestRankByCompression:
    """Tests for rank_by_compression function."""

    def test_rank_default_descending(self):
        """Test default ranking (highest compression first)."""
        results = [
            CompressionResult("A", 20, 30, -50, 0, CompressionSignal.SELL, "high"),
            CompressionResult("B", 20, 10, 50, 0, CompressionSignal.BUY, "high"),
            CompressionResult("C", 20, 18, 10, 0, CompressionSignal.HOLD, "low"),
        ]
        ranked = rank_by_compression(results)

        assert ranked[0].ticker == "B"  # +50% (best buy)
        assert ranked[1].ticker == "C"  # +10%
        assert ranked[2].ticker == "A"  # -50% (worst)

    def test_rank_ascending(self):
        """Test ascending ranking (lowest compression first)."""
        results = [
            CompressionResult("A", 20, 30, -50, 0, CompressionSignal.SELL, "high"),
            CompressionResult("B", 20, 10, 50, 0, CompressionSignal.BUY, "high"),
        ]
        ranked = rank_by_compression(results, ascending=True)

        assert ranked[0].ticker == "A"  # -50% (sells first)
        assert ranked[1].ticker == "B"  # +50%


# =============================================================================
# PRD Reference Examples
# =============================================================================


class TestPRDExamples:
    """Tests verifying examples from the PRD."""

    def test_hood_verified_sell_signal(self):
        """
        HOOD (Robinhood) - Verified Sell Signal from PRD.

        Current Price: $114.30
        2024 Actual EPS: $1.56
        Forward EPS (FY1): $0.73
        Trailing P/E (2024 actual): 73.27
        Forward P/E: 156.58
        Compression: -113.70%
        Signal: SELL (high confidence)
        """
        result = analyze_compression(
            ticker="HOOD",
            trailing_pe=73.27,
            forward_pe=156.58,
            trailing_eps=1.56,
            forward_eps=0.73,
        )

        assert result.compression_pct == pytest.approx(-113.70, rel=0.01)
        assert result.implied_growth_pct == pytest.approx(-53.21, rel=0.01)
        assert result.signal in (CompressionSignal.STRONG_SELL, CompressionSignal.SELL)

    def test_ora_buy_opportunity(self):
        """
        ORA.PA (Orange) - Buy Opportunity from PRD.

        Trailing P/E: 40.81
        Forward P/E: 11.96
        Compression: +70.69%
        Signal: BUY (best ISA opportunity)
        """
        result = analyze_compression(
            ticker="ORA.PA",
            trailing_pe=40.81,
            forward_pe=11.96,
        )

        assert result.compression_pct == pytest.approx(70.69, rel=0.01)
        assert result.signal == CompressionSignal.STRONG_BUY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



