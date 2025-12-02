"""
Unit tests for stock classification module.

Tests the classify_stock_type function with various P/E ratios including:
- VALUE stocks (P/E < 25)
- GROWTH stocks (P/E 25-50)
- HYPER_GROWTH stocks (P/E > 50, negative, or None)
- Boundary cases (exactly 25, exactly 50)
- Edge cases (None, negative, zero, extreme values)
"""

import pytest

from pe_scanner.analysis.classification import (
    StockType,
    classify_stock_type,
    get_analysis_mode_name,
)


# =============================================================================
# VALUE Stock Tests (P/E < 25)
# =============================================================================


def test_classify_value_stock_typical():
    """Test typical value stock with P/E around 15."""
    result = classify_stock_type(15.0)
    assert result == StockType.VALUE


def test_classify_value_stock_low():
    """Test low P/E value stock (P/E = 5)."""
    result = classify_stock_type(5.0)
    assert result == StockType.VALUE


def test_classify_value_stock_high():
    """Test high-end value stock (P/E = 24.9)."""
    result = classify_stock_type(24.9)
    assert result == StockType.VALUE


def test_classify_value_stock_very_low():
    """Test very low P/E (P/E = 1.0) - still positive."""
    result = classify_stock_type(1.0)
    assert result == StockType.VALUE


def test_classify_value_stock_near_zero():
    """Test P/E very close to zero but positive (0.1)."""
    result = classify_stock_type(0.1)
    assert result == StockType.VALUE


# =============================================================================
# GROWTH Stock Tests (P/E 25-50)
# =============================================================================


def test_classify_growth_stock_typical():
    """Test typical growth stock with P/E around 35."""
    result = classify_stock_type(35.0)
    assert result == StockType.GROWTH


def test_classify_growth_stock_low():
    """Test low-end growth stock (P/E = 27)."""
    result = classify_stock_type(27.0)
    assert result == StockType.GROWTH


def test_classify_growth_stock_high():
    """Test high-end growth stock (P/E = 48)."""
    result = classify_stock_type(48.0)
    assert result == StockType.GROWTH


def test_classify_growth_stock_boundary_25():
    """Test boundary case: P/E exactly 25 should be GROWTH."""
    result = classify_stock_type(25.0)
    assert result == StockType.GROWTH


def test_classify_growth_stock_boundary_50():
    """Test boundary case: P/E exactly 50 should be GROWTH."""
    result = classify_stock_type(50.0)
    assert result == StockType.GROWTH


def test_classify_growth_stock_just_above_25():
    """Test P/E just above 25 (25.01)."""
    result = classify_stock_type(25.01)
    assert result == StockType.GROWTH


def test_classify_growth_stock_just_below_50():
    """Test P/E just below 50 (49.99)."""
    result = classify_stock_type(49.99)
    assert result == StockType.GROWTH


# =============================================================================
# HYPER_GROWTH Stock Tests (P/E > 50 or invalid)
# =============================================================================


def test_classify_hyper_growth_stock_typical():
    """Test typical hyper-growth stock with P/E around 75."""
    result = classify_stock_type(75.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_extreme():
    """Test extreme P/E (P/E = 200)."""
    result = classify_stock_type(200.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_very_high():
    """Test very high P/E (P/E = 1000)."""
    result = classify_stock_type(1000.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_just_above_50():
    """Test P/E just above 50 (50.01) - should be HYPER_GROWTH."""
    result = classify_stock_type(50.01)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_none():
    """Test None P/E (no earnings data) - should be HYPER_GROWTH."""
    result = classify_stock_type(None)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_negative():
    """Test negative P/E (loss-making) - should be HYPER_GROWTH."""
    result = classify_stock_type(-10.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_negative_small():
    """Test small negative P/E (-0.5) - should be HYPER_GROWTH."""
    result = classify_stock_type(-0.5)
    assert result == StockType.HYPER_GROWTH


def test_classify_hyper_growth_stock_negative_large():
    """Test large negative P/E (-100) - should be HYPER_GROWTH."""
    result = classify_stock_type(-100.0)
    assert result == StockType.HYPER_GROWTH


# =============================================================================
# Edge Cases
# =============================================================================


def test_classify_stock_zero():
    """Test P/E of exactly zero - should be HYPER_GROWTH (invalid)."""
    # Zero is not positive, so it fails the validity check
    result = classify_stock_type(0.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_stock_float_precision():
    """Test float precision around boundaries."""
    # Just below 25
    assert classify_stock_type(24.999999) == StockType.VALUE
    # Just at 25
    assert classify_stock_type(25.000000) == StockType.GROWTH
    # Just above 50
    assert classify_stock_type(50.000001) == StockType.HYPER_GROWTH


def test_classify_stock_large_value():
    """Test extremely large P/E value."""
    result = classify_stock_type(999999.0)
    assert result == StockType.HYPER_GROWTH


# =============================================================================
# Real-World Examples (From PRD)
# =============================================================================


def test_classify_hood_value():
    """Test HOOD example from PRD - VALUE stock."""
    # HOOD has trailing P/E around 47.62 → Should be GROWTH actually
    result = classify_stock_type(47.62)
    assert result == StockType.GROWTH


def test_classify_crm_growth():
    """Test CRM example from PRD - GROWTH stock."""
    # Typical CRM P/E around 30-40
    result = classify_stock_type(35.0)
    assert result == StockType.GROWTH


def test_classify_pltr_hyper_growth():
    """Test PLTR example from PRD - HYPER_GROWTH stock."""
    # PLTR often has P/E > 50
    result = classify_stock_type(85.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_rivn_hyper_growth():
    """Test RIVN example from PRD - HYPER_GROWTH (loss-making)."""
    # RIVN is loss-making → negative P/E
    result = classify_stock_type(-20.0)
    assert result == StockType.HYPER_GROWTH


def test_classify_nvda_hyper_growth():
    """Test NVDA example from PRD - likely HYPER_GROWTH due to high valuation."""
    # NVDA can have P/E around 60-80
    result = classify_stock_type(70.0)
    assert result == StockType.HYPER_GROWTH


# =============================================================================
# Analysis Mode Name Tests
# =============================================================================


def test_get_analysis_mode_name_value():
    """Test getting analysis mode name for VALUE."""
    name = get_analysis_mode_name(StockType.VALUE)
    assert name == "VALUE (P/E Compression)"


def test_get_analysis_mode_name_growth():
    """Test getting analysis mode name for GROWTH."""
    name = get_analysis_mode_name(StockType.GROWTH)
    assert name == "GROWTH (PEG Ratio)"


def test_get_analysis_mode_name_hyper_growth():
    """Test getting analysis mode name for HYPER_GROWTH."""
    name = get_analysis_mode_name(StockType.HYPER_GROWTH)
    assert name == "HYPER_GROWTH (Price/Sales)"


# =============================================================================
# Enum Tests
# =============================================================================


def test_stock_type_enum_values():
    """Test StockType enum has correct values."""
    assert StockType.VALUE.value == "value"
    assert StockType.GROWTH.value == "growth"
    assert StockType.HYPER_GROWTH.value == "hyper_growth"


def test_stock_type_enum_members():
    """Test StockType enum has exactly 3 members."""
    members = list(StockType)
    assert len(members) == 3
    assert StockType.VALUE in members
    assert StockType.GROWTH in members
    assert StockType.HYPER_GROWTH in members


# =============================================================================
# Parametrized Tests (Coverage)
# =============================================================================


@pytest.mark.parametrize(
    "pe,expected",
    [
        # VALUE range
        (0.5, StockType.VALUE),
        (5.0, StockType.VALUE),
        (10.0, StockType.VALUE),
        (15.0, StockType.VALUE),
        (20.0, StockType.VALUE),
        (24.0, StockType.VALUE),
        (24.99, StockType.VALUE),
        # GROWTH range
        (25.0, StockType.GROWTH),
        (25.01, StockType.GROWTH),
        (30.0, StockType.GROWTH),
        (35.0, StockType.GROWTH),
        (40.0, StockType.GROWTH),
        (45.0, StockType.GROWTH),
        (49.99, StockType.GROWTH),
        (50.0, StockType.GROWTH),
        # HYPER_GROWTH range
        (50.01, StockType.HYPER_GROWTH),
        (60.0, StockType.HYPER_GROWTH),
        (75.0, StockType.HYPER_GROWTH),
        (100.0, StockType.HYPER_GROWTH),
        (200.0, StockType.HYPER_GROWTH),
        (1000.0, StockType.HYPER_GROWTH),
        # Invalid values
        (None, StockType.HYPER_GROWTH),
        (0.0, StockType.HYPER_GROWTH),
        (-1.0, StockType.HYPER_GROWTH),
        (-10.0, StockType.HYPER_GROWTH),
        (-100.0, StockType.HYPER_GROWTH),
    ],
)
def test_classify_stock_type_parametrized(pe, expected):
    """Parametrized test covering full P/E range and edge cases."""
    result = classify_stock_type(pe)
    assert result == expected, f"P/E {pe} should classify as {expected.value}"

